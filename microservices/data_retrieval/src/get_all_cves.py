import logging
import psycopg2
import json
import os
from datetime import date, datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Helper to handle Date serialization in JSON
def date_serializer(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def lambda_handler(event, context):
    query_params = event.get("queryStringParameters") or {}
    sort_by = query_params.get("sort_by", "date_added")
    
    return get_all_cves(sort_by)

def get_all_cves(sort_column):
    conn = None

    allowed_sorts = {
        "date_added": "date_added",
        "due_date": "due_date"
    }
    db_column = allowed_sorts.get(sort_column, "date_added")

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
        query = f"SELECT cve_id, date_added, due_date FROM cves ORDER BY {db_column} ASC;"
        cur.execute(query)
        rows = cur.fetchall()
        
        cve_list = [
            {
                "cve_id": row[0],
                "date_added": row[1],
                "due_date": row[2]
            } for row in rows
        ]

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "count": len(cve_list),
                "cves": cve_list
            }, default=date_serializer), 
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