import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.auth_utils import hash_password

client = TestClient(app)

@pytest.fixture
def mock_db():
    # patch where it is defined
    with patch("app.routes.get_db_connection") as mocked_get_conn:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mocked_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        yield mock_cursor
        
### TESTS ###
def test_signup_flow(mock_db):
    # Setup: Assume email doesn't exist
    mock_db.fetchone.return_value = None
    
    payload = {"email": "student@unsw.edu.au", "password": "password123"}
    response = client.post("/auth/signup", json=payload)
    
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

def test_signup_password_too_short(mock_db):
    # setup a password shorter than 8 characters
    payload = {"email": "student@unsw.edu.au", "password": "123"}
    
    response = client.post("/auth/signup", json=payload)
    
    # STATUS CODE: Unprocessable Entity
    assert response.status_code == 422

    # FastAPI's default error
    errors = response.json()["detail"]
    assert errors[0]["type"] == "string_too_short"
    assert "password" in errors[0]["loc"]

def test_signup_duplicate_fails(mock_db):
    mock_db.fetchone.return_value = ("student@unsw.edu.au",)
    
    payload = {"email": "student@unsw.edu.au", "password": "password123"}
    response = client.post("/auth/signup", json=payload)
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_validation(mock_db):
    # generate a hash
    password = "password123"
    hashed = hash_password(password)
    
    # mock return the hash in a tuple
    mock_db.fetchone.return_value = (hashed,)
    
    payload = {"email": "student@unsw.edu.au", "password": password}
    response = client.post("/auth/login", json=payload)
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user_not_found(mock_db):
    # mock user doesn't exist
    mock_db.fetchone.return_value = None
    
    payload = {"email": "stranger@unsw.edu.au", "password": "anypassword"}
    response = client.post("/auth/login", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_wrong_password(mock_db):
    # create a hash for 'correct_password'
    correct_hash = hash_password("correct_password")
    mock_db.fetchone.return_value = (correct_hash,)
    
    # log in with 'wrong_password'
    payload = {"email": "student@unsw.edu.au", "password": "wrong_password"}
    response = client.post("/auth/login", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_logout_no_token(mock_db):
    response = client.post("auth/logout")
    # no token was given
    assert response.status_code == 401

def test_logout_invalid_token(mock_db):
    # attempt logout with a fake token
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer this.is.fake"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_logout_correct(mock_db):

    correct_hash = hash_password("correct_password")
    mock_db.fetchone.return_value = (correct_hash,)

    payload = {"email": "student@unsw.edu.au", "password": "correct_password"}
    response = client.post("/auth/login", json=payload)
    token = response.json()["access_token"]

    response = client.post(
        "auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"