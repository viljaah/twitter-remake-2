from datetime import datetime, timedelta

# Our cache is just a dictionary (similar to a JavaScript object)
cache = {}

def get_from_cache(key):
    """Try to get something from cache"""
    # If the key exists in our cache
    if key in cache:
        entry = cache[key]
        now = datetime.now()
        
        # Check if it's less than 1 minute old
        if now - entry["timestamp"] < timedelta(minutes=1):
            print(f"DB Cache: Found {key} in cache!")
            return entry["data"]
        else:
            # It's too old, delete it
            print(f"DB Cache: {key} expired, removing")
            del cache[key]
    
    # Not in cache or expired
    return None

def save_to_cache(key, data):
    """Save something to the cache"""
    cache[key] = {
        "data": data,
        "timestamp": datetime.now()
    }
    print(f"DB Cache: Saved {key} to cache")