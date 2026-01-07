from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    auth_key: str = "empty" # for accessing this app
    nextcloud_url: str = "empty"
    nextcloud_user: str = "empty"
    nextcloud_password: str = "empty"
    nextcloud_folder: str = "empty"

    #API KEYS -----------------------------------------------------------
    openweather_api_key: str = "empty"
    crypto_api: str = "empty"

    #WEATHER -----------------------------------------------------------
    units: str = "metric"

    #Crypto ---------------------------------------------------
    crypto_vs_currency: str = "usd"
    crypto_graph_history_days: int = 30
    crypto_coin_ids: str = "bitcoin,solana,ethereum,litecoin"

    #First City - Ludwigsfelde
    first_city_weather_latitude: str = "52.30322"
    first_city_weather_longitude: str = "13.25405"

    #Second City - Leipzig
    second_city_weather_latitude: str = "51.33962"
    second_city_weather_longitude: str = "12.37129"

    #Calendar ---------------------------------------------------
    calendar_ical_url: str = "empty"
    calendar_garbage_url: str = "empty"
    calendar_holidays_url: str = "https://calendar.google.com/calendar/ical/de.german%23holiday%40group.v.calendar.google.com/public/basic.ics"

    #Countdown ---------------------------------------------------------
    countdown_date: str = "2026-09-31"  # YYYY-MM-DD


    flask_port: int = 5000
    flask_debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()