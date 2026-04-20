from fastapi import APIRouter, HTTPException, Depends
from microservices.auth.app.schemas import UserCreate, UserLogin
from microservices.auth.app.auth_utils import hash_password, verify_password, create_access_token, decode_access_token
import os
import psycopg2
from fastapi.security import OAuth2PasswordBearer

# --- DB CONFIGURATION CONSTANTS ---
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SSL_MODE = "prefer"
DB_SSL_ROOT_CERT = "/certs/global-bundle.pem"
DB_TIMEOUT = 3

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode=DB_SSL_MODE,
        connect_timeout=DB_TIMEOUT,
        sslrootcert=DB_SSL_ROOT_CERT,
    )

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/signup")
def signup(user: UserCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # ERROR CHECK: if user exists
        cur.execute("SELECT email FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # hash and save
        hashed_pwd = hash_password(user.password)
        cur.execute(
            "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id",
            (user.email, hashed_pwd)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return {"message": "User created successfully", "email": user.email, "id": user_id}
    finally:
        cur.close()
        conn.close()

@router.post("/login")
def login(user: UserLogin):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT hashed_password FROM users WHERE email = %s", (user.email,))
        result = cur.fetchone()
        
        # ERROR CHECK
        if not result or not verify_password(user.password, result[0]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_access_token(data={"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        cur.close()
        conn.close()

@router.post("/logout")
def logout(token: str = Depends(oauth2_schema)):

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db_connection()
    cur = conn.cursor()

    # Inserting the token in black list, so user doesnt login again with same token
    exp = payload.get("exp")
    cur.execute(
        "INSERT INTO token_blacklist (token, expires_at) VALUES (%s, to_timestamp(%s))",
        (token, exp)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Successfully logged out"}
