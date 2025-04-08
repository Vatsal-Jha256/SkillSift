from pydantic import BaseModel, Field
from typing import List, Optional

class ResumeData(BaseModel):
    """Structured model for parsed resume data"""
    raw_text: str
    extracted_skills: List[str] = []
    job_compatibility_score: Optional[float] = None
    
class SkillExtraction(BaseModel):
    """Model for skill extraction results"""
    skills: List[str]
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
class CompatibilityReport(BaseModel):
    """Model for job compatibility analysis"""
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    matched_skills: List[str]
    recommendations: Optional[List[str]] = None