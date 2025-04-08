from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

# SQLAlchemy Models
class User(Base):
    """Database model for users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resumes = relationship("Resume", back_populates="owner")

class Resume(Base):
    """Database model for resumes"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_type = Column(String)
    raw_text = Column(Text)
    parsed_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="resumes")
    analyses = relationship("ResumeAnalysis", back_populates="resume")

class ResumeAnalysis(Base):
    """Database model for resume analyses"""
    __tablename__ = "resume_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_description = Column(Text)
    extracted_skills = Column(JSON)
    compatibility_score = Column(Float)
    matched_skills = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="analyses")

# Pydantic Models for API
class ResumeBase(BaseModel):
    """Base model for resume data"""
    filename: str
    file_type: str

class ResumeCreate(ResumeBase):
    """Model for creating a new resume"""
    raw_text: str
    parsed_data: Optional[Dict[str, Any]] = None

class ResumeData(ResumeBase):
    """Structured model for parsed resume data"""
    id: int
    raw_text: str
    parsed_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class SkillExtraction(BaseModel):
    """Model for skill extraction results"""
    skills: List[str]
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    skill_categories: Optional[Dict[str, List[str]]] = None

class CompatibilityReport(BaseModel):
    """Model for job compatibility analysis"""
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    matched_skills: List[str]
    recommendations: Optional[List[str]] = None
    skill_gaps: Optional[List[str]] = None
    experience_match: Optional[float] = None
    education_match: Optional[float] = None

class AnalysisCreate(BaseModel):
    """Model for creating a new analysis"""
    resume_id: int
    job_description: str
    extracted_skills: List[str]
    compatibility_score: float
    matched_skills: List[str]
    recommendations: Optional[List[str]] = None

class AnalysisResponse(BaseModel):
    """Model for analysis response"""
    id: int
    resume_id: int
    job_description: str
    extracted_skills: List[str]
    compatibility_score: float
    matched_skills: List[str]
    recommendations: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    """Base model for user data"""
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str

class UserResponse(UserBase):
    """Model for user response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    """Model for authentication token"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Model for token data"""
    email: Optional[str] = None