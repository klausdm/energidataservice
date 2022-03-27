"""Support for Energi Data Service sensor."""
from collections import defaultdict
import logging
from datetime import datetime

from currency_converter import CurrencyConverter
import homeassistant.helpers.config_validation as cv
from homeassistant.components import sensor
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.template import Template, attach
from homeassistant.util import dt as dt_utils
from homeassistant.util import slugify as util_slugify
from homeassistant.const import (
    DEVICE_CLASS_MONETARY,
)

from jinja2 import contextfunction

from .const import (
    CONF_AREA,
    CONF_VAT,
    CONF_DECIMALS,
    CONF_TEMPLATE,
    CONF_PRICETYPE,
    PRICE_IN,
    DOMAIN,
    DEFAULT_TEMPLATE,
    UPDATE_EDS,
)
from .entity import EnergidataserviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform from a config entry."""
    config = config_entry.data
    _setup(hass, config, async_add_devices)
    return True


def _setup(hass, config, add_devices):
    """Setup the damn platform using yaml."""
    _LOGGER.debug("Dumping config %r", config)
    _LOGGER.debug("Timezone set in ha %r", hass.config.time_zone)
    _LOGGER.debug("Currency set in ha %r", hass.config.currency)
    area = config.get(CONF_AREA)
    price_type = config.get(CONF_PRICETYPE)
    decimals = config.get(CONF_DECIMALS)
    currency = hass.config.currency
    vat = config.get(CONF_VAT)
    cost_template = config.get(CONF_TEMPLATE)
    api = hass.data[DOMAIN]
    sens = EnergidataserviceSensor(
        area,
        price_type,
        decimals,
        currency,
        vat,
        api,
        cost_template,
        hass,
    )

    add_devices([sens])


class EnergidataserviceSensor(EnergidataserviceEntity):
    """Representation of Energi Data Service data."""

    def __init__(
        self,
        area,
        price_type,
        decimals,
        currency,
        vat,
        api,
        cost_template,
        hass,
    ) -> None:
        """Initialize Ally binary_sensor."""
        self._area = area
        self._currency = currency
        self._price_type = price_type
        self._decimals = decimals
        self._api = api
        self._cost_template = cost_template
        self._hass = hass
        self._friendly_name = f"Energi Data Service {area}"
        self._entity_id = sensor.ENTITY_ID_FORMAT.format(
            util_slugify(self._friendly_name)
        )
        self._unique_id = f"energidataservice_{area}"

        # Currently only supports Danish VAT.
        if vat is True:
            self._vat = 0.25
        else:
            self._vat = 0

        # Holds current price
        self._state = None

        # Holds today and tomorrow data
        self._today = None
        self._tomorrow = None

        # Holds lowest and highest prices for today
        self._today_lowpoint = {}
        self._today_highpoint = {}

        # Holds lowest and highest prices for tomorrow
        self._tomorrow_lowpoint = {}
        self._tomorrow_highpoint = {}

        # Check incase the sensor was setup using config flow.
        # This blow up if the template isnt valid.
        if not isinstance(self._cost_template, Template):
            if self._cost_template in (None, ""):
                self._cost_template = DEFAULT_TEMPLATE
            self._cost_template = cv.template(self._cost_template)
        # check for yaml setup.
        else:
            if self._cost_template.template in ("", None):
                self._cost_template = cv.template(DEFAULT_TEMPLATE)

        attach(self._hass, self._cost_template)

        # To control the updates.
        self._last_tick = None
        self._cbs = []

    async def validate_data(self) -> None:
        """Validate sensor data."""
        _LOGGER.debug("Validating sensor %s", self.name)
        if self._last_tick is None:
            self._last_tick = dt_utils.now()

        if not self._api.today:
            _LOGGER.debug("No sensor data found - calling update")
            await self._api.update()

        self._api.today = self._format_list(self._api.today)

        # Updates price for this hour.
        await self._get_current_price()

        # self.async_write_ha_state()

    async def _get_current_price(self) -> None:
        """Get price for current hour"""
        # now = dt_utils.now()
        current_state_time = datetime.fromisoformat(
            dt_utils.now()
            .replace(microsecond=0)
            .replace(second=0)
            .replace(minute=0)
            .isoformat()
        )

        if self._api.today:
            for dataset in self._api.today:
                if dataset["hour"] == current_state_time:
                    self._state = dataset["price"]
                    _LOGGER.debug("Current price updated to %f", self._state)
                    break
        else:
            _LOGGER.debug("No data found, can't update _state")

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        await super().async_added_to_hass()
        _LOGGER.debug("Added sensor '%s'", self._entity_id)
        await self.validate_data()
        async_dispatcher_connect(self._hass, UPDATE_EDS, self.validate_data)

    @staticmethod
    def _convert_currency(currency_from, currency_to, value):
        """Convert currency"""
        c = CurrencyConverter()
        return c.convert(value, currency_from, currency_to)

    def _calculate(self, value=None, fake_dt=None) -> float:
        """Do price calculations"""
        if value is None:
            value = self._state

        # Convert currency from EUR
        if self._currency != "EUR":
            value = self._convert_currency("EUR", self._currency, value)

        # Used to inject the current hour.
        # so template can be simplified using now
        if fake_dt is not None:

            def faker():
                def inner(*args, **kwargs):
                    return fake_dt

                return contextfunction(inner)

            template_value = self._cost_template.async_render(now=faker())
        else:
            template_value = self._cost_template.async_render()

        # The api returns prices in MWh
        if self._price_type in ("MWh", "mWh"):
            price = template_value / 1000 + value * float(1 + self._vat)
        else:
            price = template_value + value / PRICE_IN[self._price_type] * (
                float(1 + self._vat)
            )

        return round(price, self._decimals)

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def icon(self) -> str:
        return "mdi:flash"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._friendly_name

    @property
    def state(self):
        """Return sensor state."""
        # res = self._calculate()
        # return res
        return self._state

    @property
    def unit(self) -> str:
        """Return currency unit."""
        return self._price_type

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "current_price": self.state,
            "unit": self.unit,
            "currency": self._currency,
            "area": self._area,
            "tomorrow_valid": self.tomorrow_valid,
            "today": self.today,
            "tomorrow": self.tomorrow,
            "raw_today": self.raw_today,
            "raw_tomorrow": self.raw_tomorrow,
            "today_lowpoint": self.today_lowpoint,
            "today_highpoint": self.today_highpoint,
            "tomorrow_lowpoint": self.tomorrow_lowpoint,
            "tomorrow_highpoint": self.tomorrow_highpoint,
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return f"{self._currency}/{self._price_type}"

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return DEVICE_CLASS_MONETARY

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Energi Data Service",
        }

    @property
    def today(self) -> list:
        """Get todays prices
        Returns:
            list: sorted list where today[0] is the price of hour 00.00 - 01.00
        """

        return [i["price"] for i in self._api.today if i]
        # return None

    @property
    def tomorrow(self) -> list:
        """Get tomorrows prices
        Returns:
            list: sorted where tomorrow[0] is the price of hour 00.00 - 01.00 etc.
        """
        if self._api.tomorrow_valid:
            return [i["price"] for i in self._api.tomorrow if i]
        else:
            return None

    @property
    def raw_today(self):
        """Return the raw array with todays prices."""
        return self._api.today

    @property
    def raw_tomorrow(self):
        """Return the raw array with tomorrows prices."""
        return self._api.tomorrow

    @property
    def tomorrow_valid(self):
        """Return state of tomorrow_valid."""
        return self._api.tomorrow_valid

    @property
    def today_lowpoint(self):
        """Return lowpoint for today."""
        return self._get_specific("min", self._api.today)

    @property
    def today_highpoint(self):
        """Return highpoint for today."""
        return self._get_specific("max", self._api.today)

    @property
    def tomorrow_lowpoint(self):
        """Return lowpoint for tomorrow."""
        return self._get_specific("min", self._api.tomorrow)

    @property
    def tomorrow_highpoint(self):
        """Return highpoint for tomorrow."""
        return self._get_specific("max", self._api.tomorrow)

    def _format_list(self, data) -> list:
        """Format data as list with prices localized."""
        formatted_pricelist = []
        for i in data:
            val = defaultdict(dict)
            val["price"] = self._calculate(
                i.get("value"), fake_dt=dt_utils.as_local(i.get("start"))
            )
            val["hour"] = i.get("start")
            formatted_pricelist.append(val)
        return formatted_pricelist

    @staticmethod
    def _get_specific(datatype, data):
        """Get specific values - ie. min, max, mean values"""

        if datatype in ["MIN", "Min", "min"]:
            if data:
                ret = None
                val = None
                for i in data:
                    if ret is None:
                        ret = i["price"]
                        val = i
                    elif i["price"] < ret:
                        ret = i["price"]
                        val = i
                return val
            else:
                return None
        elif datatype in ["MAX", "Max", "max"]:
            if data:
                ret = None
                val = None
                for i in data:
                    if ret is None:
                        ret = i["price"]
                        val = i
                    elif i["price"] > ret:
                        ret = i["price"]
                        val = i
                return val
            else:
                return None
        else:
            return None