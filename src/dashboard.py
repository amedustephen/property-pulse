# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import folium
from streamlit_folium import st_folium
import numpy as np
import glob
import os
import re

# Get the directory of the script's location, assumed here to be '../src' and to be on the same folder

# --- Always resolve relative to the project root ---
# (script_dir = folder containing dashboard.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to project root
project_root = os.path.abspath(os.path.join(script_dir, ".."))

# Fetch available dates from stored CSV files
def get_available_dates():
    # Build the path to the data folder inside the project root directory
    data_dir = os.path.join(project_root, "data", "raw")

    # Use glob to find matching files
    files = glob.glob(os.path.join(data_dir, "redfin_hollywood_hills_*.csv"))
    
    # Extract valid dates from filenames (YYYY-MM-DD format)
    date_pattern = re.compile(r"redfin_hollywood_hills_(\d{4}-\d{2}-\d{2})\.csv")
    dates = sorted(
        {date_pattern.search(f).group(1) for f in files if date_pattern.search(f)},
        reverse=True
    )
    return dates

# Load selected date's data
@st.cache_data
def load_data(selected_date=None):
    if not selected_date:
        st.error("❌ No date selected.")
        return pd.DataFrame()
    
    cleaned_filename = f"redfin_hollywood_hills_cleaned_{selected_date}.csv"

    # Construct the path to the cleaned CSV file in the desired location
    path_to_clean_file = os.path.join(project_root, "data", "cleaned", cleaned_filename)
    if not os.path.exists(path_to_clean_file):
        st.error(f"❌ Cleaned data file not found: {path_to_clean_file}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path_to_clean_file)

        # 🛠 Handle missing values & clean numeric columns
        df.replace({'—': np.nan, 'N/A': np.nan, '': np.nan}, inplace=True)
        
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df["Beds"] = pd.to_numeric(df["Beds"], errors="coerce")
        df["Baths"] = pd.to_numeric(df["Baths"], errors="coerce")
        df["SqFt"] = pd.to_numeric(df["SqFt"], errors="coerce")
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        df.dropna(subset=["Price", "Beds", "Baths", "SqFt", "Latitude", "Longitude"], inplace=True)

        return df

    except FileNotFoundError:
        st.error(f"❌ Data file not found: {path_to_clean_file}")
        return pd.DataFrame()

def load_historical_data():
    master_filename = "redfin_hollywood_hills_master_cleaned.csv"
    path_to_master_file = os.path.join(project_root, "data", "cleaned", master_filename)
    try:
        df = pd.read_csv(path_to_master_file)
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df["Beds"] = pd.to_numeric(df["Beds"], errors="coerce")
        df["Baths"] = pd.to_numeric(df["Baths"], errors="coerce")
        df["SqFt"] = pd.to_numeric(df["SqFt"], errors="coerce")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df.dropna(subset=["Price", "Beds", "Baths", "SqFt", "Date"], inplace=True)
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# Streamlit UI
st.title("🏡Real Estate Dashboard")
st.write("Analyze real estate trends in Hollywood Hills using interactive visualizations.")

# Create Tabs
tab1, tab2 = st.tabs(["📆 Listings by Date", "📈 Historical Trends"])

# TAB 1: Listings by Date
with tab1:
    st.subheader("📆 View Listings by Date")

    # Dropdown to select a date
    available_dates = get_available_dates()
    selected_date = st.selectbox("Select Date", available_dates)

    # Load selected day's data
    df = load_data(selected_date)

    if df.empty:
        st.warning("⚠️ No data available for the selected date.")
        st.stop()

    # Sidebar Filters
    st.sidebar.header("🔍 Filter Listings")

    show_all = st.sidebar.checkbox("Show All Properties", value=False)

    if show_all:
        filtered_df = df
    else:
        min_price_value = max(1000, df["Price"].min()) if not np.isnan(df["Price"].min()) else 1000
        max_price_value = np.ceil(df["Price"].max() / 1_000_000) * 1_000_000 if not np.isnan(df["Price"].max()) else 1_000_000

        min_price, max_price = st.sidebar.slider(
            "Select Price Range ($)", 
            min_value=int(min_price_value), 
            max_value=int(max_price_value), 
            value=(int(min_price_value), int(max_price_value)),
            format="$%d",
            key="main_slider"
        )

        min_beds, max_beds = 1, int(np.ceil(df["Beds"].max() / 5) * 5)
        min_baths, max_baths = 1, int(np.ceil(df["Baths"].max() / 5) * 5)
        min_sqft, max_sqft = 100, int(np.ceil(df["SqFt"].max() / 10_000) * 10_000)

        selected_beds = st.sidebar.slider("Bedrooms", min_beds, max_beds, (1, 5))
        selected_baths = st.sidebar.slider("Bathrooms", min_baths, max_baths, (1, 5))
        selected_sqft = st.sidebar.slider("Square Footage", min_sqft, max_sqft, (500, 5000))

        filtered_df = df[
            (df["Price"] >= min_price) & (df["Price"] <= max_price) &
            (df["Beds"] >= selected_beds[0]) & (df["Beds"] <= selected_beds[1]) &
            (df["Baths"] >= selected_baths[0]) & (df["Baths"] <= selected_baths[1]) &
            (df["SqFt"] >= selected_sqft[0]) & (df["SqFt"] <= selected_sqft[1])
        ]

    st.subheader(f"📊 {len(filtered_df)} Listings Found")
    # Create an interactive table where users can select a row
    selected_rows = st.data_editor(
        filtered_df[["Price", "Beds", "Baths", "SqFt", "Address", "Link"]]
        .sort_values(by="Price", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,  # Makes the table responsive
        height=400,
        num_rows="dynamic",
        hide_index=True,  # Hides the index column
        column_config={"Link": st.column_config.LinkColumn()},  # Make links clickable
        key="table_selection"
    )

    # Get selected address (if any)
    selected_address = selected_rows.iloc[0]["Address"] if not selected_rows.empty else None
    
    # Price Distribution
    st.subheader("💰 Price Distribution")
    with st.container():
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Plot histogram
        sns.histplot(filtered_df["Price"], bins=30, kde=True, ax=ax)

        # Format x-axis: Convert to millions and append "M"
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x/1_000_000:.0f}M'))

        ax.set_xlabel("Price ($)")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    # Beds/Baths Analysis
    st.subheader("🛏️ Bedrooms & 🛁 Bathrooms Distribution")
    with st.container():
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))

        sns.countplot(x="Beds", data=filtered_df, ax=ax[0], hue="Beds", palette="Blues", legend=False)
        ax[0].set_title("Number of Bedrooms")
        ax[0].set_xlabel("Beds")

        sns.countplot(x="Baths", data=filtered_df, ax=ax[1], hue="Baths", palette="Reds", legend=False)
        ax[1].set_title("Number of Bathrooms")
        ax[1].set_xlabel("Baths")

        st.pyplot(fig)

    st.subheader("📍 Property Locations")
    m = folium.Map(location=[34.1, -118.3], zoom_start=12)
    # Add markers for all filtered properties
    for _, row in filtered_df.iterrows():
        popup_info = f"""
        <b>{row['Address']}</b><br>
        Price: ${row['Price']:,.0f}<br>
        Beds: {row['Beds']}, Baths: {row['Baths']}<br>
        SqFt: {row['SqFt']:,}<br>
        <a href="{row['Link']}" target="_blank">View Listing</a>
        """

        # Check if the row matches the selected property
        icon_color = "red" if selected_address and row["Address"] == selected_address else "blue"

        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=popup_info,
            icon=folium.Icon(color=icon_color, icon="home"),
        ).add_to(m)

    # Display map with full width
    st_folium(m, width=800, height=500)

# TAB 2: Historical Trends
with tab2:
    st.subheader("📈 Historical Trends")

    historical_df = load_historical_data()
    if historical_df.empty:
        st.warning("⚠️ No historical data available.")
        st.stop()

    # Convert Pandas Timestamp to Python Date for Streamlit Slider
    min_date, max_date = historical_df["Date"].min().date(), historical_df["Date"].max().date()

    if min_date == max_date:
        st.warning(f"⚠️ Only one date available: {min_date}. No range to select.")
        selected_range = (min_date, max_date)
    else:
        selected_range = st.sidebar.slider(
            "Select Date Range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM-DD",
            key="historical_slider"
        )

    # Ensure date filtering is using correct format
    filtered_historical_df = historical_df[
        (historical_df["Date"] >= pd.to_datetime(selected_range[0])) &
        (historical_df["Date"] <= pd.to_datetime(selected_range[1]))
    ]

    # Average Price Over Time
    st.subheader("📊 Average Price Over Time")
    avg_price_trend = filtered_historical_df.groupby("Date")["Price"].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    avg_price_trend.plot(ax=ax, marker="o", linestyle="-")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
    ax.set_ylabel("Average Price ($M)")
    ax.set_xlabel("Date")
    ax.set_title("Historical Trend: Average Price")
    st.pyplot(fig)

    # Number of Listings Over Time
    st.subheader("🏠 Number of Listings Over Time")
    listings_trend = filtered_historical_df.groupby("Date")["Address"].count()
    fig, ax = plt.subplots(figsize=(10, 5))
    listings_trend.plot(ax=ax, marker="o", linestyle="-", color="red")
    ax.set_ylabel("Number of Listings")
    ax.set_xlabel("Date")
    ax.set_title("Historical Trend: Number of Listings")
    st.pyplot(fig)

    # Filter Historical Trends
    st.sidebar.subheader("📊 Filter Historical Trends")
    min_date, max_date = historical_df["Date"].min().date(), historical_df["Date"].max().date()

    if min_date == max_date:
        st.warning(f"⚠️ Only one date available: {min_date}. No range to select.")
    else:
        selected_range = st.sidebar.slider(
            "Select Date Range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM-DD"
        )

        # Convert selected_range back to Pandas Timestamp before filtering
        filtered_historical_df = historical_df[
            (historical_df["Date"] >= pd.to_datetime(selected_range[0])) &
            (historical_df["Date"] <= pd.to_datetime(selected_range[1]))
        ]

    # Summary Statistics
    st.subheader(f"📊 Summary for {selected_range[0]} to {selected_range[1]}")
    st.write(filtered_historical_df.describe())

st.write("Data Source: Redfin Scraper")
