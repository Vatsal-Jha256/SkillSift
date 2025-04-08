# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import resume_routes

#TODO: let it take input of job description in textual natural language format
#TODO: add authentication to the API
#TODO: add a database to store the resume and job description
#TODO: use postman for testing
#TODO: expand skill taxonomy
#TODO: add more comprehensive tests
#TODO: add better and more scoring algorithms
#TODO: add more error handling


app = FastAPI(
	title="ResumeRover AI",
	description="AI-powered resume analysis tool"
)

# CORS Configuration for frontend integration
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Include API routes
app.include_router(resume_routes.router, prefix="/api/resume")

# Optional: Add health check endpoint
@app.get("/health")
def health_check():
	return {"status": "healthy"}
