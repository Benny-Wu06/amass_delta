import datetime
from decimal import Decimal

import psycopg2
import os
import json

conn = None


# /v1/companies/{company_name}/vulnerabilities
# i.e getting ALL of a company's vulnerabilities by their name
def lambda_handler(event, context):

    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}
    target_company = path_params.get("company_name")

    min_cvss = query_params.get("min_cvss")
    min_epss = query_params.get("min_epss")
    validated_cvss = None
    validated_epss = None

    if not target_company:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Company name is required in the URL"}),
        }
    
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
    try:
        conn = None
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
                c.company_id, 
                v.vulnerability_name, 
                v.cvss_score, 
                v.cvss_severity,
                v.epss_score
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
                # Check if the value is a Decimal or a Date
                if isinstance(value, (Decimal, datetime.date)):
                    row_dict[key] = str(value)
            results.append(row_dict)

        cur.close()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(results),
        }
    except Exception as e:
        print(f"Database error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Failed to retrieve data"}),
        }
    finally:
        if conn:
            conn.close()