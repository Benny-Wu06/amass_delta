import pytest
from microservices.visualisation.src.visualiser.visualiser import generate_plot_bytes

######################## DELETE PNG'S AFTER MANUALLY !!! ############################

def test_visualiser_data_points_success():
    dummy_data_points = {
        "company_name": "Microsoft",
        "data_points": [
            {"date": "2026-03-05", "new_cves": 5},
            {"date": "2026-03-06", "new_cves": 2},
            {"date": "2026-03-07", "new_cves": 4},
            {"date": "2026-03-08", "new_cves": 5},
            {"date": "2026-03-09", "new_cves": 0},
            {"date": "2026-03-10", "new_cves": 2},
            {"date": "2026-03-11", "new_cves": 0},
            {"date": "2026-03-12", "new_cves": 3},
            {"date": "2026-03-13", "new_cves": 1}
        ],
        "summary": {
            "total_period_increase": 22,
            "peak_growth_day": "2026-03-12"
        }
    }

    try:
        image_bytes = generate_plot_bytes(dummy_data_points)
        
        # verify output
        if isinstance(image_bytes, bytes) and len(image_bytes) > 0:
            print(f"Success! Generated {len(image_bytes)} bytes of data.")
            
            # save to a file (for manual check)
            with open("test_data_points.png", "wb") as f:
                f.write(image_bytes)
            print("Saved to 'test_data_points.png' for visual inspection.")
        else:
            print("FAIL: No binary data returned.")
            
    except Exception as e:
        print(f"FAIL: {e}")

def test_visualiser_heatmap_grid_success():
    dummy_heatmap_grid = {
        "company_name": "Apple",
        "heatmap_grid": [
            {"cvss": "0-2",   "epss": "0-0.2",   "count": 3},
            {"cvss": "2-4",   "epss": "0-0.2",   "count": 4},
            {"cvss": "4-6",   "epss": "0-0.2",   "count": 0},
            {"cvss": "6-8",   "epss": "0-0.2",   "count": 0},
            {"cvss": "8-10",  "epss": "0-0.2",   "count": 6},
            {"cvss": "0-2",   "epss": "0.2-0.4", "count": 5},
            {"cvss": "2-4",   "epss": "0.2-0.4", "count": 5},
            {"cvss": "4-6",   "epss": "0.2-0.4", "count": 0},
            {"cvss": "6-8",   "epss": "0.2-0.4", "count": 2},
            {"cvss": "8-10",  "epss": "0.2-0.4", "count": 1},
            {"cvss": "8-10",  "epss": "0.8-1.0", "count": 1}
        ]
    }

    try:
        image_bytes = generate_plot_bytes(dummy_heatmap_grid)
        
        # verify output
        if isinstance(image_bytes, bytes) and len(image_bytes) > 0:
            # save to a file (for manual check)
            with open("test_heatmap_grid.png", "wb") as f:
                f.write(image_bytes)
            print("Saved to 'test_heatmap_grid.png' for visual inspection.")
        else:
            print("FAIL: No binary data returned.")
            
    except Exception as e:
        print(f"FAIL: {e}")

def test_visualiser_invalid():
    invalid_data = {
        "invalid_field": "invalid_content"
    }
    
    # This asserts that the function raises a ValueError
    with pytest.raises(ValueError, match="Unknown data format"):
        generate_plot_bytes(invalid_data)