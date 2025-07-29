# Import necessary libraries
import os                          # for directory manipulation
import time                        # for time computation
import json
import random
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd                # for DataFrame manipulation

# Configure chrome driver
def init_chrome_driver():
    
    chrome_options = Options()
    chrome_options.add_argument(" - headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

# Target URL: Redfin search URL for Hollywood Hills, Los Angeles
base_url = "https://www.redfin.com/neighborhood/547223/CA/Los-Angeles/Hollywood-Hills"

# Initialize chrome driver
driver = init_chrome_driver()

# Initialize data storage
scraped_data = []

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

# Get the directory of the script's location, assumed here to be '../notebooks' and to be on the same folder level 
# with '../data'
script_dir = os.getcwd()
# Please note that os.getcwd() depends on the current working directory, which might not always align with the script's 
# location  

# Navigate to the parent folder
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))

# Construct the path to the desired relative location - ../data/raw/{filename}.csv
path_to_file = os.path.join(parent_dir, "data", "raw", "redfin_hollywood_hills.csv")

# Save the scraped dataset as CSV
df.to_csv(path_to_file,index=False)

print(f"Scraping complete! {len(df)} listings saved to {path_to_file}")

# Close the browser
driver.quit()
