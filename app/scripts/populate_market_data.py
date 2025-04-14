#!/usr/bin/env python
"""
Script to populate the database with sample industry data for testing.
This adds industry-specific skills, trends, salary ranges, job market demand, and career paths.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to make app imports work
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine, Base
from app.core.models import IndustrySkillSet, IndustryTrend, SalaryRange, JobMarketDemand, CareerPath
from app.core.logging import logger

# Test data for industries
INDUSTRY_DATA = {
    "Technology": {
        "skills": [
            "Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes", "Machine Learning",
            "Data Science", "SQL", "NoSQL", "REST API", "GraphQL", "Git", "CI/CD", "Agile",
            "Cloud Computing", "DevOps", "Microservices", "Node.js", "TypeScript"
        ],
        "trends": [
            {
                "name": "Artificial Intelligence",
                "description": "Growing adoption of AI across all software development",
                "relevance_score": 0.95,
                "source": "Gartner 2023"
            },
            {
                "name": "Cloud-Native Development",
                "description": "Shift towards cloud-native architectures and containerization",
                "relevance_score": 0.9,
                "source": "Stack Overflow Survey 2023"
            },
            {
                "name": "Low-Code/No-Code",
                "description": "Increasing use of visual development platforms to accelerate app creation",
                "relevance_score": 0.8,
                "source": "Forrester Research"
            }
        ],
        "jobs": [
            {
                "title": "Software Engineer",
                "salaries": [
                    {
                        "experience_level": "entry",
                        "min_salary": 70000,
                        "max_salary": 100000,
                        "median_salary": 85000
                    },
                    {
                        "experience_level": "mid",
                        "min_salary": 90000,
                        "max_salary": 140000,
                        "median_salary": 115000
                    },
                    {
                        "experience_level": "senior",
                        "min_salary": 120000,
                        "max_salary": 200000,
                        "median_salary": 160000
                    }
                ],
                "demand": {
                    "demand_score": 0.85,
                    "growth_rate": 22.1,
                    "num_openings": 150000,
                    "time_period": "2023"
                },
                "career_path": {
                    "starting_role": "Junior Software Engineer",
                    "path_steps": [
                        {
                            "role": "Software Engineer",
                            "description": "Mid-level engineer responsible for implementing features",
                            "required_skills": ["JavaScript", "React", "Node.js", "SQL", "Git"],
                            "avg_years_experience": 3
                        },
                        {
                            "role": "Senior Software Engineer",
                            "description": "Leading development efforts and mentoring junior engineers",
                            "required_skills": ["System Design", "Architecture", "Team Leadership", "Code Review"],
                            "avg_years_experience": 5
                        },
                        {
                            "role": "Engineering Manager",
                            "description": "Managing teams of engineers and coordinating project delivery",
                            "required_skills": ["Project Management", "People Management", "Technical Leadership"],
                            "avg_years_experience": 8
                        }
                    ],
                    "avg_transition_time": {"Junior to Mid": 24, "Mid to Senior": 36, "Senior to Manager": 48},
                    "skill_requirements": {
                        "required": ["JavaScript", "React", "Node.js", "SQL", "Git", "System Design", "Architecture"],
                        "recommended": ["TypeScript", "AWS", "CI/CD", "Docker", "Kubernetes"]
                    }
                }
            },
            {
                "title": "Data Scientist",
                "salaries": [
                    {
                        "experience_level": "entry",
                        "min_salary": 80000,
                        "max_salary": 110000,
                        "median_salary": 95000
                    },
                    {
                        "experience_level": "mid",
                        "min_salary": 100000,
                        "max_salary": 150000,
                        "median_salary": 125000
                    },
                    {
                        "experience_level": "senior",
                        "min_salary": 130000,
                        "max_salary": 210000,
                        "median_salary": 175000
                    }
                ],
                "demand": {
                    "demand_score": 0.9,
                    "growth_rate": 36.0,
                    "num_openings": 85000,
                    "time_period": "2023"
                },
                "career_path": {
                    "starting_role": "Junior Data Scientist",
                    "path_steps": [
                        {
                            "role": "Data Scientist",
                            "description": "Analyzing data and building machine learning models",
                            "required_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
                            "avg_years_experience": 3
                        },
                        {
                            "role": "Senior Data Scientist",
                            "description": "Leading data science initiatives and mentoring junior data scientists",
                            "required_skills": ["Advanced ML", "Deep Learning", "Data Strategy", "Team Leadership"],
                            "avg_years_experience": 5
                        },
                        {
                            "role": "Data Science Manager",
                            "description": "Managing teams of data scientists and aligning data strategies with business goals",
                            "required_skills": ["Project Management", "People Management", "Business Strategy"],
                            "avg_years_experience": 8
                        }
                    ],
                    "avg_transition_time": {"Junior to Mid": 24, "Mid to Senior": 36, "Senior to Manager": 48},
                    "skill_requirements": {
                        "required": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
                        "recommended": ["Deep Learning", "Big Data", "Cloud Computing", "NLP", "Computer Vision"]
                    }
                }
            }
        ]
    },
    "Finance": {
        "skills": [
            "Financial Analysis", "Accounting", "Investment Banking", "Financial Modeling", "Valuation",
            "Risk Management", "Bloomberg Terminal", "Excel", "VBA", "SQL", "Python", "R",
            "Financial Reporting", "Budgeting", "Forecasting", "CFA", "Asset Management", 
            "Portfolio Management", "Fixed Income", "Derivatives"
        ],
        "trends": [
            {
                "name": "FinTech Integration",
                "description": "Traditional financial institutions incorporating technology to improve services",
                "relevance_score": 0.92,
                "source": "Deloitte Financial Services Trends 2023"
            },
            {
                "name": "ESG Investing",
                "description": "Growing focus on environmental, social, and governance factors in investment decisions",
                "relevance_score": 0.88,
                "source": "BlackRock Annual Report"
            },
            {
                "name": "AI in Finance",
                "description": "Implementation of AI for risk assessment, fraud detection, and algorithmic trading",
                "relevance_score": 0.85,
                "source": "Financial Times Tech Report"
            }
        ],
        "jobs": [
            {
                "title": "Financial Analyst",
                "salaries": [
                    {
                        "experience_level": "entry",
                        "min_salary": 65000,
                        "max_salary": 85000,
                        "median_salary": 75000
                    },
                    {
                        "experience_level": "mid",
                        "min_salary": 80000,
                        "max_salary": 120000,
                        "median_salary": 100000
                    },
                    {
                        "experience_level": "senior",
                        "min_salary": 110000,
                        "max_salary": 170000,
                        "median_salary": 135000
                    }
                ],
                "demand": {
                    "demand_score": 0.8,
                    "growth_rate": 6.2,
                    "num_openings": 45000,
                    "time_period": "2023"
                },
                "career_path": {
                    "starting_role": "Junior Financial Analyst",
                    "path_steps": [
                        {
                            "role": "Financial Analyst",
                            "description": "Analyzing financial data and preparing reports for management",
                            "required_skills": ["Financial Analysis", "Excel", "Financial Modeling", "Accounting"],
                            "avg_years_experience": 3
                        },
                        {
                            "role": "Senior Financial Analyst",
                            "description": "Leading financial analyses and providing strategic recommendations",
                            "required_skills": ["Advanced Financial Modeling", "Valuation", "Forecasting", "Team Leadership"],
                            "avg_years_experience": 5
                        },
                        {
                            "role": "Finance Manager",
                            "description": "Overseeing financial operations and managing a team of analysts",
                            "required_skills": ["Budgeting", "Risk Management", "People Management", "Financial Strategy"],
                            "avg_years_experience": 8
                        }
                    ],
                    "avg_transition_time": {"Junior to Mid": 24, "Mid to Senior": 36, "Senior to Manager": 48},
                    "skill_requirements": {
                        "required": ["Financial Analysis", "Excel", "Financial Modeling", "Accounting", "Valuation"],
                        "recommended": ["Python", "SQL", "VBA", "CFA", "Risk Management"]
                    }
                }
            }
        ]
    },
    "Healthcare": {
        "skills": [
            "Electronic Health Records (EHR)", "Medical Coding", "Clinical Documentation", "HIPAA Compliance",
            "Patient Care", "Healthcare Administration", "Medical Terminology", "ICD-10", "CPT Coding",
            "Healthcare Informatics", "Clinical Research", "Quality Improvement", "Regulatory Compliance",
            "Epic", "Cerner", "MEDITECH", "Case Management", "Telehealth", "Population Health Management"
        ],
        "trends": [
            {
                "name": "Telehealth Expansion",
                "description": "Increasing adoption of remote healthcare delivery models",
                "relevance_score": 0.9,
                "source": "American Medical Association"
            },
            {
                "name": "AI in Diagnostics",
                "description": "Machine learning tools to assist in medical diagnostics and treatment planning",
                "relevance_score": 0.85,
                "source": "New England Journal of Medicine"
            },
            {
                "name": "Value-Based Care",
                "description": "Shift from fee-for-service to value-based healthcare delivery models",
                "relevance_score": 0.82,
                "source": "Healthcare Financial Management Association"
            }
        ],
        "jobs": [
            {
                "title": "Healthcare Administrator",
                "salaries": [
                    {
                        "experience_level": "entry",
                        "min_salary": 60000,
                        "max_salary": 80000,
                        "median_salary": 70000
                    },
                    {
                        "experience_level": "mid",
                        "min_salary": 75000,
                        "max_salary": 110000,
                        "median_salary": 95000
                    },
                    {
                        "experience_level": "senior",
                        "min_salary": 100000,
                        "max_salary": 160000,
                        "median_salary": 130000
                    }
                ],
                "demand": {
                    "demand_score": 0.75,
                    "growth_rate": 28.3,
                    "num_openings": 38000,
                    "time_period": "2023"
                },
                "career_path": {
                    "starting_role": "Administrative Assistant",
                    "path_steps": [
                        {
                            "role": "Healthcare Administrator",
                            "description": "Managing day-to-day operations of healthcare facilities",
                            "required_skills": ["Healthcare Administration", "HIPAA Compliance", "EHR Systems", "Staff Management"],
                            "avg_years_experience": 3
                        },
                        {
                            "role": "Healthcare Manager",
                            "description": "Overseeing departments within healthcare organizations",
                            "required_skills": ["Budgeting", "Healthcare Regulations", "Quality Improvement", "Leadership"],
                            "avg_years_experience": 6
                        },
                        {
                            "role": "Healthcare Director",
                            "description": "Strategic leadership for healthcare facilities or departments",
                            "required_skills": ["Strategic Planning", "Financial Management", "Healthcare Policy", "Executive Leadership"],
                            "avg_years_experience": 10
                        }
                    ],
                    "avg_transition_time": {"Assistant to Admin": 24, "Admin to Manager": 36, "Manager to Director": 48},
                    "skill_requirements": {
                        "required": ["Healthcare Administration", "HIPAA Compliance", "EHR Systems", "Staff Management"],
                        "recommended": ["Healthcare Informatics", "Quality Improvement", "Healthcare Policy", "Telehealth"]
                    }
                }
            }
        ]
    }
}

def populate_database():
    """Populate the database with sample industry data"""
    logger.info("Starting database population with sample industry data")
    
    db = next(get_db())
    
    try:
        # First, populate industry skill sets
        for industry_name, data in INDUSTRY_DATA.items():
            logger.info(f"Adding skills for industry: {industry_name}")
            # Check if industry already exists
            existing = db.query(IndustrySkillSet).filter(IndustrySkillSet.industry_name == industry_name).first()
            if existing:
                logger.info(f"Industry {industry_name} already exists, updating")
                existing.skills = data["skills"]
                db_industry = existing
            else:
                db_industry = IndustrySkillSet(
                    industry_name=industry_name,
                    skills=data["skills"]
                )
                db.add(db_industry)
            db.commit()
            
            # Add industry trends
            logger.info(f"Adding trends for industry: {industry_name}")
            for trend in data["trends"]:
                existing_trend = db.query(IndustryTrend).filter(
                    IndustryTrend.industry_name == industry_name,
                    IndustryTrend.trend_name == trend["name"]
                ).first()
                
                if existing_trend:
                    logger.info(f"Trend {trend['name']} already exists, updating")
                    existing_trend.description = trend["description"]
                    existing_trend.relevance_score = trend["relevance_score"]
                    existing_trend.source = trend.get("source")
                    db_trend = existing_trend
                else:
                    db_trend = IndustryTrend(
                        industry_name=industry_name,
                        trend_name=trend["name"],
                        description=trend["description"],
                        relevance_score=trend["relevance_score"],
                        source=trend.get("source")
                    )
                    db.add(db_trend)
            db.commit()
            
            # Add job data (salaries, demand, career paths)
            for job in data["jobs"]:
                job_title = job["title"]
                logger.info(f"Adding data for job: {job_title} in {industry_name}")
                
                # Add salary ranges
                for salary in job["salaries"]:
                    existing_salary = db.query(SalaryRange).filter(
                        SalaryRange.job_title == job_title,
                        SalaryRange.industry_name == industry_name,
                        SalaryRange.experience_level == salary["experience_level"]
                    ).first()
                    
                    if existing_salary:
                        logger.info(f"Salary for {job_title} ({salary['experience_level']}) already exists, updating")
                        existing_salary.min_salary = salary["min_salary"]
                        existing_salary.max_salary = salary["max_salary"]
                        existing_salary.median_salary = salary["median_salary"]
                        db_salary = existing_salary
                    else:
                        db_salary = SalaryRange(
                            job_title=job_title,
                            industry_name=industry_name,
                            experience_level=salary["experience_level"],
                            min_salary=salary["min_salary"],
                            max_salary=salary["max_salary"],
                            median_salary=salary["median_salary"],
                            currency="USD"
                        )
                        db.add(db_salary)
                db.commit()
                
                # Add market demand
                demand = job["demand"]
                existing_demand = db.query(JobMarketDemand).filter(
                    JobMarketDemand.job_title == job_title,
                    JobMarketDemand.industry_name == industry_name,
                    JobMarketDemand.time_period == demand["time_period"]
                ).first()
                
                if existing_demand:
                    logger.info(f"Demand for {job_title} ({demand['time_period']}) already exists, updating")
                    existing_demand.demand_score = demand["demand_score"]
                    existing_demand.growth_rate = demand["growth_rate"]
                    existing_demand.num_openings = demand["num_openings"]
                    db_demand = existing_demand
                else:
                    db_demand = JobMarketDemand(
                        job_title=job_title,
                        industry_name=industry_name,
                        demand_score=demand["demand_score"],
                        growth_rate=demand["growth_rate"],
                        num_openings=demand["num_openings"],
                        time_period=demand["time_period"]
                    )
                    db.add(db_demand)
                db.commit()
                
                # Add career path
                career_path = job["career_path"]
                existing_path = db.query(CareerPath).filter(
                    CareerPath.starting_role == career_path["starting_role"],
                    CareerPath.industry_name == industry_name
                ).first()
                
                if existing_path:
                    logger.info(f"Career path for {career_path['starting_role']} already exists, updating")
                    existing_path.path_steps = career_path["path_steps"]
                    existing_path.avg_transition_time = career_path["avg_transition_time"]
                    existing_path.skill_requirements = career_path["skill_requirements"]
                    db_path = existing_path
                else:
                    db_path = CareerPath(
                        starting_role=career_path["starting_role"],
                        industry_name=industry_name,
                        path_steps=career_path["path_steps"],
                        avg_transition_time=career_path["avg_transition_time"],
                        skill_requirements=career_path["skill_requirements"]
                    )
                    db.add(db_path)
                db.commit()
        
        logger.info("Database population completed successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during database population: {str(e)}")
        raise

if __name__ == "__main__":
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Populate with sample data
    populate_database()
    
    logger.info("Script completed") 