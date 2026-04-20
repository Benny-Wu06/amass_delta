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

def calculate_risk(avg_cvss, avg_epss):
    if avg_cvss is None or avg_epss is None:
        return 0, "UNKNOWN"
    
    if avg_cvss == 0 or avg_epss == 0:
        return 0, "UNKNOWN"

    risk_index = round((float(avg_cvss) / 10) * 0.6 + float(avg_epss) * 0.4, 4)

    if risk_index >= 0.8:
        rating = "CRITICAL"
    elif risk_index >= 0.6:
        rating = "HIGH"
    elif risk_index >= 0.4:
        rating = "MEDIUM"
    else:
        rating = "LOW"

    return risk_index, rating

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
                v.cvss_score, 
                v.epss_score, 
                v.date_added, 
                v.due_date,
                c.company_name
            FROM vulnerabilities v
            LEFT JOIN companies c ON v.company_id = c.id
            ORDER BY {db_column} {direction};
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        cve_list = []
        for row in rows:
            risk_index, risk_rating = calculate_risk(row[1], row[2])
            cve_list.append({
                "cve_id": row[0],
                "risk_index": risk_index,
                "risk_rating": risk_rating,
                "date_added": row[3],
                "due_date": row[4],
                "company_name": row[5]
            })

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