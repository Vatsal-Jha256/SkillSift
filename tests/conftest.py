# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
import os
import io

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    # Create test database
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop test database after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_db):
    # Create a new database session for a test
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    # Fix for compatibility with newer versions of httpx
    return TestClient(app=app)

@pytest.fixture
def sample_pdf_bytes():
    # Create a simple PDF file for testing
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Sample Resume")
    c.drawString(100, 700, "Skills: Python, AWS, Communication")
    c.drawString(100, 650, "Experience: Software Engineer")
    c.save()
    return buffer.getvalue()

@pytest.fixture
def sample_resume_analysis():
    return {
        'skills': ['python', 'aws', 'communication'],
        'skills_with_context': {
            'skills': [
                {'skill': 'python', 'proficiency': 'expert', 'category': 'programming'},
                {'skill': 'aws', 'proficiency': 'intermediate', 'category': 'cloud'},
                {'skill': 'communication', 'proficiency': 'expert', 'category': 'soft_skills'}
            ],
            'categorized_skills': {
                'programming': [{'skill': 'python', 'proficiency': 'expert'}],
                'cloud': [{'skill': 'aws', 'proficiency': 'intermediate'}],
                'soft_skills': [{'skill': 'communication', 'proficiency': 'expert'}]
            }
        },
        'structured_data': {
            'contact_info': {'email': 'test@example.com', 'phone': '123-456-7890'},
            'education': [{'degree': 'Bachelor of Science in Computer Science'}],
            'experience': [{'title': 'Software Engineer', 'description': 'Developed web applications'}],
            'skills': ['python', 'aws', 'communication']
        },
        'compatibility_score': 85.5,
        'matched_skills': ['python', 'aws'],
        'skill_gaps': ['django'],
        'skill_score': 90.0,
        'experience_score': 80.0,
        'education_score': 85.0,
        'recommendations': [
            'Consider developing skills in: django',
            'Highlight relevant coursework or projects in your resume'
        ]
    } 