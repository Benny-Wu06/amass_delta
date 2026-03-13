import psycopg2
import boto3
import json

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
    
    if not target_company:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Company name is required in the URL"})
        }
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

        # TODO WRITE QUERY
        query = '''
            SELECT 
                v.cve_id, 
                c.company_name, 
                v.vulnerability_name, 
                v.cvss_score, 
                v.cvss_severity
            FROM vulnerabilities v
            JOIN companies c ON v.company_id = c.id
            WHERE c.company_name = %s;
        '''
        
        cur.execute(query, (target_company,))

        # transform result into list of dictionaries 
        results = ['TODO']
        cur.close()

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(results)
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