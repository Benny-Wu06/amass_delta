import json
import urllib.request
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')

def cisascrapper(event, context):
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    bucket_name = os.environ['BUCKET_NAME']
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    file_name = f"raw/cisa_kev_{timestamp}.json"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=data,
            ContentType='application/json'
        )
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "success", 
                "file": file_name,
                "timestamp": timestamp
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }