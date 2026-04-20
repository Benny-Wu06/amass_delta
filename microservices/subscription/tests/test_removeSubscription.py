import sys
import os
import json
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

with patch("boto3.client"):
    from removeSubscription import lambda_handler, remove_company_from_watchlist

def make_event(watchlist_id=None, company_name=None, email=None):
    event = {}
    path = {}
    if watchlist_id is not None:
        path["id"] = watchlist_id
    if company_name is not None:
        path["company_name"] = company_name
    if path:
        event["pathParameters"] = path
    if email is not None:
        event["queryStringParameters"] = {"email": email}
    return event

def test_missing_watchlist_id():
    response = lambda_handler({}, None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Watchlist id is required in URL"}


def test_non_integer_watchlist_id():
    response = lambda_handler(make_event(watchlist_id="abc", company_name="Timmy Blud"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Watchlist id must be an integer"}


def test_missing_company_name():
    response = lambda_handler(make_event(watchlist_id="1"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Company name is required in URL"}


def test_missing_email():
    response = lambda_handler(make_event(watchlist_id="1", company_name="Timmy Blud"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


def test_invalid_email():
    response = lambda_handler(
        make_event(watchlist_id="1", company_name="Timmy Blud", email="bademail"), None
    )
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Valid email is required"}


def test_company_name_url_decoding():
    event = make_event(watchlist_id="1", company_name="Timmy+Blud", email="test@gmail.com")
    with patch("removeSubscription.remove_company_from_watchlist") as mock_rm:
        mock_rm.return_value = {"statusCode": 200, "body": "{}"}
        lambda_handler(event, None)
        mock_rm.assert_called_once_with(1, "test@gmail.com", "Timmy Blud")


def test_company_name_percent20_decoding():
    event = make_event(watchlist_id="1", company_name="Timmy%20Blud", email="test@gmail.com")
    with patch("removeSubscription.remove_company_from_watchlist") as mock_rm:
        mock_rm.return_value = {"statusCode": 200, "body": "{}"}
        lambda_handler(event, None)
        mock_rm.assert_called_once_with(1, "test@gmail.com", "Timmy Blud")


@patch("removeSubscription.get_db_connection")
def test_company_not_found_returns_404(mock_conn):
    cur = MagicMock()
    cur.fetchone.return_value = None
    mock_conn.return_value.cursor.return_value = cur

    response = remove_company_from_watchlist(1, "test@gmail.com", "Timmy Blud")
    assert response["statusCode"] == 404
    assert json.loads(response["body"]) == {"error": "Watchlist or company not found"}


@patch("removeSubscription.get_db_connection")
def test_successful_remove(mock_conn):
    cur = MagicMock()
    cur.fetchone.return_value = (99,)
    mock_conn.return_value.cursor.return_value = cur

    response = remove_company_from_watchlist(1, "test@gmail.com", "Timmy Blud")
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["watchlist_id"] == 1
    assert body["company_name"] == "Timmy Blud"
    mock_conn.return_value.commit.assert_called_once()


@patch("removeSubscription.get_db_connection")
def test_db_exception_returns_500(mock_conn):
    mock_conn.side_effect = Exception("DB down")

    response = remove_company_from_watchlist(1, "test@gmail.com", "Timmy Blud")
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"error": "Internal server error"}


@patch("removeSubscription.get_db_connection")
def test_rollback_on_exception(mock_conn):
    conn = MagicMock()
    cur = MagicMock()
    cur.execute.side_effect = Exception("query error")
    conn.cursor.return_value = cur
    mock_conn.return_value = conn

    remove_company_from_watchlist(1, "test@gmail.com", "Timmy Blud")
    conn.rollback.assert_called_once()