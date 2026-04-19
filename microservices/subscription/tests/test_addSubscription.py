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
