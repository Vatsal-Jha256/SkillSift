from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.models import IndustrySkillSet
from app.core.logging import logger
from app.core.exceptions import DatabaseError, NotFoundError # Assuming these exceptions exist or creating them

class IndustryService:
    """Service for managing industry-specific skill sets."""

    def add_industry_skill_set(self, db: Session, industry_name: str, skills: List[str]) -> IndustrySkillSet:
        """Adds a new industry skill set to the database."""
        logger.info(f"Adding skill set for industry: {industry_name}")
        try:
            # Check if industry already exists
            existing_set = db.query(IndustrySkillSet).filter(IndustrySkillSet.industry_name == industry_name).first()
            if existing_set:
                logger.warning(f"Industry skill set for '{industry_name}' already exists. Updating skills.")
                existing_set.skills = skills
                db_skill_set = existing_set
            else:
                db_skill_set = IndustrySkillSet(industry_name=industry_name, skills=skills)
                db.add(db_skill_set)
            
            db.commit()
            db.refresh(db_skill_set)
            logger.info(f"Successfully added/updated skill set for industry: {industry_name}")
            return db_skill_set
        except Exception as e:
            db.rollback()
            logger.error(f"Database error adding industry skill set for '{industry_name}': {e}")
            # Raise a specific database error if available
            raise DatabaseError(f"Could not add industry skill set: {e}") from e

    def get_skill_set_by_industry(self, db: Session, industry_name: str) -> Optional[IndustrySkillSet]:
        """Retrieves a skill set for a specific industry."""
        logger.debug(f"Fetching skill set for industry: {industry_name}")
        try:
            return db.query(IndustrySkillSet).filter(IndustrySkillSet.industry_name == industry_name).first()
        except Exception as e:
            logger.error(f"Database error fetching skill set for '{industry_name}': {e}")
            # Raise a specific database error if available
            raise DatabaseError(f"Could not fetch industry skill set: {e}") from e

    def get_all_industry_skill_sets(self, db: Session) -> List[IndustrySkillSet]:
        """Retrieves all industry skill sets."""
        logger.debug("Fetching all industry skill sets")
        try:
            return db.query(IndustrySkillSet).all()
        except Exception as e:
            logger.error(f"Database error fetching all skill sets: {e}")
            # Raise a specific database error if available
            raise DatabaseError(f"Could not fetch all industry skill sets: {e}") from e
            
    def update_industry_skill_set(self, db: Session, industry_name: str, new_skills: List[str]) -> Optional[IndustrySkillSet]:
        """Updates the skills for a specific industry."""
        logger.info(f"Updating skills for industry: {industry_name}")
        try:
            db_skill_set = db.query(IndustrySkillSet).filter(IndustrySkillSet.industry_name == industry_name).first()
            if db_skill_set:
                db_skill_set.skills = new_skills
                db.commit()
                db.refresh(db_skill_set)
                logger.info(f"Successfully updated skills for industry: {industry_name}")
                return db_skill_set
            else:
                logger.warning(f"Industry '{industry_name}' not found for update.")
                # Raise a specific not found error if available
                raise NotFoundError(f"Industry '{industry_name}' not found.")
        except Exception as e:
            db.rollback()
            logger.error(f"Database error updating industry skill set for '{industry_name}': {e}")
            # Raise a specific database error if available
            raise DatabaseError(f"Could not update industry skill set: {e}") from e

    def delete_industry_skill_set(self, db: Session, industry_name: str) -> bool:
        """Deletes the skill set for a specific industry."""
        logger.info(f"Deleting skill set for industry: {industry_name}")
        try:
            db_skill_set = db.query(IndustrySkillSet).filter(IndustrySkillSet.industry_name == industry_name).first()
            if db_skill_set:
                db.delete(db_skill_set)
                db.commit()
                logger.info(f"Successfully deleted skill set for industry: {industry_name}")
                return True
            else:
                logger.warning(f"Industry '{industry_name}' not found for deletion.")
                return False # Or raise NotFoundError
        except Exception as e:
            db.rollback()
            logger.error(f"Database error deleting industry skill set for '{industry_name}': {e}")
            # Raise a specific database error if available
            raise DatabaseError(f"Could not delete industry skill set: {e}") from e

# Optional: Define custom exceptions if they don't exist
# class DatabaseError(Exception):
#     pass

# class NotFoundError(Exception):
#     pass

# Instantiate the service (or use dependency injection)
# industry_service = IndustryService() 