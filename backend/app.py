# import deploy so the SQLAlchemy event hook is registered
import deploy
import logging
# debugging aid
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from fastapi import FastAPI
from routes.tweet_routes import tweet_router
from routes.user_routes import userRouter 
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from middleware.apiLogger import log_requests, read_request_log, read_db_count

load_dotenv()

app = FastAPI()

# register the HTTP‐logging middleware
app.middleware("http")(log_requests)

origins = [
    "http://localhost:3000",  # Adjust if running locally
    "https://twitter-remake-frontend-1qap.onrender.com",
    "http://localhost"
]
# add CORS middleware to allow requests from specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows only specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include the router - this is like app.use("/api/users", userRoutes) in Express
app.include_router(userRouter, prefix="/api")
app.include_router(tweet_router, prefix="/api")

#After this change, visiting your base URL will redirect to the FastAPI automatic documentation page where you can see and test all your API endpoints
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# /logs endpoint, in app.py because it is a route
@app.get("/logs")
async def get_logs():
    """
    returns all API calls seen since startup as
       { 
       "requests": [ ["GET","like/123"], ["POST","tweet"] ... ]
       "db_access_count": 42
       }
    """
    return {
        "requests": read_request_log(),
        "db_access_count": read_db_count()
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000)) #issues docker is taken the 8000 and not from .env
    print(f"Starting on port: {port}")  # Debug line; remove this in production
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
