# app/services/scorer.py
from typing import List, Dict

class CompatibilityScorer:
    """Service for calculating candidate-job compatibility"""
    
    @staticmethod
    def calculate_score(
        candidate_skills: List[str], 
        job_requirements: List[str]
    ) -> Dict[str, float]:
        """
        Calculate job compatibility score
        
        Args:
            candidate_skills (List[str]): Skills from candidate's resume
            job_requirements (List[str]): Required skills for the job
        
        Returns:
            Dict containing score and matched skills
        """
        # Normalize input
        candidate_skills = [skill.lower() for skill in candidate_skills]
        job_requirements = [skill.lower() for skill in job_requirements]
        
        # Calculate matched skills
        matched_skills = [
            skill for skill in candidate_skills 
            if skill in job_requirements
        ]
        
        # Simple scoring algorithm
        match_percentage = (len(matched_skills) / len(job_requirements)) * 100 \
            if job_requirements else 0
        
        return {
            'score': round(match_percentage, 2),
            'matched_skills': matched_skills,
            'recommendations': [
                skill for skill in job_requirements 
                if skill not in candidate_skills
            ]
        }