import json
import base64
from visualiser import generate_plot_bytes

def lambda_handler(event, context):
    try:
        body = event.get('body')
        data = json.loads(body) if isinstance(body, str) else body
        
        binary_data = generate_plot_bytes(data)
        
        b64_image = base64.b64encode(binary_data).decode('utf-8')
        
        return {
            "isBase64Encoded": True,
            "statusCode": 200,
            "headers": {"Content-Type": "image/png"},
            "body": b64_image
        }
    except json.JSONDecodeError as e:
        return {
            "statusCode": 400, 
            "body": json.dumps({"error": f"Invalid JSON: {str(e)}"})
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }