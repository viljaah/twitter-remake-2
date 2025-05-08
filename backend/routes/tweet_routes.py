from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from validators.tweet_validate import TweetCreate, TweetUpdate
from controllers.tweet_controller import create_tweet, get_all_tweets, update_tweet, delete_tweet, search_tweets, search_hashtags, like_tweet
from models.user_schema import User
from middleware.auth import get_current_user

from batcher_db import SessionCache, LikeCache
import time

tweet_router = APIRouter(
    prefix="/tweets",
    tags=["tweets"],
)

@tweet_router.post("")
def post_tweet(tweet: TweetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # convert the validated tweet to a dict (had to use model_dump() instead of dict() because of pydantic version)
    tweet_data = tweet.model_dump()
    # automatically add the current user id
    tweet_data["user_id"] = current_user.id
    return create_tweet(db, tweet_data)

@tweet_router.get("")
def read_all_tweets(db: Session = Depends(get_db)):
    return get_all_tweets(db)

@tweet_router.get("/search")
def search_for_tweets(query: str, db: Session = Depends(get_db)):
    return search_tweets(db, query)

@tweet_router.get("/hashtag/search")
def search_for_hashtags(query: str, db: Session = Depends(get_db)):
    return search_hashtags(db, query)

@tweet_router.patch("/{tweet_id}")
def put_tweet(tweet_id: int, tweet: TweetUpdate, db: Session = Depends(get_db)):
    return update_tweet(db, tweet_id, tweet.model_dump())

@tweet_router.delete("/{tweet_id}")
def remove_tweet(tweet_id: int, db: Session = Depends(get_db)):
    return delete_tweet(db, tweet_id)

@tweet_router.post("/{tweet_id}/like", status_code=202)
def post_like(tweet_id: int, db: Session = Depends(get_db)):
    """
    enqueue a like: increment or insert into SQLite cache.
    """
    cache = SessionCache()
    now = time.time()

    obj = cache.get(LikeCache, tweet_id)
    if obj:
        obj.count += 1
    else:
        # new batch for this tweet
        obj = LikeCache(tweetId=tweet_id, count=1, firstSeenAt=now)
        cache.add(obj)

    cache.commit()
    cache.close()

    return {"status": "queued", "cached": obj.count}