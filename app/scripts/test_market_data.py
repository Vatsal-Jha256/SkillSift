#!/usr/bin/env python
"""
Script to test the market data service with a sample candidate and job.
This will help verify that the industry-specific analysis is working correctly.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to make app imports work
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.market_data_service import MarketDataService
from app.core.logging import logger
import json

def test_market_data_service():
    """Test the market data service with sample data"""
    logger.info("Testing market data service")
    
    db = next(get_db())
    market_data_service = MarketDataService()
    
    # Test get_salary_range
    salary_data = market_data_service.get_salary_range(
        db, 
        job_title="Software Engineer", 
        industry_name="Technology",
        experience_level="mid"
    )
    
    if salary_data:
        logger.info(f"Salary range for Software Engineer (mid-level): ${salary_data.min_salary}-${salary_data.max_salary}")
    else:
        logger.warning("No salary data found")
    
    # Test get_job_market_demand
    demand_data = market_data_service.get_job_market_demand(
        db,
        job_title="Software Engineer",
        industry_name="Technology"
    )
    
    if demand_data:
        logger.info(f"Job market demand for Software Engineer: {demand_data.demand_score*100}%, Growth rate: {demand_data.growth_rate}%")
    else:
        logger.warning("No demand data found")
    
    # Test get_industry_trends
    trends = market_data_service.get_industry_trends(
        db,
        industry_name="Technology",
        limit=3
    )
    
    if trends:
        logger.info(f"Top 3 trends in Technology: {', '.join([trend.trend_name for trend in trends])}")
    else:
        logger.warning("No trends found")
    
    # Test get_career_path
    career_path = market_data_service.get_career_path(
        db,
        current_role="Junior Software Engineer",
        industry_name="Technology"
    )
    
    if career_path and career_path.path_steps:
        logger.info(f"Career path for Junior Software Engineer: {' -> '.join([step['role'] for step in career_path.path_steps])}")
    else:
        logger.warning("No career path found")
        
    # Test calculate_market_competitive_score
    logger.info("Testing market competitiveness calculation")
    
    # Sample candidate and job data
    candidate_data = {
        "skills": ["JavaScript", "React", "Node.js", "Git", "HTML", "CSS"],
        "years_of_experience": 2
    }
    
    job_data = {
        "title": "Software Engineer",
        "industry": "Technology"
    }
    
    # Calculate market competitiveness
    market_result = market_data_service.calculate_market_competitive_score(
        candidate_data=candidate_data,
        job_data=job_data,
        db=db
    )
    
    if market_result:
        logger.info(f"Market competitiveness score: {market_result['market_score']}")
        
        if market_result.get("salary_range"):
            salary = market_result["salary_range"]
            logger.info(f"Salary range: ${salary.get('min')}-${salary.get('max')} (median: ${salary.get('median')})")
        
        if market_result.get("demand_info"):
            demand = market_result["demand_info"]
            logger.info(f"Job market demand: {demand.get('demand_score')*100 if demand.get('demand_score') is not None else 'N/A'}%")
            logger.info(f"Growth rate: {demand.get('growth_rate')}%")
        
        if market_result.get("next_career_steps"):
            steps = market_result["next_career_steps"]
            if steps:
                logger.info(f"Career path: {' -> '.join([step.get('role', '') for step in steps])}")
        
        if market_result.get("market_insights"):
            insights = market_result["market_insights"]
            if insights:
                logger.info(f"Market insights: {', '.join([insight.get('trend', '') for insight in insights])}")
    else:
        logger.warning("No market competitiveness data calculated")
    
    logger.info("Market data service tests completed")

if __name__ == "__main__":
    # Run tests
    test_market_data_service()
    logger.info("Script completed") 