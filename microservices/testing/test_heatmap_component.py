import json
import os
import pytest
import boto3
import psycopg2
from botocore.config import Config

# CONFIGURATION
AWS_REGION = "ap-southeast-2"
LAMBDA_NAME = "visualisation_heatmap"

lambda_client = boto3.client(
    "lambda", 
    region_name=AWS_REGION,
    config=Config(read_timeout=30, connect_timeout=10)
)

# SEED DATA
COMPANY_NAME_1 = "TestCorp1"
VULNS_1 = [
    ("CVE-2026-001", 7.7, 0.77, "2026-01-10"),
    ("CVE-2026-002", 6.6, 0.11, "2026-03-28"),
    ("CVE-2026-003", 2.2, 0.66, "2026-03-30"), 
    ("CVE-2026-004", 3.3, 0.88, "2026-03-30"),
    ("CVE-2026-005", 9.9, 0.88, "2026-03-30"),
    ("CVE-2026-006", 4.4, 0.22, "2026-03-31"),
]

COMPANY_NAME_2 = "TestCorp2"
VULNS_2 = [
    ("CVE-2026-101", 5.5, 0.88, "2026-03-20"),
    ("CVE-2026-102", 3.3, 0.55, "2026-03-21"),
]

# FIXTRURES
@pytest.fixture(scope="module")
def conn_db():
    conn = None
    DB_PASSWORD = os.environ.get("STAGING_DB_PASSWORD")
    DB_HOST = os.environ.get("STAGING_DB_HOST")
    cert_path = os.environ.get("CERT_PATH", "global-bundle.pem")
    print('\nDB_PASSWORD', DB_PASSWORD)
    print('\ndb_host', DB_HOST)
    conn = psycopg2.connect(
            host=DB_HOST,
            port=5432,
            database=os.environ.get("DB_NAME", "postgres"),
            user=os.environ.get("DB_USER", "postgres"),
            password=DB_PASSWORD,
            sslmode="prefer",
            connect_timeout=5,
            sslrootcert=cert_path,
    )
    print('\nconnection succesful')
    yield conn
    conn.close()

@pytest.fixture(scope="function", autouse=True)
def seed_db(conn_db):
    cur = conn_db.cursor()
    
    # seed a company and its list of vulnerabilities
    def insert_data(name, vulns):
        cur.execute("INSERT INTO companies (company_name, risk_index, risk_rating) VALUES (%s, %s, %s) RETURNING id;", (name, 5.0, 'MEDIUM'))
        company_id = cur.fetchone()[0]
        for cve, cvss, epss, date in vulns:
            cur.execute("""
                INSERT INTO vulnerabilities (cve_id, company_id, vulnerability_name, description, date_added, due_date, cvss_score, epss_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (cve, company_id, "Visualisation Test", "Test Data", date, "2088-08-08", cvss, epss))
        return company_id

    id1 = insert_data(COMPANY_NAME_1, VULNS_1)
    id2 = insert_data(COMPANY_NAME_2, VULNS_2)
    conn_db.commit()

    yield

    # teardown stage, clean up both companies
    for company_id in [id1, id2]:
        cur.execute("DELETE FROM vulnerabilities WHERE company_id = %s;", (company_id,))
        cur.execute("DELETE FROM companies WHERE id = %s;", (company_id,))
    conn_db.commit()
    cur.close()

# Helper function: decodes the lambda response, parses the nested JSON body, and returns a structured dictionary of results.
def invoke_visualiser(payload):
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    raw_payload = response["Payload"].read().decode("utf-8")
    parsed = json.loads(raw_payload)
    inner_body = json.loads(parsed.get("body", "{}"))
    
    return {
        "statusCode": parsed.get("statusCode"),
        "body": inner_body,
        "function_error": response.get("FunctionError")
    }

# TESTS 
def test_lambda_success():
    event = {"pathParameters": {"company_name": COMPANY_NAME_1}}
    
    result = invoke_visualiser(event)
    
    assert result["statusCode"] == 200
    assert result["function_error"] is None

    body = result["body"]
    assert body["company_name"] == COMPANY_NAME_1
    heatmap_grid = body["heatmap_grid"]

    assert len(heatmap_grid) == 25

    # verify specific high-risk bucket (CVSS 8-10, EPSS 0.8-1.0), matches CVE-2026-005 (9.9, 0.88)
    critical_cell = next(item for item in heatmap_grid 
                         if item["cvss_range"] == "8-10" and item["epss_range"] == "0.8-1.0")
    assert critical_cell["cve_count"] == 1

    # verify a mid-range bucket (CVSS 2-4, EPSS 0.8-1.0), matches CVE-2026-004 (3.3, 0.88)
    mid_low_cell = next(item for item in heatmap_grid 
                        if item["cvss_range"] == "2-4" and item["epss_range"] == "0.8-1.0")
    assert mid_low_cell["cve_count"] == 1

    # verify an empty bucket, vo vulnerabilities in TestCorp1 fall into 0-2 CVSS
    empty_cell = next(item for item in heatmap_grid 
                      if item["cvss_range"] == "0-2")
    assert empty_cell["cve_count"] == 0

    total_cves_in_grid = sum(item["cve_count"] for item in heatmap_grid)
    assert total_cves_in_grid == 6

def test_lambda_unknown_company():
    event = {
        "pathParameters": {"company_name": "UnknownCorp"}
    }
    
    result = invoke_visualiser(event)
    
    assert result["statusCode"] == 404
    assert "error" in result["body"]
