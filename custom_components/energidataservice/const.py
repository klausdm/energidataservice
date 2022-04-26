""" Energidataservice consts """
STARTUP = """
-------------------------------------------------------------------
Energi Data Service integration

Version: %s
This is a custom integration
If you have any issues with this you need to open an issue here:
https://github.com/mtrab/energidataservice/issues
-------------------------------------------------------------------
"""

AREA_DK_EAST = "East of the great belt"
AREA_DK_WEST = "West of the great belt"

CONF_AREA = "area"
CONF_COUNTRY = "country"
CONF_CURRENCY_IN_CENT = "in_cent"
CONF_DECIMALS = "decimals"
CONF_PRICETYPE = "pricetype"
CONF_TEMPLATE = "cost_template"
CONF_VAT = "vat"

DATA = "data"
DEFAULT_NAME = "Energidataservice"
DEFAULT_TEMPLATE = "{{0.0|float}}"
DOMAIN = "energidataservice"

LIMIT = "48"

UNIQUE_ID = "unique_id"
UPDATE_EDS = "eds_update"

# Multiplier mappings
UNIT_TO_MULTIPLIER = {"MWh": 0, "kWh": 1000, "Wh": 1000000}
MULTIPLIER_TO_UNIT = {0: "MWh", 1000: "kWh", 1000000: "Wh"}
CENT_MULTIPLIER = 100

# Currency settings
_CURRENCY = {
    "DKK": {
        "name": "DKK",
        "symbol": "Kr",
        "cent": "Øre",
    },
    "NOK": {
        "name": "NOK",
        "symbol": "Kr",
        "cent": "Øre",
    },
    "SEK": {
        "name": "SEK",
        "symbol": "Kr",
        "cent": "Öre",
    },
    "EUR": {
        "name": "EUR",
        "symbol": "€",
        "cent": "c",
    },
    "USD": {
        "name": "USD",
        "symbol": "$",
        "cent": "¢",
    },
}

# Regions
# Format:
#   "Region": [_CURRENCY, "Country", "Region description", VAT, DictOfEndpoints]
_REGIONS = {
    "DK1": [
        _CURRENCY["DKK"],
        "Denmark",
        "West of the great belt",
        0.25,
        {"energidataservice", "nordpool"},
    ],
    "DK2": [
        _CURRENCY["DKK"],
        "Denmark",
        "East of the great belt",
        0.25,
        {"energidataservice", "nordpool"},
    ],
    "FI": [_CURRENCY["EUR"], "Finland", "Finland", 0.24, {"nordpool"}],
    "EE": [_CURRENCY["EUR"], "Estonia", "Estonia", 0.20, {"nordpool"}],
    "LT": [_CURRENCY["EUR"], "Lithuania", "Lithuania", 0.21, {"nordpool"}],
    "LV": [_CURRENCY["EUR"], "Latvia", "Latvia", 0.21, {"nordpool"}],
    "Oslo": [_CURRENCY["NOK"], "Norway", "Oslo", 0.25, {"nordpool"}],
    "Kr.Sand": [
        _CURRENCY["NOK"],
        "Norway",
        "Kristiansand",
        0.25,
        {"energidataservice", "nordpool"},
    ],
    "Molde": [_CURRENCY["NOK"], "Norway", "Molde, Trondheim", 0.25, {"nordpool"}],
    "Tromsø": [_CURRENCY["NOK"], "Norway", "Tromsø", 0.25, {"nordpool"}],
    "Bergen": [_CURRENCY["NOK"], "Norway", "Bergen", 0.25, {"nordpool"}],
    "SE1": [_CURRENCY["SEK"], "Sweden", "Luleå", 0.25, {"nordpool"}],
    "SE2": [_CURRENCY["SEK"], "Sweden", "Sundsvall", 0.25, {"nordpool"}],
    "SE3": [
        _CURRENCY["SEK"],
        "Sweden",
        "Stockholm",
        0.25,
        {"energidatabase", "nordpool"},
    ],
    "SE4": [
        _CURRENCY["SEK"],
        "Sweden",
        "Malmö",
        0.25,
        {"energidataservice", "nordpool"},
    ],
    "FR": [_CURRENCY["EUR"], "France", "France", 0.055, {"nordpool"}],
    "NL": [_CURRENCY["EUR"], "Netherlands", "Netherlands", 0.21, {"nordpool"}],
    "BE": [_CURRENCY["EUR"], "Belgium", "Belgium", 0.21, {"nordpool"}],
    "AT": [_CURRENCY["EUR"], "Austria", "Austria", 0.20, {"nordpool"}],
    "DE": [
        _CURRENCY["EUR"],
        "Germany",
        "Germany",
        0.19,
        {"energidataservice", "nordpool"},
    ],
}

# Mappings - OLD STYLE
AREA_MAP = {  # Text-to-area
    AREA_DK_WEST: "DK1",
    AREA_DK_EAST: "DK2",
}
AREA_TO_TEXT = {  # Area-to-text
    "DK1": AREA_DK_WEST,
    "DK2": AREA_DK_EAST,
}
CURRENCIES = {  # Currencies
    "Danske Kroner": "DKK",
    "Euro": "EUR",
}

# REGIONS = sorted(list(AREA_MAP.keys()))
CURRENCY = sorted(list(CURRENCIES.keys()))
