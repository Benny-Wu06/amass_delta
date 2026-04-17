import json
import os
import pytest
import boto3
import psycopg2
from botocore.config import Config
# from microservices.auth.app.auth_utils import hash_password
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password[:72].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

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

def invoke_auth(path, method, body=None, headers=None):
    payload = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "rawQueryString": "",
        "headers": headers or {"content-type": "application/json"},
        "body": json.dumps(body) if body else None,
        "isBase64Encoded": False,
        "requestContext": {
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test"
            }
        }
    }
    
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    
    raw_payload = response["Payload"].read().decode("utf-8")
    parsed = json.loads(raw_payload)

    # DEBUG 
    if "statusCode" not in parsed:
        error_msg = parsed.get("errorMessage", "Unknown AWS Error")
        pytest.fail(f"Lambda Crashed: {error_msg}\nFull Response: {raw_payload}")
            
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
    cur = conn_db.cursor()
    cur.execute("INSERT INTO users (email, hashed_password) VALUES (%s, %s);", (TEST_EMAIL, "already_hashed"))
    conn_db.commit()
    cur.close()
    
    payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    result = invoke_auth("/auth/signup", "POST", body=payload)
    
    assert result["statusCode"] == 400 
    assert "already registered" in str(result["body"]).lower()

def test_signup_invalid_json():
    payload = {"wrong_key": "not_an_email"}
    
    result = invoke_auth("/auth/signup", "POST", body=payload)
    
    # returns 422 unprocessable entity
    assert result["statusCode"] == 422

def test_login_success(conn_db, cleanup_user):

    hashed_pwd = hash_password(TEST_PASSWORD)
    cur = conn_db.cursor()
    cur.execute(
        "INSERT INTO users (email, hashed_password) VALUES (%s, %s);", 
        (TEST_EMAIL, hashed_pwd)
    )
    conn_db.commit()
    cur.close()

    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    result = invoke_auth("/auth/login", "POST", body=payload)

    assert result["statusCode"] == 200
    assert result["function_error"] is None
    assert "access_token" in result["body"]
    assert result["body"]["token_type"] == "bearer"

def test_login_fail(conn_db, cleanup_user):

    hashed_pwd = hash_password(TEST_PASSWORD)
    cur = conn_db.cursor()
    cur.execute(
        "INSERT INTO users (email, hashed_password) VALUES (%s, %s);", 
        (TEST_EMAIL, hashed_pwd)
    )
    conn_db.commit()
    cur.close()

    payload = {
        "email": TEST_EMAIL,
        "password": "INCORRECT_PASSWORD"
    }

    result = invoke_auth("/auth/login", "POST", body=payload)

    assert result["statusCode"] == 401
    assert result["function_error"] is None
    assert "access_token" not in result["body"]
    assert "Invalid credentials" in str(result["body"])

def test_logout_success(conn_db, cleanup_user):

    hashed_pwd = hash_password(TEST_PASSWORD)
    cur = conn_db.cursor()
    cur.execute(
        "INSERT INTO users (email, hashed_password) VALUES (%s, %s);", 
        (TEST_EMAIL, hashed_pwd)
    )
    conn_db.commit()
    cur.close()

    login_payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    login_result = invoke_auth("/auth/login", "POST", body=login_payload)

    token = login_result["body"].get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    result = invoke_auth("/auth/logout", "POST", headers=headers)

    assert result["statusCode"] == 200
    assert result["function_error"] is None
    assert "Successfully logged out" in str(result["body"])

    cur = conn_db.cursor()
    cur.execute("SELECT token FROM token_blacklist WHERE token = %s;", (token,))
    blacklisted = cur.fetchone()
    cur.close()
    assert blacklisted is not None