# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings"""
    APP_NAME: str = "AI Resume Analyzer"
    APP_VERSION: str = "0.1.0"
    
    # NLP and parsing configurations
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    SUPPORTED_FILE_TYPES: list = ['.pdf', '.docx', '.txt']
    
    # Skill extraction settings
    MIN_SKILL_CONFIDENCE: float = 0.5
    MAX_EXTRACTED_SKILLS: int = 20
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()