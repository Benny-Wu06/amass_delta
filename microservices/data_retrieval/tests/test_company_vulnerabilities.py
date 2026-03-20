import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from company_vulnerabilities import lambda_handler

# 1. Manually set the environment variables your code expects
os.environ["DB_PASSWORD"] = "testdiddyblud"
os.environ["DB_HOST"] = "localhost"  # Or your local DB IP
os.environ["CERT_PATH"] = "./global-bundle.pem"

# 2. Mimic the JSON 'event' that API Gateway usually sends
mock_event = {"pathParameters": {"company_name": "AcmeCorp"}}

# 3. Call the function
print("--- Starting Local Test ---")
response = lambda_handler(mock_event, None)

# 4. View the result
print(f"Status Code: {response['statusCode']}")
print(f"Body: {response['body']}")
