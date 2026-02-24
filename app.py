"""
main_cron.py - Cronjob friendly monitoring script
Run manually:
    python main_cron.py

Run via cron:
    */5 * * * * /usr/bin/python3 /path/to/main_cron.py >> /var/log/webmon.log 2>&1
"""

import asyncio
import time
import logging
import sys
import os

from core.engine import MonitorEngine
from outputs.local_log import write_local_log
from outputs.sheets import save_logs_gsheet
from outputs.sheets import apply_formatting
from outputs.sheets import update_summary_gsheet as update_summary
from outputs.telegram import send_telegram_text

try:
    from outputs.email import send_monitoring_alert
except Exception:
    def send_monitoring_alert(results):
        return False

from config import LIST_TAB_NAME, SPREADSHEET_NAME
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build


# ---------------- LOGGING SETUP ----------------

LOG_FILE = "/var/log/webmon.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# ---------------- GOOGLE SHEETS INIT ----------------

spreadsheet = None
list_tab = None
sheets_api = None


def init_google_sheets():
    global spreadsheet, list_tab, sheets_api

    if spreadsheet:
        return

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        "env/credentials.json",
        scopes=SCOPES
    )

    gclient = gspread.authorize(creds)
    spreadsheet = gclient.open(SPREADSHEET_NAME)
    list_tab = spreadsheet.worksheet(LIST_TAB_NAME)
    sheets_api = build("sheets", "v4", credentials=creds)

    logger.info("Google Sheets initialized")


def load_urls_from_sheet():
    try:
        init_google_sheets()
        urls = list_tab.col_values(2)[1:]
        return urls
    except Exception as e:
        logger.error(f"Failed load URLs: {e}")
        return []


# ---------------- TELEGRAM SUMMARY ----------------

def build_telegram_summary(results):
    healthy = sum(1 for r in results if r.get("Status") == "HEALTHY")
    warning = sum(1 for r in results if r.get("Status") in ("SLOW", "PARTIAL"))
    errors = [r for r in results if r.get("Status") not in ("HEALTHY", "SLOW", "PARTIAL")]

    lines = [
        "📊 WEB-MON BNPB — Scan Summary",
        f"✅ Healthy : {healthy}",
        f"⚠️ Warning : {warning}",
        f"🚫 Error   : {len(errors)}",
        "",
    ]

    for e in errors[:20]:
        lines.append(f"{e.get('URL')} | {e.get('Status')}")

    lines.append(f"\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(lines)


# ---------------- RUN SCAN ----------------

def run_once():

    logger.info("Starting monitoring scan...")

    urls = load_urls_from_sheet()

    if not urls:
        logger.warning("No URLs found in Google Sheet")
        return

    logger.info(f"Found {len(urls)} domains")

    engine = MonitorEngine(urls)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        results = loop.run_until_complete(engine.run())
    finally:
        loop.close()

    logger.info("Scan completed")

    # Save outputs
    save_logs_gsheet(results)
    update_summary(results)
    apply_formatting()

    local_file = write_local_log(results)
    logger.info(f"Local log saved: {local_file}")

    send_telegram_text(build_telegram_summary(results), silent=True)
    logger.info("Telegram notification sent")

    send_monitoring_alert(results)

    logger.info("Monitoring finished successfully")


if __name__ == "__main__":
    try:
        run_once()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)