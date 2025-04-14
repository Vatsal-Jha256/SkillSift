# SkillSift

SkillSift is a sophisticated resume analysis and career development platform that helps match candidates with job opportunities by analyzing skills, generating customized reports, and providing market insights.

## Features

- **Resume Analysis**
  - Extracts skills and experience from resumes
  - Supports multiple file formats (PDF, DOCX, etc.)
  - Optional OCR capabilities for scanned documents
  - Personal information anonymization

- **Job Market Analysis**
  - Salary range insights
  - Job market demand tracking
  - Career path guidance
  - Industry trends analysis

- **Customized Reports**
  - PDF report generation
  - Interactive HTML reports
  - Comparative analysis
  - Historical tracking

- **Privacy & Security**
  - GDPR compliance
  - Data encryption
  - Secure file handling
  - User data export/deletion capabilities

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SkillSift.git
cd SkillSift
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

### Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

After starting the server, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Resume Analysis
- `POST /analyze-resume/` - Analyze resume and extract skills
- `GET /generate-pdf-report/` - Generate PDF analysis report
- `POST /generate-html-report/` - Generate interactive HTML report

### Market Data
- `GET /salary/{job_title}` - Get salary ranges
- `GET /demand/{job_title}` - Get job market demand
- `GET /career-path/{role}` - Get career progression paths
- `GET /trends/{industry_name}` - Get industry trends

### Privacy
- `GET /privacy-policy` - View privacy policy
- `POST /delete-data` - Request data deletion
- `POST /export-data` - Request data export

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI framework
- SQLAlchemy ORM
- Pydantic data validation
- PyPDF2 for PDF processing
- spaCy for NLP operations