# app/core/dependencies.py
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.core.models import User
from app.core.exceptions import AuthenticationError
from app.services.job_description_parser import JobDescriptionParser
from app.services.slm_service import SLMService

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get the current authenticated user"""
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise AuthenticationError("Invalid authentication credentials")
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user"""
    # Add any additional checks for active users here
    return current_user 

# Dependency for JobDescriptionParser
job_description_parser_instance = JobDescriptionParser() # Create a single instance

def get_job_description_parser() -> JobDescriptionParser:
    """Dependency to get the JobDescriptionParser instance"""
    return job_description_parser_instance 

# Dependency for SLMService
slm_service_instance = SLMService() # Create a single instance

def get_slm_service() -> SLMService:
    """Dependency to get the SLMService instance"""
    return slm_service_instance 