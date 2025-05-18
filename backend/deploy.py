import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from middleware.apiLogger import increment_db_access

load_dotenv()

# get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# create an engine for connecting to the database
engine = create_engine(DATABASE_URL, echo=False)
# create a sessionmaker for our main database
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# hook into every SQL execution to count every executed statement
# by calling increment_db_access()
@event.listens_for(engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """
    this function runs right before any SQL is sent to the database.
    It uses our logger helper to record that a DB access is about to happen
    """
    increment_db_access()
