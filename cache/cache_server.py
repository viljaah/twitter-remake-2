from fastapi import FastAPI, Request, Response
import httpx  # Modern async HTTP client
import json
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# need to have cors middelware because of cors issues when trying to access backedn through caches first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend server adress
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# chose in-memory cache storage: {url_string: {"data": response_data, "timestamp": datetime_object}} instead of redis or another mehtods for caching
cache = {}

def check_invalidation():
    """Remove cache entries older than 1 minute
    and returns the number og entries removed """
    now = datetime.now()
    expired_keys = []
    
    for url in list(cache.keys()):
        cache_time = cache[url]["timestamp"]
        if now - cache_time > timedelta(minutes=1):
            expired_keys.append(url)
    
    # this is where removal of expired entities happen
    for url in expired_keys:
        del cache[url]
        
    print(f"Cache invalidation removed {len(expired_keys)} entries")
    
    return len(expired_keys)

"""
    Main request handler that implements caching logic:
    1. For GET requests: Check cache first, forward to backend if not cached
    2. For non-GET requests: Forward directly to backend (no caching)
    3. Cache successful GET responses for future requests
"""
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def handle_request(request: Request, path: str):
    method = request.method
    backend_url = f"http://backend:8000/{path}"
    
    # Add query parameters if any
    if request.query_params:
        backend_url += "?" + str(request.url.query)
    
    # Only attempt to use cache for GET requests (reads, not writes)
    if method == "GET":
        check_invalidation()
        
        cache_key = str(request.url)
        
        # If in cache and not expired (less than 1 minute old)
        if cache_key in cache:
            print(f"Cache HIT: {cache_key}")
            return cache[cache_key]["data"]
        
        #else print this: 
        print(f"Cache MISS: {cache_key}")
    
    # Forward the request to backend API server
    try:
        # Prepare headers (remove 'host' to avoid conflicts)
        headers = dict(request.headers)
        if "host" in headers:
            del headers["host"]
        
        # Get request body for non-GET requests
        body = await request.body()
        
        # Forward request to backend server
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=backend_url,
                headers=headers,
                content=body
            )
        
        # If GET request and successful, cache the response
        if method == "GET" and response.status_code == 200:
            try:
                data = response.json()
                cache[str(request.url)] = {
                    "data": data,
                    "timestamp": datetime.now()
                }
                return data
            except:
                # Not JSON, don't cache
                pass
        
         # Return the backend response as-is for non-cached responses
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        # Return a formatted error response if request fails
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )

# The caches should run as Docker containers: 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)