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

    createCompaniesSimple = '''create table companies (
    id serial primary key,
    company_name text unique not null
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