import json
from unittest.mock import MagicMock, patch
from microservices.visualisation.src.heatmap.heatmap_lambda import heatmap_lambda

# Helper Function: create a mock DB setup
def setup_mock_db(mock_get_db):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    return mock_conn, mock_cur

# TEST 1: SUCCESSFUL HEATMAP GENERATION
@patch("microservices.visualisation.src.heatmap.heatmap_lambda.get_db_connection")
def test_heatmap_success(mock_get_db):
    mock_conn, mock_cur = setup_mock_db(mock_get_db)
    
    # simulate the fetch_company_id result
    mock_cur.fetchone.return_value = (101,)
    mock_cur.fetchall.return_value = [
        ("8-10", "0.8-1.0", 5),  # high cvss, high epss
        ("0-2", "0-0.2", 10),    # low cvss, low epss
    ]

    event = {"pathParameters": {"company_name": "CompanyOne"}}
    
    response = heatmap_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["company_name"] == "CompanyOne"
    
    # grid should always have 25 items (5x5 buckets)
    assert len(body["heatmap_grid"]) == 25
    

    grid_lookup = {(item["cvss_range"], item["epss_range"]): item["cve_count"] for item in body["heatmap_grid"]}

    # verify
    assert grid_lookup[("8-10", "0.8-1.0")] == 5
    assert grid_lookup[("0-2", "0-0.2")] == 10
    assert grid_lookup[("4-6", "0.4-0.6")] == 0  # shoudl be empty
    mock_conn.close.assert_called_once()

# TEST 2: COMPANY NOT FOUND (404)
@patch("microservices.visualisation.src.heatmap.heatmap_lambda.get_db_connection")
def test_heatmap_company_not_found(mock_get_db):
    mock_conn, mock_cur = setup_mock_db(mock_get_db)
    
    # simulate company not in the database
    mock_cur.fetchone.return_value = None

    event = {"pathParameters": {"company_name": "FakeCorp"}}
    
    response = heatmap_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 404
    assert "not found" in body["error"]
    mock_conn.close.assert_called_once()

# TEST 3: EMPTY DATA (Success but all 0s)
@patch("microservices.visualisation.src.heatmap.heatmap_lambda.get_db_connection")
def test_heatmap_empty_results(mock_get_db):
    mock_conn, mock_cur = setup_mock_db(mock_get_db)
    
    mock_cur.fetchone.return_value = (99,)
    mock_cur.fetchall.return_value = [] # Company exists, but no vulnerabilities

    event = {"pathParameters": {"company_name": "OtherCompany"}}
    
    response = heatmap_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    # every cell in the 25-cell grid should be 0
    assert all(cell["cve_count"] == 0 for cell in body["heatmap_grid"])
    mock_conn.close.assert_called_once()

# TEST 4: DATABASE CONNECTION ERROR (500)
@patch("microservices.visualisation.src.heatmap.heatmap_lambda.get_db_connection")
def test_heatmap_db_error(mock_get_db):
    mock_get_db.side_effect = Exception("Connection Timeout")

    event = {"pathParameters": {"company_name": "AnyCorp"}}
    
    response = heatmap_lambda(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 500
    assert body["error"] == "Connection Timeout"