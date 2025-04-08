# app/services/skill_extractor.py
import spacy
from typing import List

class SkillExtractor:
    """Service for extracting professional skills from resume text"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize NLP model for skill extraction
        
        Args:
            model_name (str): spaCy language model to use
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise ValueError(f"SpaCy model {model_name} not found. Please install.")
        
        # Initial skill taxonomy (can be expanded)
        self.skill_taxonomy = {
            'programming': ['python', 'java', 'c++', 'javascript', 'sql', 'ruby', 'swift'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud computing'],
            'frameworks': ['django', 'flask', 'react', 'angular', 'spring', 'node.js'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'ansible'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving']
        }
    
    def extract_skills(self, resume_text: str, max_skills: int = 20) -> List[str]:
        """
        Extract skills from resume text
        
        Args:
            resume_text (str): Parsed resume text
            max_skills (int): Maximum number of skills to extract
        
        Returns:
            List[str]: Extracted skills
        """
        # Normalize text
        resume_text = resume_text.lower()
        
        # Flatten skill taxonomy
        all_skills = [skill for skills in self.skill_taxonomy.values() for skill in skills]
        
        # Match skills in resume text
        found_skills = [
            skill for skill in all_skills 
            if skill in resume_text
        ]
        
        # Remove duplicates and limit
        return list(dict.fromkeys(found_skills))[:max_skills]