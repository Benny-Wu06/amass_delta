import datetime
from decimal import Decimal

import psycopg2
import boto3
import os
import json

password = "testdiddyblud"

conn = None
def lambda_handler(event, context):
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    cert_path = os.environ.get('CERT_PATH', 'global-bundle.pem')
    path_params = event.get('pathParameters', {})
    target_company = path_params.get('company_name')

    if not target_company:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Company name is required in the URL"})
        }
    
# need to add will to the inbound security group so he can connect
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=5432,
            database='postgres',
            user='postgres',
            password=DB_PASSWORD,
            sslmode='require',
            connect_timeout = 5,
            sslrootcert=cert_path
        )
        cur = conn.cursor()

        # Retrieval Query 
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

    #     cur.execute('''CREATE TABLE departments (
    #     department_id SERIAL PRIMARY KEY,
    #     department_name VARCHAR(100) NOT NULL UNIQUE,
    #     location VARCHAR(100)
    # );''')
        
        # createCompaniesQuery =  '''create table companies(
        # id serial primary key,
        # name text not null,
        # numVulnerabilities integer, 
        # avgCVSS numeric,
        # avgEPSS numeric,
        # riskIndex numeric not null,
        # riskRating text not null
        # earliestVulnerabilityDate date);'''

        # createVulnerabilitiesQuery = '''create table vulnerabilities(
        # cveId varchar(primary key
        
        
        
        # );'''

        print('success')

        # preprocessing
        # cur.execute('''INSERT INTO vulnerabilities (cveId, companyName, cvss, epss) VALUES
        # ('Engineering', 'San Francisco'),
        # ('Human Resources', 'New York'),
        # ('Marketing', 'London'),
        # ('Sales', 'Sydney');''')
    #     conn.commit()


        # cur.execute('select * from departments;')
        # print(cur.fetchall())
        # cur.close()

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