# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
    echo=settings.DATABASE_ECHO
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 

def create_test_user():
    """Create test user for testing"""
    from app.core.models import User
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
            full_name="Test User",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        return test_user
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()