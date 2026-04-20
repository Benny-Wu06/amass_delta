import sys
import os
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

with patch("boto3.client"):
    from listAllSubscriptions import lambda_handler, list_watchlists


def test_missing_email():
    response = lambda_handler({}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


def test_invalid_email_no_at():
    response = lambda_handler({"queryStringParameters": {"email": "notanemail"}}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


def test_email_is_lowercased():
    with patch("listAllSubscriptions.list_watchlists") as mock_list:
        mock_list.return_value = {"statusCode": 200, "body": "{}"}
        lambda_handler({"queryStringParameters": {"email": "TEST@GMAIL.COM"}}, None)
        mock_list.assert_called_once_with("test@gmail.com")


@patch("listAllSubscriptions.get_db_connection")
def test_returns_empty_watchlists(mock_conn):
    cur = MagicMock()
    cur.fetchall.return_value = []
    mock_conn.return_value.cursor.return_value = cur

    response = list_watchlists("test@gmail.com")
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["email"] == "test@gmail.com"
    assert body["watchlists"] == []


@patch("listAllSubscriptions.get_db_connection")
def test_returns_watchlists_with_company_counts(mock_conn):
    cur = MagicMock()
    cur.fetchall.return_value = [
        (1, "Tech List", datetime(2024, 1, 1), 3),
        (2, "Finance", datetime(2024, 2, 1), 0),
    ]
    mock_conn.return_value.cursor.return_value = cur

    response = list_watchlists("test@gmail.com")
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body["watchlists"]) == 2
    assert body["watchlists"][0]["id"] == 1
    assert body["watchlists"][0]["name"] == "Tech List"
    assert body["watchlists"][0]["company_count"] == 3
    assert body["watchlists"][1]["company_count"] == 0


@patch("listAllSubscriptions.get_db_connection")
def test_db_exception_returns_500(mock_conn):
    mock_conn.side_effect = Exception("DB error")

    response = list_watchlists("test@gmail.com")
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"error": "Failed to retrieve watchlists"}


@patch("listAllSubscriptions.get_db_connection")
def test_response_has_content_type_header(mock_conn):
    cur = MagicMock()
    cur.fetchall.return_value = []
    mock_conn.return_value.cursor.return_value = cur

    response = list_watchlists("test@gmail.com")
    assert response.get("headers", {}).get("Content-Type") == "application/json"