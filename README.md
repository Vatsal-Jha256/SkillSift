# SkillSift - AI Resume Analyzer

## Project Overview
SkillSift is an AI-powered resume analysis tool that helps job seekers and recruiters by providing intelligent resume parsing, skill extraction, and job compatibility scoring. The application uses advanced NLP techniques to analyze resumes and provide actionable feedback.

## Phase 1 Completion Report

### 1. Backend Architecture Refinement ✅
- [x] Implemented dependency injection using FastAPI's dependency system
- [x] Added SQLAlchemy database integration with User model
- [x] Implemented comprehensive error handling with custom exceptions
- [x] Added request validation using Pydantic models
- [x] Implemented structured logging system

### 2. Resume Parsing Enhancement ✅
- [x] Improved PDF parsing to handle multi-page resumes
- [x] Added structured data extraction (contact info, education, experience)
- [x] Implemented resume section detection
- [x] Added support for multiple file formats
- [x] Enhanced error handling for parsing operations

### 3. Skill Extraction Enhancement ✅
- [x] Expanded skill taxonomy with categories
- [x] Implemented context-aware skill extraction
- [x] Added skill proficiency level detection
- [x] Implemented skill normalization
- [x] Added categorized skill output

### 4. Compatibility Scoring Enhancement ✅
- [x] Implemented weighted scoring system
- [x] Added experience level matching
- [x] Added education level matching
- [x] Implemented skill relevance scoring
- [x] Added detailed scoring breakdown

### 5. Testing Enhancement ✅
- [x] Added comprehensive unit tests
- [x] Implemented integration tests
- [x] Added test fixtures and utilities
- [x] Improved test coverage
- [x] Added error case testing

## Project Structure
```
app/
├── core/               # Core functionality
│   ├── config.py      # Configuration settings
│   ├── database.py    # Database connection
│   ├── dependencies.py # Dependency injection
│   ├── exceptions.py  # Custom exceptions
│   ├── logging.py     # Logging configuration
│   ├── models.py      # Database models
│   └── security.py    # Authentication & security
├── routes/            # API routes
│   └── resume_routes.py
├── services/          # Business logic
│   ├── parser.py
│   ├── skill_extractor.py
│   ├── scorer.py
│   ├── reporter.py
│   └── job_description_parser.py
└── main.py           # Application entry point

tests/               # Test suite
├── conftest.py     # Test configuration
├── test_parser.py
├── test_skill_extractor.py
├── test_scorer.py
└── test_reporter.py
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/skillsift.git
cd skillsift
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

5. Run tests:
```bash
pytest tests/
```

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Main Endpoints

1. Authentication:
```
POST /token
- Form data: username, password
```

2. Resume Analysis:
```
POST /api/resume/analyze-resume/
- Headers: Authorization: Bearer <token>
- Form data: file (resume file)
- Optional: job_description (string), job_requirements (list of strings)
```

3. Report Generation:
```
POST /api/resume/generate-report/
- Headers: Authorization: Bearer <token>
- Body: analysis_data (JSON)
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
APP_NAME=SkillSift
APP_VERSION=1.0.0
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 