import os
import pytest
import requests
import psycopg2

BASE_URL = "https://blj7h0zmba.execute-api.ap-southeast-2.amazonaws.com"

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
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        sslmode="prefer",
        sslrootcert=os.environ.get("CERT_PATH", "global-bundle.pem")
    )
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


# TESTS
def test_get_heatmap_returns_200():
    url = f"{BASE_URL}/v1/heatmap/{COMPANY_NAME_1}"
    params = {"days": 7}
    
    response = requests.get(url, params=params, timeout=15)
    
    # verify status code
    assert response.status_code == 200

    # verify header type
    assert "application/json" in response.headers.get("Content-Type", "")

    # verify structure
    body = response.json()
    assert body["company_name"] == COMPANY_NAME_1
    heatmap_grid = body["heatmap_grid"]
    assert isinstance(heatmap_grid, list)

    # check contents
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


def test_get_heatmap_invalid_company_404():
    url = f"{BASE_URL}/v1/heatmap/UnknownCorp"
    response = requests.get(url, timeout=15)
    
    assert response.status_code == 404
    assert "error" in response.json()

def test_post_to_heatmap_route_returns_error():
    url = f"{BASE_URL}/v1/heatmap/{COMPANY_NAME_1}"
    # attempting a POST instead of a GET
    response = requests.post(url, timeout=10)
    
    assert response.status_code == 404