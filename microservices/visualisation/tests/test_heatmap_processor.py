import pytest
from visualisation.src.heatmap.heatmap_processor import format_heatmap

def test_partial_data():
    # only two buckets have data
    mock_sql_results = [
        ('8-10', '0.8-1.0', 50),
        ('0-2', '0-0.2', 10)
    ]
    
    grid = format_heatmap(mock_sql_results)
    
    # grid must always be 5x5
    assert len(grid) == 25
    
    # find the specific cells we provided
    high_risk_cell = next(cell for cell in grid if cell['cvss_range'] == '8-10' and cell['epss_range'] == '0.8-1.0')
    low_risk_cell = next(cell for cell in grid if cell['cvss_range'] == '0-2' and cell['epss_range'] == '0-0.2')

    assert high_risk_cell['cve_count'] == 50
    assert low_risk_cell['cve_count'] == 10

    # check taht other cells ar empty
    empty_cell_1 = next(cell for cell in grid if cell['cvss_range'] == '4-6' and cell['epss_range'] == '0.4-0.6')
    empty_cell_2 = next(cell for cell in grid if cell['cvss_range'] == '4-6' and cell['epss_range'] == '0-0.2')
    empty_cell_3 = next(cell for cell in grid if cell['cvss_range'] == '2-4' and cell['epss_range'] == '0.8-1.0')
    
    assert empty_cell_1['cve_count'] == 0
    assert empty_cell_2['cve_count'] == 0
    assert empty_cell_3['cve_count'] == 0

def test_empty_results():
    # test a company with no CVEs
    grid = format_heatmap([])
    
    # grid must always be 5x5
    assert len(grid) == 25
    assert all(cell['cve_count'] == 0 for cell in grid)
