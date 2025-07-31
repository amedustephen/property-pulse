# Import libraries
import os                          # for directory manipulation
import pandas as pd                # for DataFrame manipulation
import numpy as np                 # for numerical operations
import re                          # for using regular expressions

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Load the dataset

# Get the directory of the script's location, assumed here to be '../notebooks' and to be on the same folder level with '../data'
script_dir = os.getcwd()
# Please note that os.getcwd() depends on the current working directory, which might not always align with the script's location  

# Navigate to the parent folder
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))

# Construct the path to the Excel file in the desired relative location
raw_data_path = os.path.join(parent_dir, "data", "raw", "redfin_hollywood_hills.csv")

# Read the Excel file into a DataFrame
redfin_df = pd.read_csv(raw_data_path)

# Function to clean dataset
def clean_data(df):
    
    # Replace invalid values with NaN
    df.replace({'—': np.nan, 'N/A': np.nan, '': np.nan}, inplace=True)
    
    # Drop rows with missing essential values
    df.dropna(subset=["Price", "Beds", "Baths", "SqFt"], inplace=True)
    
    # Reset index
    df.reset_index(drop=True, inplace=True)
    
    return df

# Function to handle rows with missing geo-location data
def handle_missing_geo(df):
    missing_geo = df[df['Latitude'].isna() | df['Longitude'].isna()]
    if not missing_geo.empty:
        df = df.dropna(subset=['Latitude', 'Longitude'])  # Drop listings without location data
    return df

# Helper functions to handle format issues

def extract_numeric(value):
    """Extracts numeric values from a string. Handles cases like '1 bed', '2 baths', 'Studio'."""
    if isinstance(value, str):
        match = re.search(r'\d+', value)  # Find first numeric value
        return float(match.group()) if match else np.nan
    return np.nan

def convert_columns(df):
    
    # Strip whitespace from all columns
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    #df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Convert Price column: Remove "$" and ",", then convert to float
    df['Price'] = df['Price'].str.replace('[$,]', '', regex=True).replace('', np.nan).astype(float)
    
    # Convert SqFt column
    df['SqFt'] = df['SqFt'].replace(['—', '', 'N/A'], np.nan)
    df['SqFt'] = df['SqFt'].str.replace(',', '', regex=True)
    df['SqFt'] = pd.to_numeric(df['SqFt'], errors='coerce')
    
    # Convert Beds & Baths
    df['Beds'] = df['Beds'].apply(extract_numeric)
    df['Baths'] = df['Baths'].apply(extract_numeric)
    
    # Convert Latitude & Longitude to float
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    
    return df

# Run cleaning steps
if __name__ == "__main__":
    redfin_df = clean_data(redfin_df)
    redfin_df = convert_columns(redfin_df)
    redfin_df = handle_missing_geo(redfin_df)
    
    # Save the cleaned dataset

    # Construct the path to the cleaned CSV file in the desired relative location
    path_to_file = os.path.join(parent_dir, "data", "cleaned", "redfin_hollywood_hills_cleaned.csv")

    # Save the cleaned dataset
    redfin_df.to_csv(path_to_file,index=False)

