# Property Pulse

An automated data pipeline with a simple, easy to use Streamlit dashboard to help real estate professionals access near real-time property listings, monitor market trends, and make informed, data-driven decisions

Based on the tutorial “[Python Automated Real Estate Data Pipeline Project: Web Scraping](https://hackr.io/blog/how-to-create-a-python-real-estate-data-pipeline-web-scraping)” on Hackr.io.


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

- **Selenium**: Automates web browsing to extract real estate data.
- **webdriver_manager**: Manages browser drivers for Selenium.
- **Pandas**: Stores and processes scraped data.
- **numpy**: Handle missing values & numeric transformations.
- **re**: For using regular expressions to extract numeric values from text fields.
- **streamlit**: Build an interactive web-based dashboard.
- **matplotlib**: Create plots & data visualizations.
- **seaborn**: Enhance statistical plots.
- **folium**: Render interactive maps for property locations.
- **streamlit-folium**: Integrate Folium maps into Streamlit.
- **apscheduler**: Schedule automated scraping and analysis jobs.

---

## Installation

1. Clone the repository
2. Make sure you have Python installed
3. Install Poetry (if not already installed)
4. Install dependencies:

   ```bash
   poetry install
   ```
5. Make sure **ChromeDriver** is compatible with your Chrome browser version

---

## Usage

1. Run the Script:

   Once dependencies are installed and `ChromeDriver` is set up, run the script, either manually and/or in automatic mode:

   ```bash (manual mode)
    poetry run python src/scraper.py
    poetry run python src/cleanser.py (only after scraper.py completed successfully)
    ```

   ```bash (debug mode)
    poetry run python src/scheduler.py --debug
   ```

   ```bash (automatic mode)
    poetry run python src/scheduler.py
    ```

3. Run the Streamlit App:

   ```bash 
    poetry run streamlit run src/dashboard.py
    ```

   After running the command, Streamlit will display a URL in the terminal (usually `http://localhost:8501`). Open this URL in your browser.

---

## Limitations

- **Dynamic changes** in source website's structure may require updates in selectors.
- **CAPTCHAs or anti-scraping mechanisms** can block automated scraping.
- **Legal considerations:** Ensure compliance with source website’s Terms of Service.

---

## Future Scope

- **Proxy Support:** Integrate proxy support for enhanced scraping.
- **Detailed UI:** Enhance the Streamlit interface with more detailed and user-friendly features.
- **Multiple data source:** Add support for other real estate listing sites.
- **Multithreading:** Implement multithreading to speed up the scraping experience.
- **Database storage:** Integrate database storage options.
- **Cloud migration:** Migrate the entire pipeline archiecture using more scalable high-performance data warehouse, ETL orchestration, and visualization tools.

---

## License

MIT

---

## Contact Me

For any inquiries or service requests, please reach out to me via LinkedIn or email:

- **LinkedIn:** [linkedin.com/in/amedupaulstephen/](https://www.linkedin.com/in/amedupaulstephen/)
- **Email:** amedustephen@hotmail.com

I look forward to connecting with you!