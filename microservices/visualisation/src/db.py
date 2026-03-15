import psycopg2

# --- DB CONFIGURATION CONSTANTS ---
DB_HOST = 'testdb.cjwhnekr8yms.us-east-1.rds.amazonaws.com'
DB_PORT = 5432
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = 'testdiddyblud'  # Remember to move this to an env var eventually!
DB_SSL_MODE = 'prefer'
DB_SSL_ROOT_CERT = '/certs/global-bundle.pem'
DB_TIMEOUT = 3

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS, 
        sslmode=DB_SSL_MODE,
        connect_timeout=DB_TIMEOUT,
        sslrootcert=DB_SSL_ROOT_CERT
    )
