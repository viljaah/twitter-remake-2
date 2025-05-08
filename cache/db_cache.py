# cache/simple_cache.py
import time

# Simple dictionary to store cached results
cache = {}

def get_from_cache(key):
    """Get value from cache if it exists and is not expired"""
    if key in cache:
        # Check if cache entry is expired (older than 1 minute)
        if time.time() - cache[key]['timestamp'] < 60:
            print(f"Cache hit: {key}")
            return cache[key]['data']
        else:
            # Remove expired entry
            del cache[key]
    return None

def save_to_cache(key, data):
    """Save value to cache with current timestamp"""
    cache[key] = {
        'data': data,
        'timestamp': time.time()
    }
    print(f"Saved to cache: {key}")