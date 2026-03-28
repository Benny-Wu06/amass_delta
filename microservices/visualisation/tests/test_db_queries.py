import pytest
import psycopg2
import testing.postgresql
from freezegun import freeze_time
from datetime import datetime
from src.cve_growth.cve_growth_lambda import fetch_vulnerability_data, fetch_company_id

@pytest.fixture
def mock_db():
    with testing.postgresql.Postgresql() as postgres:
        conn = psycopg2.connect(**postgres.dsn())
        cursor = conn.cursor()

        # setup schema
        cursor.execute("CREATE TABLE companies (id SERIAL PRIMARY KEY, company_name TEXT);")
        cursor.execute("""
            CREATE TABLE vulnerabilities (
                cve_id TEXT PRIMARY KEY, 
                company_id INTEGER REFERENCES companies(id), 
                date_added DATE
            );
        """)
        
        # set companies
        cursor.execute("INSERT INTO companies (company_name) VALUES ('CompanyOne') RETURNING id;")
        id_1 = cursor.fetchone()[0]
        cursor.execute("INSERT INTO companies (company_name) VALUES ('CompanyTwo') RETURNING id;")
        id_2 = cursor.fetchone()[0]

        # seed vulnerabilities
        test_data = [
            ('CVE-2026-001', id_1, datetime(2026, 3, 26)),
            ('CVE-2026-002', id_1, datetime(2026, 3, 26)),
            ('CVE-2026-003', id_1, datetime(2026, 3, 25)),
            ('CVE-2026-004', id_1, datetime(2026, 3, 12)), # Out of 7-day range
            ('CVE-2026-101', id_2, datetime(2026, 3, 26)), # Different Company
            ('CVE-2026-102', id_2, datetime(2026, 3, 23))  # Different Company
        ]
        
        for vuln in test_data:
            cursor.execute("INSERT INTO vulnerabilities VALUES (%s, %s, %s)", vuln)
        
        conn.commit()
        yield {"cursor": cursor, "id_1": id_1, "id_2": id_2}
        conn.close()

### TEST FETCH COMAPNY ID ###

def test_fetch_company_id_success(mock_db):
    cursor = mock_db["cursor"]
    assert fetch_company_id(cursor, "CompanyOne") == mock_db["id_1"]
    assert fetch_company_id(cursor, "CompanyTwo") == mock_db["id_2"]

def test_fetch_company_id_fail(mock_db):
    cursor = mock_db["cursor"]
    assert fetch_company_id(cursor, "NotCompany") is None
    
### TEST FETCH VULNERABILITY COUNT ###

@freeze_time("2026-03-26")
def test_fetch_vulnerability_data_success(mock_db):
    cursor = mock_db["cursor"]
    results = fetch_vulnerability_data(cursor, "CompanyOne", 7)

    assert len(results) == 2
    res_dict = {str(row[0]): row[1] for row in results}

    assert res_dict["2026-03-26"] == 2
    assert res_dict["2026-03-25"] == 1
    assert "2026-03-12" not in res_dict
    assert "2026-03-23" not in res_dict

@freeze_time("2026-03-26")
def test_fetch_vulnerability_data_invalid_company(mock_db):
    cursor = mock_db["cursor"]
    results = fetch_vulnerability_data(cursor, "FakeCorp", 7)
    assert results == []

@freeze_time("2026-03-26")
def test_fetch_vulnerability_data_no_results_in_range(mock_db):
    cursor = mock_db["cursor"]
    results = fetch_vulnerability_data(cursor, "CompanyOne", 0)
    assert len(results) == 0

### TEST FETCH VULNERABILITY COUNT ###