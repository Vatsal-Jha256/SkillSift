from typing import List, Dict, Any
from app.core.logging import logger

class RecommendationEngine:
    """Engine for generating personalized recommendations"""
    
    def __init__(self):
        """Initialize recommendation engine"""
        self.categories = {
            "skill_development": [],
            "content_optimization": [],
            "keyword_enhancement": [],
            "formatting_suggestions": []
        }
        
    def generate_recommendations(
        self,
        skills: List[str],
        skill_gaps: List[str],
        resume_text: str,
        job_description: str
    ) -> Dict[str, List[str]]:
        """
        Generate recommendations based on analysis results
        
        Args:
            skills (List[str]): Candidate's current skills
            skill_gaps (List[str]): Missing skills for the job
            resume_text (str): Raw resume text
            job_description (str): Raw job description text
            
        Returns:
            Dict[str, List[str]]: Recommendations by category
        """
        recommendations = self.categories.copy()
        try:
            # Skill development recommendations
            if skill_gaps:
                recommendations["skill_development"].extend([
                    f"Consider developing proficiency in {gap}" for gap in skill_gaps[:3]
                ])
            
            # Content optimization recommendations
            recommendations["content_optimization"].extend([
                "Quantify achievements with metrics where possible",
                "Use action verbs to describe experiences",
                "Ensure experiences demonstrate impact and results"
            ])
            
            # Keyword recommendations from job description
            keywords = self._extract_job_keywords(job_description)
            if keywords:
                recommendations["keyword_enhancement"].extend([
                    f"Consider incorporating relevant keywords like: {', '.join(keywords[:3])}",
                    "Align skills section with job requirements"
                ])
            
            # Formatting recommendations
            recommendations["formatting_suggestions"].extend([
                "Use consistent formatting throughout",
                "Ensure sections are clearly separated",
                "Keep resume length appropriate for experience level"
            ])
            
            # Filter out empty categories
            recommendations = {k: v for k, v in recommendations.items() if v}
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {"error": [f"Failed to generate recommendations: {str(e)}"]}
    
    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract key terms from job description"""
        # Simple keyword extraction - could be enhanced with NLP
        if not job_description:
            return []
            
        common_keywords = [
            "manage", "lead", "develop", "design", "implement",
            "analyze", "create", "build", "maintain", "improve"
        ]
        
        return [word for word in common_keywords if word.lower() in job_description.lower()]
