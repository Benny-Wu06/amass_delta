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

def test_lambda_success(lambda_client):
    event = {
        "pathParameters": {
            "cve_id": "CVE-2021-22175"
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