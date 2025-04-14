# app/main.py
from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file first

import uvicorn
from fastapi import FastAPI, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
# Uncomment the cover letter routes import
from app.routes import resume_routes, industry_routes, market_data_routes, cover_letter_routes
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import logger
from app.core.security import create_access_token, verify_password
from app.core.models import User, LoginForm
from app.core.dependencies import get_current_active_user
from sqlalchemy.orm import Session
from app.core.database import get_db

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
	title=settings.APP_NAME,
	description="AI-powered resume analysis tool",
	version=settings.APP_VERSION
)

# Custom Exception Handler for 422 Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	# Log the detailed validation errors
	logger.error(f"Validation error for request {request.method} {request.url}: {exc.errors()}")
	# You could also log exc directly: logger.error(str(exc))
	
	# Return the default 422 response structure but add our log
	return JSONResponse(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		content={"detail": exc.errors()}, # Pydantic's detailed errors
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
app.include_router(resume_routes.router, prefix="/api/resume", tags=["Resume Analysis"])
app.include_router(industry_routes.router, prefix="/api/industry", tags=["Industry Skills"])
app.include_router(market_data_routes.router, prefix="/api/market", tags=["Market Data"])
# Uncomment the cover letter router include
app.include_router(cover_letter_routes.router)
from app.routes import privacy_routes
app.include_router(privacy_routes.router, prefix="/api/privacy", tags=["Privacy and GDPR"])

# Authentication endpoint
@app.post("/api/token", tags=["Authentication"])
async def login_for_access_token(
    form_data: LoginForm,
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
