"""
main_once.py - Standalone script to run monitoring scan once
Can be executed directly with: python main_once.py
"""
import asyncio
import time
import sys
import os
from rich.console import Console
from ui.banner import banner
from ui.table_view import make_table
from outputs.local_log import write_local_log
from outputs.sheets import save_logs_gsheet
from outputs.sheets import apply_formatting
from outputs.sheets import update_summary_gsheet as update_summary
from outputs.telegram import send_telegram_text

# Optional email alerts: import if available, otherwise provide no-op fallbacks
try:
    from outputs.email import send_monitoring_alert
except Exception:
    def send_monitoring_alert(results):
        return False

from core.engine import MonitorEngine
from utils.logger import setup_logger
from config import LIST_TAB_NAME, SPREADSHEET_NAME
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()
logger = setup_logger()

# Global variables for lazy initialization
spreadsheet = None
sheets_api = None
gclient = None
list_tab = None


def init_google_sheets():
    """Initialize Google Sheets connection lazily"""
    global spreadsheet, sheets_api, gclient, list_tab

    if spreadsheet is not None:
        return  # Already initialized

    try:
        # init google sheet client (used only for reading list)
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("env/credentials.json", scopes=SCOPES)
        gclient = gspread.authorize(creds)
        spreadsheet = gclient.open(SPREADSHEET_NAME)
        list_tab = spreadsheet.worksheet(LIST_TAB_NAME)

        # Initialize sheets API
        sheets_api = build('sheets', 'v4', credentials=creds)

    except Exception as e:
        console.print(f"[red]❌ Failed to initialize Google Sheets: {e}[/]")
        console.print("[yellow]Some features may not work without Google Sheets connection[/]")
        logger.error(f"Google Sheets initialization failed: {e}")


def load_urls_from_sheet():
    """Load URLs from Google Sheet column B"""
    init_google_sheets()
    try:
        return list_tab.col_values(2)[1:]
    except Exception as e:
        logger.error(f"Failed load URLs: {e}")
        return []


#---------------- Animasi Loading ----------------
def hacking_loading(message="Initializing engine", duration=5.0):
    frames = ["[=          ]", "[==         ]", "[===        ]", "[====       ]", "[=====      ]", "[======     ]", "[=======    ]", "[========   ]", "[=========  ]",
              "[========== ]", "[===========]", "[ ==========]", "[  =========]", "[   ========]", "[    =======]", "[     ======]", "[      =====]", "[       ====]", "[        ===]", "[         ==]", "[          =]"]
    start = time.time()
    idx = 0
    while time.time() - start < duration:
        frame = frames[idx % len(frames)]
        print(f"\r{message} {frame}", end="", flush=True)
        time.sleep(0.12)
        idx += 1
    print("\r" + " " * (len(message) + 10), end="\r")


#---------------- Telegram Summary Builder ----------------
def build_telegram_summary(results):
    healthy = sum(1 for r in results if r.get("Status") == "HEALTHY")
    warning = sum(1 for r in results if r.get("Status") in ("SLOW", "PARTIAL"))
    errors = [r for r in results if r.get("Status") not in ("HEALTHY", "SLOW", "PARTIAL")]
    lines = [
        "📊 WEB-MON BNPB — Scan Summary",
        f"✅   Healthy : {healthy} situs",
        f"⚠️   Warning : {warning} situs",
        f"🚫   Error   : {len(errors)} situs",
        "━━━━━━━━━━━━━\n"
    ]
    for e in errors[:40]:
        lines += [
            f"🌐 {e.get('URL')}",
            f"📌 Status : {e.get('Status')}",
            f"⚡ Latency : {e.get('Latency')}",
            f"🔐 SSL : {e.get('SSL Status')}",
            "━━━━━━━━━━━━━\n"
        ]
    lines.append(f"📝 Logs updated to Google Sheets (Logs & Summary)")
    lines.append(f"⏰ Created_at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("Powered by Salam Tangguh, Tangguh, Tangguh !!! 💪💪💪")
    return "\n".join(lines)


#---------------- RUN ONCE SCAN ----------------
def run_once():
    """Run monitoring scan once and export results"""
    banner()
    console.print("[cyan]🖥️  Running Monitoring Check....[/]")

    urls = load_urls_from_sheet()
    console.print(f"[cyan]Found {len(urls)} domains to check[/]")
    if not urls:
        console.print("[red]Tidak ada URL di 'List VM' kolom B.[/]")
        input("ENTER to return...")
        return

    engine = MonitorEngine(urls)  # type: ignore
    total = len(urls)
    hacking_loading("Panasin mesin dulu yah...", duration=5.0)

    # PROGRESS REAL
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:

        task = progress.add_task("Scanning websites...", total=total)

        def on_update(res):
            progress.update(task, advance=1)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(engine.run(progress_callback=on_update))
        finally:
            loop.close()

    console.print("\n[bold green]✔ Scan completed![/]\n")

    console.print(make_table(results))

    init_google_sheets()  # Initialize before saving to sheets
    save_logs_gsheet(results)
    update_summary(results)
    apply_formatting()

    local_file = write_local_log(results)
    console.print(f"\n[green]✅ Local log saved to:[/] [bold]{local_file}[/]")
    console.print("\n[green]✅ Logs & Summary updated (Sheets + local file).[/]")

    send_telegram_text(build_telegram_summary(results), silent=True)
    console.print("\n[green]🚀 Telegram Notifiaction Sent Successfully.[/]")

    # Send email alerts for critical issues
    send_monitoring_alert(results)


if __name__ == "__main__":
    try:
        run_once()
    except KeyboardInterrupt:
        console.print("\n[red]⛔ Program stopped by user.[/]")
        time.sleep(1)
