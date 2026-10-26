"""
baseline_models.py
------------------
Steps 3, 4, 5: Train baseline machine learning models, evaluate metrics,
and generate explainability plots.

Models Trained:
1. Decision Tree (max_depth=3 for human readability and viva explanation)
2. Logistic Regression (with StandardScaler for linear feature sensitivity)
3. Random Forest (ensemble of trees, random_state=42)

Outputs Produced:
- outputs/tables/baseline_metrics.csv: Metrics table (Accuracy, Precision, Recall, F1)
- outputs/figures/confusion_matrices.png: 2x3 grid of confusion matrices
- outputs/figures/feature_importance_rf.png: Random Forest MDI feature importance
- outputs/figures/decision_tree_structure.png: Visual decision tree flowchart
- outputs/figures/decision_tree_rules.txt: Text rules extracted using export_text()
- outputs/models/occupancy_model.joblib: Best explainable model for the Streamlit demo

Author: 2nd-Year B.Tech APL Project Team
"""

import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from data_loading import load_all_data

# The 5 original sensor features used by Candanedo & Feldheim (2016)
FEATURE_COLUMNS = ["Temperature", "Humidity", "Light", "CO2", "HumidityRatio"]
TARGET_COLUMN = "Occupancy"


def get_models():
    """
    Return dictionary of baseline models configured with random_state=42.
    - Decision Tree: depth=3 ensures readable tree nodes for viva explanation.
    - Logistic Regression: scaled via Pipeline so coefficients are directly comparable.
    - Random Forest: n_estimators=100, max_depth=3 for stable generalization.
    """
    return {
        "Decision Tree (depth=3)": DecisionTreeClassifier(max_depth=3, random_state=42),
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(random_state=42, max_iter=1000))
        ]),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)
    }


def evaluate_model(model, X_test, y_test, model_name, test_set_name):
    """
    Calculate evaluation metrics for a single model and test set.
    Highlights Recall because missing an occupied room is the worse operational error.
    """
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    return {
        "Model": model_name,
        "Test Set": test_set_name,
        "Accuracy": acc,
        "Precision": prec,
        "Recall (Crucial)": rec,
        "F1-Score": f1,
        "Confusion Matrix": cm
    }


def plot_all_confusion_matrices(results, output_path="outputs/figures/confusion_matrices.png"):
    """
    Plot a 2x3 grid of normalized confusion matrices for each model across both test files.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))

    # results list has 6 entries (3 models x 2 test sets)
    # Row 0: Test Set 1 (Door Closed)
    # Row 1: Test Set 2 (Door Open)
    for i, res in enumerate(results):
        row = 0 if "Door Closed" in res["Test Set"] else 1
        # Model index within that row
        col = (i // 2) if (i % 2 == 0) else ((i - 1) // 2)
        # Or more cleanly find column based on model name
        if "Decision Tree" in res["Model"]:
            col = 0
        elif "Logistic Regression" in res["Model"]:
            col = 1
        else:
            col = 2

        ax = axes[row, col]
        cm = res["Confusion Matrix"]
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            ax=ax,
            xticklabels=["Pred Empty", "Pred Occ"],
            yticklabels=["True Empty", "True Occ"]
        )
        ax.set_title(f"{res['Model']}\n{res['Test Set']}\nRec: {res['Recall (Crucial)']:.2%}", fontsize=11, fontweight="bold")
        ax.set_ylabel("Actual Label", fontsize=9)
        ax.set_xlabel("Predicted Label", fontsize=9)

    plt.suptitle("Confusion Matrices Across Models and Environmental Test Conditions", fontsize=14, fontweight="bold", y=1.00)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Saved confusion matrices -> {output_path}")


def explain_random_forest(rf_model, feature_names, output_path="outputs/figures/feature_importance_rf.png"):
    """
    Plot Gini feature importances for the Random Forest model.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    importances = rf_model.feature_importances_
    df_imp = pd.DataFrame({"Sensor Feature": feature_names, "Importance": importances})
    df_imp = df_imp.sort_values(by="Importance", ascending=False)

    plt.figure(figsize=(8, 4.5))
    sns.barplot(data=df_imp, x="Importance", y="Sensor Feature", hue="Sensor Feature", palette="viridis", legend=False)
    plt.title("Random Forest Sensor Feature Importance (MDI)", fontsize=13, fontweight="bold")
    plt.xlabel("Relative Importance Score", fontsize=11)
    plt.ylabel("Sensor", fontsize=11)
    plt.grid(axis="x", linestyle="--", alpha=0.5)

    for p in plt.gca().patches:
        w = p.get_width()
        plt.gca().annotate(f"{w:.3f} ({w*100:.1f}%)", (w, p.get_y() + p.get_height() / 2.),
                           ha="left", va="center", fontsize=9, xytext=(5, 0),
                           textcoords="offset points")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[INFO] Saved Random Forest feature importance plot -> {output_path}")


def explain_decision_tree(dt_model, feature_names,
                          fig_path="outputs/figures/decision_tree_structure.png",
                          text_path="outputs/figures/decision_tree_rules.txt"):
    """
    Plot the visual decision tree diagram and export readable plain-text IF-THEN rules.
    """
    os.makedirs(os.path.dirname(fig_path), exist_ok=True)

    # 1. Visual tree plot
    plt.figure(figsize=(16, 8))
    plot_tree(
        dt_model,
        feature_names=feature_names,
        class_names=["Empty (0)", "Occupied (1)"],
        filled=True,
        rounded=True,
        fontsize=10,
        precision=2
    )
    plt.title("Explainable Decision Tree (Depth=3) Flowchart", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"[INFO] Saved Decision Tree structure plot -> {fig_path}")

    # 2. Textual rules via export_text
    tree_rules = export_text(
        dt_model,
        feature_names=feature_names,
        class_names=["Empty", "Occupied"]
    )
    with open(text_path, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("EXPLAINABLE DECISION TREE RULES (export_text)\n")
        f.write("Dataset: UCI Occupancy Detection (datatraining.txt)\n")
        f.write("=" * 60 + "\n\n")
        f.write(tree_rules)
        f.write("\n" + "=" * 60 + "\n")
        f.write("INTERPRETATION FOR VIVA:\n")
        f.write("- The root decision node splits on 'Light'.\n")
        f.write("- If Light <= threshold (~360-400 Lux), the room is almost certainly Empty.\n")
        f.write("- If Light > threshold, secondary checks on CO2 and Temperature determine\n")
        f.write("  whether occupants are physically present vs. lights left on by accident.\n")
        f.write("=" * 60 + "\n")
    print(f"[INFO] Saved Decision Tree text rules -> {text_path}")


def run_baselines():
    """Run Step 3, 4, and 5 pipeline."""
    print("[STEP 3-5] Training baseline models, evaluating metrics & explainability...")
    train_df, test1_df, test2_df = load_all_data("data")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_test1 = test1_df[FEATURE_COLUMNS]
    y_test1 = test1_df[TARGET_COLUMN]

    X_test2 = test2_df[FEATURE_COLUMNS]
    y_test2 = test2_df[TARGET_COLUMN]

    models = get_models()
    results = []

    for name, model in models.items():
        print(f"  Training {name} on {len(X_train)} training samples...")
        model.fit(X_train, y_train)

        # Evaluate on Test Set 1 (Door Closed)
        r1 = evaluate_model(model, X_test1, y_test1, name, "Test 1 (Door Closed)")
        results.append(r1)

        # Evaluate on Test Set 2 (Door Open)
        r2 = evaluate_model(model, X_test2, y_test2, name, "Test 2 (Door Open)")
        results.append(r2)

    # Convert results into a clean table (excluding raw CM matrix for CSV export)
    table_rows = []
    for r in results:
        table_rows.append({
            "Model": r["Model"],
            "Test Condition": r["Test Set"],
            "Accuracy": round(r["Accuracy"], 4),
            "Precision": round(r["Precision"], 4),
            "Recall": round(r["Recall (Crucial)"], 4),
            "F1-Score": round(r["F1-Score"], 4)
        })
    metrics_df = pd.DataFrame(table_rows)

    os.makedirs("outputs/tables", exist_ok=True)
    csv_path = "outputs/tables/baseline_metrics.csv"
    metrics_df.to_csv(csv_path, index=False)
    print(f"\n[INFO] Saved baseline metrics table -> {csv_path}\n")

    print("=" * 80)
    print("BASELINE MODEL EVALUATION SUMMARY")
    print("=" * 80)
    print(metrics_df.to_string(index=False))
    print("=" * 80 + "\n")

    # Step 4: Plot confusion matrices
    plot_all_confusion_matrices(results)

    # Step 5: Explainability
    explain_random_forest(models["Random Forest"], FEATURE_COLUMNS)
    explain_decision_tree(models["Decision Tree (depth=3)"], FEATURE_COLUMNS)

    # Step 10 Pre-requisite: Save the best explainable model for the Streamlit demo
    # We save the Decision Tree or Random Forest model
    os.makedirs("outputs/models", exist_ok=True)
    model_save_path = "outputs/models/occupancy_model.joblib"
    joblib.dump(models["Decision Tree (depth=3)"], model_save_path)
    print(f"[INFO] Saved explainable model for Streamlit demo -> {model_save_path}\n")


if __name__ == "__main__":
    run_baselines()
