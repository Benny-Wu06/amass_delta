import json
import logging
import urllib.request
import boto3
import os
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def cisascrapper(event, context):
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    bucket_name = os.environ["BUCKET_NAME"]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    file_name = f"raw/cisa_kev_{timestamp}.json"

    logger.info("Starting CISA KEV scrape, bucket=%s", bucket_name)

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()

        s3.put_object(
            Bucket=bucket_name, Key=file_name, Body=data, ContentType="application/json"
        )

        logger.info("Success CISA KEV saved to s3://%s/%s", bucket_name, file_name)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"status": "success", "file": file_name, "timestamp": timestamp}
            ),
        }
    except Exception as e:
        logger.error("CISA scrape failed: %s", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
