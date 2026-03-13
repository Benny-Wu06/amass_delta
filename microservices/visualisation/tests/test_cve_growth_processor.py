from datetime import date
from visualisation.src.cve_growth.cve_growth_processor import calculate_growth_stats

def test_calculate_growth_stats():
    mock_db_query_results = [
        (date(2026, 3, 10), 2),
        (date(2026, 3, 12), 5)
    ]
    
    # Test with a 5-day window
    data_points, total, peak_day = calculate_growth_stats(mock_db_query_results, 5)
    
    assert total == 7
    assert peak_day == "2026-03-12"
    assert len(data_points) == 5

    assert data_points == [
        {'date': '2026-03-09', 'new_cves': 0},
        {'date': '2026-03-10', 'new_cves': 2},
        {'date': '2026-03-11', 'new_cves': 0},
        {'date': '2026-03-12', 'new_cves': 5},
        {'date': '2026-03-13', 'new_cves': 0}
    ]