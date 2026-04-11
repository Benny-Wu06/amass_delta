import json
import os
import pytest
import boto3
import psycopg2

# CONFIGURATION 
LAMBDA_NAME = "get_all_companies_service"
AWS_REGION = "ap-southeast-2"

#  DB SEED DATA 
COMPANY_1 = "TestCorp_Alpha"
COMPANY_2 = "TestCorp_Beta"

@pytest.fixture(scope="module")
def db_conn():
    ### Establish connection to the real staging database ###
    conn = psycopg2.connect(
        host=os.environ.get("STAGING_DB_HOST"),
        port=5432,
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("STAGING_DB_PASSWORD"),
        sslmode="require",
        sslrootcert="global-bundle.pem" # Ensure this file is in your current dir
    )
    yield conn
    conn.close()

@pytest.fixture(autouse=True)
def seed_data(db_conn):
    ### Inserts test companies before the test and removes them after ###
    cur = db_conn.cursor()
    # Insert test companies
    cur.execute("INSERT INTO companies (company_name, risk_index, risk_rating) VALUES (%s, %s, %s) RETURNING id;", (COMPANY_1, 1.0, 'LOW'))
    id1 = cur.fetchone()[0]
    cur.execute("INSERT INTO companies (company_name, risk_index, risk_rating) VALUES (%s, %s, %s) RETURNING id;", (COMPANY_2, 9.0, 'HIGH'))
    id2 = cur.fetchone()[0]
    db_conn.commit()

    yield  

 
    cur.execute("DELETE FROM companies WHERE id IN (%s, %s);", (id1, id2))
    db_conn.commit()
    cur.close()

def test_get_all_companies_integration():
    ### Real end-to-end test: Invoke Lambda and check DB results ###
    client = boto3.client("lambda", region_name=AWS_REGION)
    
    response = client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({})
    )
    
    
    payload = json.loads(response["Payload"].read().decode("utf-8"))
    body = json.loads(payload["body"])
    
    # Assertions
    assert payload["statusCode"] == 200
    assert COMPANY_1 in body["companies"]
    assert COMPANY_2 in body["companies"]
    assert body["count"] >= 2
    
    # Verify Alphabetical Order 
    all_names = body["companies"]
    assert all_names == sorted(all_names)