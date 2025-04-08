# app/services/ocr_service.py
import io
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from typing import Optional
from app.core.logging import logger
from app.core.exceptions import OCRError

class OCRService:
    """Service for handling OCR operations on documents"""
    
    @staticmethod
    def extract_text_from_image(image_bytes: bytes) -> str:
        """
        Extract text from an image using OCR
        
        Args:
            image_bytes (bytes): Raw image data
            
        Returns:
            str: Extracted text
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise OCRError(f"Failed to extract text from image: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes, dpi: int = 300) -> str:
        """
        Extract text from a PDF using OCR
        
        Args:
            pdf_bytes (bytes): Raw PDF data
            dpi (int): DPI for image conversion
            
        Returns:
            str: Extracted text
        """
        try:
            # Convert PDF pages to images
            images = convert_from_bytes(pdf_bytes, dpi=dpi)
            
            # Extract text from each page
            text = ""
            for image in images:
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"PDF OCR error: {str(e)}")
            raise OCRError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def is_scanned_document(text: str, threshold: float = 0.3) -> bool:
        """
        Determine if a document is likely scanned based on text characteristics
        
        Args:
            text (str): Extracted text
            threshold (float): Threshold for determining if document is scanned
            
        Returns:
            bool: True if document appears to be scanned
        """
        if not text:
            return False
        
        # Check for common OCR artifacts
        ocr_indicators = [
            len(text.split()) < 50,  # Very little text
            text.count('\n') / len(text) > 0.3,  # Many line breaks
            text.count(' ') / len(text) > 0.2,  # Many spaces
            text.count('•') > 0,  # Bullet points (common in resumes)
            text.count('|') > 0,  # Vertical lines (common in tables)
            text.count('_') > 0,  # Underlines (common in forms)
        ]
        
        # Calculate score based on indicators
        score = sum(ocr_indicators) / len(ocr_indicators)
        
        # For regular text, we expect a low score
        return score > threshold 