# tests/test_reporter.py
import pytest
from app.services.reporter import ReportGenerator
import io
from PyPDF2 import PdfReader
import json
import tempfile
import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def test_pdf_report_generation():
    """Test that the PDF report is generated correctly"""
    # Create sample analysis data
    analysis_data = {
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
    
    # Generate PDF report
    pdf_bytes = ReportGenerator.generate_pdf_report(analysis_data)
    
    # Verify PDF content
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    
    # Try to read the PDF to verify it's valid
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(pdf_reader.pages) > 0
    
    # Extract text from first page
    text = pdf_reader.pages[0].extract_text()
    
    # Check for key content in the PDF
    assert "Resume Analysis Report" in text
    assert "python" in text.lower()
    assert "aws" in text.lower()
    assert "communication" in text.lower()
    assert any(s in text for s in ["85.5%", "85%"])  # Allow for rounding

def test_pdf_report_with_visualizations():
    """Test that the PDF report contains visualizations"""
    # Create sample analysis data with all required fields for visualizations
    analysis_data = {
        'skills': ['python', 'java', 'sql', 'javascript', 'react'],
        'matched_skills': ['python', 'java', 'sql'],
        'skill_gaps': ['docker', 'kubernetes', 'terraform'],
        'compatibility_score': 78.5,
        'skill_score': 85.0,
        'experience_score': 70.0,
        'education_score': 80.0,
        'scores': {
            'overall': 78.5,
            'skill': 85.0,
            'experience': 70.0,
            'education': 80.0
        },
        'recommendations': [
            'Consider learning Docker and Kubernetes for containerization',
            'Improve your cloud infrastructure skills with Terraform'
        ],
        'market_data': {
            'industry_trends': [
                {'name': 'Cloud Native', 'description': 'Adoption of cloud-native technologies is growing rapidly'},
                {'name': 'AI/ML', 'description': 'AI and machine learning skills are in high demand'},
                {'name': 'DevOps', 'description': 'DevOps practices are becoming industry standard'}
            ],
            'salary_range': {
                'min': 80000,
                'max': 120000,
                'median': 95000,
                'currency': 'USD'
            }
        }
    }
    
    # Generate PDF report
    pdf_bytes = ReportGenerator.generate_pdf_report(analysis_data)
    
    # Verify PDF content
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    
    # Try to read the PDF to verify it's valid
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(pdf_reader.pages) > 0
    
    # Extract text from first page
    text = pdf_reader.pages[0].extract_text()
    
    # Check for key content that indicates visualizations are included
    assert "Score Breakdown" in text

def test_html_report_generation():
    """Test that the HTML report is generated correctly"""
    # Create sample analysis data
    analysis_data = {
        'skills': ['python', 'java', 'sql', 'javascript', 'react'],
        'matched_skills': ['python', 'java', 'sql'],
        'skill_gaps': ['docker', 'kubernetes', 'terraform'],
        'compatibility_score': 78.5,
        'skill_score': 85.0,
        'experience_score': 70.0,
        'education_score': 80.0,
        'overall_score': 78.5,
        'scores': {
            'overall': 78.5,
            'skill': 85.0,
            'experience': 70.0,
            'education': 80.0
        },
        'recommendations': [
            'Consider learning Docker and Kubernetes for containerization',
            'Improve your cloud infrastructure skills with Terraform'
        ]
    }
    
    # Generate HTML report
    html_content = ReportGenerator.generate_html_report(analysis_data)
    
    # Verify HTML content
    assert isinstance(html_content, str)
    assert len(html_content) > 0
    
    # Check for key HTML elements
    assert "<!DOCTYPE html>" in html_content
    assert "<html lang=" in html_content
    assert "Resume Analysis Report" in html_content
    assert "Skill Development Roadmap" in html_content
    assert "Skills Analysis" in html_content
    assert "Recommendations" in html_content
    assert "roadmap-step" in html_content
    assert "python" in html_content
    assert "docker" in html_content
    assert "Score Breakdown" in html_content

def test_comparative_report_generation():
    """Test that the comparative report is generated correctly"""
    # Create current analysis data
    current_analysis = {
        'skills': ['python', 'java', 'sql', 'docker', 'kubernetes'],
        'matched_skills': ['python', 'java', 'sql', 'docker'],
        'skill_gaps': ['terraform', 'aws'],
        'compatibility_score': 85.0,
        'skill_score': 90.0,
        'experience_score': 80.0,
        'education_score': 85.0,
        'overall_score': 85.0,
        'recommendations': [
            'Learn AWS for cloud infrastructure management',
            'Consider getting certified in Terraform'
        ]
    }
    
    # Create previous analysis data
    previous_analysis = {
        'skills': ['python', 'java', 'sql'],
        'matched_skills': ['python', 'java'],
        'skill_gaps': ['docker', 'kubernetes', 'terraform', 'aws'],
        'compatibility_score': 70.0,
        'skill_score': 75.0,
        'experience_score': 65.0,
        'education_score': 70.0,
        'overall_score': 70.0,
        'recommendations': [
            'Learn containerization with Docker and Kubernetes',
            'Improve SQL database skills'
        ]
    }
    
    # Generate comparative report
    html_content = ReportGenerator.generate_comparative_report(current_analysis, previous_analysis)
    
    # Verify HTML content
    assert isinstance(html_content, str)
    assert len(html_content) > 0
    
    # Check for key HTML elements
    assert "<!DOCTYPE html>" in html_content
    assert "<html lang=" in html_content
    assert "Comparative Resume Analysis" in html_content
    assert "Score Comparison" in html_content
    assert "New Skills Gained" in html_content
    assert "Current Recommendations" in html_content
    assert "+15.0%" in html_content  # Improvement percentage

def test_report_history():
    """Test saving and retrieving report history"""
    # Create a unique test user ID
    test_user_id = f"test_user_{os.urandom(4).hex()}"
    
    # Create sample analysis data
    analysis_data = {
        'skills': ['python', 'java', 'sql'],
        'matched_skills': ['python', 'java'],
        'skill_gaps': ['docker', 'kubernetes'],
        'compatibility_score': 75.0,
        'skill_score': 80.0,
        'experience_score': 70.0,
        'education_score': 75.0,
        'overall_score': 75.0,
        'recommendations': ['Learn Docker and Kubernetes']
    }
    
    # Save report to history
    success = ReportGenerator.save_report_history(test_user_id, analysis_data)
    assert success is True
    
    # Check if the history directory and file were created
    user_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'users', test_user_id)
    history_path = os.path.join(user_dir, 'report_history.json')
    assert os.path.exists(history_path)
    
    # Check if we can load and parse the history file
    with open(history_path, 'r') as file:
        history = json.load(file)
    
    # Verify that our report is in the history
    assert len(history) == 1
    assert 'skills' in history[0]
    assert 'python' in history[0]['skills']
    assert 'timestamp' in history[0]  # Make sure timestamp was added
    
    # Clean up test files
    os.remove(history_path)
    try:
        os.rmdir(user_dir)
        os.rmdir(os.path.dirname(user_dir))  # Remove users dir if empty
    except OSError:
        pass  # Directory may not be empty
