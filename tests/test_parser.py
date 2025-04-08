# tests/unit/test_parser.py
import pytest
from app.services.parser import ResumeParser
from app.core.exceptions import ParsingError, UnsupportedFileTypeError, OCRError

def test_pdf_parsing(sample_pdf_bytes):
    """Test PDF parsing functionality"""
    parsed_text = ResumeParser.parse_resume(sample_pdf_bytes, ".pdf")
    assert isinstance(parsed_text, str)
    assert len(parsed_text) > 0
    assert "Sample Resume" in parsed_text
    assert "Python" in parsed_text
    assert "Software Engineer" in parsed_text

def test_pdf_parsing_with_ocr(sample_pdf_bytes):
    """Test PDF parsing with OCR enabled"""
    parsed_text = ResumeParser.parse_resume(sample_pdf_bytes, ".pdf", use_ocr=True)
    assert isinstance(parsed_text, str)
    assert len(parsed_text) > 0

def test_structured_data_extraction(sample_pdf_bytes):
    """Test structured data extraction from resume"""
    resume_text = ResumeParser.parse_resume(sample_pdf_bytes, ".pdf")
    structured_data = ResumeParser.extract_structured_data(resume_text)
    
    assert isinstance(structured_data, dict)
    assert "contact_info" in structured_data
    assert "education" in structured_data
    assert "experience" in structured_data
    assert "skills" in structured_data

def test_unsupported_file_type():
    """Test handling of unsupported file types"""
    with pytest.raises(UnsupportedFileTypeError):
        ResumeParser.parse_resume(b"test content", ".xyz")

def test_invalid_pdf_content():
    """Test handling of invalid PDF content"""
    with pytest.raises(ParsingError):
        ResumeParser.parse_resume(b"invalid pdf content", ".pdf")

def test_empty_content():
    """Test handling of empty content"""
    with pytest.raises(ParsingError):
        ResumeParser.parse_resume(b"", ".pdf")

def test_ocr_error_handling():
    """Test handling of OCR errors"""
    with pytest.raises(OCRError):
        ResumeParser.parse_resume(b"invalid pdf content", ".pdf", use_ocr=True)
