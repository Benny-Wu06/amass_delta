import requests
import json
import os
from datetime import datetime

# CONFIG
CHARLIE_BASE_URL = "https://tdxz7z58l6.execute-api.ap-southeast-2.amazonaws.com/prod"
CHARLIE_EMAIL = "dearryllan@gmail.com"
CHARLIE_PASSWORD = "mypassword" 

# Use a Dictionary to allow .get() lookups
VALID_COMPANIES = {
    "GOOGL": "Google", 
    "AAPL": "Apple", 
    "MSFT": "Microsoft", 
    "AVGO": "Broadcom", 
    "META": "Meta", 
    "CSCO": "Cisco", 
    "INTC": "Intel"
}

VALID_SENTIMENTS = ["positive", "negative", "neutral"]

def get_news_lambda(event, context):
    try:
        path_params = event.get("pathParameters") or {}
        company_symbol = path_params.get("company_symbol")
        
        company_name = VALID_COMPANIES.get(company_symbol)

        if not company_name:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "error": f"Invalid symbol: {company_symbol}",
                    "supported": list(VALID_COMPANIES.keys())
                })
            }

        # query extraction
        query_params = event.get("queryStringParameters") or {}
        
        # extract start date (defaults to 1st Jan 2025)
        start_date_str = query_params.get("start_date", "2025-01-01") 
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        
        # extract end date (deafults to 'today')
        end_date_str = query_params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # ERROR CHECK: start_date after to
        if (end_date - start_date).days < 0:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "'start' date must be before 'end' date"})
            }
        
        # extract sentiment
        sentiment = query_params.get("sentiment")
        
        if sentiment and (sentiment not in VALID_SENTIMENTS):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": f"Invalid sentiment: '{sentiment}'. Must be one of {VALID_SENTIMENTS} or omitted."
                })
            }
        
        # extract limit
        try:
            limit = int(query_params.get("limit", 50))
            limit = max(1, min(limit, 200))
        except ValueError:
            limit = 50

        
        # construct the parameter dictionary
        news_params = {
            "start_date": start_date_str, 
            "end_date": end_date_str,
            "limit": limit
        }
        
        # only add the key if it exists !!
        if sentiment:
            news_params["sentiment"] = sentiment

        # login
        EMAIL = os.environ.get("CHARLIE_EMAIL", CHARLIE_EMAIL)
        PASSWORD = os.environ.get("CHARLIE_PASSWORD", CHARLIE_PASSWORD)
        
        login_res = requests.post(
            f"{CHARLIE_BASE_URL}/auth/login", 
            json={"email": EMAIL, "password": PASSWORD}
        )
        login_res.raise_for_status()
        id_token = login_res.json()['authentication']['IdToken']

        # fetch news for ticker
        news_res = requests.get(
            f"{CHARLIE_BASE_URL}/news/{company_symbol}", 
            headers={"Authorization": f"Bearer {id_token}"}, 
            params=news_params
        )
        news_res.raise_for_status()
        payload = news_res.json()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "company": company_name,
                "symbol": company_symbol,
                "count": payload.get("count", 0),
                "news_data": payload.get("data", [])
            })
        }

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }