import os
from app.services.parser import ResumeParser
from app.services.skill_extractor import SkillExtractor
from app.services.reporter import ReportGenerator

# Configuration
RESUME_PATH = "/home/vatsal/Downloads/VatsalJhaResume.pdf"
OUTPUT_HTML = os.path.expanduser("~/resume_analysis.html")

def main():
    print(f"Processing resume: {RESUME_PATH}")
    
    try:
        # Read the resume file
        with open(RESUME_PATH, 'rb') as f:
            resume_bytes = f.read()
        
        # Get file extension
        file_ext = os.path.splitext(RESUME_PATH)[1].lower().replace('.', '')
        
        # Parse the resume
        print("Parsing resume...")
        parsed_data = ResumeParser.parse_resume(resume_bytes, file_ext)
        structured_data = ResumeParser.extract_structured_data(parsed_data)
        
        # Extract skills
        print("Extracting skills...")
        skill_extractor = SkillExtractor()
        skills_data = skill_extractor.extract_skills_with_context(parsed_data)
        
        # Prepare analysis data
        print("Preparing analysis data...")
        analysis_data = {
            "skills": [skill["skill"] for skill in skills_data["skills"]],
            "skills_with_context": skills_data,
            "structured_data": structured_data,
            "compatibility_score": 0.75,  # Placeholder score
            "matched_skills": ["Python", "FastAPI", "SQL", "AWS"],  # Example matched skills
            "skill_gaps": ["Docker", "Kubernetes"],  # Example skill gaps
            "skill_score": 0.8,
            "experience_score": 0.7,
            "education_score": 0.75,
            "recommendations": [
                "Consider developing skills in containerization technologies like Docker and Kubernetes",
                "Enhance cloud deployment knowledge with AWS or GCP certifications",
                "Gain more experience with NoSQL databases"
            ]
        }
        
        # Generate HTML report
        print("Generating HTML report...")
        html_content = ReportGenerator.generate_html_report(analysis_data)
        
        # Save the HTML report
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\nHTML report saved to: {OUTPUT_HTML}")
        print(f"You can open this file in your web browser to view the report.")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 