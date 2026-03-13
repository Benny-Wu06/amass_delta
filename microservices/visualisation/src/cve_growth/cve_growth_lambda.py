import json
from microservices.visualisation.src.db_queries import fetch_company_name, fetch_vulnerability_data
from cve_growth_processor import calculate_growth_stats

def cve_growth_lambda(event, context):
    try:
        company_id = event.get('pathParameters', {}).get('company_id')
        days = int(event.get('queryStringParameters', {}).get('days', 30))
        
        # error check
        if days <= 0:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Days has to be greater than zero"})
            }

        # error check
        name = fetch_company_name(db, company_id)
        if not name: 
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"Company {company_id} not found"})
            }
        
        # proceed
        raw_vuls = fetch_vulnerability_data(db, company_id, days)
        
        data_points, total_increase, peak_day = calculate_growth_stats(raw_vuls, days)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "company_name": name,
                "data_points": data_points,
                "summary": {
                    "total_period_increase": total_increase,
                    "peak_growth_day": peak_day
                }
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
