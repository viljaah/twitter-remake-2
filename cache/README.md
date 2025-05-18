# Cache Implementation README
## Overview
This document explains in detail how our caching system implements the requirements from Assignment 2. It's designed as a reference for team members to understand the internal logic and architecture decisions.

## Where to Create the Cache Folder
The cache folder should be created at the same level as your backend folder, not inside it. Your directory structure should look like this:

```
twitter-remake-2/
├── backend/               # Your existing FastAPI application
│   └── load-balancer/     # Your nginx configuration
│       └── nginx.conf
├── cache/                 # New folder for cache implementation
│   ├── Dockerfile
│   ├── requirements.txt
│   └── cache_server.py
└── docker-compose.yml     # Main Docker Compose file
```

This structure keeps your cache implementation separate from your backend code, which aligns with the assignment's requirement that "this whole subsystem should be the kind you could choose to add or remove later."

## Understanding Caching in Web Architecture

To help you better understand caching, here are some key concepts and resources:

### 1. What is Caching?

Caching stores copies of frequently accessed data so future requests can be served faster. In your assignment, you're implementing a time-based cache that invalidates entries after 1 minute.

### 2. How the Cache Server Works

Your cache server will:
- Act as a proxy between the load balancer and your API
- Store responses from GET requests
- Forward all other requests directly to the API
- Remove cached entries after 1 minute

### 3. Resources to Learn More

Here are some specific search terms and resources to help you understand caching better:

- "Flask proxy server with caching tutorial"
- "Python dictionary as cache implementation"
- "Time-based cache invalidation Python"
- "HTTP caching between services"

### 4. Key Concepts to Search For

When researching, focus on these specific concepts:

1. **HTTP Proxying** - How to forward HTTP requests from one service to another
2. **In-memory caching** - Using Python dictionaries to store cached responses
3. **Time-based cache invalidation** - Implementing expiration for cached entries
4. **Docker networking** - How containers communicate with each other

---------------------------------------------------------------------------------

Explanation of code in more detail, focusing on the specific parts:

### Understanding the Cache Invalidation Logic

```python
def check_invalidation():
    """Remove cache entries older than 1 minute"""
    now = datetime.now()  # Get current time
    expired_keys = []
    
    for url in list(cache.keys()):  # Loop through all URLs in the cache
        cache_time = cache[url]["timestamp"]  # Get when this URL was cached
        if now - cache_time > timedelta(minutes=1):  # Check if older than 1 minute
            expired_keys.append(url)  # If so, mark for deletion
    
    # Remove expired entries
    for url in expired_keys:
        del cache[url]  # Delete the expired entries from cache
```

Breaking this down:

1. `now = datetime.now()` - This gets the current time using Python's datetime module and stores it in now variable. 

2. `for url in list(cache.keys()):` - Here, `cache` is your dictionary that stores cached responses. `cache.keys()` returns all the URL strings that you've cached. We use `list()` to make a copy of the keys so we can safely modify the dictionary while iterating.

3. `cache_time = cache[url]["timestamp"]` - For each URL in the cache, we get when it was stored. Remember our cache structure is:
   ```
   cache = {
     "http://example.com/api/tweets": {
       "data": [tweet1, tweet2, ...],
       "timestamp": datetime_when_cached
     },
     "http://example.com/api/users": {
       "data": [user1, user2, ...],
       "timestamp": another_datetime
     }
   }
   ```

4. `if now - cache_time > timedelta(minutes=1):` - This checks if the current time minus the cached time is greater than 1 minute. `timedelta(minutes=1)` creates a time duration of 1 minute.

5. `del cache[url]` - The `del` keyword in Python deletes a variable or, in this case, a key-value pair from a dictionary. This permanently removes the cached data for that URL.

### Understanding the Request Forwarding and Cache Update

```python
# Forward the request to backend
try:
    # Get headers and body
    headers = dict(request.headers)  # Copy all headers from the incoming request
    if "host" in headers:
        del headers["host"]  # Remove host header to avoid conflicts
    
    body = await request.body()  # Get the request body
    
    # Send to backend
    async with httpx.AsyncClient() as client:  # Create HTTP client
        response = await client.request(  # Forward the request
            method=method,  # Same HTTP method (GET, POST, etc.)
            url=backend_url,  # The backend API URL
            headers=headers,  # Forward the headers
            content=body  # Forward the body
        )
    
    # If GET request and successful, cache the response
    if method == "GET" and response.status_code == 200:  # Only cache successful GETs
        try:
            data = response.json()  # Parse JSON response
            cache[str(request.url)] = {  # Store in cache
                "data": data,  # The actual data
                "timestamp": datetime.now()  # When we cached it
            }
            return data  # Return to client
        except:
            # Not JSON, don't cache
            pass
```

Breaking this down:

1. **Headers and Body Preparation**: 
   - `headers = dict(request.headers)` copies all HTTP headers from the original request
   - `if "host" in headers: del headers["host"]` removes the Host header which would point to our cache server, not the backend
   - `body = await request.body()` gets the request body content (for POST/PUT requests)

2. **Sending to Backend**:
   - `async with httpx.AsyncClient() as client:` creates an HTTP client
   - The `client.request()` method forwards the request to the backend with all original parameters
   - `backend_url` is the URL of your API server (like `http://backend:8000/tweets`)

3. **Caching Logic**:
   - `if method == "GET" and response.status_code == 200:` only cache successful GET requests
   - `data = response.json()` parses the JSON response
   - The key line that updates the cache is:
     ```python
     cache[str(request.url)] = {
         "data": data,
         "timestamp": datetime.now()
     }
     ```
   - This adds or updates an entry in the cache dictionary with the current time

The flow is:
1. Request comes in
2. For GETs, check cache
3. If not in cache, forward to backend
4. When response comes back from backend, store in cache with current timestamp
5. Return response to client


Additional Notes
The implementation also handles:

CORS configuration for frontend access
Error handling for failed requests
Proper header forwarding
Query parameter preservation




