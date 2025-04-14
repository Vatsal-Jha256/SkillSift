from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean, UniqueConstraint, func
from sqlalchemy.orm import relationship, Session
import logging
from app.core.database import Base
# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

# SQLAlchemy Models
# SQLAlchemy Models
class User(Base):
    """Database model for users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
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

class IndustrySkillSet(Base):
    """Database model for industry-specific skill sets"""
    __tablename__ = "industry_skill_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    industry_name = Column(String, unique=True, index=True, nullable=False)
    skills = Column(JSON, nullable=False) # Storing skills as a JSON list
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IndustryTrend(Base):
    """Database model for industry trends"""
    __tablename__ = "industry_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    industry_name = Column(String, index=True, nullable=False)
    trend_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    relevance_score = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('industry_name', 'trend_name', name='_industry_trend_uc'),)

class SalaryRange(Base):
    """Database model for salary ranges by job title and industry"""
    __tablename__ = "salary_ranges"
    
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, index=True, nullable=False)
    industry_name = Column(String, index=True, nullable=False)
    location = Column(String, index=True, nullable=True)  # Optional location specificity
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)
    median_salary = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    experience_level = Column(String, nullable=True)  # e.g., "entry", "mid", "senior"
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('job_title', 'industry_name', 'location', 'experience_level', name='_salary_range_uc'),)

class JobMarketDemand(Base):
    """Database model for job market demand data"""
    __tablename__ = "job_market_demands"
    
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, index=True, nullable=False)
    industry_name = Column(String, index=True, nullable=False)
    location = Column(String, index=True, nullable=True)  # Optional location specificity
    demand_score = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    growth_rate = Column(Float, nullable=True)  # Annual percentage growth
    num_openings = Column(Integer, nullable=True)  # Estimated number of job openings
    time_period = Column(String, nullable=True)  # e.g., "Q2 2023" or "2023"
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('job_title', 'industry_name', 'location', 'time_period', name='_job_market_demand_uc'),)

class CareerPath(Base):
    """Database model for career path recommendations"""
    __tablename__ = "career_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    starting_role = Column(String, index=True, nullable=False)
    industry_name = Column(String, index=True, nullable=False)
    path_steps = Column(JSON, nullable=False)  # List of role progressions with required skills/experience
    avg_transition_time = Column(JSON, nullable=True)  # Average time between steps in months
    skill_requirements = Column(JSON, nullable=True)  # Key skills needed for progression
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('starting_role', 'industry_name', name='_career_path_uc'),)

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

class CoverLetterTemplate(Base):
    """Database model for cover letter templates"""
    __tablename__ = "cover_letter_templates"
    
    id = Column(String, primary_key=True, index=True)  # Using string ID for semantic naming
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    industry = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # No relationship definitions

class CoverLetter(Base):
    """Database model for generated cover letters"""
    __tablename__ = "cover_letters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    template_id = Column(String, ForeignKey("cover_letter_templates.id"))
    job_title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tone = Column(String, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    # No relationship to template, just use the foreign key

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

class CoverLetterTemplateBase(BaseModel):
    """Base model for cover letter templates"""
    name: str
    content: str
    industry: Optional[str] = None

class CoverLetterTemplateCreate(CoverLetterTemplateBase):
    """Model for creating a new cover letter template"""
    id: str

class CoverLetterTemplateUpdate(CoverLetterTemplateBase):
    """Model for updating a cover letter template"""
    pass

class CoverLetterTemplate(CoverLetterTemplateBase):
    """Model for cover letter template response"""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class CoverLetterRequest(BaseModel):
    """Model for cover letter generation request"""
    template_id: str
    job_title: str
    company_name: str
    applicant_name: str
    skills: List[str]
    background: Optional[str] = None
    experience: Optional[str] = None
    hiring_manager: Optional[str] = None
    job_source: Optional[str] = None
    company_interest: Optional[str] = None
    job_description: Optional[str] = None
    tone: Optional[str] = None  # e.g., "professional", "friendly", "formal"

class CoverLetterResponse(BaseModel):
    """Model for cover letter generation response"""
    content: str
    created_at: str
    template_id: str
    meta_data: Dict[str, Any]
    
    class Config:
        orm_mode = True

class LoginForm(BaseModel):
    username: str
    password: str

class Analysis(Base):
    """Model for storing resume analysis results"""
    __tablename__ = "analysis"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    resume_filename = Column(String)
    analysis_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @classmethod
    def create_from_result(cls, db: Session, user_id: str, analysis_result: Dict) -> 'Analysis':
        """Create analysis record from results"""
        try:
            analysis = cls(
                user_id=str(user_id),
                resume_filename=analysis_result.get('resume_filename'),
                analysis_data=analysis_result
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating analysis: {str(e)}")
            raise