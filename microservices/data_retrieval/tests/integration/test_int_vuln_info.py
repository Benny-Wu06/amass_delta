import json
import os
import pytest
import datetime 
import boto3
import psycopg2

class AnyString():
    def __eq__(self, value):
        return isinstance(value, str)

# init seed vars
LAMBDA_FUNCTION_NAME = "vuln_info_lambda"
CVE_ID = "CVE-2026-99999"
COMPANY_ID = -9
VULN_NAME = "test vulnerability"
DESC = "test description"
DATE_ADDED = datetime.datetime.strptime("2026-04-01", "%Y-%m-%d").date()
DUE_DATE = datetime.datetime.strptime("2026-04-05", "%Y-%m-%d").date()
CVSS = 9
CVSS_SEVERITY = "TEST_SEVERITY"
EPSS = 0.8
EPSS_PERCENTILE = 0.9
RISK_INDEX = round((float(CVSS) / 10) * 0.6 + float(EPSS) * 0.4, 4)
RISK_RATING = "MEDIUM"


@pytest.fixture(scope="module")
def lambda_client():
    # no need to pass in env variables (aws keys), boto3 does this automatically
    # so when called from staging branch, should have the right access.
    return boto3.client("lambda")

# connect to db
def conn_db(scope="module"):
    conn = None
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    cert_path = os.environ.get("CERT_PATH", "global-bundle.pem")

    conn = psycopg2.connect(
            host=DB_HOST,
            port=5432,
            database=os.environ.get("DB_NAME", "postgres"),
            user=os.environ.get("DB_USER", "postgres"),
            password=DB_PASSWORD,
            sslmode="require",
            connect_timeout=50,
            sslrootcert=cert_path,
    )
    yield conn
    conn.close()
            

# seed db, this sets up and tears down the vulnerability for every test
def seed_db(scope="function"):
    cur = conn_db.cursor()

    query = """
        insert into vulnerabilities (cve_id, company_id, vulnerability_name, description,
          date_added, due_date, cvss_score, cvss_severity, epss_score, epss_percentile)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(query, (CVE_ID, COMPANY_ID, VULN_NAME, DESC, DATE_ADDED, DUE_DATE, CVSS, CVSS_SEVERITY, EPSS, EPSS_PERCENTILE,))
    cur.commit()

    yield

    delete_query = "DELETE FROM vulnerabilities WHERE cve_id = %s;"
    cur.execute(delete_query, (CVE_ID,))
    cur.commit()
    cur.close()

def test_vuln_retrieval_success(lambda_client):
    event = {
        "pathParameters": {
            "cve_id": CVE_ID
        }
    }
    
    response = lambda_client.invoke(
        FunctionName='vuln_info_lambda',
        InvocationType="RequestResponse",
        Payload=json.dumps(event)
    )
    
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    assert response_payload["statusCode"] == 200
    
    body = json.loads(response_payload["body"])
    # assert json body is correct