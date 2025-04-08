# app/services/scorer.py
from typing import List, Dict, Any, Optional
from app.core.logging import logger
from app.core.exceptions import CompatibilityScoringError

class CompatibilityScorer:
    """Service for calculating candidate-job compatibility"""
    
    # Skill importance weights
    SKILL_WEIGHTS = {
        "required": 1.0,
        "preferred": 0.7,
        "optional": 0.3
    }
    
    # Experience level weights
    EXPERIENCE_WEIGHTS = {
        "senior": 1.0,
        "mid": 0.7,
        "junior": 0.4,
        "entry": 0.2
    }
    
    # Education level weights
    EDUCATION_WEIGHTS = {
        "phd": 1.0,
        "master": 0.8,
        "bachelor": 0.6,
        "associate": 0.4,
        "high_school": 0.2
    }
    
    def __init__(self):
        """Initialize the compatibility scorer"""
        # Default weights for different components
        self.weights = {
            "skills": 0.6,
            "experience": 0.25,
            "education": 0.15
        }
    
    def calculate_score(
        self,
        candidate_skills: List[str], 
        job_requirements: List[str],
        candidate_experience: Optional[List[Dict[str, Any]]] = None,
        job_experience_years: Optional[int] = None,
        candidate_education: Optional[List[Dict[str, Any]]] = None,
        job_education_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate job compatibility score with weighted components
        
        Args:
            candidate_skills (List[str]): Skills from candidate's resume
            job_requirements (List[str]): Required skills for the job
            candidate_experience (Optional[List[Dict[str, Any]]]): Candidate's work experience
            job_experience_years (Optional[int]): Required years of experience
            candidate_education (Optional[List[Dict[str, Any]]]): Candidate's education
            job_education_level (Optional[str]): Required education level
        
        Returns:
            Dict containing score and matched skills
        """
        try:
            # Normalize input
            candidate_skills = [skill.lower() for skill in candidate_skills]
            job_requirements = [skill.lower() for skill in job_requirements]
            
            # Calculate skill match score
            skill_score, matched_skills, skill_gaps = self._calculate_skill_score(
                candidate_skills, job_requirements
            )
            
            # Calculate experience match score
            experience_score = 0.0
            if candidate_experience and job_experience_years:
                experience_score = self._calculate_experience_score(
                    candidate_experience, job_experience_years
                )
            
            # Calculate education match score
            education_score = 0.0
            if candidate_education and job_education_level:
                education_score = self._calculate_education_score(
                    candidate_education, job_education_level
                )
            
            # Calculate weighted total score
            total_score = (
                skill_score * self.weights["skills"] +
                experience_score * self.weights["experience"] +
                education_score * self.weights["education"]
            ) * 100
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                skill_gaps, experience_score, education_score
            )
            
            return {
                'score': round(total_score, 2),
                'matched_skills': matched_skills,
                'skill_gaps': skill_gaps,
                'skill_score': round(skill_score * 100, 2),
                'experience_score': round(experience_score * 100, 2),
                'education_score': round(education_score * 100, 2),
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Error calculating compatibility score: {str(e)}")
            raise CompatibilityScoringError(str(e))
    
    def _calculate_skill_score(
        self, candidate_skills: List[str], job_requirements: List[str]
    ) -> tuple:
        """
        Calculate skill match score
        
        Args:
            candidate_skills (List[str]): Skills from candidate's resume
            job_requirements (List[str]): Required skills for the job
        
        Returns:
            tuple: (score, matched_skills, skill_gaps)
        """
        # Calculate matched skills
        matched_skills = [
            skill for skill in candidate_skills 
            if skill in job_requirements
        ]
        
        # Calculate skill gaps
        skill_gaps = [
            skill for skill in job_requirements 
            if skill not in candidate_skills
        ]
        
        # Calculate score
        match_percentage = len(matched_skills) / len(job_requirements) if job_requirements else 0
        
        return match_percentage, matched_skills, skill_gaps
    
    def _calculate_experience_score(
        self, candidate_experience: List[Dict[str, Any]], required_years: int
    ) -> float:
        """
        Calculate experience match score
        
        Args:
            candidate_experience (List[Dict[str, Any]]): Candidate's work experience
            required_years (int): Required years of experience
        
        Returns:
            float: Experience match score
        """
        # Simple implementation - can be enhanced with more sophisticated logic
        # Assume each experience entry represents 1 year for simplicity
        candidate_years = len(candidate_experience)
        
        if candidate_years >= required_years:
            return 1.0
        elif candidate_years >= required_years * 0.7:
            return 0.7
        elif candidate_years >= required_years * 0.4:
            return 0.4
        else:
            return 0.2
    
    def _calculate_education_score(
        self, candidate_education: List[Dict[str, Any]], required_level: str
    ) -> float:
        """
        Calculate education match score
        
        Args:
            candidate_education (List[Dict[str, Any]]): Candidate's education
            required_level (str): Required education level
        
        Returns:
            float: Education match score
        """
        # Map education levels to weights
        education_levels = {
            "phd": 1.0,
            "master": 0.8,
            "bachelor": 0.6,
            "associate": 0.4,
            "high_school": 0.2
        }
        
        # Get the highest education level from candidate
        highest_level = "high_school"
        for education in candidate_education:
            degree = education.get("degree", "").lower()
            if "phd" in degree or "doctorate" in degree:
                highest_level = "phd"
                break
            elif "master" in degree:
                highest_level = "master"
                break
            elif "bachelor" in degree:
                highest_level = "bachelor"
                break
            elif "associate" in degree:
                highest_level = "associate"
                break
        
        # Get weights
        candidate_weight = education_levels.get(highest_level, 0.2)
        required_weight = education_levels.get(required_level.lower(), 0.6)
        
        # Calculate score
        if candidate_weight >= required_weight:
            return 1.0
        else:
            return candidate_weight / required_weight
    
    def _generate_recommendations(
        self, skill_gaps: List[str], experience_score: float, education_score: float
    ) -> List[str]:
        """
        Generate recommendations based on gaps
        
        Args:
            skill_gaps (List[str]): Skills that the candidate lacks
            experience_score (float): Experience match score
            education_score (float): Education match score
        
        Returns:
            List[str]: Recommendations
        """
        recommendations = []
        
        # Skill recommendations
        if skill_gaps:
            recommendations.append(f"Consider developing skills in: {', '.join(skill_gaps[:3])}")
        
        # Experience recommendations
        if experience_score < 0.7:
            if experience_score < 0.4:
                recommendations.append("Gain more relevant work experience in the field")
            else:
                recommendations.append("Consider highlighting more relevant experience in your resume")
        
        # Education recommendations
        if education_score < 0.7:
            if education_score < 0.4:
                recommendations.append("Consider pursuing additional education or certifications")
            else:
                recommendations.append("Highlight relevant coursework or projects in your resume")
        
        return recommendations