import os
import pytest
from moto import mock_aws
import boto3
import json
from microservices.data_collection.src.reference import nvdscrapper

@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
    os.environ["BUCKET_NAME"] = "test-bucket"

@mock_aws
def test_reference_uploads_to_s3(aws_credentials):
    s3 = boto3.client("s3", region_name="ap-southeast-2")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'}
    )

    result = nvdscrapper({}, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["status"] == "success"
    obj = s3.get_object(Bucket="test-bucket", Key="reference/nvd/nvdcve-2.0-2026.json.gz")
    assert obj['ContentType'] == 'application/x-gzip'

@mock_aws
def test_reference_failure():
    result = nvdscrapper({}, None)

    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "error" in body