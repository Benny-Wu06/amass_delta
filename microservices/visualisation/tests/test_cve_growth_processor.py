from datetime import date, datetime
from microservices.visualisation.src.cve_growth.cve_growth_processor import (
    calculate_growth_stats,
)


def test_calculate_growth_stats():
    mock_db_query_results = [(date(2026, 3, 10), 2), (date(2026, 3, 12), 5)]

    # Force "today" to be March 13, 2026 for consistent testing
    ref_date = datetime(2026, 3, 13)

    data_points, total, peak_day = calculate_growth_stats(
        mock_db_query_results, 5, reference_date=ref_date
    )

    assert total == 7
    assert peak_day == "2026-03-12"
    assert len(data_points) == 5

    assert data_points == [
        {"x": "2026-03-09", "y": 0},
        {"x": "2026-03-10", "y": 2},
        {"x": "2026-03-11", "y": 0},
        {"x": "2026-03-12", "y": 5},
        {"x": "2026-03-13", "y": 0},
    ]
