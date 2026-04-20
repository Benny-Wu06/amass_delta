import logging
import psycopg2
import json
import os
from datetime import date, datetime
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Helper to handle Date serialization in JSON
def date_serialiser(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serialisable")

def lambda_handler(event, context):
    query_params = event.get("queryStringParameters") or {}
    sort_by = query_params.get("sort_by", "date_added")
    
    return get_all_cves(sort_by)

def get_all_cves(sort_column):
    conn = None

    allowed_sorts = {
        "date_added": ("v.date_added", "DESC"),
        "due_date": ("v.due_date", "ASC")
    }
    db_column, direction = allowed_sorts.get(sort_column, ("v.date_added", "DESC"))

    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=5432,
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            sslmode="require",
            sslrootcert=os.environ.get("CERT_PATH", "global-bundle.pem"),
        )
        cur = conn.cursor()

        # Update query to select the correct fields and use the dynamic sort
        query = f"""
            SELECT 
                v.cve_id,
                v.vulnerability_name,
                v.description, 
                v.cvss_score, 
                v.epss_score,
                v.cvss_severity, 
                v.date_added, 
                v.due_date,
                c.company_name
            FROM vulnerabilities v
            LEFT JOIN companies c ON v.company_id = c.id
            ORDER BY {db_column} {direction};
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        cve_list = [
            {
                "cve_id": row[0],
                "vulnerability_name": row[1],
                "description": row[2],
                "cvss_score": row[3],
                "epss_score": row[4],
                "severity": row[5],
                "date_added": row[6],
                "due_date": row[7],
                "company_name": row[8]
            } for row in rows
        ]

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "count": len(cve_list),
                "cves": cve_list
            }, default=date_serialiser), 
        }

    except Exception as e:
        logger.error("Failed to fetch CVE list: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to retrieve CVE list"}),
        }
    finally:
        if conn:
            conn.close()