from flask import Flask, render_template, request, redirect, jsonify, Response
from app.config.config import settings
import logging
from app.modules.weather import (
    get_weather_first_city,
    get_weather_forecast_first_city,
    get_weather_second_city,
    get_weather_forecast_second_city,
)
from app.modules.calendar import return_calendar_events
from app.modules.crypto import get_current_crypto_price, get_historical_crypto_price, get_coin_config
from app.modules.daily_word import return_daily_word
from app.modules.nextcloud import get_random_image

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates",
)

logger = logging.getLogger(__name__)

@app.before_request
def require_auth_key():
    # logger.error("Request headers: %s", request.headers)
    header_key = request.headers.get("auth_key")
    # if not header_key or header_key != settings.auth_key:
    #     logger.error("Auth key is invalid")
    #     return redirect("https://ninawunder.com", code=302)

@app.route("/")
def index():
    return render_template("index.html", countdown_date=settings.countdown_date)


#WEATHER -----------------------------------------------------------------------
@app.route("/api/weather/first-city")
def api_weather_first_city():
    """Return weather JSON for Berlin using lat/lon."""
    return get_weather_first_city()


@app.route("/api/forecast/first-city")
def api_forecast_first_city():
    """Return short-term weather forecast (3 items)."""
    return get_weather_forecast_first_city()

@app.route("/api/weather/second-city")
def api_weather_second_city():
    """Return weather JSON for Leipzig using lat/lon."""
    return get_weather_second_city()

@app.route("/api/forecast/second-city")
def api_forecast_second_city():
    """Return short-term weather forecast (3 items)."""
    return get_weather_forecast_second_city()


#CALENDAR -----------------------------------------------------------------------
@app.route("/api/calendar")
def api_all_calendars():
    """Return events from all calendars (personal, holidays, garbage)."""
    return return_calendar_events()


#CRYPTO -----------------------------------------------------------------------
@app.route("/api/crypto-price")
def api_crypto_price():
    """
    Return current cryptocurrency prices from CoinGecko API.
    Queries prices for: bitcoin, solana, ethereum, and litecoin.
    """
    return get_current_crypto_price(settings.crypto_coin_ids, settings.crypto_vs_currency)

@app.route("/api/crypto-history/<coin_id>")
def api_crypto_price_history_single(coin_id):
    """Get last 4 days of historical prices for a single cryptocurrency."""
    return get_historical_crypto_price(coin_id, settings.crypto_vs_currency, settings.crypto_graph_history_days)

@app.route("/api/crypto-config")
def api_crypto_config():
    """Return frontend crypto config derived from environment."""
    return get_coin_config()

#DAILY WORD -----------------------------------------------------------------------
@app.route("/daily-word")
def daily_word():
    return return_daily_word()


#BACKGROUND -----------------------------------------------------------------------
@app.route("/api/background")
def api_background():
    """Return a random background image from Nextcloud."""
    result = get_random_image()
    if result:
        image_bytes, content_type = result
        return Response(image_bytes, mimetype=content_type)
    # Fallback to 404 if no image found
    return Response("No images found", status=404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.flask_port, debug=settings.flask_debug)

