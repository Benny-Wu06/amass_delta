import psycopg2
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import os


# /v1/companies/{company_name}
# get vulnerability statistics (avg cvss, epss) about a company
def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    target_company = path_params.get("company_name")

    if not target_company:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Company name is required in the URL"}),
        }
        
    target_company = str(target_company)
    return get_company_summary(target_company)


def get_company_summary(target_company: str):
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

        # handle whitespace
        target_company = target_company.replace("+", " ")
        target_company = target_company.replace("%20", " ")

        # get aggregated company info - may need to change later to dynamically derive info
        query = """
            SELECT 
            c.company_name as company,
            COUNT(v.cve_id) as cve_count,
            AVG(v.cvss_score) as avg_cvss,
            AVG(v.epss_score) as avg_epss,
            c.risk_index,
            c.risk_rating
        FROM companies c
        LEFT JOIN vulnerabilities v ON c.id = v.company_id
        WHERE c.company_name = %s
        GROUP BY c.id;
        """

        cur.execute(query, (target_company,))
        row = cur.fetchone()

        # company not found
        if not row:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Company not found"})
            }

        # build return object
        company, cve_count, avg_cvss, avg_epss, risk_index, risk_rating = row
        
        if not avg_epss:
            avg_epss = 0
        if not avg_cvss:
            avg_cvss = 0
        if not risk_index:
            risk_index = 0

        avg_epss = float(avg_epss)
        avg_cvss = float(avg_cvss)
        risk_index = float(risk_index)
        tz = ZoneInfo("Australia/Sydney")
        curr_time = datetime.now(tz)
        time_object = {
            "timestamp": str(curr_time),
            "timezone": curr_time.strftime("%Z"),
        }

        result = json.dumps(
            {
                "company": company,
                "cve_count": cve_count,
                "avg_epss": avg_epss,
                "avg_cvss": avg_cvss,
                "risk_index": risk_index,
                "risk_rating": risk_rating,
                "time": time_object,
            }
        )
        cur.close()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result,
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
