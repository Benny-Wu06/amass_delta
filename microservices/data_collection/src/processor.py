import json
import os
import boto3
import psycopg2

# Variables definitions

s3 = boto3.client('s3')

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = 5432
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
CISA_KEY    = 'enriched/enriched.json'

# Database connection

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

# Crestes tables if database empty"

def init_db(cur):
    schema_sql = """
    CREATE TABLE IF NOT EXISTS companies (
        id serial primary key,
        company_name text not null,
        num_vulnerabilities integer, 
        avg_cvss numeric,
        avg_epss numeric,
        risk_index numeric not null,
        risk_rating text not null,
        earliest_vuln_date date
    );

    CREATE TABLE IF NOT EXISTS vulnerabilities (
        cve_id varchar(20) primary key,
        company_id integer not null,
        foreign key (company_id) references companies(id),
        vulnerability_name text not null,
        description text not null,
        date_added date not null,
        due_date date not null,
        cvss_score numeric,
        cvss_severity text,
        epss_score numeric,
        epss_percentile numeric
    );
    """
    cur.execute(schema_sql)

# retrieving data from s3 bucket

def get_cisa_data():
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=CISA_KEY
    )
    raw = response['Body'].read().decode('utf-8')
    data = json.loads(raw)
    return data['vulnerabilities']

# searching for company id via companyname 

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

# creating new vuolnerablility

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

# risk calculations 

def calculate_risk(avg_cvss, avg_epss):
    if avg_cvss is None or avg_epss is None:
        return 0, 'UNKNOWN'

    risk_index = round(
        (float(avg_cvss) / 10) * 0.6 + float(avg_epss) * 0.4,
        4
    )

    if risk_index >= 0.8:
        rating = 'CRITICAL'
    elif risk_index >= 0.6:
        rating = 'HIGH'
    elif risk_index >= 0.4:
        rating = 'MEDIUM'
    else:
        rating = 'LOW'

    return risk_index, rating

# updating company stats at the end

def update_all_company_stats(cur):
    cur.execute('SELECT id FROM companies')
    company_ids = cur.fetchall()

    for (company_id,) in company_ids:
        cur.execute('''
            SELECT
                COUNT(*),
                AVG(cvss_score),
                AVG(epss_score),
                MIN(date_added)
            FROM vulnerabilities
            WHERE company_id = %s
        ''', (company_id,))

        count, avg_cvss, avg_epss, earliest_date = cur.fetchone()
        risk_index, risk_rating = calculate_risk(avg_cvss, avg_epss)

        cur.execute('''
            UPDATE companies SET
                num_vulnerabilities = %s,
                avg_cvss            = %s,
                avg_epss            = %s,
                risk_index          = %s,
                risk_rating         = %s,
                earliest_vuln_date  = %s
            WHERE id = %s
        ''', (
            count,
            avg_cvss,
            avg_epss,
            risk_index,
            risk_rating,
            earliest_date,
            company_id
        ))

    print(f"Updated stats for {len(company_ids)} companies")

# lambda fucntion

def lambda_handler(event, context):
    print("Starting processor...")

    conn = get_db_connection()
    cur = conn.cursor()

    init_db(cur)
    conn.commit()

    vulnerabilities = get_cisa_data()
    print(f"Found {len(vulnerabilities)} vulnerabilities to process")

    inserted = 0

    try:
        for vuln in vulnerabilities:
            company_name = vuln.get('vendorProject', 'Unknown')
            company_id = get_or_create_company(cur, company_name)
            insert_vulnerability(cur, vuln, company_id)
            inserted += 1

        conn.commit()
        print(f"Inserted {inserted} vulnerabilities")

        print("Updating company stats...")
        update_all_company_stats(cur)
        conn.commit()
        print("Company stats updated!")

        return {
            'statusCode': 200,
            'body': f"Inserted {inserted} vulnerabilities and updated company stats"
        }

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise

    finally:
        cur.close()
        conn.close()