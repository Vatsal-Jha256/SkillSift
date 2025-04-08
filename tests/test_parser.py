# tests/unit/test_parser.py
import pytest
from app.services.parser import ResumeParser

def test_pdf_parsing(sample_pdf_bytes):
    parsed_text = ResumeParser.parse_pdf(sample_pdf_bytes)
    assert isinstance(parsed_text, str)
    assert len(parsed_text) > 0
