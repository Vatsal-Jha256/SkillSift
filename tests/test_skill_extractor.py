# tests/unit/test_skill_extractor.py
import pytest
from app.services.skill_extractor import SkillExtractor

def test_skill_extraction():
    extractor = SkillExtractor()
    sample_text = "Experienced Python developer with AWS cloud computing skills"
    skills = extractor.extract_skills(sample_text)
    
    assert 'python' in skills
    assert 'aws' in skills
    assert 'cloud computing' in skills