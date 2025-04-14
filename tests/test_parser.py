import pytest
import os
import io
from unittest.mock import patch, MagicMock
from app.services.parser import ResumeParser
from app.core.exceptions import ParsingError, UnsupportedFileTypeError, OCRError

@pytest.fixture
def sample_pdf_bytes():
    """Fixture to provide sample PDF content for testing"""
    # Create minimal valid PDF content for testing
    return b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>/Contents 4 0 R>>\nendobj\n4 0 obj\n<</Length 72>>\nstream\nBT\n/F1 12 Tf\n72 712 Td\n(Sample Resume\nPython Developer\nSoftware Engineer\nTest Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000018 00000 n \n0000000077 00000 n \n0000000178 00000 n \n0000000457 00000 n \ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n565\n%%EOF"

@pytest.fixture
def mock_structured_data():
    """Fixture to provide expected structured data format"""
    return {
        "contact_info": {
            "email": "test@example.com",
            "phone": "123-456-7890"
        },
        "education": [
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science", 
                "school": "Test University",
                "year": "2023"
            }
        ],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Test Corp",
                "duration": "2 years",
                "description": "Developed web applications"
            }
        ],
        "skills": [
            "Python",
            "FastAPI",
            "Testing"
        ]
    }

@patch('PyPDF2.PdfReader')
def test_pdf_parsing(mock_pdf_reader, sample_pdf_bytes):
    """Test PDF parsing functionality"""
    # Create a mock for PdfReader and its page
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample Resume\nPython Developer\nSoftware Engineer\nTest Content"
    
    # Set up the mock reader
    mock_instance = mock_pdf_reader.return_value
    mock_instance.pages = [mock_page]
    
    parsed_text = ResumeParser.parse_resume(sample_pdf_bytes, "pdf")
    assert isinstance(parsed_text, str)
    assert len(parsed_text) > 0
    # Check for expected content
    assert "Sample Resume" in parsed_text
    assert "Python" in parsed_text
    assert "Software Engineer" in parsed_text

@patch('app.services.ocr_service.OCRService.extract_text_from_pdf')
def test_pdf_parsing_with_ocr(mock_ocr_service, sample_pdf_bytes):
    """Test PDF parsing with OCR enabled"""
    # Mock the OCR service to return sample text
    mock_ocr_service.return_value = "Sample Resume\nPython Developer\nOCR Extracted Content"
    
    parsed_text = ResumeParser.parse_resume(sample_pdf_bytes, "pdf", use_ocr=True)
    assert isinstance(parsed_text, str)
    assert len(parsed_text) > 0
    # Verify some text was extracted
    assert "Sample Resume" in parsed_text
    assert "OCR Extracted Content" in parsed_text

def test_structured_data_extraction():
    """Test structured data extraction from resume"""
    # Use a predefined sample text for more reliable testing
    resume_text = """
    John Doe
    test@example.com
    123-456-7890
    
    EDUCATION
    Bachelor of Science in Computer Science
    Test University, 2023
    
    EXPERIENCE
    Software Engineer
    Test Corp, 2021-2023
    Developed web applications
    
    SKILLS
    Python, FastAPI, Testing
    """
    
    structured_data = ResumeParser.extract_structured_data(resume_text)
    
    # Verify structure
    assert isinstance(structured_data, dict)
    assert "contact_info" in structured_data
    assert "education" in structured_data
    assert "experience" in structured_data
    assert "skills" in structured_data
    
    # Verify data types
    assert isinstance(structured_data["contact_info"], dict)
    assert isinstance(structured_data["education"], list)
    assert isinstance(structured_data["experience"], list)
    assert isinstance(structured_data["skills"], list)
    
    # Verify extracted content
    assert "test@example.com" in structured_data["contact_info"].get("email", "")

def test_unsupported_file_type():
    """Test handling of unsupported file types"""
    with pytest.raises(UnsupportedFileTypeError):
        ResumeParser.parse_resume(b"test content", ".xyz")

def test_invalid_pdf_content():
    """Test handling of invalid PDF content"""
    with pytest.raises(ParsingError):
        ResumeParser.parse_resume(b"invalid pdf content", "pdf")

def test_empty_content():
    """Test handling of empty content"""
    with pytest.raises(ParsingError):
        ResumeParser.parse_resume(b"", "pdf")

@patch('app.services.ocr_service.OCRService.extract_text_from_pdf')
def test_ocr_error_handling(mock_ocr_service):
    """Test handling of OCR errors"""
    mock_ocr_service.side_effect = OCRError("OCR processing failed")
    
    with pytest.raises(OCRError):
        ResumeParser.parse_resume(b"invalid pdf content", "pdf", use_ocr=True)