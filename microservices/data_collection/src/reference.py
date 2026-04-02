import json
import urllib.request
import boto3
import os

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

    body = event.get("body", {})
    if isinstance(body, str):
        body = json.loads(body)

    files_to_sync = body.get("files") or event.get("files") or default_files
    files_synced = []

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

        except Exception as e:
            print(f"Error: {str(e)}")
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

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
