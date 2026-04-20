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
    path_params = event.get("pathParameters") or {}
    watchlist_id = path_params.get("id")

    if not watchlist_id:
        logger.error("Error Watchlist id is required in URL")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Watchlist id is required in URL"}),
        }

    try:
        watchlist_id = int(watchlist_id)
    except ValueError:
        logger.error("Error Invalid watchlist id: %s", watchlist_id)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Watchlist id must be an integer"}),
        }

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
    if not email or "@" not in email:
        logger.error("Error Invalid email: %s", email)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Valid email is required"}),
        }

    return delete_watchlist(watchlist_id, email)


def delete_watchlist(watchlist_id, email):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM watchlists
            WHERE id = %s AND email = %s
            RETURNING id
            """,
            (watchlist_id, email),
        )
        row = cur.fetchone()
        if not row:
            logger.info("Watchlist not found or email mismatch: id=%s email=%s", watchlist_id, email)
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Watchlist not found"}),
            }

        conn.commit()

        logger.info("Deleted watchlist id=%d for email: %s", watchlist_id, email)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Watchlist deleted successfully",
                "id": watchlist_id,
            }),
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error("Error deleting watchlist: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
    finally:
        if conn:
            conn.close()