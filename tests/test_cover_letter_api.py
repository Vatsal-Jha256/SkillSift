import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.models import CoverLetterTemplate, CoverLetterRequest
from app.core.database import Base, engine, get_db
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.core.models import User

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(test_db):
    """Create test user"""
    db = next(get_db())
    try:
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        yield user
        db.delete(user)
        db.commit()
    finally:
        db.close()

@pytest.fixture
def auth_headers(test_user):
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

def test_create_template(auth_headers, test_db):
    """Test creating a new cover letter template"""
    template_data = {
        "id": "test-template",
        "name": "Test Template",
        "content": "Dear {hiring_manager},\nTest content\nRegards,\n{applicant_name}",
        "industry": "Technology"
    }
    
    response = client.post(
        "/api/cover-letter/templates",
        json=template_data,
        headers=auth_headers
    )
    assert response.status_code == 201, f"Failed to create template: {response.text}"
    data = response.json()
    assert data["id"] == template_data["id"]

def test_get_templates(auth_headers, test_db):
    """Test getting all templates"""
    # First create a template
    template_data = {
        "id": "test-list",
        "name": "Test List Template",
        "content": "Test content",
        "industry": "Technology"
    }
    
    client.post(
        "/api/cover-letter/templates",
        json=template_data,
        headers=auth_headers
    )
    
    response = client.get(
        "/api/cover-letter/templates",
        headers=auth_headers
    )
    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)
    assert len(templates) > 0

def test_get_template(auth_headers, test_db):
    """Test getting a specific template"""
    template_data = {
        "id": "test-get",
        "name": "Test Get Template",
        "content": "Test content",
        "industry": "Technology"
    }
    
    create_response = client.post(
        "/api/cover-letter/templates",
        json=template_data,
        headers=auth_headers
    )
    assert create_response.status_code == 201
    
    response = client.get(
        f"/api/cover-letter/templates/{template_data['id']}",
        headers=auth_headers
    )
    assert response.status_code == 200
    template = response.json()
    assert template["id"] == template_data["id"]

def test_update_template(auth_headers, test_db):
    """Test updating a template"""
    template_id = "update-test"
    create_data = {
        "id": template_id,
        "name": "Test Template",
        "content": "Original content",
        "industry": "Tech"
    }
    
    create_response = client.post(
        "/api/cover-letter/templates",
        json=create_data,
        headers=auth_headers
    )
    assert create_response.status_code == 201
    
    update_data = {
        "name": "Updated Template",
        "content": "Updated content",
        "industry": "Technology"
    }
    
    response = client.put(
        f"/api/cover-letter/templates/{template_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == update_data["name"]

def test_generate_cover_letter(auth_headers, test_db):
    """Test cover letter generation"""
    # First create a template
    template_data = {
        "id": "test-template",
        "name": "Test Template",
        "content": "Dear {hiring_manager},\nTest content\nRegards,\n{applicant_name}",
        "industry": "Technology"
    }
    
    client.post(
        "/api/cover-letter/templates",
        json=template_data,
        headers=auth_headers
    )
    
    request_data = {
        "template_id": "test-template",
        "job_title": "Software Engineer",
        "company_name": "Test Corp",
        "applicant_name": "John Doe",
        "skills": ["Python", "FastAPI", "Testing"],
        "background": "software development",
        "experience": "5 years in web development",
        "hiring_manager": "Jane Smith",
        "job_source": "LinkedIn",
        "company_interest": "innovative technology",
        "job_description": "Looking for a Python developer",
        "tone": "professional"
    }
    
    response = client.post(
        "/api/cover-letter/generate",
        json=request_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    result = response.json()
    assert "content" in result

def test_template_not_found(auth_headers):
    """Test handling of non-existent template"""
    response = client.get(
        "/api/cover-letter/templates/nonexistent",
        headers=auth_headers
    )
    assert response.status_code == 404

def test_unauthorized_access():
    """Test unauthorized access to protected endpoints"""
    endpoints = [
        ("/api/cover-letter/templates", "GET"),
        ("/api/cover-letter/templates/test", "GET"),
        ("/api/cover-letter/generate", "POST")
    ]
    
    for endpoint, method in endpoints:
        headers = {"Authorization": "Bearer invalid_token"}
        if method == "GET":
            response = client.get(endpoint, headers=headers)
        else:
            response = client.post(endpoint, json={}, headers=headers)
        assert response.status_code == 401, f"Expected 401 for {method} {endpoint}"