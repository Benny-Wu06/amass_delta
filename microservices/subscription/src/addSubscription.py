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
    company_name = (data.get("company_name") or "").strip()

    if not email or "@" not in email:
        logger.error("Error Invalid email: %s", email)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Valid email is required"}),
        }

    if not company_name:
        logger.error("Error Company name is required")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Company name is required"}),
        }

    return add_company_to_watchlist(watchlist_id, email, company_name)


def add_company_to_watchlist(watchlist_id, email, company_name):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM watchlists WHERE id = %s AND email = %s",
            (watchlist_id, email),
        )
        if not cur.fetchone():
            logger.info("Watchlist not found or email mismatch: id=%s email=%s", watchlist_id, email)
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Watchlist not found"}),
            }

        cur.execute(
            """
            INSERT INTO watchlist_companies (watchlist_id, company_name)
            VALUES (%s, %s)
            ON CONFLICT (watchlist_id, company_name) DO NOTHING
            RETURNING id, added_at
            """,
            (watchlist_id, company_name),
        )
        row = cur.fetchone()

        if not row:
            logger.info("Company already in watchlist: id=%s company=%s", watchlist_id, company_name)
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Company is already in this watchlist"
                }),
            }

        entry_id, added_at = row
        conn.commit()

        logger.info("Added company=%s to watchlist id=%d", company_name, watchlist_id)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Company added to watchlist",
                "id": entry_id,
                "watchlist_id": watchlist_id,
                "company_name": company_name,
                "added_at": str(added_at),
            }),
        }

    except Exception as e:
        logger.error("Error adding company to watchlist: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
    finally:
        if conn:
            conn.close()