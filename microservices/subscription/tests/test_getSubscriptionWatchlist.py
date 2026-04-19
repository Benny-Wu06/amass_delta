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