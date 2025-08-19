# Import libraries
import os                          # for directory manipulation
import pandas as pd                # for DataFrame manipulation
import numpy as np                 # for numerical operations
import re                          # for using regular expressions
import logging
from datetime import datetime

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Setup logging

# --- Always resolve relative to the project root ---
# (script_dir = folder containing scraper.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to project root
project_root = os.path.abspath(os.path.join(script_dir, ".."))

# --- Setup logging ---
log_file = os.path.join(project_root, "logs", "cleanser.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load dataset (specific date or full historical dataset)
def load_data(date=None):
    if date:
        raw_filename = f"redfin_hollywood_hills_{date}.csv"
    else:
        raw_filename = "redfin_hollywood_hills_master.csv"

    # Construct the path to the Excel file in the desired location
    raw_data_path = os.path.join(project_root, "data", "raw", raw_filename)

    if os.path.exists(raw_data_path):
        df = pd.read_csv(raw_data_path)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        logging.info(f"📊 Loaded data from {raw_data_path}")
        return df
    else:
        logging.warning(f"⚠️ No data found for {date or 'historical records'}!")
        return pd.DataFrame()

# Handle missing values & clean data
def clean_data(df):
    logging.info("🛠 Cleaning Data...")

    # Replace invalid values
    df.replace({"—": np.nan, "N/A": np.nan, "": np.nan}, inplace=True)

    # Convert numeric columns
    df["Price"] = df["Price"].str.replace("[$,]", "", regex=True).astype(float)
    df["SqFt"] = df["SqFt"].str.replace(",", "", regex=True).astype(float)
    df["Beds"] = df["Beds"].str.extract("(\d+)").astype(float)
    df["Baths"] = df["Baths"].str.extract("(\d+)").astype(float)

    # Convert Latitude & Longitude to float
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    # Drop rows missing essential values
    df.dropna(subset=["Price", "Beds", "Baths", "SqFt", "Latitude", "Longitude"], inplace=True)

    logging.info(f"✅ Cleaned data: {len(df)} valid listings remaining.")
    return df

# Save cleaned data & append to master dataset
def save_cleaned_data(df, date):
    cleaned_filename = f"redfin_hollywood_hills_cleaned_{date}.csv"

    # Construct the path to the cleaned CSV file in the desired relative location
    path_to_clean_file = os.path.join(project_root, "data", "cleaned", cleaned_filename)

    df.to_csv(path_to_clean_file, index=False)
    logging.info(f"✅ Saved cleaned daily data: {path_to_clean_file}")

    # Append to master dataset
    master_filename = "redfin_hollywood_hills_master_cleaned.csv"
    path_to_master_file = os.path.join(project_root, "data", "cleaned", master_filename)
    if os.path.exists(path_to_master_file):
        master_df = pd.read_csv(path_to_master_file)
        df = pd.concat([master_df, df]).drop_duplicates(subset=["Address", "Date"])

    df.to_csv(path_to_master_file, index=False)
    logging.info(f"✅ Updated master dataset: {path_to_master_file}")

# Run data preparation
def run_data_prep(date=None):
    try:
        logging.info(f"\n🚀 Running Data Prep. for {date or 'historical data'}...\n")
        df = load_data(date)

        if df.empty:
            logging.warning("⚠️ No data available to preparation.")
            return False

        df = clean_data(df)

        if date:
            save_cleaned_data(df, date)

        logging.info("✅ Data Prep. complete.\n")
        return True

    except Exception as e:
        logging.error(f"❌ Data Prep. failed: {e}")
        return False

# Run the script automatically
if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d")
    run_data_prep(today)  # Run for today’s data
    run_data_prep()       # Run historical analysis


