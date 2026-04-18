from datetime import datetime, timedelta


def calculate_growth_stats(vulnerability_counts, days, reference_date=None):
    if reference_date is None:
        reference_date = datetime.now()

    daily_counts = {str(entry[0]): entry[1] for entry in vulnerability_counts}

    data_points = []
    total_increase = 0
    peak_val = -1
    peak_day = "N/A"

    for i in range(days - 1, -1, -1):
        target_date = (reference_date - timedelta(days=i)).strftime("%Y-%m-%d")
        count = daily_counts.get(target_date, 0)

        data_points.append({"x": target_date, "y": count})

        total_increase += count
        if count > peak_val:
            peak_val = count
            peak_day = target_date

    return data_points, total_increase, peak_day
