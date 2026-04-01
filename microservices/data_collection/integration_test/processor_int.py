import boto3
import json
import pytest
import os
from unittest import TestCase
from microservices.data_collection.src.processor import lambda_handler


class TestProcessorIntegration(TestCase):
    # Setup AWS Clients

    def setup(self) -> None:
        # Getting real lambda credits from terraform variables
        self.aws_region = "ap-southeast-2"
        self.lambda_name = os.environ.get("PROCESSOR_LAMBDA_NAME")
        self.bucket_name = os.environ.get("BUCKET_NAME")
        self.db_host = os.environ.get("DB_HOST") 
        self.db_password = os.environ.get("DB_PASSWORD")
        self.test_key = "enriched/test_integration.json"

        # Database credentials
        self.db_name = "postgres"
        self.db_user = "postgres"

        self.s3_client = boto3.client('s3', region_name=aws_region)
        self.lambda_client = boto3.client('lambda', region_name=aws_region)

        self.test_data = {
            "title": "CISA Catalog",
            "count": 3,
            "vulnerabilities": [
                {
                    "cveID": "CVE-2021-22054",
                    "vendorProject": "Omnissa",
                    "vulnerabilityName": "Omnissa Workspace ONE SSRF",
                    "shortDescription": "A server-side request forgery vulnerability.",
                    "dateAdded": "2026-03-09",
                    "dueDate": "2026-03-23",
                    "cvss_score": 7.5,
                    "cvss_severity": "HIGH",
                    "epss_score": "0.937430000",
                    "epss_percentile": "0.998460000"
                },
                {
                    "cveID": "CVE-2025-26399",
                    "vendorProject": "SolarWinds",
                    "vulnerabilityName": "SolarWinds Web Help Desk Deserialization",
                    "shortDescription": "A deserialization vulnerability.",
                    "dateAdded": "2026-03-09",
                    "dueDate": "2026-03-12",
                    "cvss_score": 9.8,
                    "cvss_severity": "CRITICAL",
                    "epss_score": "0.342250000",
                    "epss_percentile": "0.969090000"
                },
                {
                    "cveID": "CVE-2020-7796",
                    "vendorProject": "Synacor",
                    "vulnerabilityName": "Synacor Zimbra SSRF Vulnerability",
                    "shortDescription": "A server-side request forgery vulnerability.",
                    "dateAdded": "2026-02-17",
                    "dueDate": "2026-03-10",
                    "cvss_score": "Awaiting Analysis",
                    "cvss_severity": None,
                    "epss_score": "0.935280000",
                    "epss_percentile": "0.998240000"
                }
            ]
        }

        self.s3_client.put_object(
            Bucket=self.bucket_name, 
            Key=self.test_key, 
            Body=json.dumps(self.test_data),
            ContentType='application/json'
        )

    def get_conn(self):
        return psycopg2.connect(
            host=self.db_host,
            port=5432,
            database='postgres',
            user='postgres',
            password=self.db_password,
            sslmode='prefer',
            connect_timeout=5
        )

    # tests
    def test_lambda_inserts_vulnerabilities(self):
        result = lambda_handler({"test": True}, None)

        self.assertEqual(result["statusCode"], 200)

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT cve_id FROM vulnerabilities WHERE cve_id = %s",
            ("CVE-TEST-00001",)
        )
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "CVE-TEST-00001")

        cur.close()
        conn.close()

    def test_lambda_creates_companies(self):
        lambda_handler({"test": True}, None)

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT company_name FROM companies WHERE company_name = %s",
            ("TestCompanyA",)
        )
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "TestCompanyA")

        cur.close()
        conn.close()

    def test_lambda_handles_awaiting_analysis(self):
        result = lambda_handler({"test": True}, None)
        self.assertEqual(result["statusCode"], 200)

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT cvss_score FROM vulnerabilities WHERE cve_id = %s",
            ("CVE-TEST-00003",)
        )
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertIsNone(row[0]) 

        cur.close()
        conn.close()

    def test_company_stats_updated(self):
        lambda_handler({"test": True}, None)

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT num_vulnerabilities, risk_rating FROM companies WHERE company_name = %s",
            ("TestCompanyA",)
        )
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 2)
        self.assertIn(row[1], ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'])

        cur.close()
        conn.close()

    # teardown
    def tearDown(self):
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=self.test_key
        )
        print("Deleted test file from S3")

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM vulnerabilities WHERE cve_id LIKE 'CVE-TEST-%'"
        )
        
        cur.execute(
            "DELETE FROM companies WHERE company_name LIKE 'TestCompany%'"
        )

        conn.commit()
        cur.close()
        conn.close()
        print("Cleaned up test data from database")

