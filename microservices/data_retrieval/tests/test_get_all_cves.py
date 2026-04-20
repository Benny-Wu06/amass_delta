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
    mock_conn, mock_cur = MagicMock(), MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchall.return_value = [
        ("CVE-2024-0002", 7.0, 0.1, date(2024, 1, 5), "Desc", date(2024, 2, 5), "Google"),
        ("CVE-2024-0001", 8.5, 0.5, date(2024, 1, 1), "Desc", date(2024, 2, 1), "Apple")
    ]

    response = get_all_cves("date_added")
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["cves"][0]["cve_id"] == "CVE-2024-0002"
    assert body["cves"][0]["risk_rating"] == "MEDIUM"
    

@patch('psycopg2.connect')
def test_get_all_cves_sorting_logic_due_date(mock_connect):
    mock_conn, mock_cur = MagicMock(), MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    
    mock_cur.fetchall.return_value = [
        ("CVE-2024-1111", 9.0, 0.9, date(2024, 1, 1), "Desc", date(2024, 2, 1), "Google"),
        ("CVE-2024-2222", 4.0, 0.2, date(2024, 1, 10), "Desc", date(2024, 2, 15), "Apple")
    ]

    event = {"queryStringParameters": {"sort_by": "due_date"}}
    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert body["cves"][0]["cve_id"] == "CVE-2024-1111"
    assert body["cves"][0]["due_date"] == "2024-02-01"

    executed_sql = mock_cur.execute.call_args[0][0]
    assert "v.due_date" in executed_sql
    assert "ORDER BY v.due_date ASC" in executed_sql

@patch('psycopg2.connect')
def test_get_all_cves_sorting_logic_date_added(mock_connect):
    mock_conn, mock_cur = MagicMock(), MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    
    mock_cur.fetchall.return_value = [
        ("CVE-2024-1111", 9.0, 0.9, date(2024, 3, 3), "Desc", date(2024, 4, 5), "Google"),
        ("CVE-2024-2222", 4.2, 0.1, date(2024, 1, 1), "Desc", date(2024, 2, 5), "Apple")
    ]

    event = {"queryStringParameters": {"sort_by": "date_added"}}
    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert body["cves"][0]["cve_id"] == "CVE-2024-1111"
    assert body["cves"][0]["date_added"] == "2024-03-03"

    executed_sql = mock_cur.execute.call_args[0][0]
    assert "ORDER BY v.date_added DESC" in executed_sql

@patch('psycopg2.connect')
def test_get_all_cves_db_error(mock_connect):
    
    mock_connect.side_effect = Exception("RDS Unreachable")

    response = get_all_cves("date_added")

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert body["error"] == "Failed to retrieve CVE list"

@patch('psycopg2.connect')
def test_get_all_cves_empty(mock_connect):
    mock_conn, mock_cur = MagicMock(), MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchall.return_value = []

    response = get_all_cves("date_added")
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["count"] == 0

    args, _ = mock_cur.execute.call_args
    executed_sql = args[0] 
    assert "v.cve_id" in executed_sql