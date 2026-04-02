import pytest
import requests

BASE_URL = "https://blj7h0zmba.execute-api.ap-southeast-2.amazonaws.com"

# MOCK INPUT (Retrieved from other routes by the user)
GROWTH_INPUT = {
    "company_name": "TestCorp1",
    "data_points": [
        {"date": "2026-03-26", "new_cves": 0},
        {"date": "2026-03-27", "new_cves": 2},
        {"date": "2026-03-28", "new_cves": 0},
        {"date": "2026-03-29", "new_cves": 4},
        {"date": "2026-03-30", "new_cves": 1}
    ],
    "summary": {"total_period_increase": 4, "peak_growth_day": "2026-03-29"}
}

HEATMAP_INPUT = {
    "company_name": "TestCorp1",
    "heatmap_grid": [
        # CVSS 0-2
        {"cvss_range": "0-2", "epss_range": "0-0.2", "cve_count": 0},
        {"cvss_range": "0-2", "epss_range": "0.2-0.4", "cve_count": 0},
        {"cvss_range": "0-2", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "0-2", "epss_range": "0.6-0.8", "cve_count": 0},
        {"cvss_range": "0-2", "epss_range": "0.8-1.0", "cve_count": 0},
        
        # CVSS 2-4
        {"cvss_range": "2-4", "epss_range": "0-0.2", "cve_count": 0},
        {"cvss_range": "2-4", "epss_range": "0.2-0.4", "cve_count": 0},
        {"cvss_range": "2-4", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "2-4", "epss_range": "0.6-0.8", "cve_count": 1},
        {"cvss_range": "2-4", "epss_range": "0.8-1.0", "cve_count": 1},
        
        # CVSS 4-6
        {"cvss_range": "4-6", "epss_range": "0-0.2", "cve_count": 0},
        {"cvss_range": "4-6", "epss_range": "0.2-0.4", "cve_count": 1},
        {"cvss_range": "4-6", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "4-6", "epss_range": "0.6-0.8", "cve_count": 0},
        {"cvss_range": "4-6", "epss_range": "0.8-1.0", "cve_count": 0},
        
        # CVSS 6-8
        {"cvss_range": "6-8", "epss_range": "0-0.2", "cve_count": 1},
        {"cvss_range": "6-8", "epss_range": "0.2-0.4", "cve_count": 0},
        {"cvss_range": "6-8", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "6-8", "epss_range": "0.6-0.8", "cve_count": 1},
        {"cvss_range": "6-8", "epss_range": "0.8-1.0", "cve_count": 0},
        
        # CVSS 8-10
        {"cvss_range": "8-10", "epss_range": "0-0.2", "cve_count": 0},
        {"cvss_range": "8-10", "epss_range": "0.2-0.4", "cve_count": 0},
        {"cvss_range": "8-10", "epss_range": "0.4-0.6", "cve_count": 0},
        {"cvss_range": "8-10", "epss_range": "0.6-0.8", "cve_count": 0},
        {"cvss_range": "8-10", "epss_range": "0.8-1.0", "cve_count": 1}
    ]
}

# TESTS
def test_visualiser_renders_growth_trend_png():
    url = f"{BASE_URL}/v1/visualise"
    
    response = requests.post(url, json=GROWTH_INPUT, timeout=20)
    
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "image/png"
    assert len(response.content) > 1000     # pngs are usually at least a few KB

def test_visualiser_renders_heatmap_png():
    url = f"{BASE_URL}/v1/visualise" # Update with your actual route
    
    response = requests.post(url, json=HEATMAP_INPUT, timeout=20)
    
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "image/png"
    assert len(response.content) > 1000     # pngs are usually at least a few KB

def test_visualiser_invalid_data_400():
    url = f"{BASE_URL}/v1/visualise"
    
    # missing 'heatmap_grid' and 'data_points'
    invalid_input = {"company_name": "BrokenCorp", "random_key": "data"}
    
    response = requests.post(url, json=invalid_input, timeout=10)
    
    assert response.status_code == 400
    assert "error" in response.json()

def test_visualiser_get_method_not_allowed():
    url = f"{BASE_URL}/v1/visualise"
    
    response = requests.get(url, timeout=10)
    
    # should be an error
    assert response.status_code == 404