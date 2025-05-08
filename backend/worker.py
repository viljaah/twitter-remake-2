import time
import threading
from sqlalchemy import text
from batcher_db import SessionCache, LikeCache
from config.db import SessionLocal

def flush_likes():
    cache   = SessionCache()
    main_db = SessionLocal()
    now     = time.time()

    batches = (
        cache.query(LikeCache)
             .filter(
                 (LikeCache.count >= 10) |
                 ((now - LikeCache.firstSeenAt) >= 60)
             )
             .all()
    )

    for batch in batches:
        main_db.execute(
            text("UPDATE tweets SET likes = likes + :inc WHERE id = :tweet_id"),
            {"inc": batch.count, "tweet_id": batch.tweetId}
        )
        cache.delete(batch)

    main_db.commit()
    cache.commit()
    main_db.close()
    cache.close()

def run_worker(poll_interval: float = 5.0):
    while True:
        flush_likes()
        time.sleep(poll_interval)

if __name__ == "__main__":
    t = threading.Thread(target=run_worker, daemon=True)
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
