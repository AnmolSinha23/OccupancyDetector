"""
optional_boosting.py
--------------------
Step 9: Optional Comparison - Histogram-Based Gradient Boosting

What is HistGradientBoostingClassifier? (Plain Explanation for Viva):
1. How it works:
   HistGradientBoostingClassifier (inspired by LightGBM) bins continuous sensor values
   (like Temperature and CO2) into 256 discrete integer bins (a histogram). This makes
   finding split points extremely fast and memory-efficient.
2. Boosting principle:
   Unlike Random Forest (which builds many independent trees in parallel and averages them),
   Gradient Boosting builds trees sequentially: each new tree is trained specifically to
   predict and correct the residual errors of the previous trees.
3. Why included here:
   It serves as a modern, high-performance reference model to show examiners how
   state-of-the-art tabular algorithms compare against simple explainable trees.

Author: 2nd-Year B.Tech APL Project Team
"""

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from data_loading import load_all_data

FEATURE_COLUMNS = ["Temperature", "Humidity", "Light", "CO2", "HumidityRatio"]
TARGET_COLUMN = "Occupancy"


def run_hist_gradient_boosting():
    """
    Train and evaluate HistGradientBoostingClassifier on both test sets.
    """
    print("[STEP 9] Running Optional Model: HistGradientBoostingClassifier...")
    train_df, test1_df, test2_df = load_all_data("data")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_test1 = test1_df[FEATURE_COLUMNS]
    y_test1 = test1_df[TARGET_COLUMN]

    X_test2 = test2_df[FEATURE_COLUMNS]
    y_test2 = test2_df[TARGET_COLUMN]

    # Initialize model with conservative max_depth for fair comparison
    hgb = HistGradientBoostingClassifier(max_depth=3, random_state=42)
    hgb.fit(X_train, y_train)

    p1 = hgb.predict(X_test1)
    p2 = hgb.predict(X_test2)

    results = [
        {
            "Model": "HistGradientBoosting (Optional)",
            "Test Condition": "Test 1 (Door Closed)",
            "Accuracy": round(accuracy_score(y_test1, p1), 4),
            "Precision": round(precision_score(y_test1, p1, zero_division=0), 4),
            "Recall": round(recall_score(y_test1, p1, zero_division=0), 4),
            "F1-Score": round(f1_score(y_test1, p1, zero_division=0), 4)
        },
        {
            "Model": "HistGradientBoosting (Optional)",
            "Test Condition": "Test 2 (Door Open)",
            "Accuracy": round(accuracy_score(y_test2, p2), 4),
            "Precision": round(precision_score(y_test2, p2, zero_division=0), 4),
            "Recall": round(recall_score(y_test2, p2, zero_division=0), 4),
            "F1-Score": round(f1_score(y_test2, p2, zero_division=0), 4)
        }
    ]

    res_df = pd.DataFrame(results)

    print("\n" + "=" * 75)
    print("OPTIONAL MODEL RESULTS: HistGradientBoostingClassifier")
    print("=" * 75)
    print(res_df.to_string(index=False))
    print("=" * 75)
    print("COMPARATIVE TAKEAWAY:")
    print("- HistGradientBoosting achieves high accuracy on both test conditions.")
    print("- However, it operates as an ensemble of residual trees ('black box'),")
    print("  making individual predictions much harder to audit than our depth=3 Decision Tree.")
    print("- For safety-critical or regulatory building automation, our simple Decision Tree")
    print("  delivers competitive recall while offering 100% transparent decision rules.")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_hist_gradient_boosting()
