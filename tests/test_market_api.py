import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.main import app
from app.core.models import IndustryTrend, SalaryRange, JobMarketDemand, CareerPath, User
from app.core.database import Base, engine, get_db
from app.core.security import get_password_hash

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

@pytest.fixture
def test_trend(test_db):
    """Create a test trend"""
    db = next(get_db())
    try:
        trend = IndustryTrend(
            industry_name="Test Industry",
            trend_name=f"Test Trend {uuid.uuid4()}",
            description="This is a test trend",
            relevance_score=0.8,
            source="Test Source"
        )
        db.add(trend)
        db.commit()
        db.refresh(trend)
        yield trend
        db.delete(trend)
        db.commit()
    finally:
        db.close()

@pytest.fixture
def test_salary(test_db):
    """Create a test salary range"""
    db = next(get_db())
    try:
        salary = SalaryRange(
            job_title="Test Engineer",
            industry_name="Test Industry",
            min_salary=50000,
            max_salary=100000,
            median_salary=75000,
            currency="USD",
            experience_level="mid"
        )
        db.add(salary)
        db.commit()
        db.refresh(salary)
        yield salary
        db.delete(salary)
        db.commit()
    finally:
        db.close()

def test_get_trends(test_trend):
    """Test getting industry trends"""
    response = client.get(f"/api/market/trends/{test_trend.industry_name}")
    assert response.status_code == 200
    trends = response.json()
    assert len(trends) > 0
    assert any(trend["trend_name"] == test_trend.trend_name for trend in trends)

def test_create_trend(auth_headers, test_db):
    """Test creating a new industry trend"""
    new_trend = {
        "industry_name": "Test Industry",
        "trend_name": f"New Test Trend {uuid.uuid4()}",
        "description": "This is a new test trend",
        "relevance_score": 0.9,
        "source": "New Test Source"
    }
    
    response = client.post(
        "/api/market/trends",
        json=new_trend,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    created_trend = response.json()
    assert created_trend["trend_name"] == new_trend["trend_name"]

def test_create_trend_unauthorized():
    """Test creating a trend without authentication"""
    new_trend = {
        "industry_name": "Test Industry",
        "trend_name": "Unauthorized Trend",
        "description": "This should not be created",
        "relevance_score": 0.9,
        "source": "Unauthorized Source"
    }
    
    response = client.post("/api/market/trends", json=new_trend)
    assert response.status_code == 401

def test_get_salary_ranges(test_salary):
    """Test getting salary ranges"""
    response = client.get(
        f"/api/market/salary/{test_salary.job_title}",
        params={
            "industry_name": test_salary.industry_name,
            "experience_level": test_salary.experience_level
        }
    )
    assert response.status_code == 200
    salaries = response.json()
    assert len(salaries) > 0

def test_analyze_market_competitiveness(test_db):
    """Test the market competitiveness analysis endpoint"""
    # Test data
    data = {
        "candidate": {
            "skills": ["JavaScript", "React", "Node.js", "Git"],
            "years_of_experience": 2
        },
        "job": {
            "title": "Software Engineer",
            "industry": "Technology"
        }
    }
    
    response = client.post("/api/market/analyze", json=data)
    
    assert response.status_code == 200
    result = response.json()
    
    # Basic validation of response structure
    assert "market_score" in result
    assert isinstance(result["market_score"], int)
    assert 0 <= result["market_score"] <= 100
    
    # Optional fields may be None depending on available data
    if result.get("salary_range"):
        assert isinstance(result["salary_range"], dict)
        
    if result.get("demand_info"):
        assert isinstance(result["demand_info"], dict)
        
    assert isinstance(result.get("next_career_steps", []), list)
    assert isinstance(result.get("market_insights", []), list)