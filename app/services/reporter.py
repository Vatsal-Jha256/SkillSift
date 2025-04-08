from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from typing import Dict, List

class ReportGenerator:
    """Service for generating resume analysis reports"""
    @staticmethod
    def generate_pdf_report(analysis_data: Dict) -> bytes:
        """
        Generate PDF report from analysis data
        Args:
        analysis_data (Dict): Comprehensive resume analysis data
        Returns:
        bytes: PDF report content
        """
        # Create a buffer to store PDF content
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Prepare styles
        styles = getSampleStyleSheet()
        
        # Content of the PDF
        story = []
        
        # Title
        title = Paragraph("Resume Analysis Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Skills Section
        skills_text = f"<b>Extracted Skills:</b> {', '.join(analysis_data.get('skills', []))}"
        skills_para = Paragraph(skills_text, styles['Normal'])
        story.append(skills_para)
        story.append(Spacer(1, 12))
        
        # Compatibility Section
        compatibility_text = f"<b>Job Compatibility Score:</b> {analysis_data.get('compatibility_score', 0)}%"
        compatibility_para = Paragraph(compatibility_text, styles['Normal'])
        story.append(compatibility_para)
        story.append(Spacer(1, 12))
        
        # Matched Skills
        matched_skills_text = f"<b>Matched Skills:</b> {', '.join(analysis_data.get('matched_skills', []))}"
        matched_skills_para = Paragraph(matched_skills_text, styles['Normal'])
        story.append(matched_skills_para)
        story.append(Spacer(1, 12))
        
        # Recommendations Section
        recommendations_text = "<b>Skill Recommendations:</b>"
        recommendations_para = Paragraph(recommendations_text, styles['Normal'])
        story.append(recommendations_para)
        
        # Add recommendation bullet points
        recommendations = analysis_data.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                rec_para = Paragraph(f"• {rec}", styles['Normal'])
                story.append(rec_para)
        
        # Build PDF
        doc.build(story)
        
        # Return PDF content as bytes
        return buffer.getvalue()