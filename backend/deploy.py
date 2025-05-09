from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from middleware.apiLogger import increment_db_access

DATABASE_URL = "postgresql://twitterdb_xm1v_user:khimHSJf2r7zVMEgG9toQEvygblUCsh4@dpg-d0c8f89r0fns73e5ohu0-a.frankfurt-postgres.render.com/twitterdb_xm1v"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# hook into every SQL execution
@event.listens_for(engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    increment_db_access()
