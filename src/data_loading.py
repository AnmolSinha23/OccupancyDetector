"""
data_loading.py
----------------
Step 1: Download, inspect, load, and parse the UCI Occupancy Detection dataset.

Author: 2nd-Year B.Tech APL Project Team
Dataset: UCI Machine Learning Repository (ID 357)
Paper: Candanedo & Feldheim (2016), Energy and Buildings
"""

import os
import urllib.request
import zipfile
import pandas as pd


# URL for fallback download if ucimlrepo is not available or fails
UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/357/occupancy+detection.zip"
EXPECTED_FILES = ["datatraining.txt", "datatest.txt", "datatest2.txt"]


def download_dataset(data_dir="data"):
    """
    Download and extract the UCI Occupancy Detection dataset.
    Tries ucimlrepo first; if it fails, falls back to downloading the official zip.
    If both fail, raises a clear error.
    """
    os.makedirs(data_dir, exist_ok=True)

    # Check if all expected files already exist
    all_exist = all(os.path.exists(os.path.join(data_dir, f)) for f in EXPECTED_FILES)
    if all_exist:
        print("[INFO] Dataset files already present in directory:", data_dir)
        return True

    print("[INFO] Dataset files not found locally. Attempting download...")

    # Method 1: Try ucimlrepo package
    try:
        print("[INFO] Method 1: Trying 'ucimlrepo' package...")
        from ucimlrepo import fetch_ucirepo
        occupancy = fetch_ucirepo(id=357)
        # ucimlrepo gives a combined dataframe or features/targets
        # But Candanedo & Feldheim specifically used the 3 distinct time-separated files.
        # So we check if files were saved or we need to write them.
        # Fall back to zip to get the exact original 3 files if ucimlrepo returns one blob.
        print("[INFO] 'ucimlrepo' reached, but downloading raw zip to preserve exact 3 experimental files.")
    except Exception as e:
        print(f"[INFO] Method 1 ('ucimlrepo') skipped or failed: {e}")

    # Method 2: Direct zip download from UCI Archive
    try:
        print(f"[INFO] Method 2: Downloading zip from {UCI_ZIP_URL} ...")
        zip_path = os.path.join(data_dir, "occupancy_detection.zip")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        req = urllib.request.Request(UCI_ZIP_URL, headers=headers)
        
        with urllib.request.urlopen(req) as response, open(zip_path, "wb") as out_file:
            out_file.write(response.read())

        print("[INFO] Download complete. Extracting files...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(data_dir)
            
        print("[INFO] Extracted files successfully to:", data_dir)
        return True
    except Exception as e:
        print(f"[ERROR] Method 2 (zip download) failed: {e}")

    raise RuntimeError(
        "FATAL: Both ucimlrepo and direct zip download failed. "
        "Please check your internet connection or download 'occupancy+detection.zip' "
        "manually from UCI and extract into the 'data/' folder."
    )


def load_occupancy_file(filepath):
    """
    Load a single occupancy text file into a clean pandas DataFrame.
    
    File Structure Details:
    - In these R-generated CSV/text files, the header contains 7 column names:
      'date', 'Temperature', 'Humidity', 'Light', 'CO2', 'HumidityRatio', 'Occupancy'.
    - The data rows contain 8 values, where the first value is the row index.
    - When pd.read_csv reads this, it automatically treats the first value as the index.
    - We parse the 'date' column into real pandas datetime objects.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Read csv: header has 7 names, row data has 8 values -> pd.read_csv makes 1st col the index
    df = pd.read_csv(filepath)

    # Ensure date is parsed to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Ensure numeric columns are cleanly cast
    numeric_cols = ["Temperature", "Humidity", "Light", "CO2", "HumidityRatio"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure target is integer 0 or 1
    df["Occupancy"] = df["Occupancy"].astype(int)

    # Sort strictly by timestamp to maintain temporal sequence
    df = df.sort_values(by="date").reset_index(drop=True)

    return df


def print_summary(df, name):
    """
    Print an informative, easy-to-understand summary of a dataset for viva inspection.
    """
    print("=" * 60)
    print(f" DATASET SUMMARY: {name}")
    print("=" * 60)
    print(f"Shape (rows, columns): {df.shape}")
    print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
    print("\nColumns & Data Types:")
    for col, dtype in df.dtypes.items():
        print(f"  - {col:15s}: {dtype}")
    
    print("\nMissing Values:")
    null_counts = df.isnull().sum()
    if null_counts.sum() == 0:
        print("  None (0 missing values across all columns)")
    else:
        for col, count in null_counts.items():
            if count > 0:
                print(f"  - {col}: {count} missing")

    print("\nClass Balance (Occupancy):")
    counts = df["Occupancy"].value_counts().to_dict()
    total = len(df)
    n_empty = counts.get(0, 0)
    n_occ = counts.get(1, 0)
    print(f"  - Empty    (0): {n_empty:5d} ({n_empty / total * 100:.2f}%)")
    print(f"  - Occupied (1): {n_occ:5d} ({n_occ / total * 100:.2f}%)")
    print("=" * 60 + "\n")


def load_all_data(data_dir="data"):
    """
    Helper function to load all three files:
      1. Training file: datatraining.txt (door closed, regular office hours)
      2. Test file 1:   datatest.txt     (door closed, similar conditions)
      3. Test file 2:   datatest2.txt    (door mostly open, challenging condition)
    Returns: (train_df, test1_df, test2_df)
    """
    download_dataset(data_dir)

    train_path = os.path.join(data_dir, "datatraining.txt")
    test1_path = os.path.join(data_dir, "datatest.txt")
    test2_path = os.path.join(data_dir, "datatest2.txt")

    train_df = load_occupancy_file(train_path)
    test1_df = load_occupancy_file(test1_path)
    test2_df = load_occupancy_file(test2_path)

    return train_df, test1_df, test2_df


if __name__ == "__main__":
    print("[STEP 1] Running data loading and inspection...\n")
    train_df, test1_df, test2_df = load_all_data("data")

    print_summary(train_df, "Training Set (datatraining.txt)")
    print_summary(test1_df, "Test Set 1 - Door Closed (datatest.txt)")
    print_summary(test2_df, "Test Set 2 - Door Open (datatest2.txt)")
