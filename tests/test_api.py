import pytest
import io
from fastapi.testclient import TestClient

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_authentication(client, test_user):
    """Test authentication flow"""
    response = client.post(
        "/api/token",
        json={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200, f"Auth failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_unauthorized_access(client):
    """Test unauthorized access"""
    response = client.post("/api/resume/analyze-resume/")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_resume_analysis(client, auth_headers):
    """Test resume analysis endpoint"""
    # Create a valid PDF with content
    pdf_content = (
        b"%PDF-1.3\n"
        b"%\x93\x8c\x8b\x9e ReportLab Generated PDF document http://www.reportlab.com\n"
        b"1 0 obj\n"
        b"<<\n"
        b"/Type /Catalog\n"
        b"/Pages 2 0 R\n"
        b">>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<<\n"
        b"/Type /Pages\n"
        b"/Count 1\n"
        b"/Kids [ 3 0 R ]\n"
        b">>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<<\n"
        b"/Type /Page\n"
        b"/Contents 4 0 R\n"
        b"/MediaBox [ 0 0 612 792 ]\n"
        b">>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< /Length 44 >>\n"
        b"stream\n"
        b"BT /F1 12 Tf 72 720 Td (Python Developer Resume) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f\n"
        b"0000000015 00000 n\n"
        b"0000000066 00000 n\n"
        b"0000000127 00000 n\n"
        b"0000000205 00000 n\n"
        b"trailer\n"
        b"<<\n"
        b"/Root 1 0 R\n"
        b"/Size 5\n"
        b">>\n"
        b"startxref\n"
        b"301\n"
        b"%%EOF\n"
    )

    files = {
        "file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    
    data = {
        "job_description": "Python developer position",
        "use_ocr": "false"
    }

    response = client.post(
        "/api/resume/analyze-resume/",
        headers={k:v for k,v in auth_headers.items() if k.lower() != "content-type"},
        files=files,
        data=data
    )
    
    assert response.status_code == 200, f"Analysis failed: {response.text}"
    result = response.json()
    assert "analysis_id" in result

def test_report_generation(client, auth_headers):
    """Test report generation"""
    # Use more complete PDF content for consistent parsing
    pdf_content = (
        b"%PDF-1.3\n"
        b"%\x93\x8c\x8b\x9e ReportLab Generated PDF document http://www.reportlab.com\n"
        b"1 0 obj\n"
        b"<<\n"
        b"/Type /Catalog\n"
        b"/Pages 2 0 R\n"
        b">>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<<\n"
        b"/Type /Pages\n"
        b"/Count 1\n"
        b"/Kids [ 3 0 R ]\n"
        b">>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<<\n"
        b"/Type /Page\n"
        b"/Contents 4 0 R\n"
        b"/MediaBox [ 0 0 612 792 ]\n"
        b">>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< /Length 44 >>\n"
        b"stream\n"
        b"BT /F1 12 Tf 72 720 Td (Python Developer Resume) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f\n"
        b"0000000015 00000 n\n"
        b"0000000066 00000 n\n"
        b"0000000127 00000 n\n"
        b"0000000205 00000 n\n"
        b"trailer\n"
        b"<<\n"
        b"/Root 1 0 R\n"
        b"/Size 5\n"
        b">>\n"
        b"startxref\n"
        b"301\n"
        b"%%EOF\n"
    )
    
    files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    analyze_response = client.post(
        "/api/resume/analyze-resume/",
        headers={k:v for k,v in auth_headers.items() if k.lower() != "content-type"},
        files=files,
        data={"use_ocr": "false"}
    )
    
    assert analyze_response.status_code == 200, f"Analysis creation failed: {analyze_response.text}"
    analysis_id = analyze_response.json()["analysis_id"]
    
    response = client.get(
        f"/api/resume/generate-pdf-report/?analysis_id={analysis_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"].lower()
    assert len(response.content) > 0

def test_invalid_file_type(client, auth_headers):
    """Test invalid file handling"""
    files = {
        "file": ("test.xyz", io.BytesIO(b"invalid"), "application/octet-stream")
    }
    
    response = client.post(
        "/api/resume/analyze-resume/",
        headers={k:v for k,v in auth_headers.items() if k.lower() != "content-type"},
        files=files
    )
    
    assert response.status_code == 400
    error_detail = response.json()["detail"].lower()
    assert any(msg in error_detail for msg in ["unsupported", "invalid", "xyz"])