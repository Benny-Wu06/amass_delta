import json
import base64
import pytest
import boto3
from botocore.config import Config

# CONFIGURATION
AWS_REGION = "ap-southeast-2"
LAMBDA_NAME = "visualisation_graph_generator"

lambda_client = boto3.client(
    "lambda", 
    region_name=AWS_REGION,
    config=Config(read_timeout=30, connect_timeout=10)
)

def invoke_visualiser(payload):
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    raw_payload = response["Payload"].read().decode("utf-8")
    parsed = json.loads(raw_payload)
    
    # Note: For the Visualiser, the 'body' is a base64 string, not a JSON dict
    return parsed

# MOCK INPUT (Retrieved from other routes by the user)
HEATMAP_INPUT = {
    "company_name": "TestCorp1",
    "heatmap_grid": [
        # CVSS 0-2
        {"cvss_range": "0-2", "epss_range": "0-0.2", "cve_count": 0},
        {"cvss_range": "0-2", "epss_range": "0.2-0.4", "cve_count": 0},
        {"cvss_range": "0-2", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "0-2", "epss_range": "0.6-0.8", "cve_count": 0},
        {"cvss_range": "0-2", "epss_range": "0.8-1.0", "cve_count": 0},
        
        # CVSS 2-4
        {"cvss_range": "2-4", "epss_range": "0-0.2", "cve_count": 0},
        {"cvss_range": "2-4", "epss_range": "0.2-0.4", "cve_count": 0},
        {"cvss_range": "2-4", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "2-4", "epss_range": "0.6-0.8", "cve_count": 1},
        {"cvss_range": "2-4", "epss_range": "0.8-1.0", "cve_count": 1},
        
        # CVSS 4-6
        {"cvss_range": "4-6", "epss_range": "0-0.2", "cve_count": 0},
        {"cvss_range": "4-6", "epss_range": "0.2-0.4", "cve_count": 1},
        {"cvss_range": "4-6", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "4-6", "epss_range": "0.6-0.8", "cve_count": 0},
        {"cvss_range": "4-6", "epss_range": "0.8-1.0", "cve_count": 0},
        
        # CVSS 6-8
        {"cvss_range": "6-8", "epss_range": "0-0.2", "cve_count": 1},
        {"cvss_range": "6-8", "epss_range": "0.2-0.4", "cve_count": 0},
        {"cvss_range": "6-8", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "6-8", "epss_range": "0.6-0.8", "cve_count": 1},
        {"cvss_range": "6-8", "epss_range": "0.8-1.0", "cve_count": 0},
        
        # CVSS 8-10
        {"cvss_range": "8-10", "epss_range": "0-0.2", "cve_count": 0},
        {"cvss_range": "8-10", "epss_range": "0.2-0.4", "cve_count": 0},
        {"cvss_range": "8-10", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "8-10", "epss_range": "0.6-0.8", "cve_count": 0},
        {"cvss_range": "8-10", "epss_range": "0.8-1.0", "cve_count": 1}
    ]
}

GROWTH_INPUT = {
    "company_name": "TestCorp1",
    "data_points": [
        {"date": "2026-03-26", "new_cves": 0},
        {"date": "2026-03-27", "new_cves": 2},
        {"date": "2026-03-28", "new_cves": 0},
        {"date": "2026-03-29", "new_cves": 4},
        {"date": "2026-03-30", "new_cves": 1}
    ],
    "summary": {"total_period_increase": 4, "peak_growth_day": "2026-03-29"}
}

# TESTS
def test_visualiser_renders_growth_trend():
    event = {"body": json.dumps(GROWTH_INPUT)}
    
    result = invoke_visualiser(event)
    
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Type"] == "image/png"
    assert result["isBase64Encoded"] is True
    
    # verify base64 string
    img_data = result["body"]
    assert len(img_data) > 100  # image shouldn't be empty

def test_visualiser_renders_heatmap():
    event = {"body": json.dumps(HEATMAP_INPUT)}
    
    result = invoke_visualiser(event)
    
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Type"] == "image/png"
    assert result["isBase64Encoded"] is True
    
    # verify base64 string
    img_data = result["body"]
    assert len(img_data) > 100  # image shouldn't be empty

def test_visualiser_invalid_format_error():
    # input json missing both required keys
    invalid_input = {"company_name": "BrokenCorp", "random_key": "data"}
    event = {"body": json.dumps(invalid_input)}
    
    result = invoke_visualiser(event)
    
    assert result["statusCode"] == 400
    body_json = json.loads(result["body"])
    assert "Unknown data format" in body_json["error"]