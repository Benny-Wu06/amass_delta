import json
import psycopg2
import os
from datetime import datetime, timedelta

# --- DB CONFIGURATION CONSTANTS ---
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SSL_MODE = "prefer"
DB_SSL_ROOT_CERT = "/certs/global-bundle.pem"
DB_TIMEOUT = 3


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode=DB_SSL_MODE,
        connect_timeout=DB_TIMEOUT,
        sslrootcert=DB_SSL_ROOT_CERT,
    )


def fetch_company_id(db, company_name):
    db.execute("SELECT id FROM companies WHERE company_name = %s;", (company_name,))
    row = db.fetchone()
    return row[0] if row else None


def fetch_vulnerability_data(db, company_name, days):
    company_id = fetch_company_id(db, company_name)

    query = """
        SELECT date_added, COUNT(*) as cve_count
        FROM vulnerabilities
        WHERE company_id = %s 
        AND date_added >= CURRENT_DATE - (%s || ' days')::interval
        GROUP BY date_added
        ORDER BY date_added ASC;
    """
    db.execute(query, (company_id, days))
    return db.fetchall()


def calculate_growth_stats(vulnerability_counts, days, reference_date=None):
    if reference_date is None:
        reference_date = datetime.now()

    daily_counts = {str(entry[0]): entry[1] for entry in vulnerability_counts}

    data_points = []
    total_increase = 0
    peak_val = -1
    peak_day = "N/A"

    for i in range(days - 1, -1, -1):
        target_date = (reference_date - timedelta(days=i)).strftime("%Y-%m-%d")
        count = daily_counts.get(target_date, 0)

        data_points.append({"date": target_date, "new_cves": count})

        total_increase += count
        if count > peak_val:
            peak_val = count
            peak_day = target_date

    return data_points, total_increase, peak_day


############## LAMBDA FUNCTION ###############

DEFAULT_DAYS = 30


def cve_growth_lambda(event, context):
    conn = None
    try:
        conn = get_db_connection()

        with conn.cursor() as db_cursor:
            company_name = event.get("pathParameters", {}).get("company_name")

            # days defaults to 30 days if none given
            query_params = event.get("queryStringParameters") or {}
            days = int(query_params.get("days", DEFAULT_DAYS))

            # error check for days
            if days <= 0:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Days has to be greater than zero"}),
                }
            
            # check if company exists
            company_id = fetch_company_id(db_cursor, company_name)
            if (company_name is None) or (company_id is None):
                return {
                    "statusCode": 404,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": f"Company '{company_name}' not found"})
                }

            # process
            raw_vuls = fetch_vulnerability_data(db_cursor, company_name, days)

            data_points, total_increase, peak_day = calculate_growth_stats(
                raw_vuls, days
            )

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "company_name": company_name,
                        "data_points": data_points,
                        "summary": {
                            "total_period_increase": total_increase,
                            "peak_growth_day": peak_day,
                        },
                    }
                ),
            }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        if conn:
            conn.close()
