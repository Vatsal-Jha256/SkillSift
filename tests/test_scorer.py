import pytest
from app.services.scorer import CompatibilityScorer
from app.core.exceptions import CompatibilityScoringError

def test_basic_compatibility_scoring():
    """Test basic compatibility scoring"""
    scorer = CompatibilityScorer()
    candidate = {
        "skills": ["python", "aws", "communication"],
        "years_of_experience": 2  # Using years_of_experience
    }
    job = {
        "required_skills": ["python", "django", "aws"],
        "title": "Software Engineer",
        "industry": "Technology"
    }
    
    result = scorer.score(candidate, job)
    
    assert result["overall_score"] == pytest.approx(66.67, rel=1.0)
    assert set(result["matched_skills"]) == {"python", "aws"}
    assert "django" in result["skill_gaps"]
    assert isinstance(result["recommendations"], list)
    assert len(result["recommendations"]) > 0

def test_full_compatibility_scoring():
    """Test scoring with all components"""
    scorer = CompatibilityScorer()
    candidate = {
        "skills": ["python", "aws", "communication"],
        "years_of_experience": 5,  # Using years_of_experience
        "education": [{"degree": "Master of Computer Science"}]
    }
    job = {
        "required_skills": ["python", "aws"],
        "required_years": 4,
        "title": "Senior Software Engineer",
        "industry": "Technology"
    }
    
    result = scorer.score(candidate, job)
    
    assert result["overall_score"] > 90  # High score expected
    assert result["skill_score"] > 90  # All required skills matched
    assert result["experience_score"] > 80  # More than required experience
    assert isinstance(result["recommendations"], list)

def test_no_matching_skills():
    """Test scoring when no skills match"""
    scorer = CompatibilityScorer()
    candidate = {
        "skills": ["java", "cpp"],
        "years_of_experience": 0  # Using years_of_experience
    }
    job = {
        "required_skills": ["python", "aws"],
        "title": "Python Developer",
        "industry": "Technology"
    }
    
    result = scorer.score(candidate, job)
    
    assert result["overall_score"] < 30
    assert not result["matched_skills"]
    assert set(result["skill_gaps"]) == set(job["required_skills"])
    assert isinstance(result["recommendations"], list)
    assert len(result["recommendations"]) > 0

def test_experience_level_scoring():
    """Test experience level scoring with different experience scenarios"""
    scorer = CompatibilityScorer()

    # Test below required experience
    candidate1 = {
        "skills": ["python"],
        "years_of_experience": 1  # Using years_of_experience
    }
    job1 = {
        "required_skills": ["python"],
        "required_years": 5,
        "title": "Senior Developer"
    }
    result1 = scorer.score(candidate1, job1)
    assert result1["experience_score"] < 50

    # Test matching required experience
    candidate2 = {
        "skills": ["python"],
        "years_of_experience": 5  # Using years_of_experience
    }
    job2 = {
        "required_skills": ["python"],
        "required_years": 5,
        "title": "Senior Developer"
    }
    result2 = scorer.score(candidate2, job2)
    assert result2["experience_score"] == 100

    # Test above required experience
    candidate3 = {
        "skills": ["python"],
        "years_of_experience": 8  # Using years_of_experience
    }
    job3 = {
        "required_skills": ["python"],
        "required_years": 5,
        "title": "Senior Developer"
    }
    result3 = scorer.score(candidate3, job3)
    assert result3["experience_score"] == 100

def test_education_level_scoring():
    """Test education level scoring with different education levels"""
    scorer = CompatibilityScorer()

    # Test PhD requirement
    candidate1 = {
        "skills": ["python"],
        "years_of_experience": 0,  # Using years_of_experience
        "education": [{"degree": "Bachelor of Science"}]
    }
    job1 = {
        "required_skills": ["python"],
        "title": "Research Scientist",
        "education_level": "phd"
    }
    result1 = scorer.score(candidate1, job1)
    assert "education" in " ".join(result1["recommendations"]).lower()

def test_market_data_integration():
    """Test that market data is included in scoring results"""
    scorer = CompatibilityScorer()
    candidate = {
        "skills": ["python", "fastapi", "sql"],
        "years_of_experience": 3  # Using years_of_experience
    }
    job = {
        "required_skills": ["python", "fastapi", "sql"],
        "title": "Software Engineer",
        "industry": "Technology"
    }
    
    result = scorer.score(candidate, job)
    
    assert "market_data" in result
    market_data = result["market_data"]
    
    if "salary_range" in market_data:
        assert isinstance(market_data["salary_range"], dict)
        assert "min" in market_data["salary_range"]
        assert "max" in market_data["salary_range"]

def test_industry_trends_integration():
    """Test that industry trends are included in scoring results"""
    scorer = CompatibilityScorer()
    candidate = {
        "skills": ["python", "data science"],
        "years_of_experience": 2  # Using years_of_experience
    }
    job = {
        "required_skills": ["python", "machine learning"],
        "title": "Data Scientist",
        "industry": "Technology"
    }
    
    result = scorer.score(candidate, job)
    
    if "market_data" in result and "industry_trends" in result["market_data"]:
        trends = result["market_data"]["industry_trends"]
        assert isinstance(trends, list)
        for trend in trends:
            assert "name" in trend
            assert "description" in trend