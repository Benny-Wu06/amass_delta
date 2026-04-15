import pytest
import os, sys
import json

from unittest.mock import MagicMock, patch
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'data_retrieval', 'src'))
sys.path.insert(0, src_path)
from get_all_companies import lambda_handler


@patch('psycopg2.connect')
def test_lambda_handler_success(mock_connect):
    ### Test the handler when the database returns valid data ###

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Simulate the DB returning a list of tuples
    mock_cursor.fetchall.return_value = [("Apple",), ("Microsoft",), ("Google",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # Call the handler 
    event = {}
    context = MagicMock()
    response = lambda_handler(event, context)

    # Assertions
    assert response["statusCode"] == 200
    body = response["body"] 
    import json
    data = json.loads(body)
    
    assert data["count"] == 3
    assert "Apple" in data["companies"]
    assert "Google" in data["companies"]
    assert "Microsoft" in data["companies"]

@patch('psycopg2.connect')
def test_lambda_sorting_logic(mock_connect):
    # Setup Mock: Database returns data in random/unsorted order
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchall.return_value = [("Zyxel",), ("Adobe",), ("Microsoft",)]
    mock_connect.return_value = mock_conn

    # Execute
    response = lambda_handler({}, None)
    data = json.loads(response["body"])
    companies = data["companies"]

    # Assert: The Lambda should have sorted these to ["Adobe", "Microsoft", "Zyxel"]
    assert companies == ["Adobe", "Microsoft", "Zyxel"]

@patch('psycopg2.connect')
def test_lambda_handler_database_error(mock_connect):
    ### Test how the handler survives a database connection failure ###

    mock_connect.side_effect = Exception("Database connection failed")

    event = {}
    context = MagicMock()
    response = lambda_handler(event, context)

    # The handler should catch the exception and return a 500, not crash
    assert response["statusCode"] == 500
    assert "error" in response["body"].lower()