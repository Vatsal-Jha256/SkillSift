# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import io
import json

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_authentication(client):
    """Test authentication flow"""
    # Test user registration/login
    response = client.post(
        "/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_unauthorized_access(client):
    """Test unauthorized access to protected endpoints"""
    response = client.post("/api/resume/analyze-resume/")
    assert response.status_code == 401

def test_resume_analysis(client, sample_pdf_bytes):
    """Test resume analysis endpoint"""
    # First authenticate
    auth_response = client.post(
        "/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Create test PDF file
    pdf_file = io.BytesIO(sample_pdf_bytes)
    pdf_file.name = "test_resume.pdf"
    
    # Test resume analysis
    response = client.post(
        "/api/resume/analyze-resume/",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test_resume.pdf", pdf_file, "application/pdf")},
        data={
            "job_description": "Looking for a Python developer with AWS experience",
            "job_requirements": json.dumps(["python", "aws"])
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "skills" in result
    assert "compatibility_score" in result
    assert "matched_skills" in result
    assert "recommendations" in result

def test_report_generation(client, sample_resume_analysis):
    """Test report generation endpoint"""
    # First authenticate
    auth_response = client.post(
        "/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Test report generation
    response = client.post(
        "/api/resume/generate-report/",
        headers={"Authorization": f"Bearer {token}"},
        json=sample_resume_analysis
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0

def test_invalid_file_type(client):
    """Test handling of invalid file types"""
    # First authenticate
    auth_response = client.post(
        "/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    token = auth_response.json()["access_token"]
    
    # Test with invalid file
    invalid_file = io.BytesIO(b"invalid file content")
    response = client.post(
        "/api/resume/analyze-resume/",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.xyz", invalid_file, "application/octet-stream")}
    )
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"] 