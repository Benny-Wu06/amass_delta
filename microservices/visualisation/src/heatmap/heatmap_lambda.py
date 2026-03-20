import json
import psycopg2
import os

# --- DB CONFIGURATION CONSTANTS ---
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
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


def get_heatmap_data(db, company_name):
    company_id = fetch_company_id(db, company_name)

    query = """
        SELECT 
            CASE
                WHEN cvss_score < 2 THEN '0-2'
                WHEN cvss_score < 4 THEN '2-4'
                WHEN cvss_score < 6 THEN '4-6'
                WHEN cvss_score < 8 THEN '6-8'
                ELSE '8-10'
            END AS cvss_range,
            CASE 
                WHEN epss_score < 0.2 THEN '0-0.2'
                WHEN epss_score < 0.4 THEN '0.2-0.4'
                WHEN epss_score < 0.6 THEN '0.4-0.6'
                WHEN epss_score < 0.8 THEN '0.6-0.8'
                ELSE '0.8-1.0'
            END AS epss_range,
            COUNT(*) as cve_count
        FROM vulnerabilities
        WHERE company_id = %s
        GROUP BY cvss_range, epss_range;
    """
    db.execute(query, (company_id,))
    return db.fetchall()


def format_heatmap(raw_data):
    cvss_buckets = ["0-2", "2-4", "4-6", "6-8", "8-10"]
    epss_buckets = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]

    # lookup map from the database results
    map = {(row[0], row[1]): row[2] for row in raw_data}

    heatmap_grid = []
    for epss in epss_buckets:
        for cvss in cvss_buckets:
            heatmap_grid.append(
                {
                    "cvss_range": cvss,
                    "epss_range": epss,
                    "cve_count": map.get((cvss, epss), 0),
                }
            )

    return heatmap_grid


############## LAMBDA FUNCTION ###############


def heatmap_lambda(event, context):
    try:
        conn = get_db_connection()

        with conn.cursor() as db_cursor:
            company_name = event.get("pathParameters", {}).get("company_name")

            if not company_name:
                return {
                    "statusCode": 404,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": f"Company {company_name} not found"}),
                }

            raw_data = get_heatmap_data(db_cursor, company_name)
            grid = format_heatmap(raw_data)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"company_name": company_name, "heatmap_grid": grid}
                ),
            }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }

    finally:
        if conn:
            conn.close()
