# app/core/logging.py
import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure structured logging for the application"""
    # Create logger
    logger = logging.getLogger("skillsift")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Create logger instance
logger = setup_logging() 