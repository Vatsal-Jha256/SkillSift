"""
Script to test privacy endpoints
"""

import requests
import json
import os
from fastapi.testclient import TestClient
import logging

from app.main import app
from app.core.logging import logger

def test_privacy_endpoints():
    """
    Test privacy-related endpoints
    """
    logger.info("Testing privacy endpoints")
    
    # Create a test client
    client = TestClient(app)
    
    # Test the privacy policy endpoint
    response = client.get("/api/privacy/privacy-policy")
    assert response.status_code == 200, f"Privacy policy endpoint failed: {response.text}"
    data = response.json()
    assert "privacy_policy" in data, "Privacy policy missing in response"
    logger.info("Privacy policy endpoint works")
    
    # Test the data retention policy endpoint
    response = client.get("/api/privacy/data-retention")
    assert response.status_code == 200, f"Data retention policy endpoint failed: {response.text}"
    data = response.json()
    assert "resume_data" in data, "Data retention policy missing resume_data"
    assert "user_data" in data, "Data retention policy missing user_data"
    logger.info("Data retention policy endpoint works")
    
    # Test authentication for protected endpoints
    response = client.post("/api/privacy/delete-data")
    assert response.status_code == 401, "Unauthenticated request should be rejected"
    logger.info("Authentication check for privacy endpoints works")
    
    logger.info("All privacy endpoint tests completed successfully")

if __name__ == "__main__":
    test_privacy_endpoints() 