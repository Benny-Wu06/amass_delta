import json
import logging
import os
import boto3
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client("ses")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
cert_path = os.environ.get("CERT_PATH", "global-bundle.pem")

FROM_EMAIL = os.environ.get("FROM_EMAIL")


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

def lambda_handler(event, context):
    logger.info("Starting alert dispatcher")
    try:
        records = event.get("Records", [])
        if not records:
            logger.error("No SNS records in event")
            return {"statusCode": 400, "body": "No SNS records"}

        sns_message = records[0]["Sns"]["Message"]
        payload = json.loads(sns_message)
        new_cves_by_company = payload.get("new_cves", {})
    except (KeyError, json.JSONDecodeError) as e:
        logger.error("Failed to parse SNS payload: %s", str(e))
        return {"statusCode": 400, "body": "Invalid SNS payload"}

    if not new_cves_by_company:
        logger.info("No new CVEs in payload")
        return {"statusCode": 200, "body": "No CVEs to alert on"}

    alerts_by_email = build_alerts_by_email(new_cves_by_company)

    if not alerts_by_email:
        logger.info("No subscribers for any affected companies")
        return {"statusCode": 200, "body": "No subscribers to alert"}

    sent = 0
    failed = 0
    for email, companies_cves in alerts_by_email.items():
        try:
            send_alert_email(email, companies_cves)
            sent += 1
        except Exception as e:
            logger.error("Failed to send email to %s: %s", email, str(e))
            failed += 1

    logger.info("Success ALert: sent=%d failed=%d", sent, failed)
    return {
        "statusCode": 200,
        "body": json.dumps({"sent": sent, "failed": failed}),
    }


def build_alerts_by_email(new_cves_by_company):
    conn = None
    alerts_by_email = {}

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        company_names = list(new_cves_by_company.keys())

        cur.execute(
            """
            SELECT DISTINCT w.email, wc.company_name
            FROM watchlists w
            JOIN watchlist_companies wc ON wc.watchlist_id = w.id
            WHERE wc.company_name = ANY(%s)
            """,
            (company_names,),
        )
        rows = cur.fetchall()

        for email, company_name in rows:
            if email not in alerts_by_email:
                alerts_by_email[email] = {}
            alerts_by_email[email][company_name] = new_cves_by_company[company_name]

        cur.close()
        return alerts_by_email

    except Exception as e:
        logger.error("Error building alerts: %s", str(e))
        raise
    finally:
        if conn:
            conn.close()


def send_alert_email(email, companies_cves):
    total_cves = sum(len(cves) for cves in companies_cves.values())
    subject = f"[CVE Alert] {total_cves} new vulnerabilities across {len(companies_cves)} companies you're watching"

    lines = [
        f"New vulnerabilities have been published for companies in your watchlists.",
        "",
    ]
    for company_name, cves in companies_cves.items():
        lines.append(f"{company_name} ({len(cves)} new)")
        for cve in cves:
            lines.append(f"")
            lines.append(f"{cve.get('cve_id')}: {cve.get('name')}")
            lines.append(f"Added: {cve.get('date_added')}")
            lines.append(f"Due Date:   {cve.get('due_date')}")
            if cve.get("cvss_score") is not None:
                lines.append(f"CVSS:  {cve.get('cvss_score')}")
            if cve.get("epss_score") is not None:
                lines.append(f"EPSS:  {cve.get('epss_score')}")
            desc = cve.get("description") or ""
            if desc:
                if len(desc) > 300:
                    desc = desc[:300] + "..."
                lines.append(f"{desc}")
        lines.append("")
    body_text = "\n".join(lines)

    ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Text": {"Data": body_text, "Charset": "UTF-8"},
            },
        },
    )
    logger.info("Sent alert to %s covering %d companies", email, len(companies_cves))