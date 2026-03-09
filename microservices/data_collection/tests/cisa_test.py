import os
import pytest
from moto import mock_aws
import boto3
import json
from microservices.data_collection.src.cisascrapper.cisa import cisascrapper

@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
    os.environ["BUCKET_NAME"] = "test-bucket"

@mock_aws
def test_cisascrapper_uploads_to_s3(aws_credentials):
    s3 = boto3.client("s3", region_name="ap-southeast-2")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'}
    )

    result = cisascrapper({}, None)


    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["status"] == "success"
    assert "cisa_kev" in body["file"]

@mock_aws
def test_cisascrapper_failure():
    result = cisascrapper({}, None)

    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "error" in body