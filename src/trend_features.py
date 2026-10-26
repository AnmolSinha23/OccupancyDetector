"""
trend_features.py
-----------------
Step 7: Temporal Trend Engineering (Contribution 2)

Key Concepts & Viva Explanation:
1. Real-Time Causality:
   A real-time deployment can only inspect current and past sensor readings ($t, t-1, t-2, ...$).
   Future readings ($t+1$) are unknown, so centering rolling windows or shifting backwards
   would cause catastrophic look-ahead data leakage. We use strictly backward-looking features.
2. Sampling Interval:
   The dataset timestamp delta is 1 minute (60 seconds). Therefore, a 5-minute trend
   window corresponds to 5 consecutive rows.
3. Features Created:
   - 'CO2_diff_5min': CO2(t) - CO2(t - 5). Captures rate of human respiration buildup.
   - 'Light_mean_5min': 5-minute rolling average of Light intensity. Smoothes sensor noise.
4. Handling Boundary Rows (Rows 0 to 4):
   - For CO2 difference: fillna(0.0) -> neutral rate of change before history is recorded.
   - For Light rolling mean: rolling(window=5, min_periods=1).mean() -> averages whatever
     history is available so far, avoiding NaNs and preserving all samples.

Outputs Produced:
- outputs/tables/trend_metrics.csv: Metrics comparison table (Baseline vs Trend-Enhanced)
- outputs/figures/trend_features_comparison.png: Visual comparison plot

Author: 2nd-Year B.Tech APL Project Team
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score

from data_loading import load_all_data

RAW_FEATURES = ["Temperature", "Humidity", "Light", "CO2", "HumidityRatio"]
TARGET_COLUMN = "Occupancy"


def verify_sampling_interval(df, dataset_name="Training"):
    """
    Check the exact time difference between consecutive sensor rows.
    """
    time_diffs = df["date"].diff().dropna()
    mode_interval = time_diffs.mode()[0]
    total_seconds = int(mode_interval.total_seconds())
    
    print(f"[INFO] {dataset_name} sampling interval: {total_seconds} seconds ({total_seconds / 60:.1f} minute).")
    print(f"       -> Therefore, a 5-minute window strictly equals 5 rows.")
    return total_seconds


def add_trend_features(df):
    """
    Engineer causality-compliant trend features using past readings only.
    """
    df = df.copy()

    # Feature 1: CO2 change over past 5 minutes (5 rows)
    # Positive slope indicates occupant entering; negative slope indicates dispersion
    df["CO2_diff_5min"] = df["CO2"] - df["CO2"].shift(5)
    # Boundary handling: First 4 rows have no 5-minute history -> fill with 0.0 (neutral slope)
    df["CO2_diff_5min"] = df["CO2_diff_5min"].fillna(0.0)

    # Feature 2: Rolling mean of Light over past 5 minutes (5 rows)
    # min_periods=1 ensures no NaNs for the initial rows
    df["Light_mean_5min"] = df["Light"].rolling(window=5, min_periods=1).mean()

    return df


def run_trend_experiments(train_df, test1_df, test2_df):
    """
    Compare baseline models (raw sensors) against trend-enhanced models.
    """
    # Verify sampling interval
    verify_sampling_interval(train_df, "Training Set")

    # Add trend features to all three splits independently
    train_trend = add_trend_features(train_df)
    test1_trend = add_trend_features(test1_df)
    test2_trend = add_trend_features(test2_df)

    TREND_FEATURES = RAW_FEATURES + ["CO2_diff_5min", "Light_mean_5min"]

    feature_sets = {
        "Raw Sensors Only (Baseline)": RAW_FEATURES,
        "Raw + Trend Features (Enhanced)": TREND_FEATURES
    }

    results = []

    for fset_name, features in feature_sets.items():
        X_tr = train_trend[features]
        y_tr = train_trend[TARGET_COLUMN]

        X_te1 = test1_trend[features]
        y_te1 = test1_trend[TARGET_COLUMN]

        X_te2 = test2_trend[features]
        y_te2 = test2_trend[TARGET_COLUMN]

        # Train models
        dt = DecisionTreeClassifier(max_depth=3, random_state=42)
        dt.fit(X_tr, y_tr)

        rf = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)
        rf.fit(X_tr, y_tr)

        for model_name, model in [("Decision Tree", dt), ("Random Forest", rf)]:
            # Evaluate Test 1 (Door Closed)
            p1 = model.predict(X_te1)
            results.append({
                "Feature Set": fset_name,
                "Model": model_name,
                "Test Condition": "Test 1 (Door Closed)",
                "Accuracy": accuracy_score(y_te1, p1),
                "Precision": precision_score(y_te1, p1, zero_division=0),
                "Recall (Crucial)": recall_score(y_te1, p1, zero_division=0),
                "F1-Score": f1_score(y_te1, p1, zero_division=0)
            })

            # Evaluate Test 2 (Door Open)
            p2 = model.predict(X_te2)
            results.append({
                "Feature Set": fset_name,
                "Model": model_name,
                "Test Condition": "Test 2 (Door Open)",
                "Accuracy": accuracy_score(y_te2, p2),
                "Precision": precision_score(y_te2, p2, zero_division=0),
                "Recall (Crucial)": recall_score(y_te2, p2, zero_division=0),
                "F1-Score": f1_score(y_te2, p2, zero_division=0)
            })

    return pd.DataFrame(results)


def plot_trend_comparison(metrics_df, output_path="outputs/figures/trend_features_comparison.png"):
    """
    Plot bar charts comparing Baseline vs Trend-Enhanced features across both test sets.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Test 1 (Door Closed)
    t1_df = metrics_df[metrics_df["Test Condition"] == "Test 1 (Door Closed)"]
    sns.barplot(
        data=t1_df,
        x="Model",
        y="Recall (Crucial)",
        hue="Feature Set",
        palette={"Raw Sensors Only (Baseline)": "#7f8c8d", "Raw + Trend Features (Enhanced)": "#27ae60"},
        ax=axes[0]
    )
    axes[0].set_title("Test 1 (Door Closed) - Recall", fontsize=12, fontweight="bold")
    axes[0].set_ylim(0.90, 1.02)
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)
    for p in axes[0].patches:
        h = p.get_height()
        if h > 0:
            axes[0].annotate(f"{h:.4f}", (p.get_x() + p.get_width() / 2., h),
                             ha="center", va="bottom", fontsize=9, xytext=(0, 2),
                             textcoords="offset points")

    # Test 2 (Door Open)
    t2_df = metrics_df[metrics_df["Test Condition"] == "Test 2 (Door Open)"]
    sns.barplot(
        data=t2_df,
        x="Model",
        y="Recall (Crucial)",
        hue="Feature Set",
        palette={"Raw Sensors Only (Baseline)": "#7f8c8d", "Raw + Trend Features (Enhanced)": "#27ae60"},
        ax=axes[1]
    )
    axes[1].set_title("Test 2 (Door Open) - Recall", fontsize=12, fontweight="bold")
    axes[1].set_ylim(0.90, 1.02)
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    for p in axes[1].patches:
        h = p.get_height()
        if h > 0:
            axes[1].annotate(f"{h:.4f}", (p.get_x() + p.get_width() / 2., h),
                             ha="center", va="bottom", fontsize=9, xytext=(0, 2),
                             textcoords="offset points")

    plt.suptitle("Impact of Adding 5-Minute Trend Features (CO2 Difference & Light Rolling Mean)",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Saved trend features comparison chart -> {output_path}")


def print_trend_summary(metrics_df):
    """
    Print formatted table and analysis of trend features.
    """
    print("\n" + "=" * 85)
    print("TREND FEATURES EXPERIMENTAL RESULTS (CONTRIBUTION 2)")
    print("=" * 85)
    formatted_df = metrics_df.copy()
    for col in ["Accuracy", "Precision", "Recall (Crucial)", "F1-Score"]:
        formatted_df[col] = formatted_df[col].round(4)
    print(formatted_df.to_string(index=False))
    print("=" * 85)
    print("VIVA INSIGHT:")
    print("- Temporal smoothing (Light_mean_5min) stabilizes predictions against momentary light flickers.")
    print("- Dynamic slope (CO2_diff_5min) captures the physical velocity of human occupancy changes.")
    print("- Because all calculations use ONLY past readings (.shift(5)), this pipeline is 100% viable")
    print("  for live microcontroller / IoT edge deployment without data leakage.")
    print("=" * 85 + "\n")


def run_trend_pipeline():
    """Run Step 7 pipeline."""
    print("[STEP 7] Running Temporal Trend Engineering (Contribution 2)...")
    train_df, test1_df, test2_df = load_all_data("data")

    metrics_df = run_trend_experiments(train_df, test1_df, test2_df)

    os.makedirs("outputs/tables", exist_ok=True)
    csv_path = "outputs/tables/trend_metrics.csv"
    metrics_df.to_csv(csv_path, index=False)
    print(f"[INFO] Saved trend metrics table -> {csv_path}")

    plot_trend_comparison(metrics_df)
    print_trend_summary(metrics_df)


if __name__ == "__main__":
    run_trend_pipeline()
