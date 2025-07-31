# Import libraries
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import logging

# Setup logging
logging.basicConfig(
    filename="logs/scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

scheduler = BlockingScheduler()

# Run scraper daily at 6 AM
def scrape_job():
    logging.info("🚀 Running scraper job...")
    result = subprocess.run(["python3", "scraper.py"], capture_output=True, text=True)
    if result.stdout:
        logging.info(result.stdout)
    if result.stderr:
        logging.error(result.stderr)  # Logs only if an error occurs

# Run data cleaning daily at 7 AM (after scraping)
def cleansing_job():
    logging.info("📊 Running data cleaning job...")
    result = subprocess.run(["python3", "cleanser.py"], capture_output=True, text=True)
    if result.stdout:
        logging.info(result.stdout)
    if result.stderr:
        logging.error(result.stderr)

# Schedule tasks
scheduler.add_job(scrape_job, "cron", hour=6)
scheduler.add_job(cleansing_job, "cron", hour=7)

# Start the scheduler
logging.info("🕒 Scheduler started...")
scheduler.start()

