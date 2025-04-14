from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.core.logging import logger
from app.services.industry_service import IndustryService
from app.core.models import User, IndustrySkillSet # Import User for dependency
from app.core.dependencies import get_current_active_user
from pydantic import BaseModel, Field

router = APIRouter()
industry_service = IndustryService() # Instantiate the service

# Pydantic models for request/response
class IndustrySkillSetBase(BaseModel):
    industry_name: str = Field(..., example="Software Development")
    skills: List[str] = Field(..., example=["python", "fastapi", "react", "sql", "docker"])

class IndustrySkillSetCreate(IndustrySkillSetBase):
    pass

class IndustrySkillSetResponse(IndustrySkillSetBase):
    id: int
    created_at: Any # Use Any for datetime if direct conversion is complex
    updated_at: Any
    
    class Config:
        orm_mode = True

@router.post("/") #, response_model=IndustrySkillSetResponse, status_code=status.HTTP_201_CREATED)
def create_industry_skill_set(
    skill_set: IndustrySkillSetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Protect endpoint
):
    """Creates a new industry skill set. Requires authentication."""
    try:
        # Pass data directly to the service
        created_set = industry_service.add_industry_skill_set(
            db=db, 
            industry_name=skill_set.industry_name, 
            skills=skill_set.skills
        )
        # Manually create response dict to avoid complex datetime serialization in Pydantic model initially
        return {
            "id": created_set.id,
            "industry_name": created_set.industry_name,
            "skills": created_set.skills,
            "created_at": created_set.created_at.isoformat(),
            "updated_at": created_set.updated_at.isoformat()
        }
    except Exception as e: # Catch specific errors later if needed (DatabaseError)
        logger.error(f"Error creating industry skill set for '{skill_set.industry_name}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{industry_name}", response_model=IndustrySkillSetResponse)
def read_industry_skill_set(
    industry_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Optional: Protect endpoint
):
    """Retrieves a specific industry skill set by name."""
    db_skill_set = industry_service.get_skill_set_by_industry(db, industry_name=industry_name)
    if db_skill_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industry skill set not found")
    return db_skill_set # Pydantic should handle ORM conversion

@router.get("/") #, response_model=List[IndustrySkillSetResponse])
def read_all_industry_skill_sets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Optional: Protect endpoint
):
    """Retrieves all industry skill sets."""
    skill_sets = industry_service.get_all_industry_skill_sets(db)
    # Manually format list response 
    response_list = [
        {
            "id": s.id,
            "industry_name": s.industry_name,
            "skills": s.skills,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        } for s in skill_sets
    ]
    return response_list

@router.put("/{industry_name}", response_model=IndustrySkillSetResponse)
def update_industry_skills(
    industry_name: str,
    skills_update: Dict[str, List[str]], # Expect {"skills": ["new", "skill", "list"]}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Protect endpoint
):
    """Updates the skills for a specific industry."""
    new_skills = skills_update.get("skills")
    if new_skills is None:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body must contain 'skills' key with a list of strings.")
    try:
        updated_set = industry_service.update_industry_skill_set(db, industry_name, new_skills)
        if updated_set is None: # Should be handled by exception now, but keep check
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industry skill set not found for update")
        return updated_set
    except Exception as e: # Catch specific errors (NotFoundError, DatabaseError)
        logger.error(f"Error updating industry skill set for '{industry_name}': {e}")
        # Check for specific exceptions if defined
        # if isinstance(e, NotFoundError):
        #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{industry_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_industry( # Corrected function name
    industry_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Protect endpoint
):
    """Deletes an industry skill set."""
    try:
        deleted = industry_service.delete_industry_skill_set(db, industry_name)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industry skill set not found for deletion")
        # No content to return on successful deletion
        return None
    except Exception as e: # Catch specific errors (DatabaseError)
        logger.error(f"Error deleting industry skill set for '{industry_name}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 