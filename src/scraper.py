# Import necessary libraries
import os                          # for directory manipulation
import time                        # for time computation
import json
import random
import re
import logging
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd                # for DataFrame manipulation

# Setup logging

# Get the directory of the script's location, assumed here to be '../src' and to be on the same folder level 
# with '../logs'
script_dir = os.getcwd()
# Please note that os.getcwd() depends on the current working directory, which might not always align with the script's 
# location  

# Navigate to the parent folder
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))

# Construct the path to the desired relative location - ../logs/{filename}.log
path_to_log_file = os.path.join(parent_dir, "logs", "scraper.log")

logging.basicConfig(
    filename=path_to_log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Optional: List of randomized user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0"
]


# Configure chrome driver
#def init_chrome_driver():
#    
#    chrome_options = Options()
#    chrome_options.add_argument(" - headless")
#    service = Service(ChromeDriverManager().install())
#    driver = webdriver.Chrome(service=service, options=chrome_options)
#    
#    return driver


def init_chrome_driver(headless=True):
    chrome_options = Options()

    # 1. Random User-Agent
    user_agent = random.choice(USER_AGENTS)
    chrome_options.add_argument(f"user-agent={user_agent}")

    # 2. Headless mode (default = True)
    if headless:
        chrome_options.add_argument("--headless=new")  # more stable than "--headless"

    # 3. Stealth flags to reduce detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 4. Additional anti-bot evasion options
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")

    # 5. Launch driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 6. Remove Selenium detection (navigator.webdriver)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
        """
    })

    return driver

def scrape():
    try:
        logging.info("🔄 Starting Redfin Scraper...")
        
        # Target URL: Redfin search URL for Hollywood Hills, Los Angeles
        base_url = "https://www.redfin.com/neighborhood/547223/CA/Los-Angeles/Hollywood-Hills"

        # Initialize chrome driver
        driver = init_chrome_driver()

        # Initialize data storage
        scraped_data = []
        today = datetime.today().strftime("%Y-%m-%d")

        # Start scraping
        page_number = 1
        while True:
            print(f"Scraping page {page_number}...")

            url = base_url if page_number == 1 else f"{base_url}/page-{page_number}"
            driver.get(url)
            time.sleep(random.uniform(5, 8))

            # Locate the main listings container
            try:
                container = driver.find_element("css selector", "div.HomeCardsContainer")
                listings = container.find_elements("css selector", "div.HomeCardContainer")
            except:
                print("Failed to locate the property list container. Exiting...")
                break

            print(f"Found {len(listings)} listings on page {page_number}")

            for listing in listings:
                # Extract price
                try:
                    price = listing.find_element("css selector", "span.bp-Homecard__Price--value").text.strip()
                except:
                    price = "N/A"

                # Extract address
                try:
                    address = listing.find_element("css selector", "div.bp-Homecard__Address").text.strip()
                except:
                    print("Skipping a listing due to missing address data")
                    continue  # Skip listings with missing elements

                # Extract beds, baths, and sqft
                try:
                    beds = listing.find_element("css selector", "span.bp-Homecard__Stats--beds").text.strip()
                except:
                    beds = "N/A"

                try:
                    baths = listing.find_element("css selector", "span.bp-Homecard__Stats--baths").text.strip()
                except:
                    baths = "N/A"

                try:
                    sqft = listing.find_element("css selector", "span.bp-Homecard__LockedStat--value").text.strip()
                except:
                    sqft = "N/A"

                # Extract listing link and listing id
                try:
                    link = listing.find_element("css selector", "a.bp-Homecard").get_attribute("href")
                    link = f"https://www.redfin.com{link}" if link.startswith("/") else link
            
                    # Extract ID after /home/
                    match = re.search(r'/home/(\d+)', link)
                    if match:
                        listing_id = match.group(1)
                    else:
                        listing_id = "N/A"
            
                except:
                    print("Skipping a listing due to missing link data")
                    continue  # Skip listings with missing elements

                # Extract image URL
                try:
                    image_element = listing.find_element("css selector", "img.bp-Homecard__Photo--image")
                    image_url = image_element.get_attribute("src")
                except:
                    image_url = "N/A"
                
                try:
                    # Extract Geo-Coordinates (Latitude & Longitude)
                    json_script = listing.find_element(By.CSS_SELECTOR, "script[type='application/ld+json']").get_attribute("innerHTML")
                    json_data = json.loads(json_script)

                    # Sometimes it's a dict, sometimes a list of dicts
                    if isinstance(json_data, list):
                        geo_data = next((item.get("geo") for item in json_data if item.get("geo")), None)
                    else:
                        geo_data = json_data.get("geo")

                    if geo_data:
                        latitude = geo_data.get("latitude", "N/A")
                        longitude = geo_data.get("longitude", "N/A")
                    else:
                        latitude = "N/A"
                        longitude = "N/A"
                except Exception as e:
                    print(f"⚠️ Failed to extract geo-coordinates: {e}")
                    latitude = "N/A"
                    longitude = "N/A"

                # Store the data
                scraped_data.append({
                    "Listing ID": listing_id,
                    "Price": price,
                    "Address": address,
                    "Beds": beds,
                    "Baths": baths,
                    "SqFt": sqft,
                    "Link": link,
                    "Image URL": image_url, 
                    "Latitude": latitude,
                    "Longitude": longitude
                })

            # Try going to the next page by checking if the next-page anchor exists
            try:
                next_page_anchor = driver.find_element(By.CSS_SELECTOR, "a[aria-label='page {}']".format(page_number + 1))
                if next_page_anchor:
                    page_number += 1
                    time.sleep(random.uniform(3, 6))
                else:
                    break
            except:
                print("✅ No more pages.")
                break

        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(scraped_data)
        df["Date"] = today  # Add date for historical tracking

        # Get the directory of the script's location, assumed here to be '../src' and to be on the same folder level 
        # with '../data'
        script_dir = os.getcwd()
        # Please note that os.getcwd() depends on the current working directory, which might not always align with the script's 
        # location  

        # Navigate to the parent folder
        parent_dir = os.path.abspath(os.path.join(script_dir, ".."))

        # Construct the path to the desired relative location - ../data/raw/{daily filename}.csv
        path_to_daily_file = os.path.join(parent_dir, "data", "raw", f"redfin_hollywood_hills_{today}.csv")
        df.to_csv(path_to_daily_file,index=False)
        logging.info(f"Saved daily data: {path_to_daily_file}")

        # Append to master dataset
        path_to_master_file = os.path.join(parent_dir, "data", "raw", "redfin_hollywood_hills_master.csv")
        if os.path.exists(path_to_master_file):
            master_df = pd.read_csv(path_to_master_file)
            df = pd.concat([master_df, df]).drop_duplicates(subset=["Address", "Date"])
        df.to_csv(path_to_master_file, index=False)
        logging.info(f"Updated master dataset: {path_to_master_file}")

        # Close the browser
        driver.quit()
        exit(0)  # Exit successfully

    except Exception as e:
        logging.error(f"❌ Scraper failed: {e}")
        exit(1)  # Exit with failure

if __name__ == "__main__":
    scrape()
