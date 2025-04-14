from typing import Dict, List, Optional
import os
import json
from datetime import datetime
from pathlib import Path
import logging
from app.core.models import CoverLetterTemplate, CoverLetterRequest, CoverLetterResponse
from app.services.slm_service import SLMService

logger = logging.getLogger("skillsift")

class CoverLetterService:
    """Service for generating customized cover letters"""
    
    def __init__(self, slm_service: Optional[SLMService] = None):
        self.slm_service = slm_service
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        self.default_templates = {
            "general": {
                "name": "General Purpose",
                "content": """Dear {hiring_manager},

I am writing to express my interest in the {job_title} position at {company_name}. With my background in {background} and experience in {experience}, I believe I am well-suited for this role.

{customized_content}

My key strengths that align with this position include:
{skills_section}

I am excited about the opportunity to bring my skills and experience to {company_name} and contribute to your team's success. I look forward to discussing how my background aligns with your needs.

Thank you for considering my application.

Sincerely,
{applicant_name}
"""
            },
            "technical": {
                "name": "Technical Role",
                "content": """Dear {hiring_manager},

I am applying for the {job_title} position at {company_name} that I saw advertised on {job_source}. As a professional with {experience} in {background}, I am confident in my ability to contribute effectively to your team.

{customized_content}

Technical skills relevant to this position:
{skills_section}

I am particularly drawn to {company_name} because of {company_interest}. I am eager to apply my technical expertise to help achieve your company's goals.

I would welcome the opportunity to discuss how my background and skills would be beneficial to your team. Thank you for considering my application.

Best regards,
{applicant_name}
"""
            },
            "creative": {
                "name": "Creative Role",
                "content": """Dear {hiring_manager},

When I discovered the {job_title} opportunity at {company_name}, I knew it was the perfect chance to combine my passion for {background} with my skills in {experience}.

{customized_content}

Creative achievements that demonstrate my fit for this role:
{skills_section}

What excites me most about {company_name} is {company_interest}. I would love to bring my creative perspective and problem-solving abilities to your innovative team.

I look forward to the possibility of discussing how my creative approach can benefit {company_name}.

Creatively yours,
{applicant_name}
"""
            }
        }
        self._initialize_default_templates()
        
    def _initialize_default_templates(self):
        """Initialize default templates if they don't exist"""
        for template_id, template_data in self.default_templates.items():
            template_file = self.templates_dir / f"{template_id}.json"
            if not template_file.exists():
                with open(template_file, "w") as f:
                    json.dump(template_data, f, indent=2)
                logger.info(f"Created default template: {template_id}")
    
    def get_templates(self) -> List[CoverLetterTemplate]:
        """Get all available cover letter templates"""
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    template_data = json.load(f)
                    template_id = template_file.stem
                    templates.append(
                        CoverLetterTemplate(
                            id=template_id,
                            name=template_data.get("name", template_id),
                            content=template_data.get("content", ""),
                            industry=template_data.get("industry", None)
                        )
                    )
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {str(e)}")
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[CoverLetterTemplate]:
        """Get a specific cover letter template by ID"""
        template_file = self.templates_dir / f"{template_id}.json"
        if not template_file.exists():
            return None
            
        try:
            with open(template_file, "r") as f:
                template_data = json.load(f)
                return CoverLetterTemplate(
                    id=template_id,
                    name=template_data.get("name", template_id),
                    content=template_data.get("content", ""),
                    industry=template_data.get("industry", None)
                )
        except Exception as e:
            logger.error(f"Error loading template {template_file}: {str(e)}")
            return None
    
    def create_template(self, template: CoverLetterTemplate) -> CoverLetterTemplate:
        """Create a new cover letter template"""
        template_file = self.templates_dir / f"{template.id}.json"
        
        template_data = {
            "name": template.name,
            "content": template.content,
            "industry": template.industry
        }
        
        with open(template_file, "w") as f:
            json.dump(template_data, f, indent=2)
        
        logger.info(f"Created template: {template.id}")
        return template
    
    def update_template(self, template_id: str, template: CoverLetterTemplate) -> Optional[CoverLetterTemplate]:
        """Update an existing cover letter template"""
        template_file = self.templates_dir / f"{template_id}.json"
        if not template_file.exists():
            return None
            
        template_data = {
            "name": template.name,
            "content": template.content,
            "industry": template.industry
        }
        
        with open(template_file, "w") as f:
            json.dump(template_data, f, indent=2)
        
        logger.info(f"Updated template: {template_id}")
        return template
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a cover letter template"""
        template_file = self.templates_dir / f"{template_id}.json"
        if not template_file.exists():
            return False
            
        os.remove(template_file)
        logger.info(f"Deleted template: {template_id}")
        return True
    
    def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetterResponse:
        """Generate a cover letter based on the template and request details"""
        template = self.get_template(request.template_id)
        if not template:
            raise ValueError(f"Template not found: {request.template_id}")
        
        # Format skills section
        skills_section = ""
        for skill in request.skills:
            skills_section += f"• {skill}\n"
        
        # Generate customized content if SLM service is available
        customized_content = ""
        if self.slm_service and request.job_description:
            try:
                prompt = f"""
                Generate a personalized paragraph for a cover letter with the following details:
                - Job Title: {request.job_title}
                - Company: {request.company_name}
                - Applicant background: {request.background}
                - Applicant key skills: {', '.join(request.skills)}
                - Job description: {request.job_description}
                - Tone: {request.tone or 'professional'}
                
                Write 1-2 paragraphs that highlight how the applicant's experience aligns with the job requirements.
                Be specific, professional, and concise. Avoid generic statements.
                """
                
                customized_content = self.slm_service.generate_text(prompt)
            except Exception as e:
                logger.error(f"Error generating customized content: {str(e)}")
                customized_content = "With my skills and experience, I am confident that I can make a significant contribution to your team and help achieve your company's goals."
        else:
            customized_content = "With my skills and experience, I am confident that I can make a significant contribution to your team and help achieve your company's goals."
        
        # Fill template with request data
        content = template.content.format(
            hiring_manager=request.hiring_manager or "Hiring Manager",
            job_title=request.job_title,
            company_name=request.company_name,
            background=request.background or "relevant fields",
            experience=request.experience or "similar roles",
            customized_content=customized_content,
            skills_section=skills_section,
            applicant_name=request.applicant_name,
            job_source=request.job_source or "your website",
            company_interest=request.company_interest or "your innovative work and company culture"
        )
        
        return CoverLetterResponse(
            content=content,
            created_at=datetime.now().isoformat(),
            template_id=request.template_id,
            meta_data={
                "tone": request.tone or "professional",
                "company": request.company_name,
                "job_title": request.job_title
            }
        ) 