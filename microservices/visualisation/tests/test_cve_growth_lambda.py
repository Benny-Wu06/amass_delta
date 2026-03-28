import json
from unittest.mock import MagicMock, patch
from datetime import datetime, date

from src.cve_growth.cve_growth_lambda import cve_growth_lambda

# Helper Function: create a mock DB setup
def setup_mock_db(mock_get_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    return mock_conn, mock_cur

# TEST 1: SUCCESSFUL RETURN
@patch("src.cve_growth.cve_growth_lambda.get_db_connection")
def test_cve_growth_success(mock_get_db):
    mock_conn, mock_cur = setup_mock_db(mock_get_db)
    
    # simulate the fetch_company_id result
    mock_cur.fetchone.return_value = (101,)

    # simulate the fetch_vulnerability_data result
    mock_cur.fetchall.return_value = [
        (date(2026, 3, 21), 0),
        (date(2026, 3, 22), 3),
        (date(2026, 3, 23), 1),
        (date(2026, 3, 24), 0),
        (date(2026, 3, 25), 1),
        (date(2026, 3, 26), 2)
    ]

    event = {
        "pathParameters": {"company_name": "AcmeCorp"},
        "queryStringParameters": {"days": "4"}
    }

    # use patch to "freeze" time for consistent testing
    with patch("src.cve_growth.cve_growth_lambda.datetime") as mock_date:
        # set "today" to March 26, 2026
        mock_date.now.return_value = datetime(2026, 3, 26)
        mock_date.strftime = datetime.strftime
        
        response = cve_growth_lambda(event, None)


    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["summary"]["total_period_increase"] == 4
    assert body["summary"]["peak_growth_day"] == "2026-03-26"
    mock_conn.close.assert_called_once()

# TEST 2: INVALID DAYS
@patch("src.cve_growth.cve_growth_lambda.get_db_connection")
def test_cve_growth_invalid_days(mock_get_db):
    setup_mock_db(mock_get_db)

    event = {
        "pathParameters": {"company_name": "AcmeCorp"},
        "queryStringParameters": {"days": "0"}
    }

    response = cve_growth_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert "error" in body
    assert "Days has to be greater than zero" in body["error"]

# TEST 3: MISSING COMPANY NAME
@patch("src.cve_growth.cve_growth_lambda.get_db_connection")
def test_cve_growth_missing_company(mock_get_db):
    setup_mock_db(mock_get_db)

    event = {
        "pathParameters": {}, # Missing company_name
        "queryStringParameters": {"days": "7"}
    }

    response = cve_growth_lambda(event, None)
    
    assert response["statusCode"] == 404
    assert "not found" in json.loads(response["body"])["error"]

# TEST 4: COMPANY NOT IN DB (The 404 Logic)
@patch("src.cve_growth.cve_growth_lambda.get_db_connection")
def test_cve_growth_company_not_found(mock_get_db):
    mock_conn, mock_cur = setup_mock_db(mock_get_db)
    # Simulate fetch_company_id returning nothing
    mock_cur.fetchone.return_value = None 

    event = {
        "pathParameters": {"company_name": "FakeCorp"},
        "queryStringParameters": {"days": "7"}
    }
    response = cve_growth_lambda(event, None)
    assert response["statusCode"] == 404
    assert "not found" in json.loads(response["body"])["error"]
    mock_conn.close.assert_called_once()

# TEST 5: DATABASE CONNECTION ERROR
@patch("src.cve_growth.cve_growth_lambda.get_db_connection")
def test_cve_growth_db_failure(mock_get_db):
    # simulate the DB driver throwing an exception
    mock_get_db.side_effect = Exception("Connection Timeout")

    event = {
        "pathParameters": {"company_name": "AcmeCorp"}
    }

    response = cve_growth_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 500
    assert body["error"] == "Connection Timeout"
