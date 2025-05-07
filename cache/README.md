I understand you need more clarity about implementing the caches for your Twitter-remake project. Let me help explain where the cache folder should be placed and provide some resources to deepen your understanding.

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

## Simple Implementation Steps

Let me break down the implementation into simpler steps:

1. **Create a Basic Flask Server**: 
   - Set up a Flask application that can receive HTTP requests

2. **Add Proxy Functionality**:
   - Forward incoming requests to your API server
   - Return the API's response to the client

3. **Add Caching Logic**:
   - For GET requests, check if the URL is in your cache
   - If yes, return the cached response
   - If no, get the response from the API, cache it, then return it

4. **Add Cache Invalidation**:
   - Before every request, check if any cached items are older than 1 minute
   - Remove expired items from the cache

5. **Dockerize the Cache Server**:
   - Create a Dockerfile to package your cache server
   - Set up environment variables for configuration



1. It should cache only read (GET) requests, not writes or deletes
2. It should invalidate cached items older than 1 minute
3. It should be written in Python
4. It should run as a Docker container


