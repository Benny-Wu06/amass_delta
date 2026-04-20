import json
import logging
import os
import boto3
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variables definitions

s3 = None
sns = None


def _get_s3():
    global s3
    if s3 is None:
        s3 = boto3.client("s3")
    return s3


def _get_sns():
    global sns
    if sns is None:
        sns = boto3.client("sns")
    return sns

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
CISA_KEY = "enriched/enriched.json"
cert_path = os.environ.get("CERT_PATH", "global-bundle.pem")

# Database connection


def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require",
        connect_timeout=3,
        sslrootcert=cert_path,
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
        epss_score numeric
    );

    CREATE TABLE IF NOT EXISTS watchlists (
        id serial primary key,
        email text not null,
        name text not null,
        created_at timestamp default now(),
        UNIQUE(email, name)
    );

    CREATE TABLE IF NOT EXISTS watchlist_companies (
        id serial primary key,
        watchlist_id integer not null references watchlists(id) ON DELETE CASCADE,
        company_name text not null,
        added_at timestamp default now(),
        UNIQUE(watchlist_id, company_name)
    );
    """
    cur.execute(schema_sql)


# retrieving data from s3 bucket


def get_cisa_data():
    response = _get_s3().get_object(Bucket=BUCKET_NAME, Key=CISA_KEY)
    raw = response["Body"].read().decode("utf-8")
    data = json.loads(raw)
    return data["vulnerabilities"]


# searching for company id via companyname


def get_or_create_company(cur, company_name):
    cur.execute("SELECT id FROM companies WHERE company_name = %s", (company_name,))
    result = cur.fetchone()

    if result:
        return result[0]

    cur.execute(
        """
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
    """,
        (company_name,),
    )

    new_id = cur.fetchone()[0]
    return new_id


# creating new vuolnerablility


def insert_vulnerability(cur, vuln, company_id):
    cvss_score = vuln.get("cvss_score")
    if not isinstance(cvss_score, (int, float)):
        cvss_score = None

    epss_score = vuln.get("epss_score")
    if epss_score:
        epss_score = float(epss_score)

    epss_percentile = vuln.get("epss_percentile")
    if epss_percentile:
        epss_percentile = float(epss_percentile)

    cur.execute(
        """
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
    """,
        (
            vuln.get("cveID"),
            company_id,
            vuln.get("vulnerabilityName"),
            vuln.get("shortDescription"),
            vuln.get("dateAdded"),
            vuln.get("dueDate"),
            cvss_score,
            vuln.get("cvss_severity"),
            epss_score,
            epss_percentile,
        ),
    )


# risk calculations


def calculate_risk(avg_cvss, avg_epss):
    if avg_cvss is None or avg_epss is None:
        return 0, "UNKNOWN"

    risk_index = round((float(avg_cvss) / 10) * 0.6 + float(avg_epss) * 0.4, 4)

    if risk_index >= 0.8:
        rating = "CRITICAL"
    elif risk_index >= 0.6:
        rating = "HIGH"
    elif risk_index >= 0.4:
        rating = "MEDIUM"
    else:
        rating = "LOW"

    return risk_index, rating


# updating company stats at the end


def update_all_company_stats(cur):
    cur.execute("SELECT id FROM companies")
    company_ids = cur.fetchall()

    for (company_id,) in company_ids:
        cur.execute(
            """
            SELECT
                COUNT(*),
                AVG(cvss_score),
                AVG(epss_score),
                MIN(date_added)
            FROM vulnerabilities
            WHERE company_id = %s
        """,
            (company_id,),
        )

        count, avg_cvss, avg_epss, earliest_date = cur.fetchone()
        risk_index, risk_rating = calculate_risk(avg_cvss, avg_epss)

        cur.execute(
            """
            UPDATE companies SET
                num_vulnerabilities = %s,
                avg_cvss            = %s,
                avg_epss            = %s,
                risk_index          = %s,
                risk_rating         = %s,
                earliest_vuln_date  = %s
            WHERE id = %s
        """,
            (
                count,
                avg_cvss,
                avg_epss,
                risk_index,
                risk_rating,
                earliest_date,
                company_id,
            ),
        )

    logger.info("Updated stats for %d companies", len(company_ids))


# lambda fucntion


def lambda_handler(event, context):
    logger.info("Starting processor")

    conn = get_db_connection()
    cur = conn.cursor()

    init_db(cur)
    conn.commit()

    vulnerabilities = get_cisa_data()
    logger.info("Found %d vulnerabilities to process", len(vulnerabilities))

    inserted = 0
    new_cves_by_company = {}

    try:
        for vuln in vulnerabilities:
            company_name = vuln.get("vendorProject", "Unknown")
            company_id = get_or_create_company(cur, company_name)
            insert_vulnerability(cur, vuln, company_id)
            if cur.rowcount > 0:
                new_cves_by_company.setdefault(company_name, []).append({
                    "cve_id": vuln.get("cveID"),
                    "name": vuln.get("vulnerabilityName"),
                    "description": vuln.get("shortDescription"),
                    "date_added": vuln.get("dateAdded"),
                    "cvss_score": vuln.get("cvss_score"),
                    "epss_score": vuln.get("epss_score"),
                    "due_date": vuln.get("dueDate"),
            })
            inserted += 1

        conn.commit()
        logger.info("Inserted %d new vulnerabilities", inserted)

        if new_cves_by_company and SNS_TOPIC_ARN:
            _get_sns().publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps({"new_cves": new_cves_by_company}),
            )
        logger.info("New CVE event to SNS for %d companies", len(new_cves_by_company))

        logger.info("Updating company stats")
        update_all_company_stats(cur)
        conn.commit()
        logger.info("Success Company stats updated")

        return {
            "statusCode": 200,
            "body": f"Inserted {inserted} vulnerabilities and updated company stats",
        }

    except Exception as e:
        conn.rollback()
        logger.error("Processor failed: %s", str(e))
        raise

    finally:
        cur.close()
        conn.close()
