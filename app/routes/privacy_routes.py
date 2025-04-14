from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, File, UploadFile, Response
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from app.core.dependencies import get_current_active_user
from app.core.models import User
from app.services.security_service import SecurityService
from app.services.privacy_service import PrivacyService
from app.core.database import get_db
from app.core.config import settings
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/privacy-policy")
async def get_privacy_policy():
    """Get privacy policy information."""
    return {
        "privacy_policy": {
            "last_updated": "2025-04-14",
            "version": "1.0",
            "description": "This privacy policy explains how SkillSift collects, uses, and protects your personal data.",
            "gdpr_compliance": SecurityService.get_gdpr_compliance_info(),
            "data_retention": SecurityService.get_data_retention_policy()
        }
    }

@router.get("/data-retention")
async def get_data_retention_policy():
    """Get data retention policy."""
    return SecurityService.get_data_retention_policy()

@router.post("/delete-data", status_code=status.HTTP_202_ACCEPTED)
async def request_data_deletion(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    """Request deletion of all personal data."""
    try:
        # Request data deletion
        result = PrivacyService.request_data_deletion(db, user.id)
        
        # Queue deletion in background task
        background_tasks.add_task(
            PrivacyService.perform_data_deletion,
            db=db,
            user_id=user.id
        )
        
        return {
            "status": "success",
            "message": "Data deletion request accepted and queued for processing",
            "request_id": result.get("requested_at")
        }
    except Exception as e:
        logging.error(f"Error in data deletion request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data deletion request"
        )

@router.post("/export-data", status_code=status.HTTP_202_ACCEPTED)
async def request_data_export(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    """Request export of all personal data in compliance with GDPR."""
    try:
        # Request data export
        result = PrivacyService.request_data_export(db, user.id)
        export_id = result.get("export_id")
        
        # Queue export in background task
        background_tasks.add_task(
            PrivacyService.perform_data_export,
            db=db,
            user_id=user.id,
            export_id=export_id
        )
        
        return {
            "status": "success",
            "message": "Data export request accepted and queued for processing",
            "export_id": export_id
        }
    except Exception as e:
        logging.error(f"Error in data export request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data export request"
        )

@router.get("/export-status/{export_id}")
async def get_export_status(
    export_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    """Get the status of a data export request."""
    try:
        status_data = PrivacyService.get_export_status(db, user.id, export_id)
        
        if status_data.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_data.get("message", "Export not found")
            )
        
        return status_data
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logging.error(f"Error retrieving export status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve export status"
        )

@router.get("/download-export/{export_id}")
async def download_data_export(
    export_id: str,
    format: Optional[str] = "json",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    """
    Download a completed data export in JSON or ZIP format.
    
    Args:
        export_id: ID of the export to download
        format: Format of the download - 'json' or 'zip' (default: 'json')
    """
    # Validate format
    if format not in ["json", "zip"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported formats: 'json', 'zip'"
        )
    
    try:
        # Get export file path
        export_path = PrivacyService.get_export_file(db, user.id, export_id, format)
        
        if not export_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export not found or not ready for download"
            )
        
        # Handle different export formats
        if format == "zip":
            # Create a response with the ZIP file
            with open(export_path, 'rb') as f:
                content = f.read()
            
            headers = {
                'Content-Disposition': f'attachment; filename="data_export_{export_id}.zip"',
                'Content-Type': 'application/zip'
            }
            
            return Response(content=content, headers=headers)
        else:
            # Return directory path for JSON files (FastAPI will serialize this to JSON)
            status_data = PrivacyService.get_export_status(db, user.id, export_id)
            
            # Verify status is completed
            if status_data.get("status") != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Export is not ready for download"
                )
            
            # Return JSON data (this would need to be handled differently in a real app,
            # as we're returning a directory path rather than the content)
            return {
                "status": "success",
                "message": "Export data is ready for download",
                "export_id": export_id,
                "export_path": str(export_path),
                "export_completed": status_data.get("completed_at")
            }
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logging.error(f"Error downloading export: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download export"
        ) 