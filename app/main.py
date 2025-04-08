# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.routes import resume_routes
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import logger
from app.core.security import create_access_token, verify_password
from app.core.models import User
from app.core.dependencies import get_current_active_user
from sqlalchemy.orm import Session
from app.core.database import get_db

#TODO: let it take input of job description in textual natural language format
#TODO: add authentication to the API
#TODO: add a database to store the resume and job description
#TODO: use postman for testing
#TODO: expand skill taxonomy
#TODO: add more comprehensive tests
#TODO: add better and more scoring algorithms
#TODO: add more error handling

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
	title=settings.APP_NAME,
	description="AI-powered resume analysis tool",
	version=settings.APP_VERSION
)

# CORS Configuration for frontend integration
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.CORS_ORIGINS,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Include API routes
app.include_router(resume_routes.router, prefix="/api/resume")

# Authentication endpoint
@app.post("/token")
async def login_for_access_token(
	form_data: OAuth2PasswordRequestForm = Depends(),
	db: Session = Depends(get_db)
):
	"""
	OAuth2 compatible token login, get an access token for future requests
	"""
	# For demo purposes, create a user if it doesn't exist
	user = db.query(User).filter(User.email == form_data.username).first()
	if not user:
		# Create a demo user
		from app.core.security import get_password_hash
		user = User(
			email=form_data.username,
			hashed_password=get_password_hash(form_data.password),
			full_name="Demo User"
		)
		db.add(user)
		db.commit()
		db.refresh(user)
	
	# Verify password
	if not verify_password(form_data.password, user.hashed_password):
		return {"error": "Incorrect username or password"}
	
	# Create access token
	access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
		data={"sub": user.email}, expires_delta=access_token_expires
	)
	
	return {"access_token": access_token, "token_type": "bearer"}

# Health check endpoint
@app.get("/health")
def health_check():
	"""Health check endpoint"""
	return {"status": "healthy", "version": settings.APP_VERSION}

# Root endpoint
@app.get("/")
def read_root():
	"""Root endpoint with API information"""
	return {
		"name": settings.APP_NAME,
		"version": settings.APP_VERSION,
		"description": "AI-powered resume analysis tool",
		"documentation": "/docs"
	}
