import pytest
from app.services.skill_extractor import SkillExtractor

@pytest.fixture
def skill_extractor():
    return SkillExtractor()

def test_basic_skill_extraction():
    """Test basic skill extraction"""
    extractor = SkillExtractor()
    text = "Proficient in Python and JavaScript, with experience in React"
    skills = extractor.extract_skills(text)
    assert "python" in skills
    assert "javascript" in skills
    assert "react" in skills

def test_skill_proficiency_detection():
    """Test proficiency level detection"""
    extractor = SkillExtractor()
    text = "Expert in Python, familiar with JavaScript, and learning React"
    result = extractor.extract_skills_with_context(text)
    skills = {s["skill"]: s["proficiency"] for s in result["skills"]}
    assert skills["python"] == "expert"
    assert skills["javascript"] == "intermediate"
    assert skills["react"] == "beginner"

def test_skill_categorization():
    """Test skill categorization"""
    extractor = SkillExtractor()
    text = "Experience with Python, React, and AWS"
    result = extractor.extract_skills_with_context(text)
    assert "programming" in result["categorized_skills"]
    assert "web_development" in result["categorized_skills"]
    assert "cloud" in result["categorized_skills"]

def test_skill_normalization():
    """Test skill name normalization"""
    extractor = SkillExtractor()
    text = "Experience with ReactJS, NodeJS, and Amazon AWS"
    skills = extractor.extract_skills(text)
    assert "react" in skills
    assert "node.js" in skills
    assert "aws" in skills

def test_max_skills_limit():
    """Test maximum skills limit"""
    extractor = SkillExtractor()
    text = "Python Java C++ JavaScript TypeScript SQL Ruby Swift Kotlin Go Rust PHP Scala R Matlab Perl Haskell React Angular Vue"
    skills = extractor.extract_skills(text, max_skills=5)
    assert len(skills) <= 5
