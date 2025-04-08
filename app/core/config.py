# app/core/config.py
from typing import Optional, List
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "AI Resume Analyzer"
    APP_NAME: str = "AI Resume Analyzer"  # Added for compatibility
    APP_VERSION: str = "1.0.0"  # Added for compatibility
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]  # Allow all origins in development

    # Database settings
    DATABASE_URL: str = "sqlite:///./app.db"
    DATABASE_ECHO: bool = False
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES: list[str] = ["pdf", "docx", "txt"]

    # OCR settings
    ENABLE_OCR: bool = True
    OCR_DPI: int = 300
    OCR_LANGUAGE: str = "eng"

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

settings = Settings()