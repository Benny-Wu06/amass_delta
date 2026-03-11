import psycopg2
import boto3

password = "testdiddyblud"

conn = None
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

    createCompaniesQuery =  '''create table companies(
	id serial primary key,
	company_name text not null,
	num_vulnerabilities integer, 
	avg_cvss numeric,
	avg_epss numeric,
	risk_index numeric not null,
	risk_rating text not null,
	earliest_vuln_date date);'''

    createCompaniesSimple = '''create table companies (
    id serial primary key,
    company_name text unique not null
    );'''

    createVulnerabilitiesQuery = '''create table vulnerabilities(
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
    );'''


    cur = conn.cursor()

    cur.execute(createCompaniesQuery)
    cur.execute(createVulnerabilitiesQuery)

    conn.commit()

    cur.execute('SELECT * from companies;')
    print(cur.fetchall())

    cur.execute('SELECT * from vulnerabilities;')
    print(cur.fetchall())

    cur.close()
except Exception as e:
    print(f"Database error: {e}")
    raise
finally:
    if conn:
       conn.close()