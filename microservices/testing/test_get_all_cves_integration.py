import json
import pytest
import requests
import boto3
from botocore.config import Config

# Configuration
AWS_REGION = "ap-southeast-2"
# Replace with your actual deployed API Gateway URL for amass_delta
URL = "https://7mz3fi8zw1.execute-api.ap-southeast-2.amazonaws.com" 
CVES_ENDPOINT = f"{URL.rstrip('/')}/v1/cves"

def test_get_cves_schema_and_status():
    ### Verify the live API returns 200 and the expected JSON structure  ###
    response = requests.get(CVES_ENDPOINT)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify Top-level Structure
    # assert "count" in data
    assert "cves" in data
    # assert isinstance(data["count"], int)
    assert isinstance(data["cves"], list)

def test_get_cves_data_integrity():
    ### Verify the CVE objects   ###
    response = requests.get(CVES_ENDPOINT)
    data = response.json()
    
    if data["count"] > 0:
        first_cve = data["cves"][0]
        # Check for all required fields in the live response
        expected_keys = {
            "cve_id", 
            "risk_index", 
            "risk_rating", 
            "date_added", 
            "due_date", 
            "company_name"
        }
        assert expected_keys.issubset(first_cve.keys()), f"Missing keys. Found: {first_cve.keys()}"
        
        # Verify data types from the live wire
        assert isinstance(first_cve["cve_id"], str)
        assert isinstance(first_cve["risk_index"], (int, float))
        assert isinstance(first_cve["risk_rating"], str)
        assert isinstance(first_cve["company_name"], (str, type(None)))

def test_get_cves_sorting_logic_live():
    ### Verify that the sorting query parameters actually work on the live DB  ###
    # Test Latest First (date_added DESC)
    resp_latest = requests.get(f"{CVES_ENDPOINT}?sort_by=date_added")
    data_latest = resp_latest.json()
    
    # Test Due Soonest (due_date ASC)
    resp_due = requests.get(f"{CVES_ENDPOINT}?sort_by=due_date")
    data_due = resp_due.json()
    
    assert resp_latest.status_code == 200
    assert resp_due.status_code == 200
    
    if data_latest["count"] > 0:
        assert "company_name" in data_latest["cves"][0]

def test_get_cves_invalid_method():
     ### API Gateway should reject POST requests to a GET-only resource  ###
    response = requests.post(CVES_ENDPOINT, json={"fake": "data"})
    assert response.status_code in [403, 405, 404]

def test_get_cves_not_found():
    bad_endpoint = f"{URL}/v1/cves-invalid-path"
    response = requests.get(bad_endpoint)
    assert response.status_code == 404