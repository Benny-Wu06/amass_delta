import psycopg2
import boto3
import json
from datetime import datetime

password = "testdiddyblud"

conn = None

# /v1/companies/{company_name}
# get vulnerability statistics (avg cvss, epss) about a company

# EXAMPLE OUTPUT:
# {
#   "company": "Microsoft",
#   "cve_count": 154,
#   "avg_epss": 0.125,
#   "avg_cvss": 7.2,
#   "risk_index": 8.5,
#   "risk_rating": "Severe",
#   "time": {
#     "timestamp": "2026-03-13T05:40:39.063Z",
#     "timezone": "GMT+11"
#   }
# }
def lambda_handler(event, context):
    path_params = event.get('pathParameters', {})
    target_company = path_params.get('company_name')
    
    target_company = 'PedalDynamics'
    if not target_company:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Company name is required in the URL"})
        }
    get_company_summary(target_company)


def get_company_summary(company):
    try:
        conn = psycopg2.connect(
            host='testdb.cjwhnekr8yms.us-east-1.rds.amazonaws.com',
            port=5432,
            database='postgres',
            user='postgres',
            password=password,
            sslmode='prefer',
            connect_timeout=3,
        sslrootcert='/certs/global-bundle.pem'
        )
        cur = conn.cursor()
        
        query = '''
            SELECT 
            c.company_name as company,
            COUNT(v.cve_id) as cve_count,
            AVG(v.epss_score) as avg_epss,
            AVG(v.cvss_score) as avg_cvss,
            c.risk_index,
            c.risk_rating
        FROM companies c
        LEFT JOIN vulnerabilities v ON c.id = v.company_id
        WHERE c.company_name = %s
        GROUP BY c.id;
        '''
        
        cur.execute(query, (target_company,))
        row = cur.fetchone()
        company, cve_count, avg_epss, avg_cvss, risk_index, risk_rating = row
        avg_epss = float(avg_epss)
        avg_cvss = float(avg_cvss)
        risk_index = float(risk_index)
        time_object = {'timestamp': str(datetime.now()), 'timezone': 'GMT+!11'}
        
        result = json.dumps({
            'company': company,
            'cve_count': cve_count,
            'avg_epss': avg_epss,
            'risk_index': risk_index,
            'risk_rating': risk_rating,
            'time': time_object
        })
        cur.close()

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
    except Exception as e:
        print(f"Database error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": "Failed to retrieve data"})
        }
    finally:
        if conn:
            conn.close()

get_company_summary(1,1)
