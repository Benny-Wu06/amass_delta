import psycopg2
import boto3

password = "testdiddyblud"

conn = None
try:
    conn = psycopg2.connect(
        host='testdb.cby62qewyxsr.ap-southeast-2.rds.amazonaws.com',
        port=5432,
        database='postgres',
        user='postgres',
        password=password,
        sslmode='prefer',
    sslrootcert='/certs/global-bundle.pem'
    )
    cur = conn.cursor()
    cur.execute('''CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100)
);''')
    
#     Create table companies (
# 	Id primary key,
# 	Name text not null,
# 	numVulnerabilities integer, 
# 	avgCVSS integer,
# 	avgEPSS integer,
# 	riskIndex integer not null,
# 	riskRating text not null
# 	earliestVulnerabilityDate dateObj?
# );

    print('success')

    # preprocessing
    cur.execute('''INSERT INTO departments (department_name, location) VALUES
('Engineering', 'San Francisco'),
('Human Resources', 'New York'),
('Marketing', 'London'),
('Sales', 'Sydney');''')
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