import json
import pytest
import os
from unittest.mock import MagicMock, patch
from microservices.integration.src.get_news_lambda import get_news_lambda

# Path to the module for patching requests
LAMBDA_PATH = "microservices.integration.src.get_news_lambda"

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Ensure environment variables exist for all tests."""
    with patch.dict(os.environ, {
        "CHARLIE_EMAIL": "dearryllan@gmail.com",
        "CHARLIE_PASSWORD": "mypassword"
    }):
        yield

# TEST 1: SUCCESSFUL NEWS FETCH
@patch(f"{LAMBDA_PATH}.requests.post")
@patch(f"{LAMBDA_PATH}.requests.get")
def test_integration_success(mock_get, mock_post):
    # setup Charlie auth mock
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        'authentication': {'IdToken': 'mock_token'}
    }

    # setup CHARLIE news retrieval response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "ticker": "AAPL",
        "count": 1,
        "data": [
            {
                "title": "Tech Growth in 2026", 
                "overall_sentiment_label": "Neutral",
                "summary": "Example summary text...",
                "url": "https://example.com"
            }
        ]
    }

    event = {
        "pathParameters": {"company_symbol": "AAPL"},
        "queryStringParameters": {
            "start_date": "2025-01-01", 
            "end_date": "2025-01-02",
            "limit": "10",
            "sentiment": "neutral"
        }
    }

    response = get_news_lambda(event, None)
    assert response["statusCode"] == 200
    
    body = json.loads(response["body"])
    assert body["company"] == "Apple"
    assert body["symbol"] == "AAPL"
    assert len(body["news_data"]) == 1
    assert body["news_data"][0]["overall_sentiment_label"] == "Neutral"

# TEST 2: UNSUPPORTED COMOPANY SYMBOL (404)
def test_integration_invalid_symbol():
    event = {
        "pathParameters": {"company_symbol": "DOGE"},
    }

    response = get_news_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 404
    assert "Invalid symbol" in body["error"]

# TEST 3: INVALID DATE RANGE (400)
def test_integration_invalid_dates():
    event = {
        "pathParameters": {"company_symbol": "AAPL"},
        "queryStringParameters": {
            "start_date": "2026-05-01",
            "end_date": "2026-04-01"
        }
    }

    response = get_news_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert "date must be before" in body["error"]

# TEST 4: INVALID SENTIMENT VALUE (400)
def test_integration_invalid_sentiment():
    event = {
        "pathParameters": {"company_symbol": "MSFT"},
        "queryStringParameters": {
            "sentiment": "bullish"
        }
    }

    response = get_news_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert "Invalid sentiment" in body["error"]

# TEST 5: EXTERNAL API FAILURE (Charlie API Auth Down)
@patch(f"{LAMBDA_PATH}.requests.post")
def test_integration_external_auth_failure(mock_post):
    # simulate a network crash
    mock_post.side_effect = Exception("Connection Timeout to Charlie")

    event = {
        "pathParameters": {"company_symbol": "GOOGL"}
    }

    response = get_news_lambda(event, None)
    body = json.loads(response["body"])
    
    assert response["statusCode"] == 500
    assert "Internal Server Error" in body["error"]
    assert "Connection Timeout" in body["details"]

# TEST 6: LIMIT CLAMPING AND PASS-THROUGH
@patch(f"{LAMBDA_PATH}.requests.post")
@patch(f"{LAMBDA_PATH}.requests.get")
def test_integration_limit_clamping(mock_get, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'authentication': {'IdToken': 't'}}

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": []}

    event = {
        "pathParameters": {"company_symbol": "META"},
        "queryStringParameters": {"limit": "999"}
    }

    get_news_lambda(event, None)
    
    # check the call_args to verify the parameters passed to Charlie
    _, kwargs = mock_get.call_args
    assert kwargs['params']['limit'] == 200
    # should be default value
    assert kwargs['params']['start_date'] == "2025-01-01"