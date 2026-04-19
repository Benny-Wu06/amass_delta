import os
import pytest
import json
import boto3
from moto import mock_aws
from unittest.mock import patch, MagicMock
from microservices.data_collection.src.processor import lambda_handler

# fixture

@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
    os.environ["BUCKET_NAME"] = "test-bucket"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PASSWORD"] = "testpassword"

@pytest.fixture
def sample_cisa_data():
    return {
        "title": "CISA Catalog",
        "count": 3,
        "vulnerabilities": [
            {
                "cveID": "CVE-2021-22054",
                "vendorProject": "Omnissa",
                "vulnerabilityName": "Omnissa Workspace ONE SSRF",
                "shortDescription": "A server-side request forgery vulnerability.",
                "dateAdded": "2026-03-09",
                "dueDate": "2026-03-23",
                "cvss_score": 7.5,
                "cvss_severity": "HIGH",
                "epss_score": "0.937430000",
                "epss_percentile": "0.998460000"
            },
            {
                "cveID": "CVE-2025-26399",
                "vendorProject": "SolarWinds",
                "vulnerabilityName": "SolarWinds Web Help Desk Deserialization",
                "shortDescription": "A deserialization vulnerability.",
                "dateAdded": "2026-03-09",
                "dueDate": "2026-03-12",
                "cvss_score": 9.8,
                "cvss_severity": "CRITICAL",
                "epss_score": "0.342250000",
                "epss_percentile": "0.969090000"
            },
            {
                "cveID": "CVE-2020-7796",
                "vendorProject": "Synacor",
                "vulnerabilityName": "Synacor Zimbra SSRF Vulnerability",
                "shortDescription": "A server-side request forgery vulnerability.",
                "dateAdded": "2026-02-17",
                "dueDate": "2026-03-10",
                "cvss_score": "Awaiting Analysis",
                "cvss_severity": None,
                "epss_score": "0.935280000",
                "epss_percentile": "0.998240000"
            }
        ]
    }

# helper

def make_mock_db():
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur


    mock_cur.fetchone.side_effect = [
        None, 
        (1,),  
        None,
        (2,),   
        None,   
        (3,),    
        (0, None, None, None),  
        (0, None, None, None),
        (0, None, None, None),
    ]

    mock_cur.fetchall.return_value = [(1,), (2,), (3,)]
    mock_cur.rowcount = 1

    return mock_conn, mock_cur

# tests

@mock_aws
def test_lambda_handler_success(aws_credentials, sample_cisa_data):
    s3 = boto3.client("s3", region_name="ap-southeast-2")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'}
    )
    s3.put_object(
        Bucket="test-bucket",
        Key="enriched/enriched.json",
        Body=json.dumps(sample_cisa_data),
        ContentType="application/json"
    )

    with patch("microservices.data_collection.src.processor.BUCKET_NAME", "test-bucket"):
        with patch("microservices.data_collection.src.processor.get_db_connection") as mock_db:
            mock_conn, mock_cur = make_mock_db()
            mock_db.return_value = mock_conn

            result = lambda_handler({}, None)

            assert result["statusCode"] == 200
            assert "inserted" in result["body"].lower()

@mock_aws
def test_lambda_handler_inserts_vulnerabilities(aws_credentials, sample_cisa_data):
    s3 = boto3.client("s3", region_name="ap-southeast-2")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'}
    )
    s3.put_object(
        Bucket="test-bucket",
        Key="enriched/enriched.json",
        Body=json.dumps(sample_cisa_data)
    )

    with patch("microservices.data_collection.src.processor.BUCKET_NAME", "test-bucket"):
        with patch("microservices.data_collection.src.processor.get_db_connection") as mock_db:
            mock_conn, mock_cur = make_mock_db()
            mock_db.return_value = mock_conn

            lambda_handler({}, None)


            assert mock_cur.execute.call_count > 0

            assert mock_conn.commit.call_count >= 2

@mock_aws
def test_lambda_handler_handles_awaiting_analysis(aws_credentials, sample_cisa_data):

    s3 = boto3.client("s3", region_name="ap-southeast-2")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'}
    )
    s3.put_object(
        Bucket="test-bucket",
        Key="enriched/enriched.json",
        Body=json.dumps(sample_cisa_data)
    )

    with patch("microservices.data_collection.src.processor.BUCKET_NAME", "test-bucket"):
        with patch("microservices.data_collection.src.processor.get_db_connection") as mock_db:
            mock_conn, mock_cur = make_mock_db()
            mock_db.return_value = mock_conn

            result = lambda_handler({}, None)

            assert result["statusCode"] == 200

@mock_aws
def test_lambda_handler_missing_bucket(aws_credentials):

    with patch("microservices.data_collection.src.processor.BUCKET_NAME", "test-bucket"):
        with patch("microservices.data_collection.src.processor.get_db_connection") as mock_db:
            mock_conn, mock_cur = make_mock_db()
            mock_db.return_value = mock_conn

            with pytest.raises(Exception):
                lambda_handler({}, None)

@mock_aws
def test_lambda_handler_db_failure(aws_credentials, sample_cisa_data):

    s3 = boto3.client("s3", region_name="ap-southeast-2")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'}
    )
    s3.put_object(
        Bucket="test-bucket",
        Key="enriched/enriched.json",
        Body=json.dumps(sample_cisa_data)
    )

    with patch("microservices.data_collection.src.processor.BUCKET_NAME", "test-bucket"):
        with patch("microservices.data_collection.src.processor.get_db_connection") as mock_db:
            mock_db.side_effect = Exception("Database connection failed")

            with pytest.raises(Exception) as exc_info:
                lambda_handler({}, None)

            assert "Database connection failed" in str(exc_info.value)