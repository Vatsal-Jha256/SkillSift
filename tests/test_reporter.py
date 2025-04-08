# tests/test_reporter.py
import pytest
from app.services.reporter import ReportGenerator
import io
from PyPDF2 import PdfReader

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
    assert "85.5" in text
    assert "django" in text.lower()
