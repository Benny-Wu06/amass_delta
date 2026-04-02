import json
import logging
import urllib.request
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def nvdscrapper(event, context):
    base_url = "https://nvd.nist.gov/feeds/json/cve/2.0/"
    bucket_name = os.environ["BUCKET_NAME"]
    default_files  = [
        "nvdcve-2.0-modified.json.gz",
        "nvdcve-2.0-2026.json.gz",
        "nvdcve-2.0-2025.json.gz",
        "nvdcve-2.0-2024.json.gz",
        "nvdcve-2.0-2023.json.gz",
        "nvdcve-2.0-2022.json.gz",
        "nvdcve-2.0-2021.json.gz",
        "nvdcve-2.0-2020.json.gz",
    ]

    files_to_sync = event.get("files", default_files)
    files_synced = []

    logger.info("Starting NVD reference sync, %d files, bucket=%s", len(files_to_sync), bucket_name)

    for file in files_to_sync:
        url = f"{base_url}{file}"
        file_name = f"reference/{file}"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=file_name,
                    Body=response.read(),
                    ContentType="application/x-gzip",
                )
            files_synced.append(file_name)
            logger.info("Synced %s", file_name)

        except Exception as e:
            logger.error("Failed to sync %s: %s", file, str(e))
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    logger.info("NVD reference sync complete, %d files synced", len(files_synced))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "status": "success",
                "file": files_synced,
            }
        ),
    }
