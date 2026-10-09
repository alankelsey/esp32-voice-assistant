"""get_weather via Open-Meteo (no API key), in °F / mph.

Registers under the tool name "get_weather". The plugin loader imports modules
alphabetically, so this file (get_weather_openmeteo) loads after upstream's
QWeather get_weather and replaces it in the registry.
"""
import httpx
from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action

TAG = __name__
logger = setup_logging()

DEFAULT_NAME = "Nampa, Idaho"
DEFAULT_LAT, DEFAULT_LON = 43.54, -116.56

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes -> short spoken phrases
WMO = {
    0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "foggy with rime",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    56: "freezing drizzle", 57: "heavy freezing drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    66: "freezing rain", 67: "heavy freezing rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
    80: "light showers", 81: "showers", 82: "heavy showers",
    85: "snow showers", 86: "heavy snow showers",
    95: "thunderstorms", 96: "thunderstorms with hail", 99: "severe thunderstorms with hail",
}

GET_WEATHER_FUNCTION_DESC = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Get the current weather and today's high and low. Call this whenever the user "
            "asks about weather, temperature, rain, snow or wind. If the user names a place, "
            "pass it as location; otherwise omit location to use the default (Nampa, Idaho)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, optionally with state or country, e.g. 'Boise' or 'Portland, Oregon'.",
                }
            },
            "required": [],
        },
    },
}


def _geocode(client: httpx.Client, location: str):
    city, _, region = (p.strip() for p in location.partition(","))
    r = client.get(GEOCODE_URL, params={"name": city, "count": 10, "language": "en", "format": "json"})
    r.raise_for_status()
    results = r.json().get("results") or []
    if not results:
        return None
    if region:  # prefer a match on state/country when the user gave one
        rl = region.lower()
        for res in results:
            if rl in (res.get("admin1", "").lower(), res.get("country", "").lower(), res.get("country_code", "").lower()):
                return res
    # otherwise prefer US results (the household is in Idaho), then the most populous
    us = [res for res in results if res.get("country_code") == "US"]
    return (us or results)[0]


def weather_report(location: str = None) -> str:
    with httpx.Client(timeout=10) as client:
        if location and location.strip():
            place = _geocode(client, location)
            if not place:
                return f"I couldn't find a place called {location}."
            name = ", ".join(x for x in (place.get("name"), place.get("admin1")) if x)
            lat, lon = place["latitude"], place["longitude"]
        else:
            name, lat, lon = DEFAULT_NAME, DEFAULT_LAT, DEFAULT_LON

        r = client.get(FORECAST_URL, params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min",
            "temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
            "timezone": "auto", "forecast_days": 1,
        })
        r.raise_for_status()
        d = r.json()

    cur, daily = d["current"], d["daily"]
    sky = WMO.get(cur["weather_code"], "unknown conditions")
    return (
        f"Weather for {name}: currently {round(cur['temperature_2m'])}°F and {sky}, "
        f"wind {round(cur['wind_speed_10m'])} mph. "
        f"Today's high {round(daily['temperature_2m_max'][0])}°F, low {round(daily['temperature_2m_min'][0])}°F."
    )


@register_function("get_weather", GET_WEATHER_FUNCTION_DESC, ToolType.WAIT)
def get_weather(location: str = None):
    try:
        report = weather_report(location)
    except Exception as e:
        logger.bind(tag=TAG).error(f"Open-Meteo request failed: {e}")
        return ActionResponse(Action.REQLLM, "The weather service could not be reached.", None)
    logger.bind(tag=TAG).info(report)
    return ActionResponse(Action.REQLLM, report, None)
