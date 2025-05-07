'''
from fastapi import FastAPI, Request, Response
import requests
import time
import uvicorn
from datetime import datetime

app = FastAPI()

# Simple dictionary cache with timestamp tracking
# Structure: {endpoint: {'data': result_data, 'timestamp': datetime}}
cache = {}  

def check_invalidation():
    """Remove cache entries older than 1 minute"""
    now = datetime.now()
    expired_keys = []
    
    for endpoint in cache:
        age = (now - cache[endpoint]['timestamp']).total_seconds()
        if age > 60:  # 60 seconds = 1 minute
            expired_keys.append(endpoint)
    
    # Remove expired entries
    for endpoint in expired_keys:
        del cache[endpoint]
    
    print(f"Cache invalidation removed {len(expired_keys)} entries")
    return len(expired_keys)

def access_cache(endpoint):
    """
    Access cache following the 3-step process:
    1. Run invalidation check
    2. Check if request is cached
    3. If not, forward to API and update cache
    """
    # Step 1: Run invalidation check
    check_invalidation()
    
    # Step 2: Check if request is cached
    if endpoint in cache:
        print(f"Cache HIT: {endpoint}")
        return cache[endpoint]['data']
    
    # Step 3: If not cached, get from API and update cache
    print(f"Cache MISS: {endpoint}")
    result = get_from_API(endpoint)
    
    # Store in cache with timestamp
    cache[endpoint] = {
        'data': result,
        'timestamp': datetime.now()
    }
    
    return result

def get_from_API(endpoint):
    """Forward request to backend API and return response"""
    url = f"http://backend:8000{endpoint}"
    
    # Measure request time
    start_time = time.time()
    
    response = requests.get(url)
    
    # Log timing
    elapsed = time.time() - start_time
    print(f"Backend request: {elapsed:.4f} seconds for {endpoint}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code {response.status_code}, at url: {url}")
        return {"error": f"Request failed with status code {response.status_code}"}

@app.get("/{full_path:path}")
async def proxy_get_request(full_path: str):
    """Proxy GET requests with caching"""
    endpoint = f"/{full_path}"
    result = access_cache(endpoint)
    return result

@app.get("/cache-stats")
async def get_cache_stats():
    """Endpoint to monitor cache status"""
    return {
        "cache_size": len(cache),
        "cached_endpoints": list(cache.keys())
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)



These should only cache reads and not writes or deletes. They
should be written in Python, and can use a like structure the dictionary. The cached
requests should automatically be removed when more than 1 minute old. Normally, we
may want a diTerent thread to deal with this. To reduce complexity, we can simply trigger
the invalidation check whenever we use the cache. So a cache access could be
something like the following.
1. Run invalidation check on cache.
2. Check if GET request is already cached.
2
IDG2001 v0.3 (draft)
3. If yes: Return. If no: Send request further (API) and update cache.
The caches should run as Docker containers.
'''

'''
requests_cache.install_cache() is the main function that enables caching. Here's what it does:

It sets up a cache database (by default, an SQLite file) with your specified name ('tweet_cache')
It monitors all requests.get() calls to automatically save responses
It automatically checks the cache first before making a new request
It handles expiration based on your settings (60 seconds in your case)

Understanding check_invalidation() Function
Your check_invalidation() function runs requests_cache.remove_expired_responses(), which:

Checks through all cached responses
Removes any that are older than the expiration time (60 seconds)

This is related to the concept mentioned in the article:
For data that might change occasionally, setting an expiration time ensures you eventually get fresh data.

Understanding the FastAPI Middleware
Your middleware function:

Runs the invalidation check before processing each request
Lets the normal request flow continue with call_next(request)
Returns the response

The comment states "Steps 2 & 3 are handled automatically by requests_cache" - this means:
When you use requests_cache, it seamlessly integrates with the standard requests library. You don't need to change your existing code beyond adding the import and install_cache line - the module automatically intercepts requests and handles caching behind the scenes.

What's Missing in Your Implementation
Based on your requirements ("implement GET caches in python. the cached should be automatically removed when more than 1 minute old"), your current code actually covers most of what you need:

✅ It caches GET requests (allowable_methods=('GET',))
✅ It removes cache entries after 1 minute (expire_after=60)
✅ It runs invalidation checks before processing requests

The main thing missing is how to use this with your actual API endpoints. You need to add routes that use requests to call your API:

'''

'''
okay I can see the json data but hwo does this work exactly when I have my to server/port running? does it mean that if I refresh my main app.py with port 8000 then the get request for the get all tweets will come from the cache_server.py?

That's a great question about how the two servers work together! Let me explain the current setup:

Your current setup has two separate servers running:

1. Your main backend (app.py) running on port 8000
2. Your cache server (cache_server.py) running on port 8001

The way this works is:

- When a user goes to http://localhost:8001/api/tweets, their request goes to your cache server
- Your cache server then:
  1. Checks if it has a cached response for this request
  2. If yes, it returns the cached response directly
  3. If no, it makes a request to http://localhost:8000/api/tweets (your main backend), stores the response in its cache, and returns it

If you refresh your main app (port 8000), that won't use the cache. The cache only gets used when requests go through port 8001.

For this to be fully integrated, you would typically:

1. Set up your frontend to make requests to the cache server (port 8001) instead of directly to your backend
2. Or set up a proxy (like your load balancer) to route requests through the cache server before they reach your backend

This way, all GET requests would benefit from caching without clients needing to know about the cache.

Your implementation satisfies the requirements you specified:
- It caches GET requests
- Cached items expire after 1 minute
- It's containerized with Docker

Is this the behavior you were expecting, or were you looking for a different integration approach?

The only thing missing is a handler for the root path /. Since you mentioned getting a "not found" when accessing http://localhost:80, that's likely because there's no route handler for the root path. You could add one like this:
python@app.get("/")
async def root():
    return {"message": "Cache server is running. Try /api/tweets to see cached

'''
from fastapi import FastAPI, Request, Response
import requests
import time
import uvicorn
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost:3000",
    "https://twitter-remake-frontend-1qap.onrender.com",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple dictionary cache with timestamp tracking
cache = {}

def check_invalidation():
    """Remove cache entries older than 1 minute"""
    now = datetime.now()
    expired_keys = []
    for endpoint in cache:
        age = (now - cache[endpoint]['timestamp']).total_seconds()
        if age > 60:  # 60 seconds = 1 minute
            expired_keys.append(endpoint)
    
    # Remove expired entries
    for endpoint in expired_keys:
        del cache[endpoint]
    
    print(f"Cache invalidation removed {len(expired_keys)} entries")
    return len(expired_keys)

async def forward_request(request: Request, endpoint: str):
    """Forward any type of request to backend with all headers and body"""
    # Include query parameters in the backend URL
    query_params = request.query_params
    backend_url = f"http://backend:8000{endpoint}"
    
    if query_params:
        query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
        backend_url = f"{backend_url}?{query_string}"
    
    # Get the request method
    method = request.method
    
    # Get the request body if it exists
    body = await request.body()
    
    # Get the request headers
    headers = dict(request.headers)
    if "host" in headers:
        del headers["host"]  # Remove host header as it will be set by requests
    
    # Measure request time
    start_time = time.time()
    
    # Make the appropriate request based on the HTTP method
    try:
        if method == "GET":
            response = requests.get(backend_url, headers=headers)
        elif method == "POST":
            response = requests.post(backend_url, data=body, headers=headers)
        elif method == "PUT":
            response = requests.put(backend_url, data=body, headers=headers)
        elif method == "DELETE":
            response = requests.delete(backend_url, headers=headers)
        elif method == "OPTIONS":
            response = requests.options(backend_url, headers=headers)
        else:
            return Response(content=b"Method not supported", status_code=405)
        
        # Log timing
        elapsed = time.time() - start_time
        print(f"Backend {method} request: {elapsed:.4f} seconds for {endpoint}")
        
        # Return response with original headers (important for CORS)
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        print(f"Error forwarding request: {e}")
        return Response(
            content=str(e).encode(),
            status_code=500
        )

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def handle_all_requests(request: Request, full_path: str):
    """Handle all types of requests, with caching only for GETs"""
    endpoint = f"/{full_path}"
    method = request.method
    
    # For GET requests, try to use cache
    if method == "GET":
        # Create a cache key that includes query parameters
        cache_key = endpoint
        if request.query_params:
            query_string = "&".join([f"{k}={v}" for k, v in request.query_params.items()])
            cache_key = f"{endpoint}?{query_string}"
        
        # Step 1: Run invalidation check
        check_invalidation()
        
        # Step 2: Check if request is cached
        if cache_key in cache:
            print(f"Cache HIT: {cache_key}")
            return cache[cache_key]['data']
        
        # Step 3: If not in cache, forward to backend
        print(f"Cache MISS: {cache_key}")
        response = await forward_request(request, endpoint)
        
        # Only cache successful JSON responses
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                import json
                response_data = json.loads(response.body)
                
                # Store in cache with timestamp
                cache[cache_key] = {
                    'data': response_data,
                    'timestamp': datetime.now()
                }
                
                return response_data
            except:
                # If not JSON, just return the response without caching
                pass
        
        return response
    
    # For non-GET requests, just forward to backend (no caching)
    return await forward_request(request, endpoint)
   
               

@app.get("/cache-stats")
async def get_cache_stats():
    """Endpoint to monitor cache status"""
    return {
        "cache_size": len(cache),
        "cached_endpoints": list(cache.keys())
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)