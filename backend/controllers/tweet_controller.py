from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.tweet_schema import Tweet
from models.hashtag_schema import Hashtag
from models.like_schema import Like
import re
from cache.db_cache import get_from_cache, save_to_cache

# create a new tweet
# route POST /tweets
# tweet_data: dict, says that tweet_data should be a dictionary
def create_tweet(db: Session, tweet_data: dict) -> Tweet:
    """
    :param db: SQLAlchemy database session
    :param tweet_data: dictionary with tweet details ('user_id', 'content'...).
    :return: the newly created tweet
    """
    # dictionary unpacking (**) lets me pass key-value pairs in a dictionary as separate keyword arguments to a function or constructor
    new_tweet = Tweet(**tweet_data)

    # extract hashtags from content
    hashtags_content = set(re.findall(r"#(\w+)", tweet_data.get("content", "")))
    for tag in hashtags_content:
        hashtag_obj = db.query(Hashtag).filter(Hashtag.name == tag).first()
        if not hashtag_obj:
            hashtag_obj = Hashtag(name=tag)
            db.add(hashtag_obj)
            db.flush()  # make sure the hashtag has an id before association
        # associate the hashtag with the tweet using the updated relationship name
        new_tweet.hashtags.append(hashtag_obj)

    # the tweet is added to the session
    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)
    return new_tweet

# retrive all tweets
# route GET /tweets
def get_all_tweets(db: Session):
    """
    return a list of tweets, with 'likes' count
    """
    # Check cache first
    cache_key = "all_tweets"
    cached_result = get_from_cache(cache_key)
    
    # If we found it in cache, return it immediately
    if cached_result is not None:
        return cached_result
    
    # Not in cache, do the database query
    rows = (
        db.query(
            Tweet,
            func.count(Like.id).label("likes")
        )
        .outerjoin(Like, Like.tweetId == Tweet.id)
        .group_by(Tweet.id)
        .all()
    )

    tweets = []
    for tweet, likes in rows:
        data = tweet.__dict__.copy()
        data.pop("_sa_instance_state", None)
        data["likes"] = likes
        tweets.append(data)

    # Save to cache for next time
    save_to_cache(cache_key, tweets)
    
    return tweets

# search for tweets that have the query string in their content
# route GET /tweets/search?={query}
def search_tweets(db: Session, query: str):
    """
    :param query: the search string
    :return: a list of tweets that match the search query, if no tweets match it returns an empty list
    """
    # .ilike() performs a case-insensitive match, it will find tweets regardless of letter case
    # %{query}% allows matching the query string anywhere within the tweet content
    tweets = db.query(Tweet).filter(Tweet.content.ilike(f"%{query}%")).all()
    return tweets

# search for tweets with hashtags that have the query string in their name
# route GET /tweets/hashtag/search?={query}
def search_hashtags(db: Session, query: str):
    """
    :param query: the search string
    :return: a list of tweets that have a hashtag matching the query
    uses a join between tweet and hashtag
    """
    tweets = (
        db.query(Tweet)
        # join the tweets table with the associated hashtags
        .join(Tweet.hashtags)
        .filter(Hashtag.name.ilike(f"%{query}%"))
        .all()
    )
    return tweets

# edit one tweet
# route PATCH /tweets/{tweet_id}
def update_tweet(db: Session, tweet_id: int, tweet_data: dict) -> Tweet:
    """
    :param tweet_id: the id of the tweet to update
    :param tweet_data: dictionary with fields to update (e.g {'content': 'New content'}...)
    """
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
    # check if there is a tweet, to avoid trying to update a non-existent tweet
    if tweet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
    # iterates over each key-value pair and updates the corresponding attribute of the tweet
    for key, value in tweet_data.items():
        setattr(tweet, key, value)
    # the changes are saved to the database
    db.commit()
    # updates the tweet instance with the latest data from the database
    db.refresh(tweet)
    return tweet

# delete one tweet
# route DELETE /tweets/{tweet_id}
def delete_tweet(db: Session, tweet_id: int) -> bool:
    """
    :param tweet_id: the id of the tweet to delete
    :return: true if the tweet was found and deleted, if not, False.
    """
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
    if tweet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
    db.delete(tweet)
    db.commit()
    return {"message": "Tweet deleted successfully"}

# add like and count the likes for a tweet
# route POST /tweets/{tweet_id}/like
def like_tweet(db: Session, tweet_id: int):
    """
    insert a new Like row for tweet_id, then return the total count
    """
    #check that the tweet exists
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
    if tweet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
    
    #new like
    new_like = Like(tweetId=tweet_id)
    db.add(new_like)
    db.commit()

    #count all likes for this tweet
    total_likes = (
        db.query(func.count(Like.id))
            .filter(Like.tweetId == tweet_id)
            .scalar()
    )

    return {"likes": total_likes}