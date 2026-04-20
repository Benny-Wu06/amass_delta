import json
import logging
import os
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
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
    query_params = event.get("queryStringParameters") or {}
    email = (query_params.get("email") or "").strip().lower()

    if not email or "@" not in email:
        logger.error("Error Invalid email: %s", email)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Valid email is required"}),
        }

    return list_watchlists(email)


def list_watchlists(email):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                w.id,
                w.name,
                w.created_at,
                COUNT(wc.id) AS company_count
            FROM watchlists w
            LEFT JOIN watchlist_companies wc ON wc.watchlist_id = w.id
            WHERE w.email = %s
            GROUP BY w.id
            ORDER BY w.created_at DESC
            """,
            (email,),
        )
        rows = cur.fetchall()

        watchlists = []
        for wl_id, name, created_at, company_count in rows:
            watchlists.append({
                "id": wl_id,
                "name": name,
                "created_at": str(created_at),
                "company_count": company_count,
            })

        cur.close()
        logger.info("Success retrieved %d watchlists for email: %s", len(watchlists), email)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "email": email,
                "watchlists": watchlists,
            }),
        }

    except Exception as e:
        logger.error("Error listing watchlists: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to retrieve watchlists"}),
        }
    finally:
        if conn:
            conn.close()