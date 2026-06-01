from app.database import SessionLocal, engine
from app import models
from sqlalchemy.orm import Session

def test_database_connection():
    """Test that we can connect to the database and create tables."""
    # Create tables
    models.Base.metadata.create_all(bind=engine)

    # Create a session
    db = SessionLocal()

    try:
        # Try to query something
        count = db.query(models.Content).count()
        print(f"Database connection successful. Current content count: {count}")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_database_connection()