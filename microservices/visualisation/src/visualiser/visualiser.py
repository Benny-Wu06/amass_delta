import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import io

def generate_plot_bytes(data):
    # create an in-memory binary stream
    buf = io.BytesIO()

    # HEATMAP
    if "heatmap_grid" in data:
        df_heat = pd.DataFrame(data["heatmap_grid"])
        pivot_table = df_heat.pivot(index="epss", columns="cvss", values="count").fillna(0)
        
        cvss_order = ["0-2", "2-4", "4-6", "6-8", "8-10"]
        epss_order = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
        pivot_table = pivot_table.reindex(index=epss_order[::-1], columns=cvss_order).fillna(0)

        plt.figure(figsize=(8, 6))
        sns.heatmap(pivot_table, annot=True, cmap="Reds", fmt='g')
        plt.title(f"{data.get('company_name', 'Company')}: Risk Heatmap")

    # LINE GRAPH
    elif "data_points" in data:
        df_line = pd.DataFrame(data['data_points'])
        summary = data['summary']
        
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_line, x='date', y='new_cves', marker='o', linewidth=5, color='#d62708')
        
        plt.title(f"CVE Growth Trend: {data.get('company_name')}", fontsize=14, pad=20)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)

        stats_box = (
            f"=== PERIOD SUMMARY ===\n"
            f"Total CVE Increase: {summary['total_period_increase']}\n"
            f"Peak Date: {summary['peak_growth_day']}"
        )

        plt.gca().annotate(
            stats_box, xy=(0.02, 0.95), xycoords='axes fraction', fontsize=10, 
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8)
        )
        plt.tight_layout()

    else:
        return {"statusCode": 400, "body": json.dumps({"error": "Unknown data format"})}

    # save to buffer
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return buf.read()