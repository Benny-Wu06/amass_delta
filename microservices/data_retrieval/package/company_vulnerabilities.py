import datetime
from decimal import Decimal

import psycopg2
import boto3
import os
import json

password = "testdiddyblud"

conn = None

# /v1/companies/{company_name}/vulnerabilities
# i.e getting ALL of a company's vulnerabilities by their name
def lambda_handler(event, context):

    path_params = event.get('pathParameters', {})
    target_company = path_params.get('company_name')

    if not target_company:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Company name is required in the URL"})
        }
    return get_company_vulnerabiltiies(target_company)

def get_company_vulnerabiltiies(target_company):
    try:
        conn = None
        DB_PASSWORD = os.environ.get('DB_PASSWORD')
        DB_HOST = os.environ.get('DB_HOST')
        cert_path = os.environ.get('CERT_PATH', 'global-bundle.pem')

        conn = psycopg2.connect(
            host=DB_HOST,
            port=5432,
            database=os.environ.get('DB_NAME', 'postgres'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=DB_PASSWORD,
            sslmode='require',
            connect_timeout = 50,
            sslrootcert=cert_path
        )
        cur = conn.cursor()

        # Retrieval Query
        query = '''
            SELECT 
                v.cve_id, 
                c.company_id, 
                v.vulnerability_name, 
                v.cvss_score, 
                v.cvss_severity
            FROM vulnerabilities v
            JOIN companies c ON v.company_id = c.id
            WHERE c.company_name = %s;
        '''
        
        cur.execute(query, (target_company,))

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