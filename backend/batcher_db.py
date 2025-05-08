import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Cache database URL (SQLite file in backend/)
BATCH_DATABASE_URL = os.getenv("BATCH_DATABASE_URL", "sqlite:///./like_cache.db")

# SQLite-specific args
connect_args = {"check_same_thread": False} if BATCH_DATABASE_URL.startswith("sqlite") else {}

# Engine, session, and Base for cache
engine_cache = create_engine(BATCH_DATABASE_URL, connect_args=connect_args)
SessionCache = sessionmaker(bind=engine_cache, autoflush=False, expire_on_commit=False)
BaseCache = declarative_base()

class LikeCache(BaseCache):
    __tablename__ = "like_cache"
    tweetId     = Column(Integer, primary_key=True, index=True)
    count       = Column(Integer, default=0, nullable=False)
    firstSeenAt = Column(Float, default=time.time, nullable=False)

# Create the cache table (and any other cache-related tables) on import
BaseCache.metadata.create_all(bind=engine_cache)

#DATABASE_URL points at your Postgres instance and is used by db.py
#BATCH_DATABASE_URL points at your local SQLite cache file (like_cache.db) and is used by batcher_db.py