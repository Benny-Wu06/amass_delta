from datetime import datetime, timedelta

def calculate_growth_stats(vulnerability_counts, days):
    # map the db list into a dictionary
    daily_counts = {str(entry[0]): entry[1] for entry in vulnerability_counts}
    
    data_points = []
    total_increase = 0
    peak_val = -1
    peak_day = "N/A"
    today = datetime.now()
    
    for i in range(days - 1, -1, -1):
        target_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        count = daily_counts.get(target_date, 0)
        
        data_points.append({"date": target_date, "new_cves": count})
        
        total_increase += count
        if count > peak_val:
            peak_val = count
            peak_day = target_date
            
    return data_points, total_increase, peak_day