import sys
import os
import json
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

with patch("boto3.client"):
    from deleteSubscriptionWatchlist import lambda_handler, delete_watchlist


def make_event(watchlist_id=None, body=None):
    event = {}
    if watchlist_id is not None:
        event["pathParameters"] = {"id": watchlist_id}
    if body is not None:
        event["body"] = json.dumps(body) if isinstance(body, dict) else body
    return event


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
    response = lambda_handler(make_event(watchlist_id="1", body={}), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


def test_invalid_email():
    response = lambda_handler(make_event(watchlist_id="1", body={"email": "bademail"}), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


@patch("deleteSubscriptionWatchlist.get_db_connection")
def test_watchlist_not_found(mock_conn):
    cur = MagicMock()
    cur.fetchone.return_value = None
    mock_conn.return_value.cursor.return_value = cur

    response = delete_watchlist(1, "test@gmail.com")
    assert response["statusCode"] == 404
    assert json.loads(response["body"]) == {"error": "Watchlist not found"}


@patch("deleteSubscriptionWatchlist.get_db_connection")
def test_successful_delete(mock_conn):
    cur = MagicMock()
    cur.fetchone.return_value = (1,)
    mock_conn.return_value.cursor.return_value = cur

    response = delete_watchlist(1, "test@gmail.com")
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["id"] == 1
    assert "deleted" in body["message"].lower()
    mock_conn.return_value.commit.assert_called_once()


@patch("deleteSubscriptionWatchlist.get_db_connection")
def test_db_exception_returns_500(mock_conn):
    mock_conn.side_effect = Exception("DB error")

    response = delete_watchlist(1, "test@gmail.com")
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"error": "Internal server error"}