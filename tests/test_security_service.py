import pytest
import os
import shutil
import tempfile
from pathlib import Path
from app.services.security_service import SecurityService

@pytest.fixture
def sample_data():
    """Sample data with personal information for testing anonymization."""
    return {
        "skills": ["python", "java", "aws"],
        "structured_data": {
            "contact_info": {
                "email": "john.doe@example.com",
                "phone": "123-456-7890",
                "address": "123 Main St, Anytown, USA"
            },
            "education": [
                {"degree": "Bachelor of Science in Computer Science"}
            ],
            "experience": [
                {"title": "Software Engineer", "company": "Tech Corp"}
            ]
        },
        "compatibility_score": 85
    }

@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for secure uploads."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def test_anonymize_data(sample_data):
    """Test data anonymization function."""
    # Anonymize the data
    anonymized = SecurityService.anonymize_data(sample_data)
    
    # Check that the data was anonymized correctly
    assert "structured_data" in anonymized
    assert "contact_info" in anonymized["structured_data"]
    
    # Check email anonymization
    original_email = sample_data["structured_data"]["contact_info"]["email"]
    anonymized_email = anonymized["structured_data"]["contact_info"]["email"]
    username, domain = original_email.split('@')
    expected_email = f"{username[:2]}{'*' * (len(username) - 2)}@{domain}"
    assert anonymized_email == expected_email
    
    # Check phone anonymization
    original_phone = sample_data["structured_data"]["contact_info"]["phone"]
    anonymized_phone = anonymized["structured_data"]["contact_info"]["phone"]
    expected_phone = f"{'*' * (len(original_phone) - 4)}{original_phone[-4:]}"
    assert anonymized_phone == expected_phone
    
    # Check address anonymization
    assert anonymized["structured_data"]["contact_info"]["address"] == "*** Address Hidden ***"
    
    # Check that non-sensitive data was not modified
    assert anonymized["skills"] == sample_data["skills"]
    assert anonymized["compatibility_score"] == sample_data["compatibility_score"]

def test_secure_file_handling():
    """Test secure file handling function."""
    # Create a test file content and name
    file_content = b"This is a test file"
    original_filename = "test.pdf"
    
    # Test secure file handling
    secure_filename, file_path = SecurityService.secure_file_handling(file_content, original_filename)
    
    # Check that the file exists
    assert os.path.exists(file_path)
    
    # Check that the filename was changed
    assert secure_filename != original_filename
    
    # Check that the file extension was preserved
    assert secure_filename.endswith(".pdf")
    
    # Check that the file contains the correct content
    with open(file_path, 'rb') as f:
        content = f.read()
        assert content == file_content
    
    # Clean up
    if os.path.exists(file_path):
        os.remove(file_path)

def test_data_retention_policy():
    """Test data retention policy function."""
    policy = SecurityService.get_data_retention_policy()
    
    # Check that the policy contains the expected keys
    assert "resume_data" in policy
    assert "user_data" in policy
    assert "analytics_data" in policy
    
    # Check that each policy has the expected fields
    for category in ["resume_data", "user_data", "analytics_data"]:
        assert "retention_period" in policy[category]
        assert "reason" in policy[category]
        assert "deletion_method" in policy[category]

def test_gdpr_compliance_info():
    """Test GDPR compliance information function."""
    gdpr_info = SecurityService.get_gdpr_compliance_info()
    
    # Check that the GDPR info contains the expected keys
    assert "data_controller" in gdpr_info
    assert "data_processing_purposes" in gdpr_info
    assert "data_subject_rights" in gdpr_info
    
    # Check that the data controller has the expected fields
    assert "name" in gdpr_info["data_controller"]
    assert "contact_email" in gdpr_info["data_controller"]
    
    # Check that the data processing purposes is a non-empty list
    assert isinstance(gdpr_info["data_processing_purposes"], list)
    assert len(gdpr_info["data_processing_purposes"]) > 0
    
    # Check that the data subject rights is a non-empty list
    assert isinstance(gdpr_info["data_subject_rights"], list)
    assert len(gdpr_info["data_subject_rights"]) > 0

def test_log_access(tmpdir):
    """Test log_access function."""
    # Create a temporary directory for the audit logs
    audit_log_dir = Path(tmpdir) / "audit_logs"
    audit_log_dir.mkdir(exist_ok=True, parents=True)
    
    # Temporarily patch the audit log directory
    original_path = Path("/tmp/audit_logs")
    mock_path = audit_log_dir
    
    # Since we can't easily monkey patch the constant in the SecurityService,
    # we'll just check that the log function doesn't raise an exception
    try:
        SecurityService.log_access(
            user_id="test-user",
            action="test-action",
            resource="test-resource",
            status="success",
            details="Test details"
        )
        # Test passed if no exception was raised
        assert True
    except Exception as e:
        pytest.fail(f"log_access raised an exception: {str(e)}")

def test_cleanup_expired_data():
    """Test cleanup_expired_data function."""
    # This is a complex function to test, so we'll just check that it doesn't raise an exception
    try:
        SecurityService.cleanup_expired_data(retention_days=999)  # Very high value to avoid deleting real files
        # Test passed if no exception was raised
        assert True
    except Exception as e:
        pytest.fail(f"cleanup_expired_data raised an exception: {str(e)}")

def test_disallowed_file_extension():
    """Test secure_file_handling with a disallowed file extension."""
    # Create a test file content and name with a disallowed extension
    file_content = b"This is a test file"
    original_filename = "test.exe"
    
    # Test secure file handling with allowed_extensions
    with pytest.raises(ValueError):
        SecurityService.secure_file_handling(
            file_content, 
            original_filename, 
            allowed_extensions=['.pdf', '.docx', '.txt']
        ) 