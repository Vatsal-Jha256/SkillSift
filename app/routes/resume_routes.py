# app/routes/resume_routes.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List
import os
from io import BytesIO
import tempfile
import os
from fastapi import BackgroundTasks
from app.core.config import settings
from app.services.parser import ResumeParser
from app.services.skill_extractor import SkillExtractor
from app.services.scorer import CompatibilityScorer
from app.services.reporter import ReportGenerator
# Update resume_routes.py to use the new parser
from app.services.job_description_parser import JobDescriptionParser

router = APIRouter()

job_description_parser = JobDescriptionParser()

skill_extractor = SkillExtractor()
scorer = CompatibilityScorer()
report_generator = ReportGenerator()

@router.post("/analyze-resume/")
async def analyze_resume(
    file: UploadFile = File(...), 
    job_requirements: List[str] = []
):
    """
    Analyze uploaded resume and generate compatibility report
    
    Args:
        file (UploadFile): Resume file to analyze
        job_requirements (List[str]): Skills required for job
    """
    # Validate file
    file_ext = os.path.splitext(file.filename)[1]
    if file_ext not in settings.SUPPORTED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Read file content
    file_content = await file.read()
    
    # Parse resume
    try:
        resume_text = ResumeParser.parse_resume(file_content, file_ext)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Extract skills
    extracted_skills = skill_extractor.extract_skills(resume_text)
    
    # Calculate compatibility
    compatibility_result = scorer.calculate_score(
        extracted_skills, 
        job_requirements
    )
    
    # Prepare analysis data
    analysis_data = {
        'skills': extracted_skills,
        'compatibility_score': compatibility_result['score'],
        'matched_skills': compatibility_result['matched_skills'],
        'recommendations': compatibility_result['recommendations']
    }
    
    return JSONResponse(content=analysis_data)

@router.post("/generate-report/")
async def generate_report(
    background_tasks: BackgroundTasks,  # Add BackgroundTasks as a parameter
    analysis_data: dict
):
    """
    Generate PDF report from analysis data
    Args:
        analysis_data (dict): Comprehensive resume analysis
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
        raise HTTPException(status_code=500, detail=str(e))
