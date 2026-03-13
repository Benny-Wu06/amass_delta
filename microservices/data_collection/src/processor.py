import json
import os
import boto3
import psycopg2

# Definijg variablies

s3 = boto3.client('s3')

DB_HOST     = 'testdb.cjwhnekr8yms.us-east-1.rds.amazonaws.com'
DB_PORT     = 5432
DB_NAME     = 'postgres'
DB_USER     = 'postgres'
DB_PASSWORD = 'testdiddyblud'

BUCKET_NAME = os.environ.get('BUCKET_NAME')
CISA_KEY    = 'cisa/data.json'

# Connecting to postgres database

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='prefer',
        connect_timeout=3
    )
    return conn

# Retrieving data from s3 Bucket

def get_cisa_data():
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=CISA_KEY
    )
    raw = response['Body'].read().decode('utf-8')
    data = json.loads(raw)
    return data['vulnerabilities']

# Searching for companyid via company_name

def get_or_create_company(cur, company_name):
    cur.execute(
        'SELECT id FROM companies WHERE company_name = %s',
        (company_name,)
    )
    result = cur.fetchone()

    if result:
        return result[0]

    cur.execute('''
        INSERT INTO companies (
            company_name,
            num_vulnerabilities,
            avg_cvss,
            avg_epss,
            risk_index,
            risk_rating,
            earliest_vuln_date
        ) VALUES (%s, 0, 0, 0, 0, 'UNKNOWN', NULL)
        RETURNING id
    ''', (company_name,))

    new_id = cur.fetchone()[0]
    return new_id

# creating vulnerabilites in the table

def insert_vulnerability(cur, vuln, company_id):
    cvss_score = vuln.get('cvss_score')
    if not isinstance(cvss_score, (int, float)):
        cvss_score = None

    epss_score = vuln.get('epss_score')
    if epss_score:
        epss_score = float(epss_score)

    epss_percentile = vuln.get('epss_percentile')
    if epss_percentile:
        epss_percentile = float(epss_percentile)

    cur.execute('''
        INSERT INTO vulnerabilities (
            cve_id,
            company_id,
            vulnerability_name,
            description,
            date_added,
            due_date,
            cvss_score,
            cvss_severity,
            epss_score,
            epss_percentile
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (cve_id) DO NOTHING
    ''', (
        vuln.get('cveID'),
        company_id,
        vuln.get('vulnerabilityName'),
        vuln.get('shortDescription'),
        vuln.get('dateAdded'),
        vuln.get('dueDate'),
        cvss_score,
        vuln.get('cvss_severity'),
        epss_score,
        epss_percentile
    ))

# lambda function

def lambda_handler(event, context):
    print("Starting processor...")

    conn = get_db_connection()
    cur = conn.cursor()

    vulnerabilities = get_cisa_data()
    print(f"Found {len(vulnerabilities)} vulnerabilities to process")

    inserted = 0
    skipped = 0

    try:
        for vuln in vulnerabilities:
            company_name = vuln.get('vendorProject', 'Unknown')
            company_id = get_or_create_company(cur, company_name)
            insert_vulnerability(cur, vuln, company_id)
            inserted += 1

        conn.commit()
        print(f"Done! Inserted: {inserted}, Skipped: {skipped}")

        return {
            'statusCode': 200,
            'body': f"Inserted {inserted} vulnerabilities"
        }

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise

    finally:
        cur.close()
        conn.close()