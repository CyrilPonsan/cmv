from ..utils.database import SessionLocal


# Base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
