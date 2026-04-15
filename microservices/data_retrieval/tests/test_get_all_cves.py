import sys
import os
import json
import pytest
from datetime import date
from unittest.mock import MagicMock, patch


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from get_all_cves import lambda_handler, get_all_cves

@patch('psycopg2.connect')
def test_get_all_cves_success(mock_connect):
    
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    
    mock_cur.fetchall.return_value = [
        ("CVE-2024-0001", date(2024, 1, 1), date(2024, 2, 1)),
        ("CVE-2024-0002", date(2024, 1, 5), date(2024, 2, 5))
    ]

    response = get_all_cves("date_added")

    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    
    assert body["count"] == 2
    assert body["cves"][0]["cve_id"] == "CVE-2024-0001"
    
    assert body["cves"][0]["date_added"] == "2024-01-01"

    
    mock_cur.execute.assert_called_with(
        "SELECT cve_id, date_added, due_date FROM cves ORDER BY date_added ASC;"
    )

@patch('psycopg2.connect')
def test_get_all_cves_sorting_logic(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = [
        ("CVE-2024-1111", date(2024, 1, 1), date(2024, 6, 1)),
        ("CVE-2024-2222", date(2024, 1, 10), date(2024, 7, 1))
    ]

    # Test sorting by due_date via lambda_handler
    event = {"queryStringParameters": {"sort_by": "due_date"}}
    response = lambda_handler(event, None)

    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["count"] == 2

    first_cve = body["cves"][0]
    assert first_cve["cve_id"] == "CVE-2024-1111"
    assert first_cve["date_added"] == "2024-01-01"
    assert first_cve["due_date"] == "2024-06-01"

    # Verify the SQL was updated to due_date
    mock_cur.execute.assert_called_with(
        "SELECT cve_id, date_added, due_date FROM cves ORDER BY due_date ASC;"
    )

@patch('psycopg2.connect')
def test_get_all_cves_db_error(mock_connect):
    
    mock_connect.side_effect = Exception("RDS Unreachable")

    response = get_all_cves("date_added")

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body
    assert body["error"] == "Failed to retrieve CVE list"

@patch('psycopg2.connect')
def test_get_all_cves_empty(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = []

    response = get_all_cves("date_added")
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["count"] == 0
    assert body["cves"] == []