# app/routes/resume_routes.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks, Query, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, Response
from typing import List, Dict, Any, Optional
import os
import tempfile
from io import BytesIO
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    UnsupportedFileTypeError, 
    ParsingError, 
    SkillExtractionError, 
    CompatibilityScoringError,
    ReportGenerationError,
    OCRError
)
from app.services.parser import ResumeParser
from app.services.skill_extractor import SkillExtractor
from app.services.scorer import CompatibilityScorer
from app.services.reporter import ReportGenerator
from app.services.job_description_parser import JobDescriptionParser
from app.core.dependencies import get_current_active_user, get_job_description_parser
from app.core.models import User, Analysis
from app.services.security_service import SecurityService
from app.core.database import get_db
from sqlalchemy.orm import Session
router = APIRouter()

# Initialize services
skill_extractor = SkillExtractor()
scorer = CompatibilityScorer()
report_generator = ReportGenerator()

@router.get("/generate-pdf-report/")
async def generate_pdf_report(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate PDF report from analysis results"""
    try:
        # Get analysis results (non-async)
        analysis = get_analysis_by_id(analysis_id, str(current_user.id), db)
        
        if not analysis:
            logger.error(f"Analysis not found: {analysis_id}")
            raise HTTPException(
                status_code=404,
                detail="No analysis found. Please analyze your resume first."
            )

        # Generate PDF
        pdf_content = report_generator.generate_pdf_report(analysis['analysis_data'])
        
        filename = f"resume_analysis_{analysis_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_analysis_by_id(analysis_id: str, user_id: str, db: Session) -> Optional[Dict]:
    """Get analysis by ID or latest"""
    try:
        logger.debug(f"Fetching analysis: id={analysis_id}, user_id={user_id}")
        
        if analysis_id == "latest":
            analysis = db.query(Analysis).filter(
                Analysis.user_id == str(user_id)
            ).order_by(Analysis.created_at.desc()).first()
        else:
            analysis = db.query(Analysis).filter(
                Analysis.id == analysis_id,
                Analysis.user_id == str(user_id)
            ).first()
            
        if not analysis:
            logger.warning(f"No analysis found: id={analysis_id}, user_id={user_id}")
            return None
            
        return {
            "id": analysis.id,
            "resume_filename": analysis.resume_filename,
            "analysis_data": analysis.analysis_data,
            "created_at": analysis.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        return None
    
@router.post("/analyze-resume/")
async def analyze_resume(
    file: UploadFile = File(...), 
    job_description: Optional[str] = Form(None),
    job_requirements: Optional[List[str]] = Form(None),
    use_ocr: bool = Query(False, description="Use OCR for text extraction"),
    anonymize: bool = Query(False, description="Anonymize personal information in the response"),
    current_user: User = Depends(get_current_active_user),
    job_parser: JobDescriptionParser = Depends(get_job_description_parser),
    db: Session = Depends(get_db)
):
    try:
        # Validate file
        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')  # Remove the dot
        logger.debug(f"Processing file with extension: {file_ext}")
        
        if file_ext not in settings.ALLOWED_FILE_TYPES:
            logger.error(f"Unsupported file type: {file_ext}")
            raise UnsupportedFileTypeError(file_ext)
        
        # Read file content
        try:
            file_content = await file.read()
            logger.debug(f"File content read successfully. File size: {len(file_content)} bytes")
            
            # Use secure file handling
            secure_filename, file_path = SecurityService.secure_file_handling(
                file_content, 
                file.filename,
                allowed_extensions=["." + ext for ext in settings.ALLOWED_FILE_TYPES]
            )
            logger.debug(f"File securely saved as: {secure_filename}")
            
            # Log this access for audit purposes
            SecurityService.log_access(
                user_id=str(current_user.id),
                action="upload",
                resource=f"resume/{secure_filename}",
                status="success"
            )
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}")
            
            # Log this access for audit purposes
            SecurityService.log_access(
                user_id=str(current_user.id),
                action="upload",
                resource=f"resume/{file.filename}",
                status="failure",
                details=str(e)
            )
            
            raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
        
        # Parse resume with fallback
        try:
            resume_text = ResumeParser.parse_resume(file_content, file_ext, use_ocr=use_ocr)
            if not resume_text.strip():
                # Try OCR if normal parsing yields no text
                logger.info("No text extracted, attempting OCR")
                resume_text = ResumeParser.parse_resume(file_content, file_ext, use_ocr=True)
            logger.debug(f"Resume text: {resume_text[:100]}...")  # Log first 100 chars
            structured_data = ResumeParser.extract_structured_data(resume_text)
            logger.debug(f"Structured data: {structured_data}")
        except OCRError as e:
            logger.warning(f"OCR Error: {str(e)}")
            # Try without OCR if OCR fails
            try:
                resume_text = ResumeParser.parse_resume(file_content, file_ext, use_ocr=False)
                structured_data = ResumeParser.extract_structured_data(resume_text)
            except Exception as e:
                logger.error(f"Resume parsing failed even without OCR: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")
        except Exception as e:
            logger.error(f"Resume parsing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")

        # Extract skills with context
        try:
            skills_data = skill_extractor.extract_skills_with_context(resume_text)
            extracted_skills = [skill["skill"] for skill in skills_data["skills"]]
            logger.debug(f"Extracted skills: {extracted_skills}")
        except Exception as e:
            logger.error(f"Skill extraction failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to extract skills: {str(e)}")

        # Process job requirements
        requirements = job_requirements or []
        if job_description:
            try:
                job_skills = job_parser.extract_job_requirements(job_description)
                requirements.extend(job_skills)
                logger.debug(f"Job skills from description: {job_skills}")
            except Exception as e:
                logger.warning(f"Job description parsing failed: {str(e)}")
                # Continue with any existing requirements

        # Calculate compatibility score
        try:
            result = scorer.calculate_score(
                resume_text=resume_text,
                job_description=job_description,
                job_requirements=job_requirements
            )
            
            result['resume_filename'] = file.filename
            analysis = Analysis.create_from_result(db, str(current_user.id), result)
    
            response_data = {
                "skills": extracted_skills,
                "skills_data": skills_data,
                "structured_data": structured_data,
                **result,
                "analysis_id": analysis.id
            }
            
            # Anonymize if requested
            if anonymize:
                response_data = SecurityService.anonymize_data(response_data)
            
            return JSONResponse(content=response_data)
        except Exception as e:
            logger.error(f"Scoring failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to calculate score: {str(e)}")

        # Prepare response data
        response_data = {
            "skills": extracted_skills,
            "skills_data": skills_data,
            "structured_data": structured_data,
            "compatibility_score": score_result["score"],
            "matched_skills": score_result["matched_skills"],
            "skill_gaps": score_result["skill_gaps"],
            "recommendations": score_result["recommendations"]
        }
        
        # Anonymize data if requested
        if anonymize:
            response_data = SecurityService.anonymize_data(response_data)
        
        logger.info("Resume analysis completed successfully")

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/generate-report/")
async def generate_report(
    background_tasks: BackgroundTasks,
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate PDF report from analysis data
    
    Args:
        analysis_data (Dict[str, Any]): Comprehensive resume analysis
        current_user (User): Current authenticated user
    """
    try:
        pdf_report = report_generator.generate_pdf_report(analysis_data)
        
        # Write the PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_report)
            temp_file_path = temp_file.name
        
        # Schedule the temp file for deletion after sending the response
        background_tasks.add_task(os.unlink, temp_file_path)
        
        # Return the file response
        return FileResponse(
            path=temp_file_path, 
            media_type='application/pdf', 
            filename='resume_analysis_report.pdf'
        )
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise ReportGenerationError(str(e))

@router.post("/generate-html-report/")
async def generate_html_report(
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate interactive HTML report from analysis data
    
    Args:
        analysis_data (Dict[str, Any]): Comprehensive resume analysis
        current_user (User): Current authenticated user
    
    Returns:
        HTMLResponse: HTML report content
    """
    try:
        # Check if we should save this report for history
        if analysis_data.get("save_history", False):
            report_generator.save_report_history(str(current_user.id), analysis_data)
        
        # Generate HTML report
        html_content = report_generator.generate_html_report(analysis_data)
        
        # Return HTML response
        return HTMLResponse(
            content=html_content,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        raise ReportGenerationError(str(e))

@router.post("/generate-comparative-report/")
async def generate_comparative_report(
    background_tasks: BackgroundTasks,
    report_data: Dict[str, Dict],
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate comparative PDF report from current and previous analysis data
    
    Args:
        report_data (Dict): Current and previous analysis data
        current_user (User): Current authenticated user
    
    Returns:
        FileResponse: PDF file
    """
    try:
        # Extract current and previous analysis data
        current_analysis = report_data.get("current_analysis", {})
        previous_analysis = report_data.get("previous_analysis", {})
        
        if not current_analysis or not previous_analysis:
            raise ValueError("Both current and previous analysis data are required")
        
        # Generate comparative report
        pdf_report = report_generator.generate_comparative_report(
            current_analysis, previous_analysis
        )
        
        # Write the PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_report)
            temp_file_path = temp_file.name
        
        # Schedule the temp file for deletion after sending the response
        background_tasks.add_task(os.unlink, temp_file_path)
        
        # Return the file response
        return FileResponse(
            path=temp_file_path, 
            media_type='application/pdf', 
            filename='comparative_report.pdf'
        )
    except Exception as e:
        logger.error(f"Error generating comparative report: {str(e)}")
        raise ReportGenerationError(str(e))

@router.get("/report-history/")
async def get_report_history(
    limit: int = 5,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's report history
    
    Args:
        limit (int): Maximum number of reports to return
        current_user (User): Current authenticated user
    
    Returns:
        List[Dict]: List of historical reports
    """
    try:
        # Get report history
        history = report_generator.get_report_history(str(current_user.id), limit)
        
        return history
    except Exception as e:
        logger.error(f"Error retrieving report history: {str(e)}")
        raise ReportGenerationError(str(e))
