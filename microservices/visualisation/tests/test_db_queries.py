import pytest
import psycopg2
import testing.postgresql
from freezegun import freeze_time
from datetime import datetime
from microservices.visualisation.src.cve_growth.cve_growth_lambda import fetch_vulnerability_data, fetch_company_id
from microservices.visualisation.src.heatmap.heatmap_lambda import fetch_heatmap_data

@pytest.fixture
def cve_growth_db():
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

def test_fetch_company_id_success(cve_growth_db):
    cursor = cve_growth_db["cursor"]
    assert fetch_company_id(cursor, "CompanyOne") == cve_growth_db["id_1"]
    assert fetch_company_id(cursor, "CompanyTwo") == cve_growth_db["id_2"]

def test_fetch_company_id_fail(cve_growth_db):
    cursor = cve_growth_db["cursor"]
    assert fetch_company_id(cursor, "NotCompany") is None
    
### TEST FETCH VULNERABILITY COUNT ###

@freeze_time("2026-03-26")
def test_fetch_vulnerability_data_success(cve_growth_db):
    cursor = cve_growth_db["cursor"]
    results = fetch_vulnerability_data(cursor, "CompanyOne", 7)

    assert len(results) == 2
    res_dict = {str(row[0]): row[1] for row in results}

    assert res_dict["2026-03-26"] == 2
    assert res_dict["2026-03-25"] == 1
    assert "2026-03-12" not in res_dict
    assert "2026-03-23" not in res_dict

@freeze_time("2026-03-26")
def test_fetch_vulnerability_data_invalid_company(cve_growth_db):
    cursor = cve_growth_db["cursor"]
    results = fetch_vulnerability_data(cursor, "FakeCorp", 7)
    assert results == []

@freeze_time("2026-03-26")
def test_fetch_vulnerability_data_no_results_in_range(cve_growth_db):
    cursor = cve_growth_db["cursor"]
    results = fetch_vulnerability_data(cursor, "CompanyOne", 0)
    assert len(results) == 0

### TEST FETCH HEATMAP ###

@pytest.fixture
def heatmap_db():
    with testing.postgresql.Postgresql() as postgres:
        conn = psycopg2.connect(**postgres.dsn())
        cursor = conn.cursor()

        # setup schema
        cursor.execute("""
            CREATE TABLE companies (
                id SERIAL PRIMARY KEY,
                company_name TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE vulnerabilities (
                cve_id TEXT PRIMARY KEY, 
                company_id INTEGER REFERENCES companies(id), 
                cvss_score NUMERIC,
                epss_score NUMERIC
            );
        """)
        
        # setup companies
        cursor.execute("INSERT INTO companies (company_name) VALUES ('HeatmapCorp') RETURNING id;")
        comp_id = cursor.fetchone()[0]

        # seed diverse vulnerabilities
        test_data = [
            # high risk
            ('CVE-HIGH-001', comp_id, 9.8, 0.95),
            ('CVE-HIGH-002', comp_id, 8.2, 0.81),
            
            # mid risk
            ('CVE-MID-001', comp_id, 5.5, 0.45),
            
            # edge case: 4.0 should go into '4-6'
            ('CVE-EDGE-001', comp_id, 4.0, 0.1), 
        ]
        
        for vuln in test_data:
            cursor.execute("INSERT INTO vulnerabilities VALUES (%s, %s, %s, %s)", vuln)
        
        conn.commit()
        yield cursor
        conn.close()

def test_fetch_heatmap_data_sql_bucketing(heatmap_db):
    results = fetch_heatmap_data(heatmap_db, "HeatmapCorp")

    # Expecting 3 unique bucket combinations:
    # 1. (8-10, 0.8-1.0) -> Count 2
    # 2. (4-6, 0.4-0.6)  -> Count 1
    # 3. (4-6, 0-0.2)    -> Count 1 (The boundary test)
    
    assert len(results) == 3

    res_map = {(row[0], row[1]): row[2] for row in results}

    # verify high risk bucket
    assert res_map.get(("8-10", "0.8-1.0")) == 2
    
    # verify mid risk bucket
    assert res_map.get(("4-6", "0.4-0.6")) == 1
    
    # verify edge Case (cvss 4.0 and epss 0.1)
    assert res_map.get(("4-6", "0-0.2")) == 1

def test_fetch_heatmap_data_isolation(heatmap_db):
    results = fetch_heatmap_data(heatmap_db, "FakeCorp")
    
    assert results == []