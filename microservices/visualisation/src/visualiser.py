import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json

def visualiser(json_data):
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return

    if "heatmap_grid" in data:
        df_heat = pd.DataFrame(data["heatmap_grid"])
        pivot_table = df_heat.pivot(index="epss", columns="cvss", values="count").fillna(0)

        # sort axis
        cvss_order = ["0-2", "2-4", "4-6", "6-8", "8-10"]
        epss_order = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
        
        # reindex
        pivot_table = pivot_table.reindex(index=epss_order[::-1], columns=cvss_order).fillna(0)

        plt.figure(figsize=(8, 6))
        sns.heatmap(pivot_table, annot=True, cmap="Reds", fmt='g')
        plt.title(f"{data.get('company_name', 'Company')}: Risk Heatmap (CVSS vs EPSS)")

        plt.savefig('cve_heatmap.png')
        print("saved: cve_heatmap.png")

    elif "data_points" in data:
        df_line = pd.DataFrame(data['data_points'])
        summary = data['summary']
        
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_line, x='date', y='new_cves', marker='o', linewidth=5, color='#d62708')
        
        # Title and Labels
        plt.title(f"CVE Growth Trend: {data.get('company_name')}", fontsize=14, pad=20)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)

        stats_box = (
            f"=== PERIOD SUMMARY ===\n"
            f"Total CVE Increase: {summary['total_period_increase']}\n"
            f"Peak Date: {summary['peak_growth_day']}"
        )

        # position summary box 'upper left'
        plt.gca().annotate(
            stats_box, 
            xy=(0.02, 0.95), 
            xycoords='axes fraction',
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8)
        )

        plt.tight_layout()
        plt.savefig('cve_growth_chart.png')
        print("saved: cve_growth_chart.png")
    
    else:
        print("error: unknown data format")
    
    plt.close()


# --- DUMMY DATA ---

cve_growth_json = """
{
    "company_name": "Microsoft",
    "data_points": [
        {"date": "2026-03-09", "new_cves": 0},
        {"date": "2026-03-10", "new_cves": 2},
        {"date": "2026-03-11", "new_cves": 0},
        {"date": "2026-03-12", "new_cves": 5},
        {"date": "2026-03-13", "new_cves": 0}
    ],
    "summary": {
        "total_period_increase": 7,
        "peak_growth_day": "2026-03-12"
    }
}
"""

heatmap_json = """
{
    "company_name": "Microsoft",
    "heatmap_grid": [
        {"cvss": "0-2",   "epss": "0-0.2",   "count": 0},
        {"cvss": "2-4",   "epss": "0-0.2",   "count": 0},
        {"cvss": "4-6",   "epss": "0-0.2",   "count": 0},
        {"cvss": "6-8",   "epss": "0-0.2",   "count": 0},
        {"cvss": "8-10",  "epss": "0-0.2",   "count": 0},
        {"cvss": "0-2",   "epss": "0.2-0.4", "count": 0},
        {"cvss": "2-4",   "epss": "0.2-0.4", "count": 0},
        {"cvss": "4-6",   "epss": "0.2-0.4", "count": 0},
        {"cvss": "6-8",   "epss": "0.2-0.4", "count": 0},
        {"cvss": "8-10",  "epss": "0.2-0.4", "count": 1},
        {"cvss": "8-10",  "epss": "0.8-1.0", "count": 1}
    ]
}
"""

visualiser(cve_growth_json)