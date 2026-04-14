import json
import os
import pytest
import boto3
import psycopg2
from botocore.config import Config

# CONFIGURATION
AWS_REGION = "ap-southeast-2"
LAMBDA_NAME = "auth-service"

lambda_client = boto3.client(
    "lambda", 
    region_name=AWS_REGION,
    config=Config(read_timeout=30, connect_timeout=10)
)

# FIXTRURES
@pytest.fixture(scope="module")
def conn_db():
    conn = None
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    cert_path = os.environ.get("CERT_PATH", "global-bundle.pem")
    print('\nDB_PASSWORD', DB_PASSWORD)
    print('\ndb_host', DB_HOST)
    conn = psycopg2.connect(
            host=DB_HOST,
            port=5432,
            database=os.environ.get("DB_NAME", "postgres"),
            user=os.environ.get("DB_USER", "postgres"),
            password=DB_PASSWORD,
            sslmode="prefer",
            connect_timeout=5,
            sslrootcert=cert_path,
    )
    print('\nconnection succesful')
    yield conn
    conn.close()

# TEST CONSTANTS
TEST_EMAIL = "component_test@unsw.edu.au"
TEST_PASSWORD = "testing_password"

@pytest.fixture(scope="function")
def cleanup_user(conn_db):
    """Yields and then deletes the test user after the test finishes."""
    yield
    cur = conn_db.cursor()
    cur.execute("DELETE FROM users WHERE email = %s;", (TEST_EMAIL,))
    conn_db.commit()
    cur.close()

# HELPER: Follows your specific Mangum-compatible structure
def invoke_auth(path, method, body=None, headers=None):
    payload = {
        "resource": "/{proxy+}",
        "path": path,
        "httpMethod": method,
        "headers": headers or {"Content-Type": "application/json"},
        "body": json.dumps(body) if body else None,
        "requestContext": {
            "resourcePath": "/{proxy+}",
            "httpMethod": method,
            "path": path
        }
    }
    
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    
    raw_payload = response["Payload"].read().decode("utf-8")
    parsed = json.loads(raw_payload)

    # --- NEW DEBUG BLOCK ---
    if "statusCode" not in parsed:
        # This catches "errorMessage" or "stackTrace" from AWS crashes
        error_msg = parsed.get("errorMessage", "Unknown AWS Error")
        pytest.fail(f"Lambda Crashed: {error_msg}\nFull Response: {raw_payload}")
    # -----------------------
            
    return {
        "statusCode": parsed.get("statusCode"),
        "body": json.loads(parsed.get("body", "{}")) if isinstance(parsed.get("body"), str) else parsed.get("body"),
        "function_error": response.get("FunctionError")
    }

# TESTS
def test_signup_success(cleanup_user):
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    result = invoke_auth("/auth/signup", "POST", body=payload)
    
    assert result["statusCode"] == 201 or result["statusCode"] == 200
    assert result["function_error"] is None
    assert result["body"]["email"] == TEST_EMAIL
    assert "id" in result["body"]

def test_signup_duplicate_email(conn_db, cleanup_user):
    # 1. Manual insert to ensure user exists
    cur = conn_db.cursor()
    cur.execute("INSERT INTO users (email, hashed_password) VALUES (%s, %s);", (TEST_EMAIL, "already_hashed"))
    conn_db.commit()
    cur.close()
    
    # 2. Try to signup with same email
    payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    result = invoke_auth("/auth/signup", "POST", body=payload)
    
    # FastAPI usually returns 400 for existing users
    assert result["statusCode"] == 400 
    assert "already registered" in str(result["body"]).lower()

def test_signup_invalid_json():
    payload = {"wrong_key": "not_an_email"}
    
    result = invoke_auth("/auth/signup", "POST", body=payload)
    
    # FastAPI returns 422 Unprocessable Entity for Pydantic validation errors
    assert result["statusCode"] == 422