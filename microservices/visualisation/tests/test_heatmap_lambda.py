import json
from microservices.visualisation.src.db import get_db_connection
from microservices.visualisation.src.db_queries import get_heatmap_data
from microservices.visualisation.src.heatmap.heatmap_processor import format_heatmap

################## !!! WORKING TRIAL !!! #######################

# DB CONNECTION STARTER CODE


def trial_db_connection_heatmap():
    try:
        conn = get_db_connection()

        with conn.cursor() as db_cursor:
            # test company 1
            company_name = "Microsoft"

            if not company_name:
                print(
                    {
                        "statusCode": 404,
                        "body": json.dumps(
                            {"error": f"Company {company_name} not found"}
                        ),
                    }
                )
                return

            raw_data = get_heatmap_data(db_cursor, company_name)
            heatmap_grid = format_heatmap(raw_data)

            print(
                {
                    "statusCode": 200,
                    "body": json.dumps(
                        {"company_name": company_name, "heatmap_grid": heatmap_grid}
                    ),
                }
            )
            return

    except Exception as e:
        print(f"Error: {str(e)}")
        print({"statusCode": 500, "body": json.dumps({"error": str(e)})})
        return

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    trial_db_connection_heatmap()  # works 👌
