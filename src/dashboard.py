# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import folium
from streamlit_folium import st_folium
import numpy as np
import os

# Load Data
@st.cache_data
def load_data():
    # Get the directory of the script's location, assumed here to be '../src' and to be on the same folder level with '../data'
    script_dir = os.getcwd()
    # Please note that os.getcwd() depends on the current working directory, which might not always align with the script's location  

    # Navigate to the parent folder
    parent_dir = os.path.abspath(os.path.join(script_dir, ".."))

    # Construct the path to the Excel file in the desired relative location
    cleaned_data_path = os.path.join(parent_dir, "data", "cleaned", "redfin_hollywood_hills_cleaned.csv")

    # Read the Excel file into a DataFrame
    df = pd.read_csv(cleaned_data_path)

    # Ensure correct data types
    df["Price"] = df["Price"].astype(float)
    df["Beds"] = df["Beds"].astype(float)
    df["Baths"] = df["Baths"].astype(float)
    df["SqFt"] = df["SqFt"].astype(float)
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    return df.dropna(subset=["Latitude", "Longitude"])  # Remove entries without coordinates

df = load_data()

# Streamlit UI
st.title("🏡 Hollywood Hills Real Estate Dashboard")
st.write("Analyze real estate trends in Hollywood Hills using interactive visualizations.")

# Sidebar Filters
st.sidebar.header("🔍 Filter Listings")

# Show all properties button
show_all = st.sidebar.checkbox("Show All Properties", value=False)

if show_all:
    filtered_df = df  # Show all properties
else:
    # Determine the max price dynamically and round up to the next 1 million
    min_price_value = max(1000, df["Price"].min())  # Ensure minimum is at least 1,000
    max_price_value = np.ceil(df["Price"].max() / 1_000_000) * 1_000_000  # Round up to next 1M

    # Price Slider
    min_price, max_price = st.sidebar.slider(
        "Select Price Range ($)", 
        min_value=int(min_price_value), 
        max_value=int(max_price_value), 
        value=(int(min_price_value), int(max_price_value)),
        format="$%d"
    )

    # Bedrooms: Round up to the next multiple of 5
    min_beds = 1
    max_beds = int(np.ceil(df["Beds"].max() / 5) * 5)

    # Bathrooms: Round up to the next multiple of 5
    min_baths = 1
    max_baths = int(np.ceil(df["Baths"].max() / 5) * 5)

    # Square Footage: Ensure a sensible range
    min_sqft = 100
    max_sqft = int(np.ceil(df["SqFt"].max() / 10_000) * 10_000)

    # Filters
    selected_beds = st.sidebar.slider("Bedrooms", min_beds, max_beds, (1, 5))
    selected_baths = st.sidebar.slider("Bathrooms", min_baths, max_baths, (1, 5))
    selected_sqft = st.sidebar.slider("Square Footage", min_sqft, max_sqft, (500, 5000))

    # Apply Filters
    filtered_df = df[
        (df["Price"] >= min_price) & (df["Price"] <= max_price) &
        (df["Beds"] >= selected_beds[0]) & (df["Beds"] <= selected_beds[1]) &
        (df["Baths"] >= selected_baths[0]) & (df["Baths"] <= selected_baths[1]) &
        (df["SqFt"] >= selected_sqft[0]) & (df["SqFt"] <= selected_sqft[1])
    ]

# Display Data Table with Interactive Selection
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

# Map Visualization
st.subheader("📍 Property Locations")

# Create map centered on Hollywood Hills
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

st.write("Data Source: Redfin Scraper")

