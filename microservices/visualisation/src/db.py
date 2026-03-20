import psycopg2
import os

# --- DB CONFIGURATION CONSTANTS ---
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
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
