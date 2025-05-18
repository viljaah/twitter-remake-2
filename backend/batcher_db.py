import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# the URL for our cache database (local SQLite database file called 'like_cache.db' in the current directory)
BATCH_DATABASE_URL = os.getenv("BATCH_DATABASE_URL", "sqlite:///./like_cache.db")

connect_args = {"check_same_thread": False} if BATCH_DATABASE_URL.startswith("sqlite") else {}

# create an engine for connecting to the cache database
engine_cache = create_engine(BATCH_DATABASE_URL, connect_args=connect_args)
# create a sessionmaker for generating new session objects
SessionCache = sessionmaker(bind=engine_cache, autoflush=False, expire_on_commit=False)
# create a base class for defining our ORM models in the cache database
BaseCache = declarative_base()

# define the LikeCache model, the structure of the like_cache table
class LikeCache(BaseCache):
    __tablename__ = "like_cache"
    tweetId = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, default=0, nullable=False)
    firstSeenAt = Column(Float, default=time.time, nullable=False)

# create the like_cache table if it does not already exist
# this runs automatically when this module is imported
BaseCache.metadata.create_all(bind=engine_cache)

#DATABASE_URL points at our Postgres and is used by db.py
#BATCH_DATABASE_URL points at our local SQLite cache file (like_cache.db) and is used by batcher_db.py