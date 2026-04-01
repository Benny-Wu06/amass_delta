import pytest
import pytest_mock
from microservices.data_retrieval.src.company_summary import lambda_handler as company_summary 
import json

# class to expect any string instead of having to match date at runtime.
class AnyString():
    def __eq__(self, value):
        return isinstance(value, str)

# given a company_name, return json object with summary about a company.
def test_success_summary(mocker):
    mock_connect = mocker.patch('src.vulnerability_info.psycopg2.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    mock_expected_data = ("GitLab", 4, 9.275, 0.791, 0.8729, 'CRITICAL')
    mock_cursor.fetchone.return_value = mock_expected_data

    test_input = {"pathParameters": {
        "company_name": "GitLab"
    }}

    response = company_summary(test_input, None)

    assert response["statusCode"] == 200
    actual_body = json.loads(response["body"])
    expected_response_body = {
        "company": "GitLab",
        "cve_count": 4,
        "avg_epss": 0.791,
        "avg_cvss": 9.275,
        "risk_index": 0.8729,
        "risk_rating": "CRITICAL",
        "time": {
            "timestamp": AnyString(),
            "timezone": AnyString()
        }
    }
    assert actual_body == expected_response_body

def test_not_found_company(mocker):
    incorrect_test_input = {"pathParameters": {
        "company_name": "diddyblud_company"
    }}
    
    mock_connect = mocker.patch('src.vulnerability_info.psycopg2.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    mock_expected_data = None
    mock_cursor.fetchone.return_value = mock_expected_data

    response = company_summary(incorrect_test_input, None)
    assert response["statusCode"] == 404
    assert response["body"] == '{"error": "Company not found"}'

def test_no_param_defined():
    incorrect_test_input = {}
    response = company_summary(incorrect_test_input, None)
    assert response["statusCode"] == 400
    assert response["body"] == '{"error": "Company name is required in the URL"}'

# note that db can store company names with spaces - need to account for this as 
# url cannot take whitespace.

# TODO: write integration test since this can only really be tested there
def test_company_name_whitespace(mocker):
    mock_connect = mocker.patch('src.vulnerability_info.psycopg2.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    mock_expected_data = ("GitLab", 4, 9.275, 0.791, 0.8729, 'CRITICAL')
    mock_cursor.fetchone.return_value = mock_expected_data

    test_input = {"pathParameters": {
        "company_name": "Sierra Wireless"
    }}

    response = company_summary(test_input, None)
    assert response["statusCode"] == 200