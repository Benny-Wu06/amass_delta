import boto3
import json
import pytest
import os

LAMBDA_NAME = "amass-rds-processor""
BUCKET_NAME = "amass-cisa-bucket-01"

def test_lambda_processor_integration():
    """
    Tests the full flow: 
    1. Triggers the Lambda
    2. Lambda reads from enriched data in s3 bucket and inserts into postgresql
    3. Verifies the output file in postgresql will be present and correct
    4. Deletes data that was inserted into postgresql
    """
    lambda_client = boto3.client('lambda', region_name='ap-southeast-2')
    s3_client = boto3.client('s3', region_name='ap-southeast-2')