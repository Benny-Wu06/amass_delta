import requests
import json
from datetime import datetime

# CHARLIE - FINANCIAL INTELLIGENCE PLATFORM
BASE_URL_STOCKS = "https://tdxz7z58l6.execute-api.ap-southeast-2.amazonaws.com/prod"

# AMASS - DATA BREACH & VULNERABILITY INTELLEGENCE PLATFORM
BASE_URL_GROWTH = "https://7mz3fi8zw1.execute-api.ap-southeast-2.amazonaws.com/v1"

EMAIL = "dearryllan@gmail.com"
PASSWORD = "mypassword" 

def test_external_stock_integration():
    # initialise a list for diff_price
    diff_price_analysis = []

    try:
        # LOG IN: uses a verified email account
        login_url = f"{BASE_URL_STOCKS}/auth/login"
        login_headers = {"accept": "application/json", "Content-Type": "application/json"}
        login_data = {"email": EMAIL, "password": PASSWORD}
        response = requests.post(login_url, json=login_data, headers=login_headers)

        # scrape the IdToken
        auth_data = response.json()
        id_token = auth_data['authentication']['IdToken']

        # calculate date required
        start_date_str = "2026-03-01"
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        today = datetime.now()
        
        delta = today - start_date
        days_to_trace = delta.days

        # GET STOCKS: APPL as an exampke
        TICKER = "APPL"
        print(f"\n--- Step 2: Fetching {TICKER} Stock Prices ({start_date_str} to today) ---")
        stocks_url = f"{BASE_URL_STOCKS}/stocks/{TICKER}/prices"
        stock_headers = {"Authorization": f"Bearer {id_token}", "accept": "application/json"}
        params = {"from": start_date_str, "to": today.strftime("%Y-%m-%d")}

        stock_response = requests.get(stocks_url, headers=stock_headers, params=params)
        
        if stock_response.status_code == 200:
            stock_json = stock_response.json()
            print(f"Successfully fetched data for {TICKER}.")
            
            for entry in stock_json.get("data", []):
                date = entry.get("date")
                open_price = entry.get("open")
                close_price = entry.get("close")
                
                diff = round(close_price - open_price, 2)
                
                diff_price_analysis.append({
                    "date": date,
                    "difference": diff
                })
        else:
            print(f"Failed to fetch stocks: {stock_response.status_code}")

        # GET CVE-GROWTH: Apple since we fetched APPL ticker
        COMPANY_NAME = "Apple"
        growth_url = f"{BASE_URL_GROWTH}/growth/{COMPANY_NAME}"
        growth_params = {"days": days_to_trace}
        
        growth_response = requests.get(growth_url, params=growth_params)

        # MERGE DATA #
        growth_json = growth_response.json() # Extract the dictionary first
        growth_lookup = {
            item["date"]: item["new_cves"] 
            for item in growth_json.get("data_points", []) 
        }

        merged_data = []
        for finance_entry in diff_price_analysis:
            current_date = finance_entry["date"]
            
            combined_entry = {
                "date": current_date,
                "cve_count_growth": growth_lookup.get(current_date, 0),
                "price_diff": finance_entry["difference"]
            }
            
            merged_data.append(combined_entry)

        print(json.dumps(merged_data, indent=2))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_external_stock_integration()