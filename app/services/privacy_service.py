import os
import json
import uuid
import shutil
import zipfile
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session
from app.core.models import User, Resume
from app.core.config import settings
from app.services.security_service import SecurityService

logger = logging.getLogger(__name__)

class PrivacyService:
    """Service for handling privacy-related operations like data export and deletion."""
    
    @staticmethod
    def request_data_deletion(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Request deletion of all user data.
        
        Args:
            db: Database session
            user_id: ID of the user requesting deletion
            
        Returns:
            Dictionary with status information
        """
        # Log the deletion request
        SecurityService.log_access(
            user_id=user_id,
            action="data_deletion_request",
            resource="user_data",
            status="initiated"
        )
        
        logger.info(f"Data deletion requested for user {user_id}")
        
        return {
            "status": "pending",
            "message": "Data deletion request received and will be processed",
            "requested_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def perform_data_deletion(db: Session, user_id: int) -> None:
        """
        Actually delete all data for a user.
        
        Args:
            db: Database session
            user_id: ID of the user whose data should be deleted
        """
        try:
            # Delete user's resumes
            resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
            for resume in resumes:
                # Delete the actual resume file if it exists
                if hasattr(resume, 'file_path') and resume.file_path and os.path.exists(resume.file_path):
                    SecurityService.securely_delete_file(resume.file_path)
                db.delete(resume)
            
            # Try to delete job applications if the model exists
            try:
                # Import dynamically to handle missing models
                job_applications = db.query(Resume).filter(Resume.user_id == user_id).all()
                for application in job_applications:
                    db.delete(application)
            except Exception as e:
                logger.info(f"Skipping job applications deletion: {str(e)}")
            
            # Try to delete saved jobs if the model exists
            try:
                from app.core.models import SavedJob
                saved_jobs = db.query(SavedJob).filter(SavedJob.user_id == user_id).all()
                for saved_job in saved_jobs:
                    db.delete(saved_job)
            except Exception as e:
                logger.info(f"Skipping saved jobs deletion: {str(e)}")
            
            # Try to delete activity logs if the model exists
            try:
                from app.core.models import ActivityLog
                activity_logs = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).all()
                for log in activity_logs:
                    db.delete(log)
            except Exception as e:
                logger.info(f"Skipping activity logs deletion: {str(e)}")
            
            # Anonymize but don't delete the user account yet
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.email = f"deleted_{user.id}@anonymous.com"
                user.full_name = f"Deleted User {user.id}"
                user.hashed_password = ""
                user.is_active = False
                if hasattr(user, 'deleted_at'):
                    user.deleted_at = datetime.now()
                
            # Commit the changes
            db.commit()
            
            logger.info(f"Data deletion completed for user {user_id}")
            
            # Log the successful deletion
            SecurityService.log_access(
                user_id=user_id,
                action="data_deletion_completed",
                resource="user_data",
                status="success"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error during data deletion for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    def request_data_export(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Request export of all user data.
        
        Args:
            db: Database session
            user_id: ID of the user requesting export
            
        Returns:
            Dictionary with export ID and status
        """
        # Create a unique ID for this export
        export_id = str(uuid.uuid4())
        
        # Create export directory if it doesn't exist
        export_base_dir = getattr(settings, "DATA_EXPORTS_DIR", "data/exports")
        os.makedirs(export_base_dir, exist_ok=True)
        
        # Create a user-specific export directory
        user_export_dir = os.path.join(export_base_dir, f"user_{user_id}")
        os.makedirs(user_export_dir, exist_ok=True)
        
        # Create export-specific directory
        export_dir = os.path.join(user_export_dir, export_id)
        os.makedirs(export_dir, exist_ok=True)
        
        # Log the export request
        SecurityService.log_access(
            user_id=user_id,
            action="data_export_request",
            resource="user_data",
            status="initiated",
            details=f"Data export request {export_id} initiated"
        )
        
        logger.info(f"Data export requested for user {user_id}, export ID: {export_id}")
        
        return {
            "export_id": export_id,
            "status": "pending",
            "message": "Data export request received and will be processed",
            "requested_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def perform_data_export(db: Session, user_id: int, export_id: str) -> None:
        """
        Actually export all data for a user.
        
        Args:
            db: Database session
            user_id: ID of the user whose data should be exported
            export_id: Unique ID for this export request
        """
        try:
            # Get the export directory
            export_base_dir = getattr(settings, "DATA_EXPORTS_DIR", "data/exports")
            user_export_dir = os.path.join(export_base_dir, f"user_{user_id}")
            export_dir = os.path.join(user_export_dir, export_id)
            
            # Ensure directory exists
            os.makedirs(export_dir, exist_ok=True)
            
            # Create metadata file
            metadata = {
                "export_id": export_id,
                "user_id": user_id,
                "exported_at": datetime.now().isoformat(),
                "status": "processing"
            }
            
            with open(os.path.join(export_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f)
            
            # Export user profile
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "name": user.full_name,
                    "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
                    "last_login": user.updated_at.isoformat() if hasattr(user, 'updated_at') and user.updated_at else None
                }
                
                with open(os.path.join(export_dir, "user_profile.json"), "w") as f:
                    json.dump(user_data, f)
            
            # Export resumes
            resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
            resumes_data = []
            
            resume_files_dir = os.path.join(export_dir, "resume_files")
            os.makedirs(resume_files_dir, exist_ok=True)
            
            for resume in resumes:
                resume_data = {
                    "id": resume.id,
                    "filename": resume.filename if hasattr(resume, 'filename') else None,
                    "file_type": resume.file_type if hasattr(resume, 'file_type') else None,
                    "raw_text": resume.raw_text if hasattr(resume, 'raw_text') else None,
                    "parsed_data": resume.parsed_data if hasattr(resume, 'parsed_data') else None,
                    "created_at": resume.created_at.isoformat() if hasattr(resume, 'created_at') and resume.created_at else None
                }
                resumes_data.append(resume_data)
                
                # Copy the actual resume file if it exists and file_path is available
                if hasattr(resume, 'file_path') and resume.file_path and os.path.exists(resume.file_path):
                    filename = os.path.basename(resume.file_path)
                    dest_path = os.path.join(resume_files_dir, filename)
                    shutil.copy2(resume.file_path, dest_path)
            
            with open(os.path.join(export_dir, "resumes.json"), "w") as f:
                json.dump(resumes_data, f)
            
            # Try to export job applications if model exists
            try:
                from app.core.models import JobApplication
                applications = db.query(JobApplication).filter(JobApplication.user_id == user_id).all()
                applications_data = []
                
                for application in applications:
                    app_data = {
                        "id": application.id,
                        "job_id": application.job_id if hasattr(application, 'job_id') else None,
                        "applied_at": application.applied_at.isoformat() if hasattr(application, 'applied_at') and application.applied_at else None,
                        "status": application.status if hasattr(application, 'status') else None,
                        "notes": application.notes if hasattr(application, 'notes') else None
                    }
                    applications_data.append(app_data)
                
                with open(os.path.join(export_dir, "job_applications.json"), "w") as f:
                    json.dump(applications_data, f)
            except Exception as e:
                logger.info(f"Skipping job applications export: {str(e)}")
            
            # Try to export saved jobs if model exists
            try:
                from app.core.models import SavedJob
                saved_jobs = db.query(SavedJob).filter(SavedJob.user_id == user_id).all()
                saved_jobs_data = []
                
                for saved_job in saved_jobs:
                    saved_job_data = {
                        "id": saved_job.id,
                        "job_id": saved_job.job_id if hasattr(saved_job, 'job_id') else None,
                        "saved_at": saved_job.saved_at.isoformat() if hasattr(saved_job, 'saved_at') and saved_job.saved_at else None
                    }
                    saved_jobs_data.append(saved_job_data)
                
                with open(os.path.join(export_dir, "saved_jobs.json"), "w") as f:
                    json.dump(saved_jobs_data, f)
            except Exception as e:
                logger.info(f"Skipping saved jobs export: {str(e)}")
            
            # Try to export activity logs if model exists
            try:
                from app.core.models import ActivityLog
                activity_logs = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).all()
                activity_logs_data = []
                
                for log in activity_logs:
                    log_data = {
                        "id": log.id,
                        "timestamp": log.timestamp.isoformat() if hasattr(log, 'timestamp') and log.timestamp else None,
                        "action": log.action if hasattr(log, 'action') else None,
                        "details": log.details if hasattr(log, 'details') else None
                    }
                    activity_logs_data.append(log_data)
                
                with open(os.path.join(export_dir, "activity_logs.json"), "w") as f:
                    json.dump(activity_logs_data, f)
            except Exception as e:
                logger.info(f"Skipping activity logs export: {str(e)}")
            
            # Create a ZIP file with all the exported data
            zip_path = os.path.join(user_export_dir, f"{export_id}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, _, files in os.walk(export_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, export_dir)
                        zip_file.write(file_path, arcname)
            
            # Update metadata to mark export as complete
            metadata["status"] = "completed"
            metadata["completed_at"] = datetime.now().isoformat()
            metadata["zip_path"] = zip_path
            
            with open(os.path.join(export_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f)
            
            logger.info(f"Data export completed for user {user_id}, export ID: {export_id}")
            
            # Log the successful export
            SecurityService.log_access(
                user_id=user_id,
                action="data_export_completed",
                resource="user_data",
                status="success",
                details=f"Data export {export_id} completed successfully"
            )
        except Exception as e:
            # Update metadata to mark export as failed
            try:
                metadata = {
                    "export_id": export_id,
                    "user_id": user_id,
                    "status": "failed",
                    "error": str(e),
                    "failed_at": datetime.now().isoformat()
                }
                
                export_base_dir = getattr(settings, "DATA_EXPORTS_DIR", "data/exports")
                user_export_dir = os.path.join(export_base_dir, f"user_{user_id}")
                export_dir = os.path.join(user_export_dir, export_id)
                
                with open(os.path.join(export_dir, "metadata.json"), "w") as f:
                    json.dump(metadata, f)
            except Exception as inner_e:
                logger.error(f"Error updating metadata for failed export {export_id}: {str(inner_e)}")
            
            logger.error(f"Error during data export for user {user_id}, export ID {export_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_export_status(db: Session, user_id: int, export_id: str) -> Dict[str, Any]:
        """
        Get the status of a data export request.
        
        Args:
            db: Database session
            user_id: ID of the user
            export_id: ID of the export
            
        Returns:
            Dictionary with export status information
        """
        # Validate and verify access to the export
        if not SecurityService.validate_export_id(export_id):
            logger.warning(f"Invalid export ID format: {export_id}")
            return {"status": "error", "message": "Invalid export ID format"}
        
        if not SecurityService.verify_export_access(export_id, str(user_id)):
            logger.warning(f"Access denied to export {export_id} for user {user_id}")
            return {"status": "error", "message": "Access denied to this export"}
        
        # Get the export directory
        export_base_dir = getattr(settings, "DATA_EXPORTS_DIR", "data/exports")
        user_export_dir = os.path.join(export_base_dir, f"user_{user_id}")
        export_dir = os.path.join(user_export_dir, export_id)
        
        # Check if the export directory exists
        if not os.path.exists(export_dir):
            logger.warning(f"Export directory not found for user {user_id}, export ID: {export_id}")
            return {"status": "error", "message": "Export not found"}
        
        # Check if metadata.json exists
        metadata_path = os.path.join(export_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            logger.warning(f"Metadata file not found for export {export_id}")
            return {
                "export_id": export_id,
                "status": "unknown",
                "message": "Export metadata not found"
            }
        
        # Read metadata file
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            # Check for ZIP file
            zip_path = os.path.join(user_export_dir, f"{export_id}.zip")
            metadata["zip_available"] = os.path.exists(zip_path)
            
            # Add size information if available
            if metadata["zip_available"]:
                metadata["zip_size_bytes"] = os.path.getsize(zip_path)
                metadata["zip_size_mb"] = round(metadata["zip_size_bytes"] / (1024 * 1024), 2)
            
            # Log this access
            SecurityService.log_access(
                user_id=user_id,
                action="export_status_check",
                resource="data_export",
                status="success",
                details=f"User checked status of export {export_id}"
            )
            
            return metadata
        except Exception as e:
            logger.error(f"Error reading metadata for export {export_id}: {str(e)}")
            return {
                "export_id": export_id,
                "status": "error",
                "message": f"Error reading export metadata: {str(e)}"
            }
    
    @staticmethod
    def get_export_file(db: Session, user_id: int, export_id: str, format: str = "json") -> Optional[str]:
        """
        Get the path to the exported file.
        
        Args:
            db: Database session
            user_id: ID of the user
            export_id: ID of the export
            format: Format of the export ("json" or "zip")
            
        Returns:
            Path to the export file, or None if not found
        """
        # Validate and verify access to the export
        if not SecurityService.validate_export_id(export_id):
            logger.warning(f"Invalid export ID format: {export_id}")
            return None
        
        if not SecurityService.verify_export_access(export_id, str(user_id)):
            logger.warning(f"Access denied to export {export_id} for user {user_id}")
            return None
        
        # Get the export directory
        export_base_dir = getattr(settings, "DATA_EXPORTS_DIR", "data/exports")
        user_export_dir = os.path.join(export_base_dir, f"user_{user_id}")
        
        if format.lower() == "zip":
            # Return the ZIP file path
            zip_path = os.path.join(user_export_dir, f"{export_id}.zip")
            if os.path.exists(zip_path):
                # Log this access
                SecurityService.log_access(
                    user_id=user_id,
                    action="export_download",
                    resource="data_export",
                    status="success",
                    details=f"User downloaded export {export_id} in ZIP format"
                )
                return zip_path
        else:
            # Return the directory for JSON files
            export_dir = os.path.join(user_export_dir, export_id)
            if os.path.exists(export_dir):
                # Log this access
                SecurityService.log_access(
                    user_id=user_id,
                    action="export_download",
                    resource="data_export",
                    status="success",
                    details=f"User downloaded export {export_id} in JSON format"
                )
                return export_dir
        
        logger.warning(f"Export file not found for user {user_id}, export ID: {export_id}, format: {format}")
        return None 