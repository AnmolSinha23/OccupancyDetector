"""
run_all.py
----------
Master pipeline execution script for IIIT Bhopal CSE-3006 APL Project.
Runs all project steps sequentially from raw data download to metrics and explainability.

Execution Order:
1. data_loading: Download and inspect dataset
2. exploration: Generate time-series, class balance, and correlation plots
3. baseline_models: Train Decision Tree, Logistic Regression, Random Forest, save metrics & explainability plots
4. sensor_ablation: Run leave-one-out and single-sensor ablation experiments
5. trend_features: Extract 5-minute past-only trends and compare models
6. hyperparameter_tune: Perform chronological validation split and tune tree depth
7. optional_boosting: Run HistGradientBoosting reference comparison

Author: 2nd-Year B.Tech APL Project Team
"""

import sys
import os

# Ensure src/ is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from data_loading import load_all_data, print_summary
from exploration import run_exploration
from baseline_models import run_baselines
from sensor_ablation import run_ablation
from trend_features import run_trend_pipeline
from hyperparameter_tune import run_hyperparameter_study
from optional_boosting import run_hist_gradient_boosting


def main():
    print("=" * 80)
    print("   ADVANCED PROGRAMMING LAB: ROOM OCCUPANCY DETECTION PIPELINE")
    print("   Based on Candanedo & Feldheim (2016), Energy and Buildings")
    print("=" * 80 + "\n")

    # Step 1: Data Loading & Inspection
    print(">>> [STEP 1/7] DOWNLOADING AND INSPECTING DATASET...")
    train_df, test1_df, test2_df = load_all_data("data")
    print_summary(train_df, "Training Set (datatraining.txt)")
    print_summary(test1_df, "Test Set 1 - Door Closed (datatest.txt)")
    print_summary(test2_df, "Test Set 2 - Door Open (datatest2.txt)")

    # Step 2: Exploratory Data Analysis & Plots
    print(">>> [STEP 2/7] RUNNING EXPLORATORY VISUALIZATIONS...")
    run_exploration()

    # Step 3, 4, 5: Baseline Models, Metrics, Explainability & Model Saving
    print(">>> [STEP 3-5/7] TRAINING BASELINE MODELS & EXPLAINABILITY...")
    run_baselines()

    # Step 6: Sensor Ablation Study (Contribution 1)
    print(">>> [STEP 6/7] EXECUTING SENSOR ABLATION EXPERIMENTS...")
    run_ablation()

    # Step 7: Temporal Trend Engineering (Contribution 2)
    print(">>> [STEP 7/7] COMPUTING CAUSAL TREND FEATURES...")
    run_trend_pipeline()

    # Step 8: Hyperparameter Tuning (Chronological Split)
    print(">>> [EXTRA] HYPERPARAMETER VALIDATION SPLIT...")
    run_hyperparameter_study()

    # Step 9: Optional Model Comparison (HistGradientBoosting)
    print(">>> [OPTIONAL] HISTOGRAM GRADIENT BOOSTING REFERENCE...")
    run_hist_gradient_boosting()

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL PIPELINE STEPS COMPLETED SUCCESSFULLY!")
    print("Figures saved in: outputs/figures/")
    print("Tables saved in:  outputs/tables/")
    print("Model saved in:   outputs/models/occupancy_model.joblib")
    print("Run web demo with: streamlit run app.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
