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
    
    query_params = event.get("queryStringParameters") or {}
    email = (query_params.get("email") or "").strip().lower()

    if not email or "@" not in email:
        logger.error("Error Invalid email: %s", email)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Valid email is required"}),
        }

    return get_watchlist(watchlist_id, email)


def get_watchlist(watchlist_id, email):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, email, name, created_at
            FROM watchlists
            WHERE id = %s AND email = %s
            """,
            (watchlist_id, email),
        )
        watchlist_row = cur.fetchone()

        if not watchlist_row:
            logger.info("Watchlist not found or email mismatch: id=%s email=%s", watchlist_id, email)
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Watchlist not found"}),
            }

        w_id, w_email, w_name, w_created_at = watchlist_row

        cur.execute(
            """
            SELECT
                wc.company_name,
                wc.added_at,
                c.num_vulnerabilities,
                c.avg_cvss,
                c.avg_epss,
                c.risk_index,
                c.risk_rating
            FROM watchlist_companies wc
            LEFT JOIN companies c ON c.company_name = wc.company_name
            WHERE wc.watchlist_id = %s
            ORDER BY wc.added_at DESC
            """,
            (watchlist_id,),
        )
        company_rows = cur.fetchall()

        companies = []
        for cname, added_at, num_vulns, avg_cvss, avg_epss, risk_index, risk_rating in company_rows:
            companies.append({
                "company_name": cname,
                "added_at": str(added_at),
                "num_vulnerabilities": num_vulns if num_vulns is not None else 0,
                "avg_cvss": float(avg_cvss) if avg_cvss is not None else 0,
                "avg_epss": float(avg_epss) if avg_epss is not None else 0,
                "risk_index": float(risk_index) if risk_index is not None else 0,
                "risk_rating": risk_rating if risk_rating is not None else "UNKNOWN",
            })

        cur.close()
        logger.info("Success retrieved watchlist id=%d for email: %s", w_id, w_email)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "id": w_id,
                "email": w_email,
                "name": w_name,
                "created_at": str(w_created_at),
                "companies": companies,
            }),
        }

    except Exception as e:
        logger.error("Error retrieving watchlist: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to retrieve watchlist"}),
        }
    finally:
        if conn:
            conn.close()