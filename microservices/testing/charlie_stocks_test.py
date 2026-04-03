import requests
import json
from datetime import datetime

# Config for Team 1 (Stocks)
BASE_URL_STOCKS = "https://tdxz7z58l6.execute-api.ap-southeast-2.amazonaws.com/prod"
# Config for Team 2 (Growth)
BASE_URL_GROWTH = "https://7mz3fi8zw1.execute-api.ap-southeast-2.amazonaws.com/v1"

EMAIL = "dearryllan@gmail.com"
PASSWORD = "mypassword" 

def test_external_stock_integration():
    print("--- Step 1: Logging In (Team 1) ---")
    login_url = f"{BASE_URL_STOCKS}/auth/login"
    login_headers = {"accept": "application/json", "Content-Type": "application/json"}
    login_data = {"email": EMAIL, "password": PASSWORD}

    # Initialize a list to hold final output for printing at the end
    final_price_analysis = []

    try:
        response = requests.post(login_url, json=login_data, headers=login_headers)
        if response.status_code != 200:
            print(f"Login Failed: {response.text}")
            return

        auth_data = response.json()
        # Navigating the nested structure to get IdToken
        id_token = auth_data['authentication']['IdToken']
        print("Successfully retrieved IdToken.")

        # --- Date Calculation ---
        start_date_str = "2026-03-01"
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        today = datetime.now()
        
        # Calculate the number of days between now and start_date
        delta = today - start_date
        days_to_trace = delta.days
        print(f"Tracing back {days_to_trace} days to reach {start_date_str}")

        # --- Step 2: Fetch Stock Data (Team 1) ---
        ticker = "AAPL"
        print(f"\n--- Step 2: Fetching {ticker} Stock Prices ({start_date_str} to today) ---")
        stocks_url = f"{BASE_URL_STOCKS}/stocks/{ticker}/prices"
        stock_headers = {"Authorization": f"Bearer {id_token}", "accept": "application/json"}
        params = {"from": start_date_str, "to": today.strftime("%Y-%m-%d")}

        stock_response = requests.get(stocks_url, headers=stock_headers, params=params)
        
        if stock_response.status_code == 200:
            stock_json = stock_response.json()
            print(f"Successfully fetched data for {ticker}.")
            
            # --- Transformation Logic ---
            for entry in stock_json.get("data", []):
                date = entry.get("date")
                open_price = entry.get("open")
                close_price = entry.get("close")
                
                # Calculate difference (Close - Open)
                diff = round(close_price - open_price, 2)
                
                final_price_analysis.append({
                    "date": date,
                    "difference": diff
                })
        else:
            print(f"Failed to fetch stocks: {stock_response.status_code}")

        # --- Step 3: Fetch Growth Data (Team 2) ---
        print(f"\n--- Step 3: Fetching Apple Growth Data (last {days_to_trace} days) ---")
        growth_url = f"{BASE_URL_GROWTH}/growth/Apple"
        growth_params = {"days": days_to_trace}
        
        growth_response = requests.get(growth_url, params=growth_params)

        # add logic
        final_price_analysis
        growth_response

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_external_stock_integration()