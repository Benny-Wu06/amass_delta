import json
import pytest
import requests
import boto3
from botocore.config import Config
from decimal import Decimal

AWS_REGION = "ap-southeast-2"
URL = "https://7mz3fi8zw1.execute-api.ap-southeast-2.amazonaws.com/"
FUNCTION_NAME = "company_vulnerabilities_service"

lambda_client = boto3.client(
    "lambda",
    region_name=AWS_REGION,
    config=Config(read_timeout=30, connect_timeout=10),
)


class TestVulnerabilityRetrievalComponent:
    ##  Tests the Lambda directly via Boto3 (Bypasses API Gateway) ## 
    
    def test_retrieval_by_company_200(self):
        payload = {
            "pathParameters": {"company_name": "Google"}
        }
        result = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        
        parsed = json.loads(result["Payload"].read())
        assert parsed["statusCode"] == 200
        body = json.loads(parsed["body"])
        assert isinstance(body, dict)
        assert body["company"] == "Google"
        assert isinstance(body["vulnerabilities"], list)
        assert len(body["vulnerabilities"]) > 0

    def test_retrieval_by_company_200_1_filter(self):
        payload = {
            "pathParameters": {"company_name": "Google"},
            "queryStringParameters": {"min_cvss": "7.0"}
        }
        result = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        parsed = json.loads(result["Payload"].read())
        
        assert parsed["statusCode"] == 200
        body = json.loads(parsed["body"])
        assert isinstance(body, dict)
        assert body["company"] == "Google"
        assert isinstance(body["vulnerabilities"], list)
        assert len(body["vulnerabilities"]) > 0

    def test_retrieval_by_company_200_2_filters(self):
        payload = {
            "pathParameters": {"company_name": "Google"},
            "queryStringParameters": {"min_cvss": "7.0", "min_epss": "0.1"}
        }
        result = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        parsed = json.loads(result["Payload"].read())
        
        assert parsed["statusCode"] == 200
        body = json.loads(parsed["body"])
        assert isinstance(body, dict)
        assert body["company"] == "Google"
        assert isinstance(body["vulnerabilities"], list)
        assert len(body["vulnerabilities"]) > 0

    def test_invalid_cvss_returns_400(self):
        payload = {
            "pathParameters": {"company_name": "Google"},
            "queryStringParameters": {"min_cvss": "11.0"} # Out of range
        }
        result = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            Payload=json.dumps(payload),
        )
        parsed = json.loads(result["Payload"].read())
        assert parsed["statusCode"] == 400
        assert "min_cvss must be 0-10" in parsed["body"]

    def test_invalid_epss_returns_400(self):
        payload = {
            "pathParameters": {"company_name": "Google"},
            "queryStringParameters": {"min_epss": "11.0"} # Out of range
        }
        result = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            Payload=json.dumps(payload),
        )
        parsed = json.loads(result["Payload"].read())
        assert parsed["statusCode"] == 400
        assert "min_epss must be 0-1" in parsed["body"]

class TestVulnerabilityRetrievalIntegration:
    def _assert_full_schema(self, vuln):
        ## Helper to validate the complete schema and types for a single vulnerability ##
        expected_keys = [
            "cve_id", "name", "description", "dateAdded", 
            "dueDate", "cvss", "epss", "risk_index", 
            "risk_rating", "time"
        ]
        # Key Existence Check
        for key in expected_keys:
            assert key in vuln, f"Contract Failure: Missing key '{key}'"
        
        # Strict Type Validation
        assert isinstance(vuln["cve_id"], str)
        assert isinstance(vuln["name"], str)
        assert isinstance(vuln["cvss"], (int, float))
        assert isinstance(vuln["epss"], (int, float))
        assert isinstance(vuln["risk_index"], (int, float))
        assert isinstance(vuln["risk_rating"], str)
        
        # Nested Object Validation
        assert "timestamp" in vuln["time"]
        assert vuln["time"]["timezone"] == "UTC"

    ## Tests the End-to-End flow via API Gateway ## 
    def test_get_request_success_no_filter(self):
        endpoint = f"{URL}/v1/companies/Google/vulnerabilities"
        response = requests.get(endpoint, timeout=30)
        assert response.status_code == 200

        data = response.json()

        # verify structure
        assert data["company"] == "Google"
        assert isinstance(data["cve_count"], int)
        assert "timezone" in data["time"]

        # Full Schema & Type Validation 
        if data["cve_count"] > 0:
            for vuln in data["vulnerabilities"]:
                self._assert_full_schema(vuln)

    def test_get_request_success_1_filter(self):
        endpoint = f"{URL}/v1/companies/Google/vulnerabilities"
        response = requests.get(endpoint, params={"min_cvss": "5.0"}, timeout=30)
        assert response.status_code == 200
        
        data = response.json()

        assert data["cve_count"] == len(data["vulnerabilities"])

        if data["cve_count"] > 0:
            for vuln in data["vulnerabilities"]:
                
                assert float(vuln["cvss"]) >= 5.0
                # Full Schema Check
                self._assert_full_schema(vuln)
    

    def test_get_request_success_2_filters(self):
        endpoint = f"{URL}/v1/companies/Google/vulnerabilities"
        response = requests.get(endpoint, params={"min_cvss": "5.0", "min_epss": "0.5"}, timeout=30)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        
        data = response.json()
        
        if data["cve_count"] > 0:
            for vuln in data["vulnerabilities"]:
                
                assert float(vuln["cvss"]) >= 7.0
                assert float(vuln["epss"]) >= 0.1
                # Full Schema Check
                self._assert_full_schema(vuln)
        
    def test_404_on_missing_route(self):
        # Testing a route that shouldn't exist
        response = requests.get(f"{URL}/v1/wrong_path")
        assert response.status_code in [403, 404] 