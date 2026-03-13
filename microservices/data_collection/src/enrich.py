import json
import urllib.request
import boto3
import os
import io
from datetime import datetime
import gzip

s3 = boto3.client('s3')

nvd_data_cache = {}

def enrichment(event, context):
    cve_list = []
    epss = {}
    chunk = 80
    bucket_name = os.environ['BUCKET_NAME']
    nvd_data = [    'reference/nvdcve-2.0-2026.json.gz', 
                     'reference/nvdcve-2.0-2025.json.gz', 
                     'reference/nvdcve-2.0-2024.json.gz', 
                     'reference/nvdcve-2.0-2023.json.gz', 
                     'reference/nvdcve-2.0-2022.json.gz', 
                     'reference/nvdcve-2.0-2021.json.gz', 
                     'reference/nvdcve-2.0-2020.json.gz',
                     'reference/nvdcve-2.0-modified.json.gz',]

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix="raw/")
    if 'Contents' not in response:
        return None
    all_files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
    recent_raw = all_files[0]['Key']
    response = s3.get_object(Bucket=bucket_name, Key=recent_raw)

    for nvd in nvd_data:
        try:
            cvss_list = s3.get_object(Bucket=bucket_name, Key=nvd)
            with gzip.GzipFile(fileobj=cvss_list['Body']) as file:
                cvss_data = json.load(file)
                for cve in cvss_data.get('vulnerabilities', []):
                    cve_id = cve['cve']['id']
                    metrics = cve['cve'].get('metrics', {})
                    cvss_scores = metrics.get('cvssMetricV31') or metrics.get('cvssMetricV30') or metrics.get('cvssMetricV2')
                    if cvss_scores:
                        nvd_data_cache[cve_id] = cvss_scores[0]['cvssData']['baseScore']
                    else:
                        nvd_data_cache[cve_id] = "Awaiting Analysis"
        except s3.exceptions.NoSuchKey:
            continue
    

    data = json.loads(response['Body'].read().decode('utf-8'))
    
    for cve in data.get('vulnerabilities', []):
        cve_list.append(cve['cveID'])

    for i in range(0, len(cve_list), chunk):
        batch = cve_list[i : i + chunk]
        ids = ",".join(batch)
        url = f"https://api.first.org/data/v1/epss?cve={ids}"
        try:
            with urllib.request.urlopen(url, timeout=15) as api_res:
                api_data = json.loads(api_res.read().decode('utf-8'))
                for entry in api_data.get('data', []):
                    epss[entry['cve']] = entry.get('epss', "N/A")
        except Exception as e:
            print(f"Error Getting EPSS: {e}")

    for cve in data.get('vulnerabilities', []):
        cve['cvss_score'] = nvd_data_cache.get(cve['cveID'], "Awaiting Analysis")
        cve['epss_score'] = epss.get(cve['cveID'], "N/A")
    dest_key = "enriched/enriched.json"
    s3.put_object(
        Bucket=bucket_name,
        Key=dest_key,
        Body=json.dumps(data, indent=4),
        ContentType='application/json'
    )
    return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully enriched and saved to {dest_key}")
        }