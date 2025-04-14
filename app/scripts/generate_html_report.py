import os
from app.services.reporter import ReportGenerator

# Create sample analysis data
analysis_data = {
    "skills": ["python", "fastapi", "sqlalchemy", "pytest", "docker"],
    "skills_data": {
        "skills": [
            {"skill": "python", "proficiency": "expert", "category": "programming"},
            {"skill": "fastapi", "proficiency": "intermediate", "category": "web framework"},
            {"skill": "sqlalchemy", "proficiency": "intermediate", "category": "database"},
            {"skill": "pytest", "proficiency": "intermediate", "category": "testing"},
            {"skill": "docker", "proficiency": "beginner", "category": "devops"}
        ],
        "categorized_skills": {
            "programming": [{"skill": "python", "proficiency": "expert"}],
            "web framework": [{"skill": "fastapi", "proficiency": "intermediate"}],
            "database": [{"skill": "sqlalchemy", "proficiency": "intermediate"}],
            "testing": [{"skill": "pytest", "proficiency": "intermediate"}],
            "devops": [{"skill": "docker", "proficiency": "beginner"}]
        }
    },
    "structured_data": {
        "contact_info": {"email": "test@example.com", "phone": "123-456-7890"},
        "education": [{"degree": "Bachelor of Science in Computer Science"}],
        "experience": [{"title": "Software Engineer", "description": "Developed web applications"}]
    },
    "compatibility_score": 85,
    "matched_skills": ["python", "fastapi", "sqlalchemy"],
    "skill_gaps": ["kubernetes", "aws"],
    "skill_score": 80,
    "experience_score": 90,
    "education_score": 85,
    "recommendations": [
        "Consider developing skills in Kubernetes for containerization orchestration",
        "Learn AWS cloud services for better cloud deployment understanding"
    ]
}

# Set output file path
output_dir = os.path.expanduser("~/")
output_file = os.path.join(output_dir, "resume_report.html")

# Generate HTML report
html_content = ReportGenerator.generate_html_report(analysis_data)

# Save the HTML report
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML report saved to: {output_file}") 