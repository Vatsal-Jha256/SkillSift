# app/core/config.py
from typing import Optional, List
from pydantic import BaseModel
import os # Import os

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
    
    # Hugging Face Inference API settings
    HF_API_TOKEN: Optional[str] = os.getenv("HF_API_TOKEN")
    HF_MODEL_API_URL="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    
    # Privacy and security settings
    DATA_EXPORTS_DIR: str = "data/exports"
    SECURE_UPLOADS_DIR: str = "data/secure_uploads"
    AUDIT_LOGS_DIR: str = "data/audit_logs"

settings = Settings()