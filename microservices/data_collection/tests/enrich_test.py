import json
import gzip
import io
import os
import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch, MagicMock
from microservices.data_collection.src.enrich import enrichment

@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
    os.environ["BUCKET_NAME"] = "test-bucket"

@patch('urllib.request.urlopen')
@mock_aws
def test_enrichment_success(mock_urlopen):
    s3 = boto3.client("s3", region_name="ap-southeast-2")
    bucket_name = os.environ["BUCKET_NAME"]
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'}
    )
    raw_data = {
        "vulnerabilities": [
        {
            "cveID": "CVE-2026-3910",
            "vendorProject": "Google",
            "product": "Chromium V8",
            "vulnerabilityName": "Google Chromium V8 Improper Restriction of Operations Within the Bounds of a Memory Buffer Vulnerability",
            "dateAdded": "2026-03-13",
            "shortDescription": "Google Chromium V8 contains an improper restriction of operations within the bounds of a memory buffer vulnerability that could allow a remote attacker to execute arbitrary code inside a sandbox via a crafted HTML page. This vulnerability could affect multiple web browsers that utilize Chromium, including, but not limited to, Google Chrome, Microsoft Edge, and Opera.",
            "requiredAction": "Apply mitigations per vendor instructions, follow applicable BOD 22-01 guidance for cloud services, or discontinue use of the product if mitigations are unavailable.",
            "dueDate": "2026-03-27",
            "knownRansomwareCampaignUse": "Unknown",
            "notes": "https:\/\/chromereleases.googleblog.com\/2026\/03\/stable-channel-update-for-desktop_12.html ; https:\/\/nvd.nist.gov\/vuln\/detail\/CVE-2026-3910",
            "cwes": [
                "CWE-119"
            ]
        },
        ]
    }
    s3.put_object(
        Bucket=bucket_name,
        Key="raw/cisa_2026.json",
        Body=json.dumps(raw_data)
    )

    nvd_fake = {
        "vulnerabilities": [{
            "cve": {
                "id": "CVE-2026-3910",
                "metrics": {
                    "cvssMetricV31": [{
                        "source": "nvd@nist.gov",
                        "cvssData": {"baseScore": 10.0}
                    }]
                }
            }
        }]
    }
    
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb') as file:
        file.write(json.dumps(nvd_fake).encode('utf-8'))
    
    s3.put_object(
        Bucket=bucket_name,
        Key="reference/nvdcve-2.0-2026.json.gz",
        Body=buf.getvalue()
    )
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "data": [{"cve": "CVE-2024-1234", "epss": "0.95"}]
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    result = enrichment({}, None)

    assert result['statusCode'] == 200
    assert "Successfully enriched" in result['body']

    bucket_name = os.environ["BUCKET_NAME"]
    enriched_obj = s3.get_object(Bucket=bucket_name, Key="enriched/enriched.json")
    enriched_data = json.loads(enriched_obj['Body'].read().decode('utf-8'))
    vulnerability = enriched_data['vulnerabilities'][0]
    assert vulnerability['cveID'] == "CVE-2026-3910"
    assert vulnerability["cvss_score"] == 10

@mock_aws
def test_enrichment_no_raw_files():
    s3 = boto3.client("s3", region_name="ap-southeast-2")
    bucket_name = os.environ["BUCKET_NAME"]
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'}
    )

    result = enrichment({}, None)
    assert result is None