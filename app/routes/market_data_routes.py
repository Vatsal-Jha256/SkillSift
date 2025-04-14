from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.core.logging import logger
from app.services.market_data_service import MarketDataService
from app.core.models import SalaryRange, JobMarketDemand, CareerPath, IndustryTrend, User
from app.core.dependencies import get_current_active_user
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

router = APIRouter()
market_data_service = MarketDataService()

# Pydantic models for requests and responses
class SalaryRangeBase(BaseModel):
    job_title: str = Field(..., example="Software Engineer")
    industry_name: str = Field(..., example="Technology")
    location: Optional[str] = Field(None, example="San Francisco")
    min_salary: int = Field(..., example=80000)
    max_salary: int = Field(..., example=120000)
    median_salary: int = Field(..., example=95000)
    currency: str = Field("USD", example="USD")
    experience_level: Optional[str] = Field(None, example="mid")
    source: Optional[str] = Field(None, example="Industry Survey 2023")

class SalaryRangeCreate(SalaryRangeBase):
    pass

class SalaryRangeResponse(SalaryRangeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class JobMarketDemandBase(BaseModel):
    job_title: str = Field(..., example="Data Scientist")
    industry_name: str = Field(..., example="Technology")
    location: Optional[str] = Field(None, example="Remote")
    demand_score: float = Field(..., example=0.85)
    growth_rate: Optional[float] = Field(None, example=15.2)
    num_openings: Optional[int] = Field(None, example=12000)
    time_period: Optional[str] = Field(None, example="Q2 2023")
    source: Optional[str] = Field(None, example="Bureau of Labor Statistics")

class JobMarketDemandCreate(JobMarketDemandBase):
    pass

class JobMarketDemandResponse(JobMarketDemandBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CareerStepModel(BaseModel):
    role: str
    description: str
    required_skills: List[str]
    avg_years_experience: Optional[float] = None
    typical_salary_range: Optional[Dict[str, int]] = None

class CareerPathBase(BaseModel):
    starting_role: str = Field(..., example="Junior Developer")
    industry_name: str = Field(..., example="Technology")
    path_steps: List[Dict[str, Any]] = Field(..., example=[
        {"role": "Mid-level Developer", "description": "Responsible for implementing features", 
         "required_skills": ["JavaScript", "React", "Node.js"], "avg_years_experience": 3},
        {"role": "Senior Developer", "description": "Leading development efforts", 
         "required_skills": ["System Design", "Architecture", "Team Leadership"], "avg_years_experience": 5}
    ])
    avg_transition_time: Optional[Dict[str, int]] = Field(None, example={"Junior to Mid": 24, "Mid to Senior": 36})
    skill_requirements: Optional[Dict[str, List[str]]] = Field(None)

class CareerPathCreate(CareerPathBase):
    pass

class CareerPathResponse(CareerPathBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class IndustryTrendBase(BaseModel):
    industry_name: str = Field(..., example="Technology")
    trend_name: str = Field(..., example="Artificial Intelligence")
    description: str = Field(..., example="Growing adoption of AI in software development")
    relevance_score: float = Field(..., example=0.9)
    source: Optional[str] = Field(None, example="Industry Report 2023")

class IndustryTrendCreate(IndustryTrendBase):
    pass

class IndustryTrendResponse(IndustryTrendBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class MarketCompetitivenessRequest(BaseModel):
    candidate: Dict[str, Any]
    job: Dict[str, Any]

class MarketCompetitivenessResponse(BaseModel):
    market_score: int
    salary_range: Optional[Dict[str, Any]] = None
    demand_info: Optional[Dict[str, Any]] = None
    next_career_steps: List[Dict[str, Any]] = []
    market_insights: List[Dict[str, Any]] = []

# Salary Range endpoints
@router.post("/salary", response_model=SalaryRangeResponse, status_code=status.HTTP_201_CREATED)
async def create_salary_range(
    salary_data: SalaryRangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new salary range entry"""
    logger.info(f"Creating salary range for {salary_data.job_title} in {salary_data.industry_name}")
    
    try:
        # Check if entry already exists
        existing = db.query(SalaryRange).filter(
            SalaryRange.job_title == salary_data.job_title,
            SalaryRange.industry_name == salary_data.industry_name,
            SalaryRange.location == salary_data.location,
            SalaryRange.experience_level == salary_data.experience_level
        ).first()
        
        if existing:
            # Update existing entry
            for key, value in salary_data.dict().items():
                setattr(existing, key, value)
            db_salary = existing
        else:
            # Create new entry
            db_salary = SalaryRange(**salary_data.dict())
            db.add(db_salary)
            
        db.commit()
        db.refresh(db_salary)
        return db_salary
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating salary range: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Could not create salary range: {str(e)}")

@router.get("/salary/{job_title}", response_model=List[SalaryRangeResponse])
async def get_salary_ranges(
    job_title: str,
    industry_name: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get salary ranges for a job title with optional filters"""
    try:
        query = db.query(SalaryRange).filter(SalaryRange.job_title.ilike(f"%{job_title}%"))
        
        if industry_name:
            query = query.filter(SalaryRange.industry_name == industry_name)
        if location:
            query = query.filter(SalaryRange.location == location)
        if experience_level:
            query = query.filter(SalaryRange.experience_level == experience_level)
            
        results = query.all()
        if not results:
            raise HTTPException(status_code=404, detail="No salary data found for the specified criteria")
            
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching salary data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch salary data: {str(e)}")

# Job Market Demand endpoints
@router.post("/demand", response_model=JobMarketDemandResponse, status_code=status.HTTP_201_CREATED)
async def create_job_market_demand(
    demand_data: JobMarketDemandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new job market demand entry"""
    logger.info(f"Creating job market demand for {demand_data.job_title} in {demand_data.industry_name}")
    
    try:
        # Check if entry already exists
        existing = db.query(JobMarketDemand).filter(
            JobMarketDemand.job_title == demand_data.job_title,
            JobMarketDemand.industry_name == demand_data.industry_name,
            JobMarketDemand.location == demand_data.location,
            JobMarketDemand.time_period == demand_data.time_period
        ).first()
        
        if existing:
            # Update existing entry
            for key, value in demand_data.dict().items():
                setattr(existing, key, value)
            db_demand = existing
        else:
            # Create new entry
            db_demand = JobMarketDemand(**demand_data.dict())
            db.add(db_demand)
            
        db.commit()
        db.refresh(db_demand)
        return db_demand
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating job market demand: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Could not create job market demand: {str(e)}")

@router.get("/demand/{job_title}", response_model=List[JobMarketDemandResponse])
async def get_job_market_demand(
    job_title: str,
    industry_name: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get job market demand data for a job title with optional filters"""
    try:
        query = db.query(JobMarketDemand).filter(JobMarketDemand.job_title.ilike(f"%{job_title}%"))
        
        if industry_name:
            query = query.filter(JobMarketDemand.industry_name == industry_name)
        if location:
            query = query.filter(JobMarketDemand.location == location)
            
        # Order by most recent time period
        query = query.order_by(JobMarketDemand.time_period.desc())
            
        results = query.all()
        if not results:
            raise HTTPException(status_code=404, detail="No job market demand data found for the specified criteria")
            
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job market demand data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch job market demand data: {str(e)}")

# Career Path endpoints
@router.post("/career-path", response_model=CareerPathResponse, status_code=status.HTTP_201_CREATED)
async def create_career_path(
    career_path_data: CareerPathCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new career path entry"""
    logger.info(f"Creating career path for {career_path_data.starting_role} in {career_path_data.industry_name}")
    
    try:
        # Check if entry already exists
        existing = db.query(CareerPath).filter(
            CareerPath.starting_role == career_path_data.starting_role,
            CareerPath.industry_name == career_path_data.industry_name
        ).first()
        
        if existing:
            # Update existing entry
            for key, value in career_path_data.dict().items():
                setattr(existing, key, value)
            db_career_path = existing
        else:
            # Create new entry
            db_career_path = CareerPath(**career_path_data.dict())
            db.add(db_career_path)
            
        db.commit()
        db.refresh(db_career_path)
        return db_career_path
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating career path: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Could not create career path: {str(e)}")

@router.get("/career-path/{role}", response_model=List[CareerPathResponse])
async def get_career_path(
    role: str,
    industry_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get career path data for a role with optional industry filter"""
    try:
        query = db.query(CareerPath).filter(CareerPath.starting_role.ilike(f"%{role}%"))
        
        if industry_name:
            query = query.filter(CareerPath.industry_name == industry_name)
            
        results = query.all()
        if not results:
            raise HTTPException(status_code=404, detail="No career path data found for the specified criteria")
            
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching career path data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch career path data: {str(e)}")

# Industry Trend endpoints
@router.post("/trends", response_model=IndustryTrendResponse, status_code=status.HTTP_201_CREATED)
async def create_industry_trend(
    trend_data: IndustryTrendCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new industry trend entry"""
    logger.info(f"Creating industry trend '{trend_data.trend_name}' for {trend_data.industry_name}")
    
    try:
        # Check if entry already exists
        existing = db.query(IndustryTrend).filter(
            IndustryTrend.industry_name == trend_data.industry_name,
            IndustryTrend.trend_name == trend_data.trend_name
        ).first()
        
        if existing:
            # Update existing entry
            for key, value in trend_data.dict().items():
                setattr(existing, key, value)
            db_trend = existing
        else:
            # Create new entry
            db_trend = IndustryTrend(**trend_data.dict())
            db.add(db_trend)
            
        db.commit()
        db.refresh(db_trend)
        return db_trend
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating industry trend: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Could not create industry trend: {str(e)}")

@router.get("/trends/{industry_name}", response_model=List[IndustryTrendResponse])
async def get_industry_trends(
    industry_name: str,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get industry trends for a specific industry"""
    try:
        trends = db.query(IndustryTrend).filter(
            IndustryTrend.industry_name == industry_name
        ).order_by(
            IndustryTrend.relevance_score.desc()
        ).limit(limit).all()
        
        if not trends:
            raise HTTPException(status_code=404, detail=f"No trends found for industry: {industry_name}")
            
        return trends
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching industry trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch industry trends: {str(e)}")

# Market competitiveness analysis endpoint
@router.post("/analyze", response_model=MarketCompetitivenessResponse)
async def analyze_market_competitiveness(
    data: MarketCompetitivenessRequest,
    db: Session = Depends(get_db)
):
    """Analyze market competitiveness for a candidate against a job"""
    try:
        result = market_data_service.calculate_market_competitive_score(
            candidate_data=data.candidate,
            job_data=data.job,
            db=db
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing market competitiveness: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze market competitiveness: {str(e)}") 