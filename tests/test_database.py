# tests/test_database.py
import pytest
from sqlalchemy.orm import Session
from app.core.models import User
from app.core.security import get_password_hash

def test_create_user(db_session: Session):
    """Test user creation in database"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True

def test_get_user(db_session: Session):
    """Test retrieving user from database"""
    # Create test user
    user = User(
        email="get_test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Get Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Retrieve user
    retrieved_user = db_session.query(User).filter(User.email == "get_test@example.com").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "get_test@example.com"
    assert retrieved_user.full_name == "Get Test User"

def test_update_user(db_session: Session):
    """Test updating user in database"""
    # Create test user
    user = User(
        email="update_test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Update Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Update user
    user.full_name = "Updated Name"
    db_session.commit()
    db_session.refresh(user)
    
    assert user.full_name == "Updated Name"

def test_delete_user(db_session: Session):
    """Test deleting user from database"""
    # Create test user
    user = User(
        email="delete_test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Delete Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Delete user
    db_session.delete(user)
    db_session.commit()
    
    # Try to retrieve deleted user
    deleted_user = db_session.query(User).filter(User.email == "delete_test@example.com").first()
    assert deleted_user is None

def test_unique_email_constraint(db_session: Session):
    """Test that email must be unique"""
    # Create first user
    user1 = User(
        email="duplicate@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="First User"
    )
    db_session.add(user1)
    db_session.commit()
    
    # Try to create second user with same email
    user2 = User(
        email="duplicate@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Second User"
    )
    db_session.add(user2)
    
    with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
        db_session.commit()

def test_password_hashing(db_session: Session):
    """Test that passwords are properly hashed"""
    password = "testpassword"
    hashed = get_password_hash(password)
    
    user = User(
        email="hash_test@example.com",
        hashed_password=hashed,
        full_name="Hash Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    retrieved_user = db_session.query(User).filter(User.email == "hash_test@example.com").first()
    assert retrieved_user.hashed_password != password
    assert len(retrieved_user.hashed_password) > len(password) 