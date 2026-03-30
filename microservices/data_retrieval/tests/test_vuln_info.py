import pytest
from microservices.data_retrieval.src.vulnerability_info import lambda_handler
import json

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

    response = lambda_handler(test_input, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body == {'meow': 'meow'}
