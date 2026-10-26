"""
exploration.py
--------------
Step 2: Exploratory Data Analysis (EDA) and visualizations.

Generates and saves three required figures:
1. outputs/figures/time_series_light_co2.png: Light and CO2 sensor readings over time
   colored by Occupied (1) vs Empty (0).
2. outputs/figures/class_balance.png: Class balance comparison across Training,
   Test 1 (Door Closed), and Test 2 (Door Open).
3. outputs/figures/correlation_heatmap.png: Correlation heatmap among all 5 sensor features.

Author: 2nd-Year B.Tech APL Project Team
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from data_loading import load_all_data


def plot_time_series(train_df, output_path="outputs/figures/time_series_light_co2.png"):
    """
    Plot Light and CO2 over time for the training dataset.
    Points are coloured by Occupancy (0 = Empty, 1 = Occupied).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # We take the training set to show typical weekly office behavior
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # Subplot 1: Light (Lux) over time
    sns.lineplot(
        data=train_df,
        x="date",
        y="Light",
        color="gray",
        alpha=0.4,
        linewidth=0.8,
        ax=ax1,
        label="Light Trend"
    )
    scatter1 = sns.scatterplot(
        data=train_df,
        x="date",
        y="Light",
        hue="Occupancy",
        palette={0: "#2b5c8f", 1: "#e74c3c"},
        style="Occupancy",
        markers={0: ".", 1: "o"},
        s=25,
        alpha=0.7,
        ax=ax1
    )
    ax1.set_title("Light Intensity (Lux) Over Time (Training Set)", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Light (Lux)", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # Custom legend for subplot 1
    handles, _ = scatter1.get_legend_handles_labels()
    ax1.legend(handles=[handles[1], handles[2]], labels=["Empty (0)", "Occupied (1)"], loc="upper right")

    # Subplot 2: CO2 (ppm) over time
    sns.lineplot(
        data=train_df,
        x="date",
        y="CO2",
        color="gray",
        alpha=0.4,
        linewidth=0.8,
        ax=ax2,
        label="CO2 Trend"
    )
    scatter2 = sns.scatterplot(
        data=train_df,
        x="date",
        y="CO2",
        hue="Occupancy",
        palette={0: "#2b5c8f", 1: "#e74c3c"},
        style="Occupancy",
        markers={0: ".", 1: "o"},
        s=25,
        alpha=0.7,
        ax=ax2
    )
    ax2.set_title("CO2 Concentration (ppm) Over Time (Training Set)", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Timestamp", fontsize=11)
    ax2.set_ylabel("CO2 (ppm)", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    handles2, _ = scatter2.get_legend_handles_labels()
    ax2.legend(handles=[handles2[1], handles2[2]], labels=["Empty (0)", "Occupied (1)"], loc="upper right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[INFO] Saved time series plot -> {output_path}")


def plot_class_balance(train_df, test1_df, test2_df, output_path="outputs/figures/class_balance.png"):
    """
    Plot bar charts comparing the class balance (Empty vs Occupied)
    across all three dataset splits.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    summary_rows = []
    datasets = [
        ("Training\n(datatraining)", train_df),
        ("Test 1: Door Closed\n(datatest)", test1_df),
        ("Test 2: Door Open\n(datatest2)", test2_df)
    ]

    for name, df in datasets:
        counts = df["Occupancy"].value_counts()
        total = len(df)
        summary_rows.append({
            "Dataset": name,
            "Class": "Empty (0)",
            "Count": counts.get(0, 0),
            "Percentage": (counts.get(0, 0) / total) * 100
        })
        summary_rows.append({
            "Dataset": name,
            "Class": "Occupied (1)",
            "Count": counts.get(1, 0),
            "Percentage": (counts.get(1, 0) / total) * 100
        })

    bal_df = pd.DataFrame(summary_rows)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Raw counts
    sns.barplot(
        data=bal_df,
        x="Dataset",
        y="Count",
        hue="Class",
        palette={"Empty (0)": "#3498db", "Occupied (1)": "#e67e22"},
        ax=ax1
    )
    ax1.set_title("Sample Counts per Class", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Number of Samples", fontsize=11)
    ax1.set_xlabel("")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)
    for p in ax1.patches:
        h = p.get_height()
        if h > 0:
            ax1.annotate(f"{int(h)}", (p.get_x() + p.get_width() / 2., h),
                         ha='center', va='bottom', fontsize=9, xytext=(0, 3),
                         textcoords='offset points')

    # Percentages
    sns.barplot(
        data=bal_df,
        x="Dataset",
        y="Percentage",
        hue="Class",
        palette={"Empty (0)": "#3498db", "Occupied (1)": "#e67e22"},
        ax=ax2
    )
    ax2.set_title("Class Proportion (%)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Percentage (%)", fontsize=11)
    ax2.set_xlabel("")
    ax2.set_ylim(0, 100)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)
    for p in ax2.patches:
        h = p.get_height()
        if h > 0:
            ax2.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h),
                         ha='center', va='bottom', fontsize=9, xytext=(0, 3),
                         textcoords='offset points')

    plt.suptitle("Class Balance Across Training and Test Datasets", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Saved class balance plot -> {output_path}")


def plot_correlation_heatmap(train_df, output_path="outputs/figures/correlation_heatmap.png"):
    """
    Plot Pearson correlation heatmap between sensor measurements and occupancy.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    sensor_cols = ["Temperature", "Humidity", "Light", "CO2", "HumidityRatio", "Occupancy"]
    corr_matrix = train_df[sensor_cols].corr()

    plt.figure(figsize=(8, 6.5))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.8,
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation"}
    )
    plt.title("Sensor Correlation Matrix (Training Set)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[INFO] Saved correlation heatmap -> {output_path}")


def run_exploration():
    """Run all exploratory data analysis visualizations."""
    print("[STEP 2] Running Exploratory Data Analysis (EDA)...")
    train_df, test1_df, test2_df = load_all_data("data")

    plot_time_series(train_df)
    plot_class_balance(train_df, test1_df, test2_df)
    plot_correlation_heatmap(train_df)
    print("[STEP 2] All EDA plots saved successfully to outputs/figures/\n")


if __name__ == "__main__":
    run_exploration()
