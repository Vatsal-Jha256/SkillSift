# app/services/parser.py
import io
import re
import PyPDF2
import docx
from typing import Union, Optional, Dict, Any, List
from app.core.logging import logger
from app.core.exceptions import ParsingError, UnsupportedFileTypeError, OCRError
from app.services.ocr_service import OCRService

class ResumeParser:
    """Service for parsing different resume file formats"""
    
    # Regular expressions for extracting structured data
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    EDUCATION_PATTERNS = [
        r'(?i)(?:education|academic background|qualification)',
        r'(?i)(?:bachelor|master|phd|doctorate|degree)',
        r'(?i)(?:university|college|institute)'
    ]
    EXPERIENCE_PATTERNS = [
        r'(?i)(?:experience|work experience|employment history|professional experience)',
        r'(?i)(?:job|position|role|employment)'
    ]
    SKILLS_PATTERNS = [
        r'(?i)(?:skills|technical skills|competencies|expertise)',
        r'(?i)(?:proficient in|experienced with|knowledge of)'
    ]
    
    @staticmethod
    def parse_pdf(file_content: bytes, use_ocr: bool = False) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_content (bytes): Raw PDF data
            use_ocr (bool): Whether to use OCR for text extraction
            
        Returns:
            str: Extracted text
        """
        try:
            if use_ocr:
                try:
                    return OCRService.extract_text_from_pdf(file_content)
                except OCRError as e:
                    # Re-raise OCR errors directly
                    raise e
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                # If page has no text, it might be scanned
                if not page_text.strip() and not use_ocr:
                    logger.info("No text extracted from PDF page, attempting OCR")
                    try:
                        return OCRService.extract_text_from_pdf(file_content)
                    except OCRError as e:
                        # Re-raise OCR errors directly
                        raise e
                text += page_text + "\n"
            return text.strip()
        except OCRError:
            # Re-raise OCR errors directly
            raise
        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")
            raise ParsingError(str(e))
    
    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            # Combine text from paragraphs
            return " ".join([para.text for para in doc.paragraphs if para.text]).strip()
        except Exception as e:
            logger.error(f"DOCX parsing error: {str(e)}")
            raise ParsingError(str(e))
    
    @staticmethod
    def parse_txt(file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8').strip()
        except Exception as e:
            logger.error(f"TXT parsing error: {str(e)}")
            raise ParsingError(str(e))
    
    @classmethod
    def parse_resume(cls, file_content: bytes, file_extension: str, use_ocr: bool = False) -> str:
        """
        Route parsing based on file type
        
        Args:
            file_content (bytes): Raw file content
            file_extension (str): File extension
            use_ocr (bool): Whether to use OCR for text extraction
        
        Returns:
            str: Extracted text content
        """
        parsers = {
            '.pdf': lambda content: cls.parse_pdf(content, use_ocr),
            '.docx': cls.parse_docx,
            '.txt': cls.parse_txt
        }
        
        parser = parsers.get(file_extension.lower())
        if not parser:
            logger.error(f"Unsupported file type: {file_extension}")
            raise UnsupportedFileTypeError(file_extension)
        
        return parser(file_content)
    
    @classmethod
    def extract_structured_data(cls, text: str) -> Dict[str, Any]:
        """
        Extract structured data from resume text
        
        Args:
            text (str): Parsed resume text
            
        Returns:
            Dict[str, Any]: Structured resume data
        """
        # Initialize structured data
        structured_data = {
            "contact_info": {},
            "education": [],
            "experience": [],
            "skills": [],
            "sections": {}
        }
        
        # Split text into lines
        lines = text.split('\n')
        
        # Extract contact information
        for line in lines:
            # Email
            email_match = re.search(cls.EMAIL_PATTERN, line)
            if email_match:
                structured_data["contact_info"]["email"] = email_match.group()
            
            # Phone
            phone_match = re.search(cls.PHONE_PATTERN, line)
            if phone_match:
                structured_data["contact_info"]["phone"] = phone_match.group()
        
        # Detect section boundaries
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Education section
            if any(re.search(pattern, line_lower) for pattern in cls.EDUCATION_PATTERNS):
                structured_data["sections"]["education"] = i
            
            # Experience section
            if any(re.search(pattern, line_lower) for pattern in cls.EXPERIENCE_PATTERNS):
                structured_data["sections"]["experience"] = i
            
            # Skills section
            if any(re.search(pattern, line_lower) for pattern in cls.SKILLS_PATTERNS):
                structured_data["sections"]["skills"] = i
        
        # Extract education information
        if "education" in structured_data["sections"]:
            start_idx = structured_data["sections"]["education"]
            education_text = "\n".join(lines[start_idx:start_idx+20])  # Approximate education section
            structured_data["education"] = cls._extract_education(education_text)
        
        # Extract experience information
        if "experience" in structured_data["sections"]:
            start_idx = structured_data["sections"]["experience"]
            experience_text = "\n".join(lines[start_idx:start_idx+50])  # Approximate experience section
            structured_data["experience"] = cls._extract_experience(experience_text)
        
        # Extract skills
        if "skills" in structured_data["sections"]:
            start_idx = structured_data["sections"]["skills"]
            skills_text = "\n".join(lines[start_idx:start_idx+20])  # Approximate skills section
            structured_data["skills"] = cls._extract_skills_list(skills_text)
        
        return structured_data
    
    @staticmethod
    def _extract_education(text: str) -> List[Dict[str, str]]:
        """Extract education information from text"""
        education = []
        # Simple extraction - can be enhanced with NLP
        lines = text.split('\n')
        for line in lines:
            if re.search(r'(?i)(?:bachelor|master|phd|doctorate|degree)', line):
                education.append({"degree": line.strip()})
        
        return education
    
    @staticmethod
    def _extract_experience(text: str) -> List[Dict[str, str]]:
        """Extract work experience from text"""
        experience = []
        # Simple extraction - can be enhanced with NLP
        lines = text.split('\n')
        current_experience = {}
        
        for line in lines:
            if re.search(r'(?i)(?:present|current|20\d{2})', line):
                if current_experience:
                    experience.append(current_experience)
                current_experience = {"title": line.strip()}
            elif current_experience and line.strip():
                if "description" not in current_experience:
                    current_experience["description"] = line.strip()
                else:
                    current_experience["description"] += " " + line.strip()
        
        if current_experience:
            experience.append(current_experience)
        
        return experience
    
    @staticmethod
    def _extract_skills_list(text: str) -> List[str]:
        """Extract skills from text"""
        skills = []
        # Simple extraction - can be enhanced with NLP
        lines = text.split('\n')
        for line in lines:
            # Look for comma-separated skills
            if ',' in line:
                skills.extend([skill.strip() for skill in line.split(',')])
            # Look for bullet points
            elif re.search(r'[•\-\*]', line):
                skills.append(line.replace('•', '').replace('-', '').replace('*', '').strip())
        
        return [skill for skill in skills if skill]