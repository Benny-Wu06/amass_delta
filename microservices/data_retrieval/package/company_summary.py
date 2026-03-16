import psycopg2
import boto3
import json
from datetime import datetime
from zoneinfo import ZoneInfo

password = "testdiddyblud"

conn = None

# /v1/companies/{company_name}
# get vulnerability statistics (avg cvss, epss) about a company
def lambda_handler(event, context):
    path_params = event.get('pathParameters', {})
    target_company = path_params.get('company_name')

    if not target_company:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Company name is required in the URL"})
        }
    return get_company_summary(target_company)


def get_company_summary(target_company):
    try:
        conn = psycopg2.connect(
            host='testdb.cjwhnekr8yms.us-east-1.rds.amazonaws.com',
            port=5432,
            database='postgres',
            user='postgres',
            password=password,
            sslmode='prefer',
            connect_timeout=50,
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
        tz = ZoneInfo('Australia/Sydney')
        curr_time = datetime.now(tz)
        time_object = {'timestamp': str(curr_time), 'timezone': curr_time.strftime('%Z')}
        
        result = json.dumps({
            'company': company,
            'cve_count': cve_count,
            'avg_epss': avg_epss,
            'avg_cvss': avg_cvss,
            'risk_index': risk_index,
            'risk_rating': risk_rating,
            'time': time_object
        })
        cur.close()

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': result
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
