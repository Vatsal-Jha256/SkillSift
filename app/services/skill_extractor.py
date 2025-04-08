# app/services/skill_extractor.py
import spacy
from typing import List, Dict, Any, Tuple
from app.core.logging import logger
from app.core.exceptions import SkillExtractionError

class SkillExtractor:
    """Service for extracting professional skills from resume text"""
    
    # Proficiency level indicators
    PROFICIENCY_LEVELS = {
        "expert": ["expert", "master", "advanced", "proficient", "skilled", "experienced"],
        "intermediate": ["intermediate", "moderate", "familiar", "knowledgeable"],
        "beginner": ["beginner", "basic", "novice", "learning", "familiarity"]
    }
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize NLP model for skill extraction
        
        Args:
            model_name (str): spaCy language model to use
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.error(f"SpaCy model {model_name} not found")
            raise SkillExtractionError(f"SpaCy model {model_name} not found. Please install.")
        
        # Expanded skill taxonomy with categories
        self.skill_taxonomy = {
            'programming': [
                'python', 'java', 'c++', 'javascript', 'typescript', 'sql', 'ruby', 'swift', 
                'kotlin', 'go', 'rust', 'php', 'scala', 'r', 'matlab', 'perl', 'haskell'
            ],
            'web_development': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 
                'spring', 'express', 'laravel', 'bootstrap', 'jquery', 'sass', 'webpack'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'cloud computing', 'serverless', 'lambda', 
                'ec2', 's3', 'dynamodb', 'cloudfront', 'cloudformation', 'terraform'
            ],
            'databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 
                'oracle', 'sql server', 'dynamodb', 'cassandra', 'neo4j'
            ],
            'devops': [
                'git', 'docker', 'kubernetes', 'jenkins', 'ansible', 'terraform', 
                'ci/cd', 'github actions', 'gitlab ci', 'puppet', 'chef', 'prometheus'
            ],
            'mobile_development': [
                'ios', 'android', 'react native', 'flutter', 'swift', 'kotlin', 
                'objective-c', 'xamarin', 'mobile app development'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'data analysis', 'data visualization', 
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'r'
            ],
            'soft_skills': [
                'communication', 'leadership', 'teamwork', 'problem solving', 'time management',
                'project management', 'collaboration', 'adaptability', 'creativity', 'critical thinking'
            ],
            'project_management': [
                'agile', 'scrum', 'kanban', 'waterfall', 'jira', 'trello', 'asana', 
                'project planning', 'risk management', 'stakeholder management'
            ],
            'security': [
                'cybersecurity', 'information security', 'network security', 'penetration testing',
                'security protocols', 'encryption', 'authentication', 'authorization', 'oauth'
            ]
        }
        
        # Create phrase matcher for skills
        self.skill_matcher = self._create_skill_matcher()
    
    def _create_skill_matcher(self):
        """
        Create a SpaCy phrase matcher for skills
        
        Returns:
            PhraseMatcher: Configured matcher for skill detection
        """
        from spacy.matcher import PhraseMatcher
        
        matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
        
        # Flatten skills and convert to spaCy tokens
        all_skills = [skill for skills in self.skill_taxonomy.values() for skill in skills]
        patterns = [self.nlp.make_doc(skill) for skill in all_skills]
        matcher.add("SKILLS", patterns)
        
        return matcher
    
    def extract_skills(self, resume_text: str, max_skills: int = 20) -> List[str]:
        """
        Extract skills from resume text
        
        Args:
            resume_text (str): Parsed resume text
            max_skills (int): Maximum number of skills to extract
        
        Returns:
            List[str]: Extracted skills
        """
        try:
            # Normalize text
            resume_text = resume_text.lower()
            
            # Process text with spaCy
            doc = self.nlp(resume_text)
            
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
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            raise SkillExtractionError(str(e))
    
    def extract_skills_with_context(self, resume_text: str, max_skills: int = 20) -> Dict[str, Any]:
        """
        Extract skills with context and proficiency levels
        
        Args:
            resume_text (str): Parsed resume text
            max_skills (int): Maximum number of skills to extract
        
        Returns:
            Dict[str, Any]: Extracted skills with context and proficiency
        """
        try:
            # Normalize text
            resume_text = resume_text.lower()
            
            # Process text with spaCy
            doc = self.nlp(resume_text)
            
            # Find matches using phrase matcher
            matches = self.skill_matcher(doc)
            
            # Extract matched skills with context
            skills_with_context = []
            
            for match_id, start, end in matches:
                skill = doc[start:end].text
                
                # Get context (sentence containing the skill)
                sent = None
                for sentence in doc.sents:
                    if start >= sentence.start and end <= sentence.end:
                        sent = sentence.text
                        break
                
                # Determine proficiency level
                proficiency = self._determine_proficiency_level(sent or "")
                
                # Categorize skill
                category = self._categorize_skill(skill)
                
                skills_with_context.append({
                    "skill": skill,
                    "context": sent,
                    "proficiency": proficiency,
                    "category": category
                })
            
            # Remove duplicates based on skill name
            unique_skills = []
            seen_skills = set()
            
            for skill_data in skills_with_context:
                if skill_data["skill"] not in seen_skills and len(unique_skills) < max_skills:
                    unique_skills.append(skill_data)
                    seen_skills.add(skill_data["skill"])
            
            # Group skills by category
            categorized_skills = {}
            for skill_data in unique_skills:
                category = skill_data["category"]
                if category not in categorized_skills:
                    categorized_skills[category] = []
                categorized_skills[category].append(skill_data)
            
            return {
                "skills": unique_skills,
                "categorized_skills": categorized_skills
            }
        except Exception as e:
            logger.error(f"Error extracting skills with context: {str(e)}")
            raise SkillExtractionError(str(e))
    
    def _determine_proficiency_level(self, context: str) -> str:
        """
        Determine proficiency level from context
        
        Args:
            context (str): Context containing the skill
        
        Returns:
            str: Proficiency level (expert, intermediate, beginner)
        """
        context = context.lower()
        
        # Check for proficiency indicators
        for level, indicators in self.PROFICIENCY_LEVELS.items():
            for indicator in indicators:
                if indicator in context:
                    return level
        
        # Default to intermediate if no clear indicator
        return "intermediate"
    
    def _categorize_skill(self, skill: str) -> str:
        """
        Categorize a skill based on the taxonomy
        
        Args:
            skill (str): Skill to categorize
        
        Returns:
            str: Category name
        """
        skill = skill.lower()
        
        for category, skills in self.skill_taxonomy.items():
            if skill in skills:
                return category
        
        # Default category if not found
        return "other"