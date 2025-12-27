from app.config.config import settings
import requests
from flask import jsonify
from datetime import datetime


#First City - Ludwigsfelde ------------------------------------------------------------
def get_weather_first_city():
    if settings.openweather_api_key:
        try:
            resp = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": settings.first_city_weather_latitude,
                    "lon": settings.first_city_weather_longitude,
                    "appid": settings.openweather_api_key,
                    "units": settings.units,
                    "lang": "en",
                },
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            return jsonify({
                "source": "openweathermap",
                "units": settings.units,
                "city": data.get("name") or "Ludwigsfelde",
                "temp": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "icon": (data.get("weather") or [{}])[0].get("icon"),
                "sunrise": data.get("sys", {}).get("sunrise"),
                "sunset": data.get("sys", {}).get("sunset"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "rain_precipitation": data.get("rain", {}).get("1h"),
            })
        except Exception:
            pass

    return jsonify({
        "source": "static",
        "units": settings.units,
        "city": "Ludwigsfelde",
        "temp": 18.0,
        "temp_min": 16.0,
        "temp_max": 20.0,
        "feels_like": 18.5,
        "description": "clear sky",
        "icon": "01d",
        "wind_speed": 5.0,
        "rain_precipitation": None,
    })

def get_weather_forecast_first_city():
    if not settings.openweather_api_key:
        raise ValueError("Missing OpenWeather API key in settings")

    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={
            "lat": settings.first_city_weather_latitude,
            "lon": settings.first_city_weather_longitude,
            "units": settings.units,
            "appid": settings.openweather_api_key,
        },
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()

    forecasts = data.get("list", [])
    if not forecasts:
        raise ValueError("No forecast data returned")

    days = {}
    for entry in forecasts:
        dt = datetime.utcfromtimestamp(entry["dt"])
        day = dt.date()
        if day == datetime.utcnow().date():  # Skip today
            continue
        temp = entry["main"]["temp"]
        desc = entry["weather"][0]["description"]
        icon = entry["weather"][0]["icon"]

        if day not in days:
            days[day] = {
                "temps": [],
                "descriptions": [desc],
                "icons": [icon],
                "dt": entry["dt"],
            }
        days[day]["temps"].append(temp)

    items = []
    for i, (day, values) in enumerate(sorted(days.items())):
        temps = values["temps"]
        items.append({
            "dt": values["dt"],
            "date": day.isoformat(),
            "temp": sum(temps) / len(temps),
            "temp_min": min(temps),
            "temp_max": max(temps),
            "description": values["descriptions"][0],
            "icon": values["icons"][0],
        })
        if i == 3:  # only next 4 days
            break

    return jsonify({
        "source": "openweathermap",
        "units": settings.units,
        "items": items,
    })


#Second City - Leipzig ----------------------------------------------------------------
def get_weather_second_city():
    if settings.openweather_api_key:
        try:
            resp = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": settings.second_city_weather_latitude,
                    "lon": settings.second_city_weather_longitude,
                    "appid": settings.openweather_api_key,
                    "units": settings.units,
                    "lang": "en",
                },
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            return jsonify({
                "source": "openweathermap",
                "units": settings.units,
                "city": data.get("name") or "Leipzig",
                "temp": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "icon": (data.get("weather") or [{}])[0].get("icon"),
                "sunrise": data.get("sys", {}).get("sunrise"),
                "sunset": data.get("sys", {}).get("sunset"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "rain_precipitation": data.get("rain", {}).get("1h"),
            })
        except Exception:
            pass

    return jsonify({
        "source": "static",
        "units": settings.units,
        "city": "Leipzig",
        "temp": 18.0,
        "temp_min": 16.0,
        "temp_max": 20.0,
        "feels_like": 18.5,
        "description": "clear sky",
        "icon": "01d",
        "wind_speed": 5.0,
        "rain_precipitation": None,
    })

def get_weather_forecast_second_city():
    if not settings.openweather_api_key:
        raise ValueError("Missing OpenWeather API key in settings")

    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={
            "lat": settings.second_city_weather_latitude,
            "lon": settings.second_city_weather_longitude,
            "units": settings.units,
            "appid": settings.openweather_api_key,
        },
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()

    forecasts = data.get("list", [])
    if not forecasts:
        raise ValueError("No forecast data returned")

    days = {}
    for entry in forecasts:
        dt = datetime.utcfromtimestamp(entry["dt"])
        day = dt.date()
        if day == datetime.utcnow().date():  # Skip today
            continue
        temp = entry["main"]["temp"]
        desc = entry["weather"][0]["description"]
        icon = entry["weather"][0]["icon"]

        if day not in days:
            days[day] = {
                "temps": [],
                "descriptions": [desc],
                "icons": [icon],
                "dt": entry["dt"],
            }
        days[day]["temps"].append(temp)

    items = []
    for i, (day, values) in enumerate(sorted(days.items())):
        temps = values["temps"]
        items.append({
            "dt": values["dt"],
            "date": day.isoformat(),
            "temp": sum(temps) / len(temps),
            "temp_min": min(temps),
            "temp_max": max(temps),
            "description": values["descriptions"][0],
            "icon": values["icons"][0],
        })
        if i == 3:  # only next 4 days
            break

    return jsonify({
        "source": "openweathermap",
        "units": settings.units,
        "items": items,
    })