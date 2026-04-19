import json
import os
import pytest
import boto3
import psycopg2
from botocore.config import Config

# --- CONFIGURATION ---
AWS_REGION = "ap-southeast-2"
LAMBDA_NAME = "integration_stocks_cve_growth"
TEST_SYMBOL = "MSFT"
TEST_COMPANY_NAME = "Microsoft"

# Use unique CVE IDs for testing to avoid clashing with real data
VULNS = [
    ("CVE-2026-TEST-999", 8.0, 0.90, "2026-04-10"),
    ("CVE-2026-TEST-1000", 7.0, 0.50, "2026-04-10"),
    ("CVE-2026-TEST-1001", 5.0, 0.40, "2026-04-11"),
]

lambda_client = boto3.client(
    "lambda", 
    region_name=AWS_REGION,
    config=Config(read_timeout=30, connect_timeout=10)
)

@pytest.fixture(scope="module")
def conn_db():
    cert_path = os.environ.get("CERT_PATH", "global-bundle.pem")
    conn = psycopg2.connect(
        host=os.environ.get("STAGING_DB_HOST"),
        port=5432,
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("STAGING_DB_PASSWORD"),
        sslmode="prefer",
        sslrootcert=cert_path,
        connect_timeout=5
    )
    yield conn
    conn.close()

@pytest.fixture(scope="function", autouse=True)
def seed_db(conn_db):
    cur = conn_db.cursor()
    try:
        cur.execute("SELECT id FROM companies WHERE company_name = %s;", (TEST_COMPANY_NAME,))
        res = cur.fetchone()
        if not res:
            pytest.fail(f"Could not find company {TEST_COMPANY_NAME} in DB.")
        company_id = res[0]

        for cve, cvss, epss, date in VULNS:
            cur.execute("""
                INSERT INTO vulnerabilities (cve_id, company_id, vulnerability_name, description, date_added, due_date, cvss_score, epss_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cve_id) DO UPDATE SET vulnerability_name = EXCLUDED.vulnerability_name;
            """, (cve, company_id, "Merge Test", "Test Data", date, "2088-08-08", cvss, epss))
        
        conn_db.commit() 
        cur.close() 
    except Exception as e:
        conn_db.rollback()
        raise e

    yield

    # cleanup
    cur = conn_db.cursor()
    try:
        test_ids = tuple(v[0] for v in VULNS)
        cur.execute("DELETE FROM vulnerabilities WHERE cve_id IN %s;", (test_ids,))
        conn_db.commit()
    finally:
        cur.close()

def invoke_lambda(payload):
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    raw_payload = response["Payload"].read().decode("utf-8")
    parsed = json.loads(raw_payload)
    return {
        "statusCode": parsed.get("statusCode"),
        "body": json.loads(parsed.get("body", "{}")),
        "function_error": response.get("FunctionError")
    }

def test_stocks_cve_supported_symbol():
    event = {
        "pathParameters": {"company_symbol": "MSFT"},
        "queryStringParameters": {"from": "2026-04-01", "to": "2026-04-10"}
    }
    result = invoke_lambda(event)

    if result["statusCode"] != 200:
        print(f"DEBUG BODY: {result['body']}")

    assert result["statusCode"] == 200

def test_stocks_cve_unsupported_symbol():
    event = {"pathParameters": {"company_symbol": "INVALID_TICKER"}}
    result = invoke_lambda(event)
    assert result["statusCode"] == 404

def test_stocks_cve_data_merge_accuracy():
    # We seeded VULNS with 2 entries on 2026-04-10
    event = {
        "pathParameters": {"company_symbol": "MSFT"},
        "queryStringParameters": {"from": "2026-04-10", "to": "2026-04-10"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 200
    merged_results = result["body"].get("merged_results", [])
    
    # Check if April 10th exists in the response and has cve_growth = 2
    target_date = "2026-04-10"
    day_entry = next((item for item in merged_results if item["date"] == target_date), None)
    
    assert day_entry is not None, f"Date {target_date} missing from results"
    assert day_entry["cve_growth"] == 2
    assert "price_diff" in day_entry

def test_stocks_cve_invalid_date_range():
    event = {
        "pathParameters": {"company_symbol": "MSFT"},
        "queryStringParameters": {"from": "2026-05-01", "to": "2026-04-01"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 400
    assert "error" in result["body"]

def test_stocks_cve_missing_query_params():
    event = {
        "pathParameters": {"company_symbol": "AAPL"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 200
    assert result["body"]["company"] == "Apple"
    # verify period defaults are applied
    assert "period" in result["body"]
    assert result["body"]["period"]["from"] == "2025-01-01"

def test_stocks_cve_no_data_period():
    # future date
    event = {
        "pathParameters": {"company_symbol": "GOOGL"},
        "queryStringParameters": {"from": "2029-01-01", "to": "2029-01-02"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 200
    # return an empty list or entries with 0s
    # just want to make sure it doesn't 500
    assert isinstance(result["body"]["merged_results"], list)