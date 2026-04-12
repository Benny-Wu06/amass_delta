import logging
import psycopg2
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    return get_all_companies()


def get_all_companies():
    conn = None
    try:
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        DB_HOST = os.environ.get("DB_HOST")
        cert_path = os.environ.get("CERT_PATH", "global-bundle.pem")

        conn = psycopg2.connect(
            host=DB_HOST,
            port=5432,
            database=os.environ.get("DB_NAME", "postgres"),
            user=os.environ.get("DB_USER", "postgres"),
            password=DB_PASSWORD,
            sslmode="require",
            connect_timeout=50,
            sslrootcert=cert_path,
        )
        cur = conn.cursor()

        # Query to get all unique company names
        query = "SELECT DISTINCT company_name FROM companies ORDER BY company_name ASC;"
        cur.execute(query)
        

        rows = cur.fetchall()
        
        companies_list = sorted([row[0] for row in rows])

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "count": len(companies_list),
                "companies": companies_list
            }),
        }

    except Exception as e:
        logger.error("Failed to fetch company list: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to retrieve company list"}),
        }

    finally:
        if conn:
            conn.close()