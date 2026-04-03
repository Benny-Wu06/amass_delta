import sys
import os
import json
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from company_vulnerabilities import lambda_handler

# CONSTANTS 
EXPECTED_COLUMNS = [
    "cve_id", "company_id", "vulnerability_name", "description", 
    "date_added", "due_date", "cvss_score", "epss_score", 
    "risk_index", "risk_rating"
]

# HELPER
def create_mock_cursor(rows, columns):
    mock_cur = MagicMock()
    mock_cur.description = [(col,) for col in columns]
    mock_cur.fetchall.return_value = rows
    return mock_cur

# TEST CASES

@patch("psycopg2.connect")
def test_get_vulnerabilities_success(mock_connect):
    ## CASE 1: Success - Basic retrieval for a company ##
    mock_conn = MagicMock()
    mock_row = [("CVE-2026-1111", 1, "SQLi", "Description", "2026-01-01", "2026-02-01", 9.8, 0.5, 85.0, "CRITICAL")]
    mock_cur = create_mock_cursor(mock_row, EXPECTED_COLUMNS)
    
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    
    event = {"pathParameters": {"company_name": "Google"}}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])

    # Verify structure
    assert body["company"] == "Google"
    assert body["cve_count"] == 1
    assert "timestamp" in body["time"]
    assert body["time"]["timezone"] == "UTC"

    #  Verify Vulnerability Content 
    assert isinstance(body["vulnerabilities"], list)
    assert len(body["vulnerabilities"]) == 1
    
    vuln = body["vulnerabilities"][0]
    assert vuln["cve_id"] == "CVE-2026-1111"
    assert vuln["cvss"] == 9.8
    assert vuln["risk_rating"] == "CRITICAL"

def test_missing_company_name():
    ## CASE 2: Error - No company name in URL ##
    event = {"pathParameters": {}}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 400
    assert "Company name is required" in response["body"]

@patch("psycopg2.connect") 
def test_invalid_cvss_range(mock_connect):
    ## CASE 3: Error - User provides impossible CVSS score ##
    event = {
        "pathParameters": {"company_name": "Google"},
        "queryStringParameters": {"min_cvss": "15.0"}
    }
    response = lambda_handler(event, None)

    assert response["statusCode"] == 400
    assert "min_cvss" in response["body"]
    mock_connect.assert_not_called()

@patch("psycopg2.connect")
def test_invalid_epss_range(mock_connect):
    ## CASE 4: Error - User provides impossible EPSS score ##
    event = {
        "pathParameters": {"company_name": "Google"},
        "queryStringParameters": {"min_epss": "1.5"}
    }
    response = lambda_handler(event, None)

    assert response["statusCode"] == 400
    assert "min_epss" in response["body"]
    mock_connect.assert_not_called()

@patch("psycopg2.connect")
def test_database_connection_error(mock_connect):
    ## CASE 5: Error - Database connection failure ##
    mock_connect.side_effect = Exception("Connection Refused")

    event = {"pathParameters": {"company_name": "Google"}}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 500
    assert "Failed to retrieve data" in response["body"]

@patch("psycopg2.connect")
def test_filter_logic_applied(mock_connect):
    ## CASE 6: Logic - Verify both filters are added to query ##
    mock_conn = MagicMock()
    mock_row = [("CVE-2026-9999", 2, "Data breach", "Desc", "2026-01-01", "2026-02-01", 7.5, 0.1, 70.0, "HIGH")]
    mock_cur = create_mock_cursor(mock_row, EXPECTED_COLUMNS) 
    
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    event = {
        "pathParameters": {"company_name": "Google"},
        "queryStringParameters": {"min_cvss": "7.0", "min_epss": "0.1"}
    }
    
    response = lambda_handler(event, None)
    called_args = mock_cur.execute.call_args[0]
    sql_query = called_args[0]

    assert "AND v.cvss_score >=" in sql_query
    assert "AND v.epss_score >=" in sql_query
    assert response["statusCode"] == 200
    
    # Verify body 
    body = json.loads(response["body"])
    assert body["company"] == "Google"
    assert body["cve_count"] == 1
    assert body["vulnerabilities"][0]["name"] == "Data breach"
    assert "time" in body

@patch("psycopg2.connect")
def test_only_one_filter_applied(mock_connect):
    ## CASE 7: Logic - Verify 1 filter is used to query ##
    mock_conn = MagicMock()
    mock_row = [("CVE-2026-8888", 3, "Auth Bypass", "Desc", "2026-01-01", "2026-02-01", 5.0, 0.05, 40.0, "MEDIUM")]
    mock_cur = create_mock_cursor(mock_row, EXPECTED_COLUMNS)
    
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    event = {
        "pathParameters": {"company_name": "Google"},
        "queryStringParameters": {"min_cvss": "5.0"}
    }
    
    response = lambda_handler(event, None)
    sql_query = mock_cur.execute.call_args[0][0]
    
    assert "cvss_score >=" in sql_query
    assert "AND v.epss_score" not in sql_query 
    assert response["statusCode"] == 200

    # Verify body
    body = json.loads(response["body"])
    assert body["cve_count"] == 1
    # Specific check for the ID inside the list
    assert body["vulnerabilities"][0]["cve_id"] == "CVE-2026-8888"
    assert body["company"] == "Google"