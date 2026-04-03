import datetime
import logging
from decimal import Decimal

import psycopg2
import os
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

conn = None


# /v1/companies/{company_name}/vulnerabilities
# i.e getting ALL of a company's vulnerabilities by their name
def lambda_handler(event, context):

    path_params = event.get("pathParameters")
    if path_params is None: path_params = {}
    
    query_params = event.get("queryStringParameters")
    if query_params is None: query_params = {}
    target_company = path_params.get("company_name")
    

    min_cvss = query_params.get("min_cvss")
    min_epss = query_params.get("min_epss")
    validated_cvss = None
    validated_epss = None

    if not target_company:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Company name is required in the URL", "received_params": path_params}),
        }
    
    # handle whitespace
    target_company = target_company.replace("+", " ").replace("%20", " ")

    # Validate Min_cvss and Min_epss
    if min_cvss is not None:
        try:
            val = float(min_cvss)
            if 0 <= val <= 10:
                validated_cvss = val
            else:
                return {"statusCode": 400, "body": json.dumps({"error": "min_cvss must be 0-10"})}
        except ValueError:
            return {"statusCode": 400, "body": json.dumps({"error": "min_cvss must be 0-10"})}


    if min_epss is not None:
        try:
            val = float(min_epss)
            if 0 <= val <= 1:
                validated_epss = val
            else:
                return {"statusCode": 400, "body": json.dumps({"error": "min_epss must be 0-1"})}
        except ValueError:
            return {"statusCode": 400, "body": json.dumps({"error": "min_epss must be 0-1"})}

    return get_company_vulnerabiltiies(target_company, validated_cvss, validated_epss)


def get_company_vulnerabiltiies(target_company, min_cvss=None, min_epss=None):
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

        # Retrieval base Query 
        query = """
            SELECT 
                v.cve_id, 
                c.id, 
                v.vulnerability_name,
                v.description,
                v.date_added,
                v.due_date,
                v.cvss_score,
                v.epss_score, 
                c.risk_index,
                c.risk_rating
            FROM vulnerabilities v
            JOIN companies c ON v.company_id = c.id
            WHERE c.company_name = %s
        """
        params = [target_company]

        if min_cvss is not None:
            query += " AND v.cvss_score >= %s"
            params.append(min_cvss)
        
        if min_epss is not None:
            query += " AND v.epss_score >= %s"
            params.append(min_epss)
        
        query += ";"

        cur.execute(query, tuple(params))

        # transform result into list of dictionaries
        columns = [desc[0] for desc in cur.description]
        results = []
        for row in cur.fetchall():
            row_dict = dict(zip(columns, row))
            for key, value in row_dict.items():
                if isinstance(value, (Decimal, datetime.date, datetime.datetime)):
                    row_dict[key] = str(value)
            results.append(row_dict)

        cur.close()
        response_data = {
            "company": target_company,
            "cve_count": len(results),
            "vulnerabilities": results,
            "time": {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                "timezone": "UTC"
            }
        }
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response_data),
        }
    except Exception as e:
        logger.error("Database error in company_vulnerabilities: %s", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*" 
            },
            "body": json.dumps({
                "error": "Failed to retrieve data",
                "details": str(e),
                "trace": error_details 
            }),
        }
    finally:
        if conn:
            conn.close()