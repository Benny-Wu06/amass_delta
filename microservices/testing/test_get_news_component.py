import json
import pytest
import boto3
from botocore.config import Config

# CONFIGURATION
AWS_REGION = "ap-southeast-2"
LAMBDA_NAME = "integration_get_news"
TEST_SYMBOL = "MSFT"

lambda_client = boto3.client(
    "lambda", 
    region_name=AWS_REGION,
    config=Config(read_timeout=30, connect_timeout=10)
)

def invoke_lambda(payload):
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    raw_payload = response["Payload"].read().decode("utf-8")
    parsed = json.loads(raw_payload)
    
    # extrawct body
    body_content = parsed.get("body", "{}")
    if isinstance(body_content, str):
        body_content = json.loads(body_content)

    return {
        "statusCode": parsed.get("statusCode"),
        "body": body_content,
        "function_error": response.get("FunctionError")
    }

# TESTS
def test_get_news_success():
    event = {
        "pathParameters": {"company_symbol": TEST_SYMBOL},
        "queryStringParameters": {"limit": "5"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 200
    assert result["body"]["symbol"] == TEST_SYMBOL
    assert result["body"]["company"] == "Microsoft"
    assert isinstance(result["body"]["news_data"], list)

def test_get_news_unsupported_symbol():
    event = {
        "pathParameters": {"company_symbol": "BITCOIN"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 404
    assert "error" in result["body"]

def test_get_news_invalid_sentiment():
    event = {
        "pathParameters": {"company_symbol": TEST_SYMBOL},
        "queryStringParameters": {"sentiment": "super-angry"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 400
    assert "Invalid sentiment" in result["body"]["error"]

def test_get_news_invalid_date_order():
    event = {
        "pathParameters": {"company_symbol": TEST_SYMBOL},
        "queryStringParameters": {
            "start_date": "2026-04-20",
            "end_date": "2026-04-10"
        }
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 400
    assert "must be before" in result["body"]["error"]

def test_get_news_limit_bounds():
    event = {
        "pathParameters": {"company_symbol": TEST_SYMBOL},
        "queryStringParameters": {"limit": "500"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 200
    assert "news_data" in result["body"]

def test_get_news_valid_sentiment_filter():
    event = {
        "pathParameters": {"company_symbol": "AAPL"},
        "queryStringParameters": {"sentiment": "positive", "limit": "2"}
    }
    result = invoke_lambda(event)
    
    assert result["statusCode"] == 200
    assert result["body"]["company"] == "Apple"