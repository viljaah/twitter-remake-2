from fastapi import FastAPI, Request, Response
import httpx  # Modern async HTTP client
import json
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Fixed: Now a list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache
cache = {}

def check_invalidation():
    """Remove cache entries older than 1 minute"""
    now = datetime.now()
    expired_keys = []
    
    for url in list(cache.keys()):
        cache_time = cache[url]["timestamp"]
        if now - cache_time > timedelta(minutes=1):
            expired_keys.append(url)
    
    # Remove expired entries
    for url in expired_keys:
        del cache[url]
        
    print(f"Cache invalidation removed {len(expired_keys)} entries")
    
    return len(expired_keys)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def handle_request(request: Request, path: str):
    method = request.method
    backend_url = f"http://backend:8000/{path}"
    
    # Add query parameters if any
    if request.query_params:
        backend_url += "?" + str(request.url.query)
    
    # For GET requests, check cache
    if method == "GET":
        # First run invalidation check on entire cache
        check_invalidation()
        
        cache_key = str(request.url)
        
        # If in cache and not expired (less than 1 minute old)
        if cache_key in cache:
            print(f"Cache HIT: {cache_key}")
            return cache[cache_key]["data"]
        
        print(f"Cache MISS: {cache_key}")
    
    # Forward the request to backend
    try:
        # Get headers and body
        headers = dict(request.headers)
        if "host" in headers:
            del headers["host"]
        
        body = await request.body()
        
        # Send to backend
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
        
        # Return the response from backend
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        # Fixed error response format
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)