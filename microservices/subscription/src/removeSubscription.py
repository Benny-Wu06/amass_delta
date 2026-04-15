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
    company_name = path_params.get("company_name")

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

    if not company_name:
        logger.error("Error Company name is required in URL")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Company name is required in URL"}),
        }
    
    company_name = company_name.replace("+", " ").replace("%20", " ")

    query_params = event.get("queryStringParameters") or {}
    email = (query_params.get("email") or "").strip().lower()

    if not email or "@" not in email:
        logger.error("Error Invalid email: %s", email)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Valid email is required"}),
        }

    return remove_company_from_watchlist(watchlist_id, email, company_name)


def remove_company_from_watchlist(watchlist_id, email, company_name):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM watchlist_companies
            WHERE watchlist_id = %s
              AND company_name = %s
              AND watchlist_id IN (
                  SELECT id FROM watchlists WHERE id = %s AND email = %s
              )
            RETURNING id
            """,
            (watchlist_id, company_name, watchlist_id, email),
        )
        row = cur.fetchone()

        if not row:
            logger.info(
                "Nothing to remove: watchlist_id=%s email=%s company=%s",
                watchlist_id, email, company_name,
            )
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "error": "Watchlist or company not found"
                }),
            }

        conn.commit()

        logger.info(
            "Removed company=%s from watchlist id=%d for email: %s",
            company_name, watchlist_id, email,
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Company removed from watchlist",
                "watchlist_id": watchlist_id,
                "company_name": company_name,
            }),
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error("Error removing company from watchlist: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
    finally:
        if conn:
            conn.close()