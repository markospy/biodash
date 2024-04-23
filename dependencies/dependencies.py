# This module manages the connection with the database.

from database.database import session_local


# Dependency database
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
