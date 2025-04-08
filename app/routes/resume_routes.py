# app/routes/resume_routes.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Any, Optional
import os
import tempfile
from io import BytesIO
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
from app.core.dependencies import get_current_active_user
from app.core.models import User

router = APIRouter()

# Initialize services
job_description_parser = JobDescriptionParser()
skill_extractor = SkillExtractor()
scorer = CompatibilityScorer()
report_generator = ReportGenerator()

@router.post("/analyze-resume/")
async def analyze_resume(
    file: UploadFile = File(...), 
    job_description: Optional[str] = None,
    job_requirements: Optional[List[str]] = None,
    use_ocr: bool = Query(False, description="Use OCR for text extraction"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze uploaded resume and generate compatibility report
    
    Args:
        file (UploadFile): Resume file to analyze
        job_description (Optional[str]): Natural language job description
        job_requirements (Optional[List[str]]): Pre-defined skills required for job
        use_ocr (bool): Whether to use OCR for text extraction
        current_user (User): Current authenticated user
    """
    try:
        # Validate file
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.SUPPORTED_FILE_TYPES:
            raise UnsupportedFileTypeError(file_ext)
        
        # Read file content
        file_content = await file.read()
        
        # Parse resume
        try:
            resume_text = ResumeParser.parse_resume(file_content, file_ext, use_ocr=use_ocr)
            structured_data = ResumeParser.extract_structured_data(resume_text)
        except OCRError as e:
            logger.error(f"OCR error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"OCR processing failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise ParsingError(str(e))
        
        # Extract skills with context
        try:
            skills_data = skill_extractor.extract_skills_with_context(resume_text)
            extracted_skills = [skill["skill"] for skill in skills_data["skills"]]
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            raise SkillExtractionError(str(e))
        
        # Process job requirements
        requirements = job_requirements or []
        if job_description:
            try:
                job_skills = job_description_parser.extract_job_requirements(job_description)
                requirements.extend(job_skills)
            except Exception as e:
                logger.error(f"Error parsing job description: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse job description: {str(e)}"
                )
        
        # Calculate compatibility score
        try:
            score_result = scorer.calculate_score(
                candidate_skills=extracted_skills,
                job_requirements=requirements,
                candidate_experience=structured_data.get("experience"),
                candidate_education=structured_data.get("education")
            )
        except Exception as e:
            logger.error(f"Error calculating score: {str(e)}")
            raise CompatibilityScoringError(str(e))
        
        # Generate report
        try:
            report_data = {
                "resume_text": resume_text,
                "structured_data": structured_data,
                "skills_data": skills_data,
                "score_result": score_result,
                "job_description": job_description,
                "job_requirements": requirements
            }
            
            report_path = report_generator.generate_report(report_data)
            
            return FileResponse(
                report_path,
                media_type="application/pdf",
                filename="resume_analysis_report.pdf"
            )
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise ReportGenerationError(str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )

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
