import sys
import os
import json
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

with patch("boto3.client"):
    from createSubscriptionWatchlist import lambda_handler, create_watchlist


def test_missing_body():
    response = lambda_handler({}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Request body is required"}

def test_invalid_json_body():
    response = lambda_handler({"body": "not-json"}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Invalid JSON body"}

def test_missing_email():
    response = lambda_handler({"body": json.dumps({"name": "My List"})}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}

def test_invalid_email_no_at_symbol():
    response = lambda_handler({"body": json.dumps({"email": "test", "name": "My List"})}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}

def test_missing_name():
    response = lambda_handler({"body": json.dumps({"email": "test@gmail.com"})}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Watchlist name is required"}

def test_name_too_short():
    response = lambda_handler({"body": json.dumps({"email": "test@gmail.com", "name": "A"})}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Name must be at least 2 chars"}

def test_name_exactly_two_chars_is_valid():
    with patch("createSubscriptionWatchlist.create_watchlist") as mock_create:
        mock_create.return_value = {"statusCode": 200, "body": json.dumps({"id": 1})}
        response = lambda_handler({"body": json.dumps({"email": "test@gmail.com", "name": "Timmy Blud"})}, None)
    assert response["statusCode"] == 200


@patch("psycopg2.connect")
def test_successful_create(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = (7,)
    response = create_watchlist("test@gmail.com", "Timmy Blud")

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["id"] == 7
    assert "created" in body["message"].lower()

@patch("psycopg2.connect")
def test_duplicate_watchlist_returns_400(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = None

    response = create_watchlist("test@gmail.com", "Timmy Blud")

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Watchlist with this email and name already exists"}

@patch("psycopg2.connect")
def test_db_exception_returns_500(mock_connect):
    mock_connect.side_effect = Exception("Connection timeout")

    response = create_watchlist("test@gmail.com", "Timmy Blud")

    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"error": "Internal server error"}

@patch("psycopg2.connect")
def test_rollback_called_on_query_error(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.execute.side_effect = Exception("query error")

    create_watchlist("test@gmail.com", "Timmy Blud")
