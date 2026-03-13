import psycopg2
import json
from visualisation.db_queries import get_heatmap_data, fetch_company_name
from visualisation.src.heatmap.heatmap_processor import format_heatmap

password = "testdiddyblud"

# DB CONNECTION STARTER CODE
conn = None
try:
    conn = psycopg2.connect(
        host='testdb.cjwhnekr8yms.us-east-1.rds.amazonaws.com',
        port=5432,
        database='postgres',
        user='postgres',
        password=password,
        sslmode='prefer',
        connect_timeout=3,
        sslrootcert='/certs/global-bundle.pem'
    )
    db_cursor = conn.cursor()

    try:
        company_id = 1      # test company 1

        name = fetch_company_name(db_cursor, company_id)
        if not name: 
            print({
                "statusCode": 404,
                "body": json.dumps({"error": f"Company {company_id} not found"})
            } )
        
        raw_data = get_heatmap_data(db_cursor, company_id)
        grid = format_heatmap(raw_data)
        
        print({
            "statusCode": 200,
            "body": json.dumps({
                "company_name": name,
                "grid": grid
            })
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        print( {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        })

    db_cursor.close()

except Exception as e:
    print(f"Database error: {e}")
    raise
finally:
    if conn:
       conn.close()