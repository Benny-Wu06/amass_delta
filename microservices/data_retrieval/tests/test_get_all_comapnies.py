import json
import pytest
from unittest.mock import MagicMock, patch
from get_all_companies import get_all_companies

@patch('psycopg2.connect')
def test_get_all_companies_success(mock_connect):

    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    

    mock_cur.fetchall.return_value = [("Apple",), ("Google",), ("Microsoft",)]
    

    response = get_all_companies()
    

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    
    assert body["count"] == 3
    assert body["companies"] == ["Apple", "Google", "Microsoft"]
    

    mock_cur.execute.assert_called_with(
        "SELECT DISTINCT company_name FROM companies ORDER BY company_name ASC;"
    )

@patch('psycopg2.connect')
def test_get_all_companies_db_error(mock_connect):

    mock_connect.side_effect = Exception("Connection Timeout")
    

    response = get_all_companies()
    

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body
    assert body["error"] == "Failed to retrieve company list"

@patch('psycopg2.connect')
def test_get_all_companies_empty(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    
    mock_cur.fetchall.return_value = []
    
    response = get_all_companies()
    body = json.loads(response["body"])
    
    assert response["statusCode"] == 200
    assert body["count"] == 0
    assert body["companies"] == []