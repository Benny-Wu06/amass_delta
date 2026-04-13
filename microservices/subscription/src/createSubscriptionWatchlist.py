import json
import logging
import os
import boto3
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
sns = boto3.client("sns")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
CISA_KEY = "enriched/enriched.json"
cert_path = os.environ.get("CERT_PATH", "global-bundle.pem")


def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require",
        connect_timeout=3,
        sslrootcert=cert_path,
    )
    return conn

def lambda_handler(event, context):
    body = event.get("body")
    if not body:
        logger.error("No body in request")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Request body is required"}),
        }

    try:
        data = json.loads(body) if isinstance(body, str) else body
    except json.JSONDecodeError:
        logger.error("Error Invalid JSON body")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()

    if not email or "@" not in email:
        logger.error("Error Invalid email: %s", email)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Valid email is required"}),
        }
    if not name:
        logger.error("Error Watchlist name is required")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Watchlist name is required"}),
        }
    if len(name) < 2:
        logger.error("Error Watchlist name must be at least 2 characters")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Name must be at least 2 chars"}),
        }

    return create_watchlist(email, name)

def create_watchlist(email, name):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO watchlists (email, name)
            VALUES (%s, %s)
            ON CONFLICT (email, name) DO NOTHING
            RETURNING id
            """,
            (email, name),
        )
        row = cur.fetchone()

        if not row:
            logger.info("Watchlist already exists for email: %s name: %s", email, name)
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Watchlist with this email and name already exists"
                }),
            }

        watchlist_id = row[0]
        conn.commit()

        logger.info("Created watchlist id=%d for email: %s name: %s", watchlist_id, email, name)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Watchlist created successfully",
                "id": watchlist_id,
            }),
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error("Error creating watchlist: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
    finally:
        if conn:
            conn.close()