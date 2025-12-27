"""
Caching module for CoinGecko API responses.
Implements a simple in-memory cache with 5-minute expiration to prevent rate limiting.
"""
import time
from typing import Optional, Dict, Any
from threading import Lock

# Cache storage: {cache_key: {"data": ..., "timestamp": ...}}
_cache: Dict[str, Dict[str, Any]] = {}
# Rate limit tracking: {cache_key: timestamp_of_last_429}
_rate_limit_errors: Dict[str, float] = {}
_cache_lock = Lock()

CACHE_EXPIRATION_SECONDS = 300
# After a 429 error, wait 10 minutes before trying again
RATE_LIMIT_COOLDOWN_SECONDS = 600


def get_cache_key(api_endpoint: str, params: Optional[Dict] = None) -> str:
    """
    Generate a unique cache key for an API request.
    
    Args:
        api_endpoint: The API endpoint URL
        params: Optional dictionary of query parameters
        
    Returns:
        A unique cache key string
    """
    if params:
        # Sort params for consistent key generation
        sorted_params = sorted(params.items())
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        return f"{api_endpoint}?{param_str}"
    return api_endpoint


def get_cached_response(cache_key: str) -> Optional[Any]:
    """
    Retrieve cached response if it exists (even if expired, for fallback use).
    
    Args:
        cache_key: The cache key to look up
        
    Returns:
        Cached data if exists, None otherwise
    """
    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]["data"]
    return None


def is_cache_valid(cache_key: str) -> bool:
    """
    Check if cached response exists and is still valid (not expired).
    
    Args:
        cache_key: The cache key to check
        
    Returns:
        True if cache exists and is valid, False otherwise
    """
    with _cache_lock:
        if cache_key in _cache:
            cached_item = _cache[cache_key]
            age = time.time() - cached_item["timestamp"]
            return age < CACHE_EXPIRATION_SECONDS
    return False


def set_cached_response(cache_key: str, data: Any) -> None:
    """
    Store a response in the cache.
    
    Args:
        cache_key: The cache key to store under
        data: The data to cache
    """
    with _cache_lock:
        _cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }


def _is_rate_limited(cache_key: str) -> bool:
    """
    Check if this cache key is currently in rate limit cooldown.
    
    Args:
        cache_key: The cache key to check
        
    Returns:
        True if we should not attempt to fetch (still in cooldown)
    """
    with _cache_lock:
        if cache_key in _rate_limit_errors:
            time_since_error = time.time() - _rate_limit_errors[cache_key]
            return time_since_error < RATE_LIMIT_COOLDOWN_SECONDS
    return False


def _record_rate_limit_error(cache_key: str) -> None:
    """Record that we got a rate limit error for this cache key."""
    with _cache_lock:
        _rate_limit_errors[cache_key] = time.time()


def _is_429_error(exception: Exception) -> bool:
    """Check if the exception is a 429 rate limit error."""
    # Check if it's a requests HTTPError with status 429
    if hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
        if exception.response.status_code == 429:
            return True
    
    # Fallback: check error string
    error_str = str(exception).lower()
    return "429" in error_str or "too many requests" in error_str


def get_cached_or_fetch(cache_key: str, fetch_func, *args, **kwargs) -> Any:
    """
    Get data from cache if available and valid, otherwise fetch and cache it.
    This function ensures we always return data, using expired cache as fallback if fetch fails.
    Implements rate limit cooldown: if we got a 429 recently, don't try fetching again.
    
    Args:
        cache_key: The cache key for this request
        fetch_func: Function to call if cache miss or expired
        *args, **kwargs: Arguments to pass to fetch_func
        
    Returns:
        Cached or freshly fetched data
        
    Raises:
        Exception: If fetch fails and no cached data is available
    """
    # First, check if we have valid cached data
    if is_cache_valid(cache_key):
        cached_data = get_cached_response(cache_key)
        if cached_data is not None:
            return cached_data
    
    # Check if we're in rate limit cooldown
    if _is_rate_limited(cache_key):
        cached_data = get_cached_response(cache_key)
        if cached_data is not None:
            # Return expired cache rather than hitting the API again
            return cached_data
        # No cache available, but we're rate limited - raise an informative error
        raise Exception("Rate limited and no cached data available")
    
    # Try to get expired cache as fallback
    cached_data = get_cached_response(cache_key)
    
    try:
        fresh_data = fetch_func(*args, **kwargs)
        set_cached_response(cache_key, fresh_data)
        # Clear rate limit error if we successfully fetched
        with _cache_lock:
            _rate_limit_errors.pop(cache_key, None)
        return fresh_data
    except Exception as e:
        # Check if this is a 429 error
        if _is_429_error(e):
            _record_rate_limit_error(cache_key)
            # Return cached data if available (even if expired)
            if cached_data is not None:
                return cached_data
        else:
            # For other errors, also try to return cached data
            if cached_data is not None:
                return cached_data
        # Re-raise if no cached data available
        raise e

