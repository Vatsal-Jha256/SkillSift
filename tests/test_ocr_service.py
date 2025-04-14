import pytest
from PIL import Image
import io
from reportlab.pdfgen import canvas
from app.services.ocr_service import OCRService
from app.core.exceptions import OCRError

@pytest.fixture
def sample_image_bytes():
    """Create a test image with text"""
    image = Image.new('RGB', (100, 30), color='white')
    return image

@pytest.fixture
def sample_pdf_bytes():
    """Create a minimal PDF with text for testing"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(10, 10, "Sample Test Document")
    c.save()
    return buffer.getvalue()

def test_extract_text_from_image(sample_image_bytes):
    """Test OCR text extraction from image"""
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    sample_image_bytes.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Test OCR
    text = OCRService.extract_text_from_image(img_byte_arr)
    assert isinstance(text, str)

def test_extract_text_from_pdf(sample_pdf_bytes):
    """Test OCR text extraction from PDF"""
    text = OCRService.extract_text_from_pdf(sample_pdf_bytes)
    assert isinstance(text, str)
    assert len(text) > 0

def test_is_scanned_document():
    """Test scanned document detection"""
    # Test with text that looks like OCR output
    ocr_text = "Sample Resume\n\nSkills:\n• Python\n• AWS\n\nExperience:\n• Software Engineer"
    assert OCRService.is_scanned_document(ocr_text) is True
    
    # Test with regular text
    regular_text = "This is a regular document with normal formatting and spacing."
    assert OCRService.is_scanned_document(regular_text) is False

def test_invalid_image_bytes():
    """Test handling of invalid image data"""
    with pytest.raises(OCRError):
        OCRService.extract_text_from_image(b"invalid image data")

def test_invalid_pdf_bytes():
    """Test handling of invalid PDF data"""
    with pytest.raises(OCRError):
        OCRService.extract_text_from_pdf(b"invalid pdf data")