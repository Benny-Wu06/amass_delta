import sys
import os
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

with patch("boto3.client"):
    from addSubscription import lambda_handler, make_event, add_company_to_watchlist


def test_missing_watchlist_id():
    response = lambda_handler({}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Watchlist id is required in URL"}


def test_non_integer_watchlist_id():
    response = lambda_handler(make_event(watchlist_id="abc"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Watchlist id must be an integer"}


def test_missing_body():
    response = lambda_handler(make_event(watchlist_id="1"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Request body is required"}


def test_invalid_json_body():
    event = make_event(watchlist_id="1")
    event["body"] = "not-json"
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Invalid JSON body"}


def test_missing_email():
    response = lambda_handler(
        make_event(watchlist_id="1", body={"company_name": "Timmy Blud"}), None
    )
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


def test_invalid_email_no_at():
    response = lambda_handler(
        make_event(watchlist_id="1", body={"email": "notanemail", "company_name": "Timmy Blud"}), None
    )
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


def test_missing_company_name():
    response = lambda_handler(
        make_event(watchlist_id="1", body={"email": "test@gmail.com"}), None
    )
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Company name is required"}


@patch("addSubscription.get_db_connection")
def test_watchlist_not_found(mock_conn):
    cur = MagicMock()
    cur.fetchone.return_value = None
    mock_conn.return_value.__enter__ = MagicMock(return_value=mock_conn.return_value)
    mock_conn.return_value.cursor.return_value = cur

    resp = add_company_to_watchlist(1, "test@gmail.com", "Timmy Blud")
    assert resp["statusCode"] == 400
    assert "Watchlist not found" in json.loads(resp["body"])["error"]


@patch("addSubscription.get_db_connection")
def test_company_already_in_watchlist(mock_conn):
    cur = MagicMock()
    cur.fetchone.side_effect = [(1,), None]
    mock_conn.return_value.cursor.return_value = cur

    resp = add_company_to_watchlist(1, "test@gmail.com", "Timmy Blud")
    assert resp["statusCode"] == 400
    assert "already in this watchlist" in json.loads(resp["body"])["error"]


@patch("addSubscription.get_db_connection")
def test_successful_add(mock_conn):
    cur = MagicMock()
    cur.fetchone.side_effect = [(1,), (42, datetime(2024, 1, 1))]
    mock_conn.return_value.cursor.return_value = cur

    resp = add_company_to_watchlist(1, "test@gmail.com", "Timmy Blud")
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["id"] == 42
    assert body["company_name"] == "Timmy Blud"
    assert body["watchlist_id"] == 1
    mock_conn.return_value.commit.assert_called_once()


@patch("addSubscription.get_db_connection")
def test_db_exception_returns_500(mock_conn):
    mock_conn.side_effect = Exception("DB error")

    resp = add_company_to_watchlist(1, "test@gmail.com", "Timmy Blud")
    assert resp["statusCode"] == 500
    assert "Internal server error" in json.loads(resp["body"])["error"]