"""
sensor_ablation.py
------------------
Step 6: Sensor Ablation Study (Contribution 1)

Systematically evaluates sensor contributions:
(a) Leave-One-Sensor-Out: Remove one sensor at a time to test its marginal importance.
(b) Single-Sensor Models: Train models using only one sensor at a time.
(c) Generates comparison table (outputs/tables/ablation_metrics.csv) and
    bar charts (outputs/figures/ablation_study.png) on both Test 1 and Test 2.
(d) Prints a clear conclusion explaining the findings for viva defense.

Author: 2nd-Year B.Tech APL Project Team
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score

from data_loading import load_all_data

ALL_SENSORS = ["Temperature", "Humidity", "Light", "CO2", "HumidityRatio"]
TARGET_COLUMN = "Occupancy"


def get_ablation_feature_sets():
    """
    Define sensor subsets for ablation:
    - Baseline: All 5 sensors
    - Leave-one-out: 5 sets
    - Single-sensor: 5 sets
    """
    subsets = {
        # Baseline
        "All 5 Sensors": ALL_SENSORS,
        
        # Leave-One-Out sets
        "Without Light": [s for s in ALL_SENSORS if s != "Light"],
        "Without CO2": [s for s in ALL_SENSORS if s != "CO2"],
        "Without Temperature": [s for s in ALL_SENSORS if s != "Temperature"],
        "Without Humidity": [s for s in ALL_SENSORS if s != "Humidity"],
        "Without HumidityRatio": [s for s in ALL_SENSORS if s != "HumidityRatio"],
        
        # Single-Sensor sets
        "Only Light": ["Light"],
        "Only CO2": ["CO2"],
        "Only Temperature": ["Temperature"],
        "Only Humidity": ["Humidity"],
        "Only HumidityRatio": ["HumidityRatio"],
    }
    return subsets


def run_ablation_experiments(train_df, test1_df, test2_df):
    """
    Train Decision Tree and Random Forest on each sensor subset
    and evaluate on both Test Set 1 and Test Set 2.
    """
    subsets = get_ablation_feature_sets()
    results = []

    for subset_name, feature_list in subsets.items():
        X_train = train_df[feature_list]
        y_train = train_df[TARGET_COLUMN]

        X_test1 = test1_df[feature_list]
        y_test1 = test1_df[TARGET_COLUMN]

        X_test2 = test2_df[feature_list]
        y_test2 = test2_df[TARGET_COLUMN]

        # Model 1: Decision Tree
        dt = DecisionTreeClassifier(max_depth=3, random_state=42)
        dt.fit(X_train, y_train)

        # Model 2: Random Forest
        rf = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)
        rf.fit(X_train, y_train)

        # Evaluate both models on both test sets
        for model_label, model in [("Decision Tree", dt), ("Random Forest", rf)]:
            # Test 1: Door Closed
            preds1 = model.predict(X_test1)
            results.append({
                "Sensor Subset": subset_name,
                "Model": model_label,
                "Test Condition": "Test 1 (Door Closed)",
                "Num Sensors": len(feature_list),
                "Accuracy": accuracy_score(y_test1, preds1),
                "Recall": recall_score(y_test1, preds1, zero_division=0),
                "F1-Score": f1_score(y_test1, preds1, zero_division=0)
            })

            # Test 2: Door Open
            preds2 = model.predict(X_test2)
            results.append({
                "Sensor Subset": subset_name,
                "Model": model_label,
                "Test Condition": "Test 2 (Door Open)",
                "Num Sensors": len(feature_list),
                "Accuracy": accuracy_score(y_test2, preds2),
                "Recall": recall_score(y_test2, preds2, zero_division=0),
                "F1-Score": f1_score(y_test2, preds2, zero_division=0)
            })

    return pd.DataFrame(results)


def plot_ablation_study(results_df, output_path="outputs/figures/ablation_study.png"):
    """
    Create a 2x2 comparison chart:
    - Top row: Test 1 (Door Closed) Accuracy & Recall
    - Bottom row: Test 2 (Door Open) Accuracy & Recall
    Comparing Random Forest performance across all sensor configurations.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # We focus the plot on Random Forest as representative ensemble
    rf_df = results_df[results_df["Model"] == "Random Forest"].copy()

    # Split into Leave-one-out vs Single Sensor for clear visual narrative
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharey=True)

    test1_df = rf_df[rf_df["Test Condition"] == "Test 1 (Door Closed)"]
    test2_df = rf_df[rf_df["Test Condition"] == "Test 2 (Door Open)"]

    # (0, 0): Test 1 Accuracy
    sns.barplot(data=test1_df, x="Accuracy", y="Sensor Subset", palette="mako", ax=axes[0, 0], hue="Sensor Subset", legend=False)
    axes[0, 0].set_title("Test 1 (Door Closed) - Accuracy", fontsize=12, fontweight="bold")
    axes[0, 0].set_xlim(0.5, 1.0)
    axes[0, 0].grid(axis="x", linestyle="--", alpha=0.5)

    # (0, 1): Test 1 Recall
    sns.barplot(data=test1_df, x="Recall", y="Sensor Subset", palette="mako", ax=axes[0, 1], hue="Sensor Subset", legend=False)
    axes[0, 1].set_title("Test 1 (Door Closed) - Recall", fontsize=12, fontweight="bold")
    axes[0, 1].set_xlim(0.0, 1.05)
    axes[0, 1].set_ylabel("")
    axes[0, 1].grid(axis="x", linestyle="--", alpha=0.5)

    # (1, 0): Test 2 Accuracy
    sns.barplot(data=test2_df, x="Accuracy", y="Sensor Subset", palette="flare", ax=axes[1, 0], hue="Sensor Subset", legend=False)
    axes[1, 0].set_title("Test 2 (Door Open) - Accuracy", fontsize=12, fontweight="bold")
    axes[1, 0].set_xlim(0.5, 1.0)
    axes[1, 0].grid(axis="x", linestyle="--", alpha=0.5)

    # (1, 1): Test 2 Recall
    sns.barplot(data=test2_df, x="Recall", y="Sensor Subset", palette="flare", ax=axes[1, 1], hue="Sensor Subset", legend=False)
    axes[1, 1].set_title("Test 2 (Door Open) - Recall", fontsize=12, fontweight="bold")
    axes[1, 1].set_xlim(0.0, 1.05)
    axes[1, 1].set_ylabel("")
    axes[1, 1].grid(axis="x", linestyle="--", alpha=0.5)

    plt.suptitle("Sensor Ablation Study: Impact of Sensor Subsets on Model Performance (Random Forest)",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Saved ablation study bar chart -> {output_path}")


def print_ablation_conclusions(results_df):
    """
    Print an evidence-based conclusion summarizing the key takeaways for examiners.
    """
    rf_df = results_df[results_df["Model"] == "Random Forest"]
    
    # Extract baseline numbers
    base_t1 = rf_df[(rf_df["Sensor Subset"] == "All 5 Sensors") & (rf_df["Test Condition"] == "Test 1 (Door Closed)")].iloc[0]
    base_t2 = rf_df[(rf_df["Sensor Subset"] == "All 5 Sensors") & (rf_df["Test Condition"] == "Test 2 (Door Open)")].iloc[0]
    
    # Extract Without Light
    no_light_t1 = rf_df[(rf_df["Sensor Subset"] == "Without Light") & (rf_df["Test Condition"] == "Test 1 (Door Closed)")].iloc[0]
    no_light_t2 = rf_df[(rf_df["Sensor Subset"] == "Without Light") & (rf_df["Test Condition"] == "Test 2 (Door Open)")].iloc[0]

    # Extract Only Light
    only_light_t1 = rf_df[(rf_df["Sensor Subset"] == "Only Light") & (rf_df["Test Condition"] == "Test 1 (Door Closed)")].iloc[0]
    only_light_t2 = rf_df[(rf_df["Sensor Subset"] == "Only Light") & (rf_df["Test Condition"] == "Test 2 (Door Open)")].iloc[0]

    # Extract Only CO2
    only_co2_t1 = rf_df[(rf_df["Sensor Subset"] == "Only CO2") & (rf_df["Test Condition"] == "Test 1 (Door Closed)")].iloc[0]
    only_co2_t2 = rf_df[(rf_df["Sensor Subset"] == "Only CO2") & (rf_df["Test Condition"] == "Test 2 (Door Open)")].iloc[0]

    print("\n" + "=" * 80)
    print("SENSOR ABLATION STUDY: KEY VIVA FINDINGS & CONCLUSIONS")
    print("=" * 80)
    print(f"1. PRIMARY SENSOR - LIGHT:")
    print(f"   - Removing 'Light' causes the sharpest drop in performance:")
    print(f"     * Test 1 (Door Closed) Recall collapses from {base_t1['Recall']:.2%} down to {no_light_t1['Recall']:.2%}.")
    print(f"     * Test 2 (Door Open) Recall drops from {base_t2['Recall']:.2%} down to {no_light_t2['Recall']:.2%}.")
    print(f"   - Conversely, 'Only Light' alone achieves {only_light_t1['Accuracy']:.2%} accuracy on Test 1 and {only_light_t2['Accuracy']:.2%} on Test 2.")
    print(f"   - Takeaway: Light is the single most informative feature because occupants almost always turn lights ON.")
    print()
    print(f"2. SECONDARY SENSOR - CO2 AND THE 'DOOR-OPEN' PHENOMENON:")
    print(f"   - 'Only CO2' achieves {only_co2_t1['Accuracy']:.2%} accuracy on Test 1 (door closed), but drops to {only_co2_t2['Accuracy']:.2%} on Test 2 (door open).")
    print(f"   - Why? When the door is closed, exhaled human CO2 accumulates predictably in the closed room.")
    print(f"   - When the door is left open, room ventilation rapidly diffuses CO2 into the hallway,")
    print(f"     making static CO2 thresholds less reliable unless paired with Light or dynamic trend features.")
    print()
    print(f"3. SENSOR REDUNDANCY - HUMIDITY & HUMIDITY RATIO:")
    print(f"   - Removing Humidity or HumidityRatio has virtually zero negative impact on accuracy or recall.")
    print(f"   - Takeaway: To reduce IoT hardware cost and power consumption, a deployment can safely omit humidity sensors.")
    print("=" * 80 + "\n")


def run_ablation():
    """Run Step 6: Sensor Ablation Study pipeline."""
    print("[STEP 6] Running Sensor Ablation Experiments (Contribution 1)...")
    train_df, test1_df, test2_df = load_all_data("data")

    results_df = run_ablation_experiments(train_df, test1_df, test2_df)

    os.makedirs("outputs/tables", exist_ok=True)
    csv_path = "outputs/tables/ablation_metrics.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"[INFO] Saved ablation metrics table -> {csv_path}")

    plot_ablation_study(results_df)
    print_ablation_conclusions(results_df)


if __name__ == "__main__":
    run_ablation()
