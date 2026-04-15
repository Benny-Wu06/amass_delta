import json
import pytest
import requests
import boto3
import psycopg2
from botocore.config import Config
from decimal import Decimal

AWS_REGION = "ap-southeast-2"
URL = "https://7mz3fi8zw1.execute-api.ap-southeast-2.amazonaws.com"
FUNCTION_NAME = "get_all_companies_service"
COMPANIES_ENDPOINT = f"{URL.rstrip('/')}/v1/companies"

lambda_client = boto3.client(
    "lambda",
    region_name=AWS_REGION,
    config=Config(read_timeout=30, connect_timeout=10),
)


def test_get_companies_schema():
    ### Verify the response has the correct keys and data types ###
    endpoint = f"{URL}/v1/companies"
    response = requests.get(COMPANIES_ENDPOINT)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify Structure
    assert "count" in data
    assert "companies" in data
    assert isinstance(data["count"], int)
    assert isinstance(data["companies"], list)

def test_get_companies_content():
    ### Verify specific known data exists in the production/staging database ###
    response = requests.get(COMPANIES_ENDPOINT)
    data = response.json()
    
    assert data["count"] > 0
    # Check for a few major players you saw in your manual test
    expected_samples = ["7-Zip", "Adobe", "Microsoft", "Zyxel"]
    for company in expected_samples:
        assert company in data["companies"], f"Expected {company} to be in the list"

def test_api_invalid_method():
    endpoint = f"{URL}/v1/companies"

    response = requests.post(COMPANIES_ENDPOINT, json={"test": "data"})
    assert response.status_code == 404

def test_api_not_found():
    endpoint = f"{URL}/v1/non-existent-route"
    response = requests.get(endpoint)
    assert response.status_code == 404