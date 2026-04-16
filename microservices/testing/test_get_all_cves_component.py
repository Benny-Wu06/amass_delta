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
        ("CVE-2026-0001", 9.8, "Critical", date(2026, 4, 1), date(2026, 5, 1), "Google")
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
    assert "count" in body
    assert isinstance(body["cves"], list)
    assert body["cves"][0]["cve_id"] == "CVE-2026-0001"
    assert body["cves"][0]["company_name"] == "Google"

@patch('psycopg2.connect')
def test_lambda_default_behavior_no_params(mock_connect):
    ### Verifies the component handles a missing queryStringParameters key (default behavior) ### 
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = []

    event = {"queryStringParameters": None}

    response = lambda_handler(event, None)
    
    assert response["statusCode"] == 200
    expected_query = """
            SELECT 
                v.cve_id, 
                c.risk_index, 
                c.risk_rating, 
                v.date_added, 
                v.due_date,
                c.company_name
            FROM vulnerabilities v
            LEFT JOIN companies c ON v.company_id = c.id
            ORDER BY v.date_added DESC;
        """
    mock_cur.execute.assert_called_with(expected_query)

def test_lambda_missing_env_vars():
    ###  Verifies the component handles system/env failures gracefully ### 

    with patch.dict(os.environ, {}, clear=True):
        event = {"queryStringParameters": {}}
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 500
        assert "error" in json.loads(response["body"])