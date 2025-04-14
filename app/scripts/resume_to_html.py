import os
import requests
import tempfile

# Configuration
RESUME_PATH = "/home/vatsal/Downloads/VatsalJhaResume.pdf"
API_BASE_URL = "http://localhost:8000"  # Change if your API runs on a different port
OUTPUT_HTML = os.path.expanduser("~/resume_analysis.html")

# Get authentication token
def get_auth_token():
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{API_BASE_URL}/token", data=login_data)
    if response.status_code != 200:
        raise Exception(f"Authentication failed: {response.text}")
    
    return response.json().get("access_token")

# Step 1: Upload and analyze the resume
def analyze_resume(resume_path, token):
    # Prepare the files and data for the request
    with open(resume_path, 'rb') as f:
        resume_bytes = f.read()
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Sample job description
    job_description = """
    Senior Software Engineer - Python
    
    Requirements:
    - 5+ years of experience in Python development
    - Experience with web frameworks like FastAPI or Flask
    - Strong understanding of RESTful APIs
    - Knowledge of SQL and NoSQL databases
    - Experience with cloud services (AWS, GCP, or Azure)
    - Familiarity with containerization (Docker, Kubernetes)
    - Good understanding of software design patterns
    - Excellent problem-solving and communication skills
    """
    
    files = {"file": ("resume.pdf", resume_bytes, "application/pdf")}
    data = {"job_description": job_description}
    
    # Call the API to analyze the resume
    response = requests.post(
        f"{API_BASE_URL}/api/resume/analyze-resume/", 
        files=files, 
        data=data,
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Resume analysis failed: {response.text}")
    
    return response.json()

# Step 2: Generate the HTML report
def generate_html_report(analysis_data, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Call the API to generate an HTML report
    response = requests.post(
        f"{API_BASE_URL}/api/resume/generate-html-report/", 
        json=analysis_data,
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"HTML report generation failed: {response.text}")
    
    return response.text

# Main process
def main():
    print(f"Processing resume: {RESUME_PATH}")
    
    try:
        # Get authentication token
        token = get_auth_token()
        print("Authentication successful")
        
        # Analyze the resume
        print("Analyzing resume...")
        analysis_result = analyze_resume(RESUME_PATH, token)
        print("Resume analyzed successfully")
        
        # Generate the HTML report
        print("Generating HTML report...")
        html_content = generate_html_report(analysis_result, token)
        
        # Save the HTML report
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\nHTML report saved to: {OUTPUT_HTML}")
        print(f"You can open this file in your web browser to view the report.")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 