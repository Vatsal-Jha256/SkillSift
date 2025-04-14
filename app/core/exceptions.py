# app/core/exceptions.py
from fastapi import HTTPException, status

class ResumeAnalyzerException(HTTPException):
    """Base exception for the Resume Analyzer application"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)

class FileProcessingError(ResumeAnalyzerException):
    """Exception for file processing errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class UnsupportedFileTypeError(FileProcessingError):
    """Exception for unsupported file types"""
    def __init__(self, file_type: str):
        super().__init__(detail=f"Unsupported file type: {file_type}")

class FileTooLargeError(FileProcessingError):
    """Exception for files that exceed size limits"""
    def __init__(self, max_size_mb: int):
        super().__init__(detail=f"File exceeds maximum size of {max_size_mb}MB")

class ParsingError(FileProcessingError):
    """Exception for resume parsing errors"""
    def __init__(self, detail: str):
        super().__init__(detail=f"Error parsing resume: {detail}")

class SkillExtractionError(ResumeAnalyzerException):
    """Exception for skill extraction errors"""
    def __init__(self, detail: str):
        super().__init__(detail=f"Error extracting skills: {detail}", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class CompatibilityScoringError(ResumeAnalyzerException):
    """Exception for compatibility scoring errors"""
    def __init__(self, detail: str):
        super().__init__(detail=f"Error calculating compatibility score: {detail}", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class ReportGenerationError(ResumeAnalyzerException):
    """Exception for report generation errors"""
    def __init__(self, detail: str):
        super().__init__(detail=f"Error generating report: {detail}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DatabaseError(ResumeAnalyzerException):
    """Exception for database errors"""
    def __init__(self, detail: str):
        super().__init__(detail=f"Database error: {detail}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AuthenticationError(ResumeAnalyzerException):
    """Exception for authentication errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class AuthorizationError(ResumeAnalyzerException):
    """Exception for authorization errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)

class ResourceNotFoundError(ResumeAnalyzerException):
    """Exception for resource not found errors"""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(detail=f"{resource_type} with id {resource_id} not found", status_code=status.HTTP_404_NOT_FOUND)

class NotFoundError(ResumeAnalyzerException):
    """Exception for generic not found errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class OCRError(Exception):
    """Exception raised when there is an error performing OCR"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message) 