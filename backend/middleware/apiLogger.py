import os
import threading
from fastapi import Request

BASE_DIR        = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR         = os.path.join(BASE_DIR, "logs")
REQUESTS_FILE   = os.path.join(LOG_DIR, "requests.txt")
DBCOUNT_FILE    = os.path.join(LOG_DIR, "dbcount.txt")

os.makedirs(LOG_DIR, exist_ok=True)
for path in (REQUESTS_FILE, DBCOUNT_FILE):
    if not os.path.exists(path):
        open(path, "w").close()

file_lock = threading.Lock()

# HTTP middleware to log every incoming request
async def log_requests(request: Request, call_next):
    method = request.method
    # strip leading “/” so “/like/123” : “like/123”; keep “/” as “/”
    path = request.url.path.lstrip("/") or "/"
    entry = f"{method} {path}\n"

    with file_lock:
        with open(REQUESTS_FILE, "a") as f:
            f.write(entry)

    return await call_next(request)

# called on each DB access
def increment_db_access():
    with file_lock:
        # read current count
        with open(DBCOUNT_FILE, "r+") as f:
            data = f.read().strip()
            count = int(data) if data else 0
            # bump
            f.seek(0)
            f.write(str(count + 1))
            f.truncate()

# for /logs route, read the file and split into [METHOD, path]
def read_request_log() -> list[list[str]]:
    with file_lock:
        with open(REQUESTS_FILE) as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    return [ln.split(" ", 1) for ln in lines]

# read current DB count
def read_db_count() -> int:
    with file_lock:
        with open(DBCOUNT_FILE) as f:
            data = f.read().strip()
    return int(data) if data else 0