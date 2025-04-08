import pytest
from app.services.scorer import CompatibilityScorer

def test_compatibility_scoring():
    scorer = CompatibilityScorer()
    candidate_skills = ['python', 'aws', 'communication']
    job_requirements = ['python', 'django', 'aws']
    
    result = scorer.calculate_score(candidate_skills, job_requirements)
    
    assert result['score'] == 66.67
    assert set(result['matched_skills']) == {'python', 'aws'}
    assert 'django' in result['recommendations']