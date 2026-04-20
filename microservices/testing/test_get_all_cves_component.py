import json
import os, sys
from unittest.mock import patch, MagicMock
from datetime import date
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'data_retrieval', 'src'))
sys.path.insert(0, src_path)
from get_all_cves import lambda_handler

@patch('psycopg2.connect')
def test_lambda_contract_success(mock_connect):
    ###  Verifies the full contract: Event Input -> Lambda -> API Gateway Compatible Output ### 

    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = [
        ("CVE-2026-0001", "Heartbleed 2.0", "Critical vuln", 9.8, 0.95, "Critical", date(2026, 4, 1), date(2026, 5, 1), "Google")
    ]

    # Simulate a real API Gateway Event
    event = {
        "queryStringParameters": {"sort_by": "date_added"},
        "requestContext": {"stage": "prod"}
    }

    # Execute
    response = lambda_handler(event, None)

    # Component Assertions
    assert "statusCode" in response
    assert response["statusCode"] == 200
    
    # Verify Headers (Critical for CORS and Frontend integration)
    assert response["headers"]["Content-Type"] == "application/json"
    
    # Verify Body is a valid JSON string
    body = json.loads(response["body"])
    assert body["count"] == 1
    
    
    first_cve = body["cves"][0]
    assert first_cve["cve_id"] == "CVE-2026-0001"
    assert first_cve["vulnerability_name"] == "Heartbleed 2.0"
    assert first_cve["severity"] == "Critical"
    assert first_cve["company_name"] == "Google"

@patch('psycopg2.connect')
def test_lambda_default_behavior_no_params(mock_connect):
    ### Verifies the component handles a missing queryStringParameters key (default behavior) ### 
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = []

    for event in [{"queryStringParameters": None}, {}]:
        response = lambda_handler(event, None)
        assert response["statusCode"] == 200
        
        actual_query = mock_cur.execute.call_args[0][0]
        assert "v.cvss_severity" in actual_query
        assert "ORDER BY v.date_added DESC" in actual_query

def test_lambda_missing_env_vars():
    ###  Verifies the component handles system/env failures gracefully ### 

    with patch.dict(os.environ, {}, clear=True):
        event = {"queryStringParameters": {}}
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert "error" in body