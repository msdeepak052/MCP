import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")


def weather_code_to_description(code: int) -> str:
    """Convert WMO weather code to a human-readable description."""
    codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, f"Unknown condition (code {code})")


@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for any city in the world."""

    # Step 1: Convert city name to latitude/longitude using Open-Meteo geocoding API
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}

    with httpx.Client() as client:
        geo_response = client.get(geo_url, params=geo_params)
        geo_data = geo_response.json()

    if not geo_data.get("results"):
        return f"City '{city}' not found. Please check the spelling and try again."

    result = geo_data["results"][0]
    lat = result["latitude"]
    lon = result["longitude"]
    name = result["name"]
    country = result.get("country", "")

    # Step 2: Fetch current weather using Open-Meteo weather API
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "wind_speed_unit": "kmh",
    }

    with httpx.Client() as client:
        weather_response = client.get(weather_url, params=weather_params)
        weather_data = weather_response.json()

    current = weather_data["current"]
    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind = current["wind_speed_10m"]
    condition = weather_code_to_description(current["weather_code"])

    return (
        f"Weather in {name}, {country}:\n"
        f"  Condition  : {condition}\n"
        f"  Temperature: {temp}°C\n"
        f"  Humidity   : {humidity}%\n"
        f"  Wind Speed : {wind} km/h"
    )


if __name__ == "__main__":
    mcp.run()
