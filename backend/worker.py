import time
import threading
from sqlalchemy import text
from batcher_db import SessionCache, LikeCache
from config.db import SessionLocal

# The flush_likes function is responsible for moving likes
# from the cache database into the main database (our postgres)
def flush_likes():
    # open a new session for the cache database and the maon database
    cache = SessionCache()
    main_db = SessionLocal()
    # get the current time (in seconds)
    now = time.time()

    # a query for all LikeCache entries where:
    # count >= 10: we have a full batch ready or 
    # now - firstSeenAt >= 60: we have waited long enough
    batches = (
        cache.query(LikeCache)
             .filter(
                 (LikeCache.count >= 10) |
                 ((now - LikeCache.firstSeenAt) >= 60)
             )
             .all()
    )

    for batch in batches:
        # increment the likes count on the tweets table
        # it avoids loading the Tweet ORM and does the update in a single statement
        main_db.execute(
            text("UPDATE tweets SET likes = likes + :inc WHERE id = :tweet_id"),
            {"inc": batch.count, "tweet_id": batch.tweetId}
        )
        # remove this from the cache so it wont be processed again
        cache.delete(batch)

    # commit the changes to both databases, and close the sessions
    main_db.commit()
    cache.commit()
    main_db.close()
    cache.close()

def run_worker(poll_interval: float = 5.0):
    """
    run flush_likes in an infinite loop, pausing poll_interval seconds between each run
    poll_interval: how many seconds to sleep between each flush attempt
    """
    while True:
        # try to flush
        flush_likes()
        # wait 5 sec before checking again
        time.sleep(poll_interval)

if __name__ == "__main__":
    t = threading.Thread(target=run_worker, daemon=True)
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
