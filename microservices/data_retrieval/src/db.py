import psycopg2
import boto3

password = "testdiddyblud"

conn = None

# need to add will to the inbound security group so he can connect
try:
    conn = psycopg2.connect(
        host='testdb.cby62qewyxsr.ap-southeast-2.rds.amazonaws.com',
        port=5432,
        database='postgres',
        user='postgres',
        password=password,
        sslmode='prefer',
        connect_timeout = 5,
    sslrootcert='/certs/global-bundle.pem'
    )
    cur = conn.cursor()
#     cur.execute('''CREATE TABLE departments (
#     department_id SERIAL PRIMARY KEY,
#     department_name VARCHAR(100) NOT NULL UNIQUE,
#     location VARCHAR(100)
# );''')
    
    companiesQuery =  '''create table companies(
	id serial primary key,
	name varchar(100) not null,
	numVulnerabilities integer, 
	avgCVSS integer,
	avgEPSS integer,
	riskIndex integer not null,
	riskRating text not null
	earliestVulnerabilityDate dateObj?);'''

    createVulnerabilitiesQuery = '''create table vulnerabilities(
    cveId varchar(primary key
    
    
    
    );'''

    print('success')

    # preprocessing
    # cur.execute('''INSERT INTO vulnerabilities (cveId, companyName, cvss, epss) VALUES
    # ('Engineering', 'San Francisco'),
    # ('Human Resources', 'New York'),
    # ('Marketing', 'London'),
    # ('Sales', 'Sydney');''')
#     conn.commit()


    cur.execute('select * from departments;')
    print(cur.fetchall())
    cur.close()
except Exception as e:
    print(f"Database error: {e}")
    raise
finally:
    if conn:
        conn.close()