import json
import os
import boto3
import pytest
import requests
from botocore.config import Config

AWS_REGION = "ap-southeast-2"
URL = "https://3y9896hlw6.execute-api.ap-southeast-2.amazonaws.com"
BUCKET_NAME = "amass-cisa-bucket-staging"

lambda_client = boto3.client(
    "lambda",
    region_name=AWS_REGION,
    config=Config(read_timeout=700, connect_timeout=10),
)

s3_client = boto3.client("s3", region_name=AWS_REGION)
s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)

def invoke_lambda(function_name, payload=None):
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload or {}),
    )
    function_error = response.get("FunctionError")
    parsed = json.loads(response["Payload"].read())
    return {
        "statusCode": parsed.get("statusCode"),
        "body": parsed.get("body"),
        "raw": parsed,
        "function_error": function_error,
    }

@pytest.fixture(scope="function", autouse=True)
def clearns3bucket():
    bucket.objects.all().delete()

class TestCisaComponent:

    def test_cisa_works_200(self):
        result = invoke_lambda("cisa_scraper")
        assert result["function_error"] is None
        assert result["statusCode"] == 200


class TestCisaIntegration:

    def test_get_scrape_returns_200(self):
        response = requests.get(f"{URL}/scrape", timeout=60)
        assert response.status_code == 200


class TestNvdScrapperComponent:

    def test_nvd_scrapper_returns_200(self):
        result = invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})
        assert result["function_error"] is None
        assert result["statusCode"] == 200