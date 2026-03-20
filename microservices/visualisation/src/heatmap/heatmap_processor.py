def format_heatmap(raw_data):
    cvss_buckets = ["0-2", "2-4", "4-6", "6-8", "8-10"]
    epss_buckets = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]

    # lookup map from the database results
    map = {(row[0], row[1]): row[2] for row in raw_data}

    heatmap_grid = []
    for epss in epss_buckets:
        for cvss in cvss_buckets:
            heatmap_grid.append(
                {
                    "cvss_range": cvss,
                    "epss_range": epss,
                    "cve_count": map.get((cvss, epss), 0),
                }
            )

    return heatmap_grid
