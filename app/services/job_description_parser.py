from typing import List
import spacy
from spacy.matcher import PhraseMatcher

class JobDescriptionParser:
    """
    Service for extracting job requirements and skills from natural language job descriptions
    """
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize NLP model for job description parsing
        
        Args:
            model_name (str): SpaCy language model to use
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise ValueError(f"SpaCy model {model_name} not found. Please install.")
        
        # Predefined skill categories to help with extraction
        self.skill_categories = {
            'technical_skills': ['programming', 'cloud', 'frameworks', 'tools'],
            'soft_skills': ['communication', 'leadership', 'teamwork']
        }
        
        # Expanded skill taxonomy from SkillExtractor
        self.skill_taxonomy = {
            'programming': ['python', 'java', 'c++', 'javascript', 'sql', 'ruby', 'swift'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud computing'],
            'frameworks': ['django', 'flask', 'react', 'angular', 'spring', 'node.js'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'ansible'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving']
        }
        
        # Create phrase matcher for skills
        self.skill_matcher = self._create_skill_matcher()

    def _create_skill_matcher(self):
        """
        Create a SpaCy phrase matcher for skills
        
        Returns:
            PhraseMatcher: Configured matcher for skill detection
        """
        matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
        
        # Flatten skills and convert to spaCy tokens
        all_skills = [skill for skills in self.skill_taxonomy.values() for skill in skills]
        patterns = [self.nlp.make_doc(skill) for skill in all_skills]
        matcher.add("SKILLS", patterns)
        
        return matcher

    def extract_job_requirements(self, job_description: str, max_skills: int = 20) -> List[str]:
        """
        Extract job requirements and skills from a natural language job description
        
        Args:
            job_description (str): Full text of the job description
            max_skills (int): Maximum number of skills to extract
        
        Returns:
            List[str]: Extracted job requirements/skills
        """
        # Preprocess job description
        doc = self.nlp(job_description.lower())
        
        # Find matches using phrase matcher
        matches = self.skill_matcher(doc)
        
        # Extract matched skills
        found_skills = [
            doc[start:end].text 
            for match_id, start, end in matches
        ]
        
        # Remove duplicates, maintain order, limit skills
        unique_skills = list(dict.fromkeys(found_skills))[:max_skills]
        
        return unique_skills