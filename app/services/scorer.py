# app/services/scorer.py
from typing import List, Dict, Any, Optional
from collections import Counter # Import Counter
from app.core.logging import logger
from app.core.exceptions import CompatibilityScoringError
import re
import spacy # Import spacy
from nltk.corpus import stopwords # Import stopwords
from app.services.slm_service import SLMService # ADDED Import
from app.services.industry_service import IndustryService # ADDED Import
from app.services.market_data_service import MarketDataService # ADDED Import for market data
from sqlalchemy.orm import Session # ADDED Import
from app.core.database import get_db  # Changed from app.db.session to app.core.database
from app.services.skill_extractor import SkillExtractor # ADDED Import for skill extraction
# Ensure stopwords are downloaded (optional, can be done once outside the app)
try:
    STOP_WORDS = set(stopwords.words('english'))
except LookupError:
    logger.warning("NLTK stopwords not found. Downloading...")
    import nltk
    nltk.download('stopwords')
    STOP_WORDS = set(stopwords.words('english'))

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
            "skill": 0.6,
            "experience": 0.25,
            "education": 0.15
        }
        # Load spacy model for keyword extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("SpaCy model 'en_core_web_sm' not found for Scorer. Keyword recommendations will be limited.")
            self.nlp = None
        # Initialize SLM Service
        self.slm_service = SLMService()
        # Initialize Industry Service (needed here to fetch skills)
        self.industry_service = IndustryService()
        # Initialize Market Data Service
        self.market_data_service = MarketDataService()
        self.skill_extractor= SkillExtractor()
    
    def calculate_score(
        self,
        candidate_skills: List[str] = None,
        job_requirements: List[str] = None,
        candidate_experience: Any = None,
        candidate_education: Any = None,
        resume_text: str = None,
        job_description: str = None,
        industry: str = None
    ) -> Dict:
        """
        Calculate compatibility score between candidate and job
        
        Args:
            candidate_skills (List[str], optional): Pre-extracted skills
            job_requirements (List[str], optional): Required skills
            candidate_experience (Any, optional): Experience info
            candidate_education (Any, optional): Education info 
            resume_text (str, optional): Raw resume text
            job_description (str, optional): Raw job description
            industry (str, optional): Industry name
            
        Returns:
            Dict: Score and recommendations
        """
        try:
            # Extract skills if not provided
            if not candidate_skills and resume_text:
                candidate_skills = self.skill_extractor.extract_skills(resume_text)
            
            if not job_requirements and job_description:
                job_requirements = self.skill_extractor.extract_skills(job_description)

            # Get industry skills
            industry_skills = self._get_industry_skills(industry) if industry else []

            # Calculate scores
            skill_score, matched_skills, skill_gaps, industry_recommendations = self._calculate_skill_score(
                candidate_skills=candidate_skills or [],
                job_requirements=job_requirements or [],
                industry_skills=industry_skills
            )

            # Calculate experience score
            exp_score = self._calculate_experience_score(
                candidate_experience=candidate_experience or [],
                required_years=3  # Default, should be extracted from job description
            )

            # Calculate overall score with weights
            overall_score = (skill_score * 0.7) + (exp_score * 0.3)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                candidate={"skills": candidate_skills, "experience": candidate_experience},
                job={"requirements": job_requirements, "industry": industry},
                matched_skills=matched_skills,
                skill_gaps=skill_gaps,
                industry_recommendations=industry_recommendations
            )

            return {
                "overall_score": round(overall_score * 100),
                "skill_score": round(skill_score * 100),
                "experience_score": round(exp_score * 100),
                "matched_skills": matched_skills,
                "skill_gaps": skill_gaps,
                "recommendations": recommendations,
                "industry_recommendations": industry_recommendations
            }

        except Exception as e:
            logger.error(f"Error calculating score: {str(e)}")
            raise CompatibilityScoringError(str(e))
    
    def _calculate_skill_score(
        self, candidate_skills: List[str], job_requirements: List[str], industry_skills: List[str] = []
    ) -> tuple:
        """
        Calculate skill match score
        
        Args:
            candidate_skills (List[str]): Skills from candidate's resume
            job_requirements (List[str]): Required skills for the job
            industry_skills (List[str]): Skills relevant to the industry
        
        Returns:
            tuple: (score, matched_skills, skill_gaps, industry_recommendations)
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
        
        # Calculate industry recommendations - skills that are in industry list but not in candidate skills
        industry_recommendations = [
            skill for skill in industry_skills
            if skill not in candidate_skills and skill not in job_requirements
        ]
        
        # Base score calculation
        match_percentage = len(matched_skills) / len(job_requirements) if job_requirements else 0
        
        # Apply industry skills bonus
        # Give extra weight to skills that are both job requirements and industry skills
        if industry_skills and matched_skills:
            industry_matched = [skill for skill in matched_skills if skill in industry_skills]
            industry_bonus = len(industry_matched) / len(job_requirements) * 0.2  # 20% bonus for industry-relevant skills
            match_percentage = min(1.0, match_percentage + industry_bonus)  # Cap at 1.0
        
        return match_percentage, matched_skills, skill_gaps, industry_recommendations
    
    def _calculate_experience_score(
        self, candidate_experience: Any, required_years: int
    ) -> float:
        """
        Calculate experience match score
        
        Args:
            candidate_experience: Either an integer (total years) or a list of experience dictionaries
            required_years (int): Required years of experience
        
        Returns:
            float: Experience match score
        """
        # Handle case where candidate_experience is already an integer
        if isinstance(candidate_experience, (int, float)):
            total_years = float(candidate_experience)
        else:
            # Original logic for handling list of dictionaries
            total_years = 0
            for exp in candidate_experience:
                duration_text = exp.get("duration", "").lower()
                # Find numbers (integers or floats) in the duration string
                years_found = re.findall(r"\d+\.?\d*", duration_text)
                if years_found:
                    # Assume the first number found is the relevant duration in years
                    try:
                        total_years += float(years_found[0])
                    except ValueError:
                        pass # Ignore if conversion fails
        
        logger.debug(f"Calculated candidate experience: {total_years} years")

        # Score based on ratio, capped at 1.0
        if required_years <= 0: # Avoid division by zero
            return 1.0 if total_years > 0 else 0.0
        
        score = min(total_years / required_years, 1.0)
        return score
    
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
    
    def _extract_jd_keywords(self, job_description_text: Optional[str]) -> set:
        """Extract potential keywords from job description using spaCy noun chunks and entities."""
        if not self.nlp or not job_description_text:
            return set()
        
        try:
            jd_doc = self.nlp(job_description_text)
            potential_keywords = set()
            
            # Noun Chunks
            for chunk in jd_doc.noun_chunks:
                for token in chunk:
                    if not token.is_stop and not token.is_punct and len(token.lemma_) > 2:
                        potential_keywords.add(token.lemma_.lower())
            
            # Named Entities
            for ent in jd_doc.ents:
                for token in ent:
                     if not token.is_stop and not token.is_punct and len(token.lemma_) > 2:
                         potential_keywords.add(token.lemma_.lower())
                if len(ent.text.split()) > 1 or ent.label_ in ['ORG', 'PRODUCT', 'TECH']:
                     potential_keywords.add(ent.text.lower())
            
            # Fallback if needed
            if not potential_keywords:
                 potential_keywords = {token.lemma_.lower() for token in jd_doc if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and not token.is_stop and len(token.lemma_) > 2}
            
            logger.debug(f"Extracted JD keywords (spaCy): {potential_keywords}")
            return potential_keywords
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return set()

    def _generate_recommendations(
        self, 
        candidate: Dict,
        job: Dict,
        matched_skills: List[str], 
        skill_gaps: List[str],
        industry_recommendations: List[str]
    ) -> List[str]:
        """
        Generate tailored recommendations based on match analysis
        
        Args:
            candidate (Dict): Candidate profile
            job (Dict): Job details
            matched_skills (List[str]): Skills that matched job requirements
            skill_gaps (List[str]): Missing skills for the job
            industry_recommendations (List[str]): Industry-specific skill recommendations
            
        Returns:
            List[str]: List of recommendation strings
        """
        recommendations = []
        
        # Add skill gap recommendations
        if skill_gaps:
            if len(skill_gaps) <= 3:
                recommendations.append(
                    f"Focus on developing these specific skills: {', '.join(skill_gaps)}"
                )
            else:
                recommendations.append(
                    f"Consider developing some of these skills: {', '.join(skill_gaps[:5])}"
                )
        
        # Add industry-specific recommendations
        if industry_recommendations:
            recommendations.append(
                f"To be more competitive in this industry, consider focusing on: {', '.join(industry_recommendations[:3])}"
            )
            
        # Add experience recommendations
        candidate_exp = candidate.get("years_of_experience", 0)
        required_exp = job.get("required_years", 0)
        
        if candidate_exp < required_exp:
            recommendations.append(
                f"Gain {required_exp - candidate_exp} more years of experience or highlight projects that demonstrate equivalent expertise"
            )
        
        # Add education recommendations
        candidate_education = candidate.get("education", [])
        required_education = job.get("education_level", "")
        
        if required_education:
            # Map education levels to weights for comparison
            education_levels = {
                "phd": 5,
                "master": 4,
                "bachelor": 3,
                "associate": 2,
                "high_school": 1
            }
            
            # Get the highest education level from candidate
            highest_level = "high_school"  # Default
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
            
            # Compare education levels
            candidate_level_value = education_levels.get(highest_level, 1)
            required_level_value = education_levels.get(required_education.lower(), 3)
            
            if candidate_level_value < required_level_value:
                # Convert level to readable format
                readable_level = {
                    "phd": "PhD or doctorate",
                    "master": "Master's degree",
                    "bachelor": "Bachelor's degree",
                    "associate": "Associate's degree",
                    "high_school": "High school diploma"
                }
                required_readable = readable_level.get(required_education.lower(), required_education)
                
                recommendations.append(
                    f"This position typically requires a {required_readable}. Consider advancing your education or highlighting equivalent experience."
                )
                
        # Try to get industry trends for trend-based recommendations
        try:
            db = next(get_db())
            industry_name = job.get("industry", "")
            if industry_name:
                trends = self.market_data_service.get_industry_trends(db, industry_name, limit=3)
                if trends:
                    trend_names = [trend.trend_name for trend in trends]
                    recommendations.append(
                        f"Stay updated on current industry trends like: {', '.join(trend_names)}"
                    )
        except Exception as e:
            logger.warning(f"Could not fetch industry trends for recommendations: {e}")
            
        # If no specific recommendations, add a generic one
        if not recommendations:
            recommendations.append("You're well-matched for this position. Consider highlighting your matched skills in your application.")
                
        return recommendations

    def _get_industry_skills(self, industry: str) -> List[str]:
        """
        Get skills associated with a specific industry
        
        Args:
            industry (str): Industry name
            
        Returns:
            List[str]: List of skills for the industry
        """
        if not industry:
            logger.warning("No industry provided, returning empty skill list")
            return []
            
        try:
            # Use industry service to get the skill set
            db = next(get_db())
            skill_set = self.industry_service.get_skill_set_by_industry(db, industry)
            if skill_set:
                logger.info(f"Fetched {len(skill_set.skills)} skills for industry: {industry}")
                return skill_set.skills
            else:
                logger.warning(f"No skill set found for identified industry: {industry}")
                return []
        except Exception as e:
            logger.error(f"Error getting industry skills: {str(e)}")
            return []

    def _get_industry_trends(self, industry: str) -> List[Dict]:
        """
        Get current trends for a specific industry
        
        Args:
            industry (str): Industry name
            
        Returns:
            List[Dict]: List of industry trends with descriptions
        """
        if not industry:
            logger.warning("No industry provided, returning empty trends list")
            return []
            
        try:
            db = next(get_db())
            trends = self.market_data_service.get_industry_trends(db, industry)
            if trends:
                return [{"name": trend.trend_name, "description": trend.description} for trend in trends]
            else:
                logger.warning(f"No trends found for industry: {industry}")
                return []
        except Exception as e:
            logger.error(f"Error getting industry trends: {str(e)}")
            return []
    
    def _get_salary_estimate(self, job_title: str, industry: str, experience_level: str = None) -> Dict:
        """
        Get salary range estimate for a job title in an industry
        
        Args:
            job_title (str): Job title
            industry (str): Industry name
            experience_level (str, optional): Experience level (entry, mid, senior)
            
        Returns:
            Dict: Salary range information
        """
        try:
            db = next(get_db())
            salary_data = self.market_data_service.get_salary_range(
                db, job_title, industry, experience_level=experience_level
            )
            
            if salary_data:
                return {
                    "min": salary_data.min_salary,
                    "max": salary_data.max_salary,
                    "median": salary_data.median_salary,
                    "currency": salary_data.currency
                }
            else:
                logger.warning(f"No salary data found for {job_title} in {industry}")
                return {}
        except Exception as e:
            logger.error(f"Error getting salary estimate: {str(e)}")
            return {}
    
    def _get_job_market_demand(self, job_title: str, industry: str) -> Dict:
        """
        Get job market demand information
        
        Args:
            job_title (str): Job title
            industry (str): Industry name
            
        Returns:
            Dict: Job market demand information
        """
        try:
            db = next(get_db())
            demand_data = self.market_data_service.get_job_market_demand(db, job_title, industry)
            
            if demand_data:
                return {
                    "demand_score": demand_data.demand_score,
                    "growth_rate": demand_data.growth_rate,
                    "openings": demand_data.num_openings,
                    "time_period": demand_data.time_period
                }
            else:
                logger.warning(f"No market demand data found for {job_title} in {industry}")
                return {}
        except Exception as e:
            logger.error(f"Error getting job market demand: {str(e)}")
            return {}
    
    def _get_career_path_recommendations(self, current_role: str, industry: str) -> List[Dict]:
        """
        Get career path recommendations
        
        Args:
            current_role (str): Current job title/role
            industry (str): Industry name
            
        Returns:
            List[Dict]: Career path recommendations
        """
        try:
            db = next(get_db())
            career_path = self.market_data_service.get_career_path(db, current_role, industry)
            
            if career_path and career_path.path_steps:
                # Return the next steps in the career path (up to 3)
                return career_path.path_steps[:3]
            else:
                logger.warning(f"No career path data found for {current_role} in {industry}")
                return []
        except Exception as e:
            logger.error(f"Error getting career path recommendations: {str(e)}")
            return []
            
    def score(self, candidate: Dict, job: Dict) -> Dict:
        """
        Calculate overall compatibility score
        
        Args:
            candidate (Dict): Candidate profile data
            job (Dict): Job posting data
        
        Returns:
            Dict: Scoring results with recommendations
        """
        # Extract relevant data
        candidate_skills = candidate.get("skills", [])
        job_requirements = job.get("required_skills", [])
        industry_skills = job.get("industry_skills", [])
        required_years = job.get("required_years", 0)
        candidate_experience = candidate.get("years_of_experience", 0)
        job_title = job.get("title", "")
        industry = job.get("industry", "")
        
        # Get education info
        candidate_education = candidate.get("education", [])
        required_education = job.get("education_level", "bachelor")  # Default to bachelor's
        
        # Calculate skill score
        skill_score, matched_skills, skill_gaps, industry_recommendations = self._calculate_skill_score(
            candidate_skills, job_requirements, industry_skills
        )
        
        # Calculate experience score
        exp_score = self._calculate_experience_score(candidate_experience, required_years)
        
        # Calculate education score if provided
        edu_score = 1.0  # Default perfect score
        if required_education and candidate_education:
            edu_score = self._calculate_education_score(candidate_education, required_education)
        
        # Calculate overall score (weighted average)
        overall_score = (skill_score * 0.6) + (exp_score * 0.25) + (edu_score * 0.15)
        
        # Generate specific recommendations
        recommendations = self._generate_recommendations(
            candidate={
                "skills": candidate_skills,
                "years_of_experience": candidate_experience,
                "education": candidate_education
            },
            job={
                "requirements": job_requirements,
                "industry": industry,
                "required_years": required_years,
                "education_level": required_education,
                "title": job_title
            },
            matched_skills=matched_skills,
            skill_gaps=skill_gaps,
            industry_recommendations=industry_recommendations
        )
        
        # Get market data if available
        market_data = {}
        try:
            if job_title and industry:
                db = next(get_db())
                # Determine experience level based on years
                exp_level = "entry"
                if candidate_experience >= 5:
                    exp_level = "senior"
                elif candidate_experience >= 2:
                    exp_level = "mid"
                
                # Get salary estimate
                salary_data = self._get_salary_estimate(job_title, industry, exp_level)
                if salary_data:
                    market_data["salary_range"] = salary_data
                
                # Get job market demand
                demand_data = self._get_job_market_demand(job_title, industry)
                if demand_data:
                    market_data["job_market_demand"] = demand_data
                
                # Get career path recommendations
                career_path = self._get_career_path_recommendations(job_title, industry)
                if career_path:
                    market_data["career_path"] = career_path
                
                # Get industry trends
                trends = self._get_industry_trends(industry)
                if trends:
                    market_data["industry_trends"] = trends
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            # Continue without market data
        
        result = {
            "overall_score": round(overall_score * 100),
            "skill_score": round(skill_score * 100),
            "experience_score": round(exp_score * 100),
            "matched_skills": matched_skills,
            "skill_gaps": skill_gaps,
            "industry_recommendations": industry_recommendations,
            "recommendations": recommendations,
            "market_data": market_data  # Always include market_data, even if empty
        }
        
        return result