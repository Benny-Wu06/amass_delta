import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io

# Custom styling
sns.set_theme(style="darkgrid")
plt.rcParams.update({
    'font.family': 'monospace',
    'font.monospace': ['Courier New', 'DejaVu Sans Mono', 'Consolas', 'Lucida Console'],
    'axes.titlesize': 16,
    'axes.labelsize': 12,
    'figure.dpi': 150
})

def generate_plot_bytes(data):
    buf = io.BytesIO()

    # HEATMAP
    if "heatmap_grid" in data:
        df_heat = pd.DataFrame(data["heatmap_grid"])
        pivot_table = df_heat.pivot(index="epss", columns="cvss", values="count").fillna(0)
        cvss_order = ["0-2", "2-4", "4-6", "6-8", "8-10"]
        epss_order = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
        pivot_table = pivot_table.reindex(index=epss_order[::-1], columns=cvss_order).fillna(0)

        plt.figure(figsize=(9, 7))
        ax = sns.heatmap(pivot_table, annot=True, cmap="Reds", fmt='g')
        ax.set_xlabel("CVSS Score", fontweight='bold')
        ax.set_ylabel("EPSS Score", fontweight='bold')
        plt.title(f"{data.get('company_name', 'Company')}: Risk Heatmap", pad=20, fontweight='bold')

    # LINE GRAPH
    elif "data_points" in data:
        df_line = pd.DataFrame(data['data_points'])
        summary = data['summary']
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(data=df_line, x='date', y='new_cves', marker='o', linewidth=2.5, color='#d62708')
        
        ax.set_xlabel("Observation Date", fontweight='bold', labelpad=10)
        ax.set_ylabel("New CVEs Reported", fontweight='bold', labelpad=10)
        plt.title(f"CVE Growth Trend: {data.get('company_name')}", fontsize=16, pad=20, fontweight='bold')
        
        stats_box = (f"Total Increase: {summary['total_period_increase']}\nPeak: {summary['peak_growth_day']}")
        plt.gca().annotate(stats_box, xy=(0.02, 0.9), xycoords='axes fraction', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        plt.tight_layout()
    else:
        raise ValueError("Unknown data format: missing required keys")

    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf.read()