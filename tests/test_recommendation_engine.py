import pytest
from app.services.recommendation_engine import RecommendationEngine

def test_skill_recommendations():
    """Test skill improvement recommendations"""
    engine = RecommendationEngine()
    candidate_skills = ["python", "javascript"]
    job_requirements = ["python", "react", "node.js"]
    recs = engine.generate_recommendations(
        skills=candidate_skills,
        skill_gaps=["react", "node.js"],
        resume_text="Python and JavaScript developer",
        job_description="Looking for Python, React and Node.js developer"
    )
    assert "skill_development" in recs
    assert any("react" in rec.lower() for rec in recs["skill_development"])
    assert any("node.js" in rec.lower() for rec in recs["skill_development"])

def test_career_path_recommendations():
    """Test career path recommendations"""
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(
        skills=["python", "javascript"],
        skill_gaps=["react"],
        resume_text="3 years experience as Software Developer",
        job_description="Senior Software Developer position"
    )
    assert "content_optimization" in recommendations
    assert len(recommendations["content_optimization"]) > 0

def test_training_recommendations():
    """Test training course recommendations"""
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(
        skills=["python"],
        skill_gaps=["react", "node.js"],
        resume_text="Python developer",
        job_description="Full stack developer position"
    )
    assert "skill_development" in recommendations
    assert any("react" in rec.lower() for rec in recommendations["skill_development"])
    assert any("node.js" in rec.lower() for rec in recommendations["skill_development"])

def test_resume_improvement_suggestions():
    """Test resume improvement suggestions"""
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(
        skills=["python"],
        skill_gaps=[],
        resume_text="Developed software applications",
        job_description="Senior developer position"
    )
    assert "content_optimization" in recommendations
    assert any("quantify" in rec.lower() for rec in recommendations["content_optimization"])

def test_interview_prep_recommendations():
    """Test interview preparation recommendations"""
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(
        skills=["python", "leadership"],
        skill_gaps=["system design"],
        resume_text="Senior Software Engineer experience",
        job_description="Senior Software Engineer position requiring system design skills"
    )
    assert "skill_development" in recommendations
    assert any("system design" in rec.lower() for rec in recommendations["skill_development"])

def test_recommendation_engine_initialization():
    """Test recommendation engine initializes correctly"""
    engine = RecommendationEngine()
    assert isinstance(engine, RecommendationEngine)
    assert hasattr(engine, 'categories')
    assert all(cat in engine.categories for cat in [
        "skill_development",
        "content_optimization",
        "keyword_enhancement",
        "formatting_suggestions"
    ])

def test_generate_recommendations():
    """Test recommendation generation with sample data"""
    engine = RecommendationEngine()
    skills = ["python", "sql"]
    skill_gaps = ["docker", "kubernetes"]
    resume_text = "Software engineer with Python experience"
    job_description = "Looking for a developer to manage and develop applications"
    
    recommendations = engine.generate_recommendations(
        skills=skills,
        skill_gaps=skill_gaps,
        resume_text=resume_text,
        job_description=job_description
    )
    
    assert isinstance(recommendations, dict)
    assert "skill_development" in recommendations
    assert any("docker" in rec.lower() for rec in recommendations["skill_development"])
    assert "content_optimization" in recommendations
    assert "formatting_suggestions" in recommendations
    
def test_empty_inputs():
    """Test recommendation generation with empty inputs"""
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(
        skills=[],
        skill_gaps=[],
        resume_text="",
        job_description=""
    )
    
    assert isinstance(recommendations, dict)
    assert len(recommendations) > 0
    assert "content_optimization" in recommendations
    assert "formatting_suggestions" in recommendations

def test_extract_job_keywords():
    """Test keyword extraction from job description"""
    engine = RecommendationEngine()
    job_description = "Looking for a developer to manage and develop applications"
    
    keywords = engine._extract_job_keywords(job_description)
    assert isinstance(keywords, list)
    assert len(keywords) > 0
    assert "manage" in keywords
    assert "develop" in keywords
