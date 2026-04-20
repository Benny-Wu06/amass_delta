import sys
import os
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

with patch("boto3.client"):
    from getSubscriptionWatchlist import lambda_handler, get_watchlist


def make_event(watchlist_id=None, email=None):
    event = {}
    if watchlist_id is not None:
        event["pathParameters"] = {"id": watchlist_id}
    if email is not None:
        event["queryStringParameters"] = {"email": email}
    return event


def test_missing_watchlist_id():
    response = lambda_handler({}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Watchlist id is required in URL"}


def test_non_integer_watchlist_id():
    response = lambda_handler(make_event(watchlist_id="abc", email="test@gmail.com"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Watchlist id must be an integer"}


def test_missing_email():
    response = lambda_handler(make_event(watchlist_id="1"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


def test_invalid_email():
    response = lambda_handler(make_event(watchlist_id="1", email="bademail"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}

@patch("getSubscriptionWatchlist.get_db_connection")
def test_watchlist_not_found_returns_404(mock_conn):
    cur = MagicMock()
    cur.fetchone.return_value = None
    mock_conn.return_value.cursor.return_value = cur

    response = get_watchlist(1, "test@gmail.com")
    assert response["statusCode"] == 404
    assert json.loads(response["body"]) == {"error": "Watchlist not found"}


@patch("getSubscriptionWatchlist.get_db_connection")
def test_successful_get_with_companies(mock_conn):
    cur = MagicMock()
    created = datetime(2026, 1, 1, 12, 0, 0)
    added = datetime(2026, 2, 1, 8, 0, 0)
    cur.fetchone.return_value = (1, "test@gmail.com", "My List", created)
    cur.fetchall.return_value = [("Timmy Blud", added, 5, 7.5, 0.3, 6.2, "HIGH")]
    mock_conn.return_value.cursor.return_value = cur

    response = get_watchlist(1, "test@gmail.com")
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["id"] == 1
    assert body["email"] == "test@gmail.com"
    assert body["name"] == "My List"
    assert len(body["companies"]) == 1
    company = body["companies"][0]
    assert company["company_name"] == "Timmy Blud"
    assert company["num_vulnerabilities"] == 5
    assert abs(company["avg_cvss"] - 7.5) < 1e-9
    assert company["risk_rating"] == "HIGH"


@patch("getSubscriptionWatchlist.get_db_connection")
def test_company_null_values_default_correctly(mock_conn):
    cur = MagicMock()
    cur.fetchone.return_value = (1, "test@gmail.com", "My List", datetime(2026, 1, 1))
    cur.fetchall.return_value = [("Timmy Blud", datetime(2026, 2, 1), None, None, None, None, None)]
    mock_conn.return_value.cursor.return_value = cur

    response = get_watchlist(1, "test@gmail.com")
    body = json.loads(response["body"])
    company = body["companies"][0]
    assert company["num_vulnerabilities"] == 0
    assert company["avg_cvss"] == 0
    assert company["avg_epss"] == 0
    assert company["risk_index"] == 0
    assert company["risk_rating"] == "UNKNOWN"


@patch("getSubscriptionWatchlist.get_db_connection")
def test_empty_watchlist(mock_conn):
    cur = MagicMock()
    cur.fetchone.return_value = (1, "test@gmail.com", "Empty", datetime(2026, 1, 1))
    cur.fetchall.return_value = []
    mock_conn.return_value.cursor.return_value = cur

    response = get_watchlist(1, "test@gmail.com")
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["companies"] == []


@patch("getSubscriptionWatchlist.get_db_connection")
def test_db_exception_returns_500(mock_conn):
    mock_conn.side_effect = Exception("DB error")

    response = get_watchlist(1, "test@gmail.com")
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"error": "Failed to retrieve watchlist"}