from db.database import SessionLocal


# Dependency database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
