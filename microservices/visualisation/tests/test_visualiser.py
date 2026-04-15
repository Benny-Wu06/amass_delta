import pytest
from microservices.visualisation.src.visualiser.visualiser import generate_plot_bytes

######################## DELETE PNG'S AFTER MANUALLY !!! ############################


def test_visualiser_data_points_success():
    dummy_data_points = {
        "data_points": [
            {"x": "2026-03-05", "y": 5},
            {"x": "2026-03-06", "y": 2},
            {"x": "2026-03-07", "y": 4},
            {"x": "2026-03-08", "y": 5},
            {"x": "2026-03-09", "y": 0},
            {"x": "2026-03-10", "y": 2},
            {"x": "2026-03-11", "y": 0},
            {"x": "2026-03-12", "y": 3},
            {"x": "2026-03-13", "y": 1},
        ],
        "metadata": {
            "x_label": "Date",
            "y_label": "New Vulnerabilities",
            "title": "Microsoft Vulnerability Growth"
        },
        "summary": {
            "total_period_increase": 22,
            "peak_growth_day": "2026-03-12"
        },
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
            {"cvss_range": "0-2", "epss_range": "0-0.2", "cve_count": 3},
            {"cvss_range": "2-4", "epss_range": "0-0.2", "cve_count": 4},
            {"cvss_range": "4-6", "epss_range": "0-0.2", "cve_count": 0},
            {"cvss_range": "6-8", "epss_range": "0-0.2", "cve_count": 0},
            {"cvss_range": "8-10", "epss_range": "0-0.2", "cve_count": 6},
            {"cvss_range": "0-2", "epss_range": "0.2-0.4", "cve_count": 5},
            {"cvss_range": "2-4", "epss_range": "0.2-0.4", "cve_count": 5},
            {"cvss_range": "4-6", "epss_range": "0.2-0.4", "cve_count": 0},
            {"cvss_range": "6-8", "epss_range": "0.2-0.4", "cve_count": 2},
            {"cvss_range": "8-10", "epss_range": "0.2-0.4", "cve_count": 1},
            {"cvss_range": "8-10", "epss_range": "0.8-1.0", "cve_count": 1},
        ],
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
    invalid_data = {"invalid_field": "invalid_content"}

    # This asserts that the function raises a ValueError
    with pytest.raises(ValueError, match="Unknown data format"):
        generate_plot_bytes(invalid_data)
