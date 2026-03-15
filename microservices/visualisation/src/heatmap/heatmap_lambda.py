import json
from db import get_db_connection
from db_queries import get_heatmap_data, fetch_company_name
from heatmap_processor import format_heatmap

def heatmap_lambda(event, context):
    try:
        conn = get_db_connection()

        with conn.cursor() as db_cursor:

            company_id = event.get('pathParameters', {}).get('company_id')

            name = fetch_company_name(db_cursor, company_id)
            if not name: 
                return {
                    "statusCode": 404,
                    "headers": {"Content-Type: application/json"},
                    "body": json.dumps({"error": f"Company {company_id} not found"})
                }
            
            raw_data = get_heatmap_data(db_cursor, company_id)
            grid = format_heatmap(raw_data)
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type: application/json"},
                "body": json.dumps({
                    "company_name": name,
                    "heatmap_grid": grid
                })
            }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
    finally:
        if conn:
            conn.close()