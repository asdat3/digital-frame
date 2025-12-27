import requests
from app.config.config import settings
from flask import jsonify, request
from app.modules.crypto_cache import get_cache_key, get_cached_or_fetch, get_cached_response

def _fetch_coin_list():
    """Internal function to fetch coin list from API."""
    resp = requests.get(
        "https://api.coingecko.com/api/v3/coins/list",
        headers={
            "x-cg-demo-api-key": settings.crypto_api,
        },
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()


def get_coin_id():
    """
    Get list of all available coins from CoinGecko API.
    Uses caching to prevent rate limiting (10-minute cache).
    
    Returns:
        JSON response with coin list or error message
    """
    if not settings.crypto_api or settings.crypto_api == "empty":
        return jsonify({
            "error": "Crypto API is not set",
            "data": [],
        }), 200
    
    try:
        cache_key = get_cache_key("https://api.coingecko.com/api/v3/coins/list")
        data = get_cached_or_fetch(cache_key, _fetch_coin_list)
        return jsonify({"data": data}), 200
    except Exception as e:
        cache_key = get_cache_key("https://api.coingecko.com/api/v3/coins/list")
        cached_data = get_cached_response(cache_key)
        if cached_data is not None:
            return jsonify({"data": cached_data}), 200
        return jsonify({
            "error": f"Failed to get coin ID: {str(e)}",
            "data": [],
        }), 500

def get_coin_config():
    """
    Get coin configuration from CoinGecko API.
    
    Returns:
        JSON response with coin configuration
    """
    coin_config = {
        "bitcoin": {
            "name": "Bitcoin",
            "imageUrl": "https://assets.coingecko.com/coins/images/1/small/bitcoin.png",
        },
        "ethereum": {
            "name": "Ethereum",
            "imageUrl": "https://assets.coingecko.com/coins/images/279/small/ethereum.png",
        },
        "solana": {
            "name": "Solana",
            "imageUrl": "https://assets.coingecko.com/coins/images/4128/small/solana.png",
        },
        "litecoin": {
            "name": "Litecoin",
            "imageUrl": "https://assets.coingecko.com/coins/images/2/small/litecoin.png",
        },
    }

    coin_colors = {
        "bitcoin":  {"border": "rgba(255, 140, 0, 0.8)",  "background": "rgba(247, 147, 26, 0.1)"},
        "ethereum": {"border": "rgba(59, 130, 246, 0.8)", "background": "rgba(59, 130, 246, 0.1)"},
        "solana":   {"border": "rgba(138, 43, 226, 0.8)",  "background": "rgba(138, 43, 226, 0.1)"},
        "litecoin": {"border": "rgba(136, 136, 136, 0.8)", "background": "rgba(191, 191, 191, 0.1)"},
    }

    coin_ids_list = [coin_id.strip() for coin_id in settings.crypto_coin_ids.split(',') if coin_id.strip()]
    
    return jsonify({
        "coin_ids": coin_ids_list,
        "coin_config": coin_config,
        "coin_colors": coin_colors,
    })

def _fetch_current_prices(coin_ids: str, vs_currencies: str):
    """Internal function to fetch current prices from API."""
    resp = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        headers={
            "x-cg-demo-api-key": settings.crypto_api,
        },
        params={
            "ids": coin_ids,
            "vs_currencies": vs_currencies,
        },
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()


def _fetch_yesterday_price_data(coin_id: str, vs_currency: str):
    """Internal function to fetch historical data for yesterday's price calculation."""
    hist_resp = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
        headers={
            "x-cg-demo-api-key": settings.crypto_api,
        },
        params={
            "vs_currency": vs_currency,
            "days": 2,
            "interval": "daily",
        },
        timeout=5,
    )
    hist_resp.raise_for_status()
    return hist_resp.json()


def get_current_crypto_price(coin_ids: str, vs_currencies: str):
    """
    Get current cryptocurrency prices and yesterday's prices from CoinGecko API.
    Uses caching to prevent rate limiting (10-minute cache).
    
    Args:
        coin_ids: Comma-separated coin IDs (default: "bitcoin")
        vs_currencies: Comma-separated target currencies (default: "usd")
    
    Returns:
        JSON response with price data (including yesterday's price) or error message
    """
    if not settings.crypto_api or settings.crypto_api == "empty":
        return jsonify({
            "error": "Crypto API is not set",
            "data": [],
        }), 200

    current_cache_key = get_cache_key(
        "https://api.coingecko.com/api/v3/simple/price",
        {"ids": coin_ids, "vs_currencies": vs_currencies}
    )
    
    # Always check for cached data first, even if expired
    cached_current = get_cached_response(current_cache_key)
    
    try:
        current_data = get_cached_or_fetch(
            current_cache_key,
            _fetch_current_prices,
            coin_ids,
            vs_currencies
        )
        
        coin_list = coin_ids.split(',')
        vs_currency = vs_currencies.split(',')[0]
        yesterday_data = {}
        
        for coin_id in coin_list:
            try:
                hist_cache_key = get_cache_key(
                    f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
                    {"vs_currency": vs_currency, "days": 2, "interval": "daily"}
                )
                hist_data = get_cached_or_fetch(
                    hist_cache_key,
                    _fetch_yesterday_price_data,
                    coin_id,
                    vs_currency
                )
                
                prices = hist_data.get("prices", [])
                if len(prices) >= 2:
                    yesterday_price = prices[-2][1]
                    yesterday_data[coin_id] = {"usd": yesterday_price}
                elif len(prices) == 1:
                    yesterday_price = prices[0][1]
                    yesterday_data[coin_id] = {"usd": yesterday_price}
            except Exception as e:
                hist_cache_key = get_cache_key(
                    f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
                    {"vs_currency": vs_currency, "days": 2, "interval": "daily"}
                )
                cached_hist = get_cached_response(hist_cache_key)
                if cached_hist is not None:
                    prices = cached_hist.get("prices", []) if isinstance(cached_hist, dict) else []
                    if len(prices) >= 2:
                        yesterday_data[coin_id] = {"usd": prices[-2][1]}
                    elif len(prices) == 1:
                        yesterday_data[coin_id] = {"usd": prices[0][1]}
        
        result = {}
        for coin_id, current_price_info in current_data.items():
            result[coin_id] = current_price_info.copy()
            if coin_id in yesterday_data:
                result[coin_id]["usd_yesterday"] = yesterday_data[coin_id]["usd"]
        
        return jsonify({"data": result}), 200
    except Exception as e:
        # If fetch failed, try to use any cached data we have (even if expired)
        if cached_current is not None:
            result = {}
            for coin_id, current_price_info in cached_current.items():
                result[coin_id] = current_price_info.copy()
            return jsonify({"data": result}), 200
        
        # Last resort: try to get cached data one more time
        cached_current = get_cached_response(current_cache_key)
        if cached_current is not None:
            result = {}
            for coin_id, current_price_info in cached_current.items():
                result[coin_id] = current_price_info.copy()
            return jsonify({"data": result}), 200
        
        return jsonify({
            "error": f"Failed to get crypto price: {str(e)}",
            "data": [],
        }), 500



def _fetch_historical_prices(coin_id: str, vs_currency: str, days: int, api_key: str):
    """Internal function to fetch historical prices from API."""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": "daily",
    }
    
    headers = {}
    if api_key and api_key != "empty":
        headers["x-cg-demo-api-key"] = api_key
    
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_historical_crypto_price(coin_id: str, vs_currency: str, days: int):
    """
    Get historical cryptocurrency prices from the CoinGecko API.
    Uses caching to prevent rate limiting (10-minute cache).

    Args:
        coin_id: Coin ID (e.g., "bitcoin", "ethereum")
        vs_currency: Target currency (e.g., "usd", "eur")
        days: Number of days of historical data to retrieve

    Returns:
        Flask JSON response with historical price data or error message
    """
    api_key = (request.headers.get("x-cg-demo-api-key") or 
               request.args.get("x_cg_demo_api_key") or 
               settings.crypto_api)
    
    if not api_key or api_key == "empty":
        return jsonify({
            "error": "Crypto API is not set",
            "prices": []
        }), 200

    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        cache_key = get_cache_key(url, {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily"
        })
        
        data = get_cached_or_fetch(
            cache_key,
            _fetch_historical_prices,
            coin_id,
            vs_currency,
            days,
            api_key
        )

        prices = data.get("prices", [])

        return jsonify({
            "coin": coin_id,
            "vs_currency": vs_currency,
            "days": days,
            "prices": prices
        }), 200

    except requests.exceptions.RequestException as e:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        cache_key = get_cache_key(url, {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily"
        })
        cached_data = get_cached_response(cache_key)
        if cached_data is not None:
            prices = cached_data.get("prices", []) if isinstance(cached_data, dict) else []
            return jsonify({
                "coin": coin_id,
                "vs_currency": vs_currency,
                "days": days,
                "prices": prices
            }), 200
        
        return jsonify({
            "error": f"Failed to fetch crypto prices: {str(e)}",
            "prices": []
        }), 500
