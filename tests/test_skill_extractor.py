# tests/unit/test_skill_extractor.py
import pytest
from app.services.skill_extractor import SkillExtractor
from app.core.exceptions import SkillExtractionError

def test_basic_skill_extraction():
    """Test basic skill extraction functionality"""
    extractor = SkillExtractor()
    sample_text = "Experienced Python developer with AWS cloud computing skills"
    skills = extractor.extract_skills(sample_text)
    
    assert 'python' in skills
    assert 'aws' in skills
    assert 'cloud computing' in skills

def test_skill_extraction_with_context():
    """Test skill extraction with context and proficiency"""
    extractor = SkillExtractor()
    sample_text = """Expert Python developer with 5 years of experience.
    Intermediate knowledge of AWS cloud services.
    Strong communication and leadership skills."""
    
    result = extractor.extract_skills_with_context(sample_text)
    
    assert 'skills' in result
    assert 'categorized_skills' in result
    
    skills = result['skills']
    assert any(s['skill'] == 'python' and s['proficiency'] == 'expert' for s in skills)
    assert any(s['skill'] == 'aws' and s['proficiency'] == 'intermediate' for s in skills)
    assert any(s['skill'] == 'communication' for s in skills)
    
    categories = result['categorized_skills']
    assert 'programming' in categories
    assert 'cloud' in categories
    assert 'soft_skills' in categories

def test_empty_text():
    """Test handling of empty text"""
    extractor = SkillExtractor()
    skills = extractor.extract_skills("")
    assert isinstance(skills, list)
    assert len(skills) == 0

def test_text_without_skills():
    """Test handling of text without any recognizable skills"""
    extractor = SkillExtractor()
    sample_text = "This text contains no technical or professional skills."
    skills = extractor.extract_skills(sample_text)
    assert isinstance(skills, list)
    assert len(skills) == 0

def test_skill_normalization():
    """Test skill name normalization"""
    extractor = SkillExtractor()
    sample_text = """Experience with:
    - PYTHON programming
    - Amazon AWS cloud
    - ReactJS frontend
    """
    skills = extractor.extract_skills(sample_text)
    
    assert 'python' in skills  # lowercase
    assert 'aws' in skills    # acronym
    assert 'react' in skills  # normalized name

def test_invalid_input():
    """Test handling of invalid input"""
    extractor = SkillExtractor()
    with pytest.raises(SkillExtractionError):
        extractor.extract_skills(None)