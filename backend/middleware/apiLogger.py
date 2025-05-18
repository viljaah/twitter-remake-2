import os
import threading
from fastapi import Request

# determine the base directory so we can place our logs folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# define a logs directory under BASE_DIR, this is where we will store our log files
LOG_DIR = os.path.join(BASE_DIR, "logs")
# REQUESTS_FILE tracks each HTTP request
REQUESTS_FILE = os.path.join(LOG_DIR, "requests.txt")
# DBCOUNT_FILE tracks how many times our database was accessed
DBCOUNT_FILE = os.path.join(LOG_DIR, "dbcount.txt")

# make sure the logs directory exists, if not, create it
os.makedirs(LOG_DIR, exist_ok=True)
for path in (REQUESTS_FILE, DBCOUNT_FILE):
    if not os.path.exists(path):
        open(path, "w").close()

# a lock to prevent multiple threads from writing to the files at the same time
file_lock = threading.Lock()

# HTTP middleware to log every incoming request
async def log_requests(request: Request, call_next):
    """
    middleware function that runs on every HTTP request.
    It writes a simple line to our requests log, then passes control to the next handler
    """
    # get the http method (GET; POST...)
    method = request.method
    # strip leading “/” so “/like/123” becomes “like/123”
    # but if the path is "/", keep “/” as “/”
    path = request.url.path.lstrip("/") or "/"
    # single-line log
    entry = f"{method} {path}\n"

    with file_lock:
        with open(REQUESTS_FILE, "a") as f:
            f.write(entry)

    return await call_next(request)

# database access counter, called on each DB access
def increment_db_access():
    """
    called every time the application is about to run a SQL statement.
    It reads the existing count from our 'dbcount.txt' file, increments it by one,
    and writes it back
    """
    with file_lock:
        # read current count
        with open(DBCOUNT_FILE, "r+") as f:
            # read the file, strip whitespace, and parse as int
            data = f.read().strip()
            count = int(data) if data else 0
            # reset file pointer to the start so we can overwrite
            f.seek(0)
            # write the new increment count
            f.write(str(count + 1))
            # truncate the file to remove any old data
            f.truncate()

# for /logs route, read the file and split into [METHOD, path]
def read_request_log() -> list[list[str]]:
    with file_lock:
        with open(REQUESTS_FILE) as f:
            # read non-empty, stripped lines
            lines = [ln.strip() for ln in f if ln.strip()]
    # split each line on the first space into [method, path]
    return [ln.split(" ", 1) for ln in lines]

# read current DB count
def read_db_count() -> int:
    """
    reads the current integer count from dbcount.txt and returns it.
    If the file is empty or missing, returns 0.
    """
    with file_lock:
        with open(DBCOUNT_FILE) as f:
            data = f.read().strip()
    return int(data) if data else 0