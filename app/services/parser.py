# app/services/parser.py
import io
import PyPDF2
import docx
from typing import Union, Optional

class ResumeParser:
    """Service for parsing different resume file formats"""
    
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            # Focus on first page for MVP
            first_page = pdf_reader.pages[0]
            return first_page.extract_text().strip()
        except Exception as e:
            raise ValueError(f"PDF parsing error: {str(e)}")
    
    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            # Combine text from paragraphs
            return " ".join([para.text for para in doc.paragraphs if para.text]).strip()
        except Exception as e:
            raise ValueError(f"DOCX parsing error: {str(e)}")
    
    @staticmethod
    def parse_txt(file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8').strip()
        except Exception as e:
            raise ValueError(f"TXT parsing error: {str(e)}")
    
    @classmethod
    def parse_resume(cls, file_content: bytes, file_extension: str) -> str:
        """
        Route parsing based on file type
        
        Args:
            file_content (bytes): Raw file content
            file_extension (str): File extension
        
        Returns:
            str: Extracted text content
        """
        parsers = {
            '.pdf': cls.parse_pdf,
            '.docx': cls.parse_docx,
            '.txt': cls.parse_txt
        }
        
        parser = parsers.get(file_extension.lower())
        if not parser:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        return parser(file_content)