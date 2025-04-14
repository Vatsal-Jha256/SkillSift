import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, get_db
from app.core.models import User
from app.core.security import get_password_hash
import io

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Test client with database"""
    return TestClient(app)

@pytest.fixture
def test_user(test_db):
    """Create test user"""
    db = next(get_db())
    try:
        # Remove existing test user if any
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        # Create new test user
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers"""
    response = client.post(
        "/api/token",
        json={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200, f"Auth failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}