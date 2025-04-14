from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, get_slm_service
from app.core.models import (
    CoverLetterTemplate, CoverLetterTemplateCreate, CoverLetterTemplateUpdate,
    CoverLetterRequest, CoverLetterResponse, User
)
from app.services.cover_letter_service import CoverLetterService
import logging

logger = logging.getLogger("skillsift")
router = APIRouter(prefix="/api/cover-letter", tags=["Cover Letter"])

@router.get("/templates", response_model=List[CoverLetterTemplate])
def get_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available cover letter templates"""
    service = CoverLetterService()
    return service.get_templates()

@router.get("/templates/{template_id}", response_model=CoverLetterTemplate)
def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific cover letter template"""
    service = CoverLetterService()
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found"
        )
    return template

@router.post("/templates", response_model=CoverLetterTemplate, status_code=status.HTTP_201_CREATED)
def create_template(
    template: CoverLetterTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new cover letter template"""
    service = CoverLetterService()
    
    # Check if template with this ID already exists
    existing_template = service.get_template(template.id)
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template with id {template.id} already exists"
        )
    
    return service.create_template(template)

@router.put("/templates/{template_id}", response_model=CoverLetterTemplate)
def update_template(
    template_id: str,
    template: CoverLetterTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing cover letter template"""
    service = CoverLetterService()
    
    # Check if template exists
    existing_template = service.get_template(template_id)
    if not existing_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found"
        )
    
    # Create a template object with the existing ID
    update_data = CoverLetterTemplateCreate(
        id=template_id,
        name=template.name,
        content=template.content,
        industry=template.industry
    )
    
    updated_template = service.update_template(template_id, update_data)
    if not updated_template:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template"
        )
    
    return updated_template

@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a cover letter template"""
    service = CoverLetterService()
    
    # Check if template exists
    existing_template = service.get_template(template_id)
    if not existing_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found"
        )
    
    success = service.delete_template(template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )
    
    return None

@router.post("/generate", response_model=CoverLetterResponse)
def generate_cover_letter(
    request: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    slm_service = Depends(get_slm_service)
):
    """Generate a cover letter based on the template and request details"""
    service = CoverLetterService(slm_service=slm_service)
    
    # Check if template exists
    template = service.get_template(request.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {request.template_id} not found"
        )
    
    try:
        return service.generate_cover_letter(request)
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate cover letter: {str(e)}"
        ) 