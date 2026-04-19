import requests
import json
import os
import psycopg2
from datetime import datetime, timedelta

# CONFIG
BASE_URL_STOCKS = "https://tdxz7z58l6.execute-api.ap-southeast-2.amazonaws.com/prod"

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

### CVE GROWTH ###
def get_internal_cve_growth(company_name, from_date, to_date):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM companies WHERE company_name = %s;", (company_name,))
            res = cur.fetchone()
            if not res: return {}
            company_id = res[0]

            query = """
                SELECT date_added::text, COUNT(*) 
                FROM vulnerabilities
                WHERE company_id = %s 
                AND date_added >= %s AND date_added <= %s
                GROUP BY date_added ORDER BY date_added ASC;
            """
            cur.execute(query, (company_id, from_date, to_date))
            return {row[0]: row[1] for row in cur.fetchall()}
    finally:
        if conn: conn.close()

# COMAPNY SYMBOLS THAT ALIGN WITH BOTH CHARLIE AND AMASS
VALID_COMPANY_SYMBOLS = {
    "GOOGL": "Google", 
    "AAPL": "Apple", 
    "MSFT": "Microsoft", 
    "AVGO": "Broadcom", 
    "META": "Meta", 
    "CSCO": "Cisco", 
    "INTC": "Intel"
}

### INTEGRATION LOGIC ###
def stocks_cve_growth_lambda(event, context):
    try:
        path_params = event.get("pathParameters") or {}
        company_symbol = path_params.get("company_symbol")
        company_name = VALID_COMPANY_SYMBOLS.get(company_symbol)

        # ERROR CHECK: If symbol is not in our allowed list
        if not company_name:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": f"Invalid or unsupported company symbol: {company_symbol}",
                    "supported_symbols": list(VALID_COMPANY_SYMBOLS.keys())
                })
            }

        query_params = event.get("queryStringParameters") or {}
        from_str = query_params.get("from", "2025-01-01")
        to_str = query_params.get("to", datetime.now().strftime("%Y-%m-%d"))

        # ERROR CHECK: invalid date range
        if from_str > to_str:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Invalid date range: 'from' date must be before 'to' date.",
                    "provided": {"from": from_str, "to": to_str}
                })
            }

        # auth CHARLIE
        EMAIL = os.environ.get("CHARLIE_EMAIL", "dearryllan@gmail.com")
        PASSWORD = os.environ.get("CHARLIE_PASSWORD", "mypassword")
        
        login_res = requests.post(
            f"{BASE_URL_STOCKS}/auth/login", 
            json={"email": EMAIL, "password": PASSWORD},
            timeout=5
        )
        login_res.raise_for_status()
        
        auth_payload = login_res.json().get('authentication', {})
        id_token = auth_payload.get('IdToken')
        
        if not id_token:
            raise ValueError("Auth succeeded but IdToken is missing from response")

        # fetch stock prices
        stock_url = f"{BASE_URL_STOCKS}/stocks/{company_symbol}/prices"
        stock_resp = requests.get(
            stock_url, 
            headers={"Authorization": f"Bearer {id_token}"}, 
            params={"from": from_str, "to": to_str},
            timeout=5
        )
        stock_resp.raise_for_status()
        
        # fetch growth data
        growth_lookup = get_internal_cve_growth(company_name, from_str, to_str)

        # merge the two data
        merged_data = []
        stock_data = stock_resp.json().get("data", [])
        
        for entry in stock_data:
            date_key = entry.get("date")
            # Calculate diff, defaulting to 0 if keys are missing
            open_p = entry.get("open", 0)
            close_p = entry.get("close", 0)
            
            merged_data.append({
                "date": date_key,
                "price_diff": round(close_p - open_p, 2),
                "cve_growth": growth_lookup.get(date_key, 0)
            })

        # RETURN STANDARDISED RESPONSE
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "company": company_name,
                "period": {"from": from_str, "to": to_str},
                "merged_results": merged_data
            })
        }

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }