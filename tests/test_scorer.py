import pytest
from app.services.scorer import CompatibilityScorer
from app.core.exceptions import CompatibilityScoringError

def test_basic_compatibility_scoring():
    """Test basic compatibility scoring"""
    scorer = CompatibilityScorer()
    candidate_skills = ['python', 'aws', 'communication']
    job_requirements = ['python', 'django', 'aws']
    
    result = scorer.calculate_score(candidate_skills, job_requirements)
    
    assert result['score'] == pytest.approx(66.67, rel=0.01)
    assert set(result['matched_skills']) == {'python', 'aws'}
    assert 'django' in result['skill_gaps']
    assert result['recommendations']

def test_full_compatibility_scoring():
    """Test scoring with all components"""
    scorer = CompatibilityScorer()
    candidate_skills = ['python', 'aws', 'communication']
    job_requirements = ['python', 'aws']
    candidate_experience = [
        {'title': 'Senior Developer', 'duration': '3 years'},
        {'title': 'Developer', 'duration': '2 years'}
    ]
    candidate_education = [
        {'degree': 'Master of Computer Science'}
    ]
    
    result = scorer.calculate_score(
        candidate_skills=candidate_skills,
        job_requirements=job_requirements,
        candidate_experience=candidate_experience,
        job_experience_years=4,
        candidate_education=candidate_education,
        job_education_level='master'
    )
    
    assert result['score'] > 90  # High score expected
    assert result['skill_score'] == 100  # All required skills matched
    assert result['experience_score'] > 80  # More than required experience
    assert result['education_score'] == 100  # Education matches requirement

def test_no_matching_skills():
    """Test scoring when no skills match"""
    scorer = CompatibilityScorer()
    candidate_skills = ['java', 'cpp']
    job_requirements = ['python', 'aws']
    
    result = scorer.calculate_score(candidate_skills, job_requirements)
    
    assert result['score'] == 0
    assert not result['matched_skills']
    assert set(result['skill_gaps']) == set(job_requirements)
    assert len(result['recommendations']) > 0

def test_experience_level_scoring():
    """Test experience level scoring"""
    scorer = CompatibilityScorer()
    candidate_experience = [
        {'title': 'Junior Developer', 'duration': '1 year'}
    ]
    
    result = scorer.calculate_score(
        candidate_skills=['python'],
        job_requirements=['python'],
        candidate_experience=candidate_experience,
        job_experience_years=5
    )
    
    assert result['experience_score'] < 50  # Low score due to insufficient experience

def test_education_level_scoring():
    """Test education level scoring"""
    scorer = CompatibilityScorer()
    candidate_education = [
        {'degree': 'Bachelor of Science'}
    ]
    
    result = scorer.calculate_score(
        candidate_skills=['python'],
        job_requirements=['python'],
        candidate_education=candidate_education,
        job_education_level='phd'
    )
    
    assert result['education_score'] < 70  # Lower score due to education mismatch

def test_invalid_input():
    """Test handling of invalid input"""
    scorer = CompatibilityScorer()
    with pytest.raises(CompatibilityScoringError):
        scorer.calculate_score(None, ['python'])