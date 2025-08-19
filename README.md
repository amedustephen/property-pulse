# Property Pulse

An automated data pipeline with a simple, easy to use Streamlit dashboard to help real estate professionals access near real-time property listings, monitor market trends, and make informed, data-driven decisions

---

## Features

- Scrapes real estate listings from Redfin using Selenium.
- Cleans and structures the data to ensure accuracy and consistency.
- Stores historical data for long-term trend analysis.
- Visualizes key insights using an interactive Streamlit dashboard.

---

## Project Folder Structure

property_pulse/ 
├── data/ 
│ ├── cleaned 
│ └── raw 
├── notebooks/ 
│ ├── Redfin_EDA.ipynb                                 
│ ├── Redfin_Scraper.ipynb                            
│ └── Redfin_Scraping_Experiment.ipynb    
├── src/ 
│ ├── __init__.py 
│ ├── scraper.py 
│ ├── cleanser.py 
│ ├── dashboard.py 
│ └── scheduler.py 
├── .env 
├── .gitignore 
├── pyproject.toml 
└── README.md

---

## Script Breakdown

### 1️⃣ src/scraper.py
- Standalone script generated from "notebooks/Redfin_Scraper.ipynb" to run locally
- scrapes property listings from "redfin.com/neighborhood/547223/CA/Los-Angeles/Hollywood-Hills"
- Extracts a range of essential details, including prices, addresses, beds/baths, images, and geo-coordinates
- Stores output in csv format in "data/raw/"


### 2️⃣ src/cleanser.py
- Standalone script generated from "notebooks/Redfin_EDA.ipynb" to run locally
- Gets scraped data from "data/raw/" and clean up to ensure it is structured for visualization and further processing
- Stores output in csv format in "data/cleaned/"

### 3️⃣ src/dashboard.py
- Streamlit interactive dashboard for users to explore and analyze the scraped real estate data dynamically
- Gets inout from "data/cleaned/"

### 4️⃣ src/scheduler.py
- schedules scraping and data cleansing jobs to run at predefined times every day

---

## Libraries Used

- **Selenium**: Automates browser interactions to navigate through pages and handle dynamic content.
- **BeautifulSoup (bs4)**: Parses the HTML content of each page to extract relevant car details.
- **Pandas**: Organizes the scraped data into a structured DataFrame and saves it as a CSV file.
- **OS, sys, time**: Provides basic system interaction, such as file operations, output flushing, and time delays.

---




Automated real estate data pipeline that scrapes property listings, cleans the data, visualizes trends, and tracks historical prices over time
