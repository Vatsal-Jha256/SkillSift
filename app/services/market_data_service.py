from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.models import SalaryRange, JobMarketDemand, CareerPath, IndustryTrend
from app.core.logging import logger
from app.core.exceptions import DatabaseError, NotFoundError
import statistics

class MarketDataService:
    """Service for managing market data operations including salary ranges, job market demand, and career paths."""
    
    def get_salary_range(self, db: Session, job_title: str, industry_name: str, location: Optional[str] = None, 
                         experience_level: Optional[str] = None) -> Optional[SalaryRange]:
        """
        Get salary range for a specific job title and industry
        
        Args:
            db (Session): Database session
            job_title (str): Job title to lookup
            industry_name (str): Industry name
            location (str, optional): Specific location for salary data
            experience_level (str, optional): Experience level (entry, mid, senior)
            
        Returns:
            Optional[SalaryRange]: Salary range data if found
        """
        logger.debug(f"Fetching salary range for {job_title} in {industry_name}")
        try:
            query = db.query(SalaryRange).filter(
                SalaryRange.job_title.ilike(f"%{job_title}%"),
                SalaryRange.industry_name == industry_name
            )
            
            if location:
                query = query.filter(SalaryRange.location == location)
            
            if experience_level:
                query = query.filter(SalaryRange.experience_level == experience_level)
            
            # Order by most specific match first
            salary_data = query.order_by(
                SalaryRange.location.desc(),  # Non-null locations first
                SalaryRange.experience_level.desc()  # Non-null experience levels first
            ).first()
            
            return salary_data
        except Exception as e:
            logger.error(f"Error fetching salary range: {str(e)}")
            raise DatabaseError(f"Could not fetch salary data: {str(e)}")
    
    def get_job_market_demand(self, db: Session, job_title: str, industry_name: str, 
                             location: Optional[str] = None) -> Optional[JobMarketDemand]:
        """
        Get job market demand data for a specific job title and industry
        
        Args:
            db (Session): Database session
            job_title (str): Job title to lookup
            industry_name (str): Industry name
            location (str, optional): Specific location for demand data
            
        Returns:
            Optional[JobMarketDemand]: Job market demand data if found
        """
        logger.debug(f"Fetching job market demand for {job_title} in {industry_name}")
        try:
            query = db.query(JobMarketDemand).filter(
                JobMarketDemand.job_title.ilike(f"%{job_title}%"),
                JobMarketDemand.industry_name == industry_name
            )
            
            if location:
                query = query.filter(JobMarketDemand.location == location)
            
            # Get the most recent data first
            job_demand = query.order_by(
                JobMarketDemand.location.desc(),  # Non-null locations first
                JobMarketDemand.time_period.desc()  # Most recent time period
            ).first()
            
            return job_demand
        except Exception as e:
            logger.error(f"Error fetching job market demand: {str(e)}")
            raise DatabaseError(f"Could not fetch job market demand data: {str(e)}")
    
    def get_career_path(self, db: Session, current_role: str, industry_name: str) -> Optional[CareerPath]:
        """
        Get career path data for a specific role and industry
        
        Args:
            db (Session): Database session
            current_role (str): Current job title/role
            industry_name (str): Industry name
            
        Returns:
            Optional[CareerPath]: Career path data if found
        """
        logger.debug(f"Fetching career path for {current_role} in {industry_name}")
        try:
            career_path = db.query(CareerPath).filter(
                CareerPath.starting_role.ilike(f"%{current_role}%"),
                CareerPath.industry_name == industry_name
            ).first()
            
            return career_path
        except Exception as e:
            logger.error(f"Error fetching career path: {str(e)}")
            raise DatabaseError(f"Could not fetch career path data: {str(e)}")
    
    def get_industry_trends(self, db: Session, industry_name: str, limit: int = 5) -> List[IndustryTrend]:
        """
        Get current trends for a specific industry
        
        Args:
            db (Session): Database session
            industry_name (str): Industry name
            limit (int): Maximum number of trends to return
            
        Returns:
            List[IndustryTrend]: List of industry trends
        """
        logger.debug(f"Fetching trends for {industry_name}")
        try:
            trends = db.query(IndustryTrend).filter(
                IndustryTrend.industry_name == industry_name
            ).order_by(
                IndustryTrend.relevance_score.desc()
            ).limit(limit).all()
            
            return trends
        except Exception as e:
            logger.error(f"Error fetching industry trends: {str(e)}")
            raise DatabaseError(f"Could not fetch industry trends: {str(e)}")
    
    def find_similar_job_titles(self, db: Session, job_title: str, limit: int = 5) -> List[str]:
        """
        Find similar job titles based on existing data
        
        Args:
            db (Session): Database session
            job_title (str): Job title to find similar titles for
            limit (int): Maximum number of titles to return
            
        Returns:
            List[str]: List of similar job titles
        """
        logger.debug(f"Finding similar job titles for {job_title}")
        try:
            # Get distinct job titles with similar names
            similar_titles = db.query(SalaryRange.job_title).filter(
                SalaryRange.job_title.ilike(f"%{job_title}%")
            ).distinct().limit(limit).all()
            
            return [title[0] for title in similar_titles]
        except Exception as e:
            logger.error(f"Error finding similar job titles: {str(e)}")
            raise DatabaseError(f"Could not find similar job titles: {str(e)}")
    
    def calculate_market_competitive_score(self, candidate_data: Dict, job_data: Dict, db: Session) -> Dict:
        """
        Calculate market competitiveness score for a candidate based on their skills and experience
        
        Args:
            candidate_data (Dict): Candidate profile data
            job_data (Dict): Job posting data
            db (Session): Database session
            
        Returns:
            Dict: Market competitiveness analysis
        """
        logger.debug("Calculating market competitiveness score")
        result = {
            "market_score": 0,
            "salary_range": None,
            "demand_info": None,
            "next_career_steps": [],
            "market_insights": []
        }
        
        try:
            job_title = job_data.get("title", "")
            industry = job_data.get("industry", "")
            candidate_skills = candidate_data.get("skills", [])
            candidate_exp_years = candidate_data.get("years_of_experience", 0)
            
            # Skip if essential data is missing
            if not job_title or not industry:
                logger.warning("Missing job title or industry for market analysis")
                return result
            
            # Get experience level based on years
            exp_level = "entry"
            if candidate_exp_years >= 5:
                exp_level = "senior"
            elif candidate_exp_years >= 2:
                exp_level = "mid"
            
            # Fetch salary data
            salary_data = self.get_salary_range(db, job_title, industry, experience_level=exp_level)
            if salary_data:
                result["salary_range"] = {
                    "min": salary_data.min_salary,
                    "max": salary_data.max_salary,
                    "median": salary_data.median_salary,
                    "currency": salary_data.currency
                }
            
            # Fetch demand data
            demand_data = self.get_job_market_demand(db, job_title, industry)
            if demand_data:
                result["demand_info"] = {
                    "demand_score": demand_data.demand_score,
                    "growth_rate": demand_data.growth_rate,
                    "openings": demand_data.num_openings,
                    "time_period": demand_data.time_period
                }
                # Add market score component based on demand
                result["market_score"] += demand_data.demand_score * 40  # 40% of score from demand
            
            # Fetch career path
            career_path = self.get_career_path(db, job_title, industry)
            if career_path and career_path.path_steps:
                # Get next steps in career path (up to 3)
                next_steps = career_path.path_steps[:3]
                result["next_career_steps"] = next_steps
            
            # Fetch industry trends
            trends = self.get_industry_trends(db, industry)
            if trends:
                result["market_insights"] = [
                    {"trend": trend.trend_name, "description": trend.description}
                    for trend in trends
                ]
            
            # Calculate skills match with market demand (if we have market skill data)
            if career_path and career_path.skill_requirements:
                market_skills = career_path.skill_requirements.get("required", [])
                if market_skills:
                    matched_market_skills = [skill for skill in candidate_skills if skill in market_skills]
                    market_skills_score = len(matched_market_skills) / len(market_skills) if market_skills else 0
                    # Add market score component based on in-demand skills
                    result["market_score"] += market_skills_score * 60  # 60% of score from skills
            
            # Cap the final score at 100
            result["market_score"] = min(round(result["market_score"]), 100)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating market competitiveness score: {str(e)}")
            return result 