import json
import pytest
from unittest.mock import MagicMock, patch
from microservices.integration.stocks_cve_growth_lambda import stocks_cve_growth_lambda

# path constants
LAMBDA_PATH = "microservices.integration.stocks_cve_growth_lambda"

# setup mock DB
def setup_mock_db(mock_get_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    return mock_conn, mock_cur

# TEST 1: SUCCESSFUL INTEGRATION
@patch(f"{LAMBDA_PATH}.requests.post")
@patch(f"{LAMBDA_PATH}.requests.get")
@patch(f"{LAMBDA_PATH}.get_db_connection")
def test_integration_success(mock_get_db, mock_get, mock_post):
    mock_conn, mock_cur = setup_mock_db(mock_get_db)
    
    # setup DB mocks
    mock_cur.fetchone.return_value = (101,)
    mock_cur.fetchall.return_value = [("2026-03-01", 2)]

    # setup charlie auth mock
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'authentication': {'IdToken': 'mock_token'}}

    # setup cahrlie stocks mock
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "data": [{"date": "2026-03-01", "open": 150.0, "close": 155.0}]
    }

    event = {
        "pathParameters": {"company_symbol": "AAPL"},
        "queryStringParameters": {"from": "2026-03-01", "to": "2026-03-01"}
    }

    response = stocks_cve_growth_lambda(event, None)
    assert response["statusCode"] == 200
    
    body = json.loads(response["body"])
    assert body["company"] == "Apple"
    assert body["merged_results"][0]["price_diff"] == 5.0

# TEST 2: UNSUPPORTED SYMBOL (404)
def test_integration_invalid_symbol():
    event = {
        "pathParameters": {"company_symbol": "DOGE"},
    }

    response = stocks_cve_growth_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 404
    assert "Invalid or unsupported company symbol" in body["error"]

# TEST 3: INVALID DATE RANGE (400)
def test_integration_invalid_dates():
    event = {
        "pathParameters": {"company_symbol": "AAPL"},
        "queryStringParameters": {
            "from": "2026-04-01",
            "to": "2026-03-01" # Start after End
        }
    }

    response = stocks_cve_growth_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert "date must be before" in body["error"]

# TEST 4: EXTERNAL API FAILURE (Charlie API Down)
@patch(f"{LAMBDA_PATH}.requests.post")
def test_integration_external_auth_failure(mock_post):
    # simulate Charlie API throwing a 401 Unauthorized or 500
    mock_post.return_value.status_code = 401
    mock_post.return_value.raise_for_status.side_effect = Exception("Unauthorized")

    event = {
        "pathParameters": {"company_symbol": "AAPL"}
    }

    response = stocks_cve_growth_lambda(event, None)
    
    assert response["statusCode"] == 500
    assert "Internal Server Error" in json.loads(response["body"])["error"]

# TEST 5: INTERNAL DB FAILURE
@patch(f"{LAMBDA_PATH}.requests.get")
@patch(f"{LAMBDA_PATH}.requests.post")
@patch(f"{LAMBDA_PATH}.get_db_connection")
def test_integration_internal_db_failure(mock_get_db, mock_post, mock_get):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'authentication': {'IdToken': 't'}}
    
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": []}
    
    # amass DB Fails
    mock_get_db.side_effect = Exception("DB Connection Timeout")

    event = {"pathParameters": {"company_symbol": "AAPL"}}
    response = stocks_cve_growth_lambda(event, None)
    
    assert response["statusCode"] == 500
    assert "DB Connection Timeout" in json.loads(response["body"])["details"]