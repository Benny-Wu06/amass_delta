import json
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Custom styling
sns.set_theme(style="darkgrid")
plt.rcParams.update(
    {
        "font.family": "monospace",
        "font.monospace": [
            "Courier New",
            "DejaVu Sans Mono",
            "Consolas",
            "Lucida Console",
        ],
        "axes.titlesize": 16,
        "axes.labelsize": 12,
        "figure.dpi": 150,
    }
)


def generate_plot_bytes(data):
    buf = io.BytesIO()

    if "heatmap_grid" in data:
        generate_heatmap(data)
    elif "data_points" in data:
        generate_line_graph(data)
    else:
        raise ValueError("Unknown data format: missing required keys")

    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf.read()


############################## GRAPH GENERATION HELPERS #################################


def generate_heatmap(data):
    df_heat = pd.DataFrame(data["heatmap_grid"])
    pivot_table = df_heat.pivot(
        index="epss_range", columns="cvss_range", values="cve_count"
    ).fillna(0)
    cvss_order = ["0-2", "2-4", "4-6", "6-8", "8-10"]
    epss_order = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
    pivot_table = pivot_table.reindex(
        index=epss_order[::-1], columns=cvss_order
    ).fillna(0)

    plt.figure(figsize=(9, 7))
    ax = sns.heatmap(pivot_table, annot=True, cmap="Reds", fmt="g")
    ax.set_xlabel("CVSS Score", fontweight="bold")
    ax.set_ylabel("EPSS Score", fontweight="bold")
    plt.title(
        f"{data.get('company_name', 'Company')}: Risk Heatmap",
        pad=20,
        fontweight="bold",
    )


def generate_line_graph(data):
    # split fields
    df_line = pd.DataFrame(data["data_points"])
    metadata = data.get("metadata", {})
    summary = data["summary"]

    plt.figure(figsize=(10, 6))

    # use 'x' and 'y' from the generalised data
    ax = sns.lineplot(
        data=df_line, 
        x="x", 
        y="y", 
        marker="o", 
        linewidth=2.5, 
        color="#d62708"
    )

    ax.set_xlabel(metadata.get("x_label", "X Axis"), fontweight="bold", labelpad=10)
    ax.set_ylabel(metadata.get("y_label", "Y Axis"), fontweight="bold", labelpad=10)
    plt.title(
        metadata.get("title", "Growth Trend"),
        fontsize=16,
        pad=20,
        fontweight="bold",
    )

    # optional
    if summary:
        # Check for generalized keys or fall back to specific ones
        total = summary.get("total_period_increase", "N/A")
        peak = summary.get("peak_growth_day", "N/A")
        
        stats_box = f"Total: {total}\nPeak: {peak}"
        plt.gca().annotate(
            stats_box,
            xy=(0.02, 0.9),
            xycoords="axes fraction",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8),
        )

    plt.tight_layout()


###########################################################################################


############## LAMBDA FUNCTION ###############


def visualiser_lambda(event, context):
    try:
        body = event.get("body")
        data = json.loads(body) if isinstance(body, str) else body

        binary_data = generate_plot_bytes(data)

        b64_image = base64.b64encode(binary_data).decode("utf-8")

        logger.info(f"Success generated visualisation for company: {data.get('company_name', 'Company')}")
        return {
            "isBase64Encoded": True,
            "statusCode": 200,
            "headers": {"Content-Type": "image/png"},
            "body": b64_image,
        }

    except ValueError as e:
        logger.error(f"Error: {str(e)}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
