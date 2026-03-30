import pytest
import pytest_mock
from microservices.data_retrieval.src.vulnerability_info import lambda_handler as vuln_info 
import json

# class to expect any string instead of having to match date at runtime.
class AnyString():
    def __eq__(self, value):
        return isinstance(value, str)

# given a cve_id string, return json object with vulnerability info.
def test_correct_cve_id(mocker):
    mock_connect = mocker.patch('src.vulnerability_info.psycopg2.connect')

    mock_cursor = mock_connect.return_value.cursor.return_value

    mock_expected_data = ("CVE-2021-22175", "GitLab Server-Side Request Forgery (SSRF) Vulnerability", "GitLab contains a server-side request forgery (SSRF) vulnerability when requests to the internal network for webhooks are enabled.",
                          "2026-02-18", "2026-03-11", 9.8, 0.74079)
   
    mock_cursor.fetchone.return_value = mock_expected_data

    test_input = {"pathParameters": {
        "cve_id": "CVE-2021-22175"
    }}

    response = vuln_info(test_input, None)

    assert response["statusCode"] == 200
    actual_body = json.loads(response["body"])
    expected_response_body = {
        "cve_id": "CVE-2021-22175",
        "name": "GitLab Server-Side Request Forgery (SSRF) Vulnerability",
        "description": "GitLab contains a server-side request forgery (SSRF) vulnerability when requests to the internal network for webhooks are enabled.",
        "dateAdded": "2026-02-18",
        "dueDate": "2026-03-11",
        "cvss": 9.8,
        "epss": 0.74079,
        "risk_index": 0.8843,
        "risk_rating": 'CRITICAL',
        "time": {
            "timestamp": AnyString(),
            "timezone": AnyString()
        }
    }
    assert actual_body == expected_response_body

def test_not_found_cve():
    incorrect_test_input = {"pathParameters": {
        "cve_id": "CVE-1998-0001"
    }}
    
    response = vuln_info(incorrect_test_input, None)
    assert response["statusCode"] == 404

def test_no_param_defined():
    incorrect_test_input = {}
    response = vuln_info(incorrect_test_input, None)
    assert response["statusCode"] == 400
    assert response["body"] == '{"error": "cve_id is required in the URL"}'

def test_wrong_format_cve():
    incorrect_test_input = {"pathParameters": {
        "cve_id": "CVE-103-0001"
    }}

    response = vuln_info(incorrect_test_input, None)
    assert response["statusCode"] == 400
    assert response["body"] == '{"error": "Invalid CVE ID format"}'