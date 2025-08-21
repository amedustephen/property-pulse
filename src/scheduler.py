# Import libraries
import os
import sys
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.blocking import BlockingScheduler

# --- Resolve project root ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))

# --- Log setup with rotation + UTF-8 ---
log_file = os.path.join(project_root, "logs", "scheduler.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[handler, logging.StreamHandler(sys.stdout)]
)

scheduler = BlockingScheduler()

# --- Utility: run a script inside the same Python (Poetry env) ---
def run_script(script_name):
    script_path = os.path.join(script_dir, script_name)
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.stdout:
        logging.info(result.stdout.strip())
    if result.stderr:
        logging.error(result.stderr.strip())
    return result.returncode == 0

# --- Jobs ---
def scrape_job():
    logging.info("🚀 Starting scraper job...")
    success = run_script("scraper.py")
    if not success:
        logging.error("❌ Scraper failed — skipping cleanser.")
        return
    logging.info("✅ Scraper finished successfully — launching cleanser...")
    run_script("cleanser.py")

# --- Main entry ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Run once (scraper → cleanser) and exit")
    args = parser.parse_args()

    if args.debug:
        logging.info("🧪 Debug mode: running once and exiting.")
        scrape_job()
    else:
        logging.info("🕒 Scheduler started in production mode.")
        scheduler.add_job(scrape_job, "cron", hour=2)  # runs daily at 2 AM
        scheduler.start()
