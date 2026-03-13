import json
from db_queries import fetch_company_name, fetch_vulnerability_data
from cve_growth_process import process_time_series

def cve_growth_lambda(event, context):
    try:
        company_id = event.get('pathParameters', {}).get('company_id')
        days = int(event.get('queryStringParameters', {}).get('days', 30))
        
        name = fetch_company_name(db, company_id)
        if not name: 
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"Company {company_id} not found"})
            }
        
        raw_vuls = fetch_vulnerability_data(db, company_id, days)
        
        results = process_time_series(raw_vuls, days)
        results['company'] = name
        
        return {
            "statusCode": 200, 
            "body": json.dumps(results)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
