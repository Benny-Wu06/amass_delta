import json
from decimal import Decimal
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from company_vulnerabilities import lambda_handler


#
#   MOCk connection
#
@patch('psycopg2.connect')
def test_locally(mock_connect):
    
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    # Simulate the columns in your SQL table
    mock_cur.description = [
        ('cve_id',), ('company_name',), ('vulnerability_name',), 
        ('cvss_score',), ('cvss_severity',)
    ]
    
    # Simulate two rows of data found for "AcmeCorp"
    mock_cur.fetchall.return_value = [
        ('CVE-2026-1234', 'AcmeCorp', 'Injection', Decimal('9.8'), 'CRITICAL'),
        ('CVE-2026-5678', 'AcmeCorp', 'Broken Auth', Decimal('7.5'), 'HIGH')
    ]

    # 3. Create the mock API Gateway Event
    event = {
        "pathParameters": {
            "company_name": "AcmeCorp"
        }
    }

    # 4. Run the handler
    print("Testing Lambda Handler with 'AcmeCorp'...")
    response = lambda_handler(event, None)

    # 5. Print the formatted result
    print(f"Status: {response['statusCode']}")
    print("Body JSON Output:")
    print(json.dumps(json.loads(response['body']), indent=4))

if __name__ == "__main__":
    test_locally()