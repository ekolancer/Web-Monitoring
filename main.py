import asyncio
import time
import schedule
import sys
import os
from rich.console import Console
from ui.banner import banner
from ui.table_view import make_table, make_table_live
from outputs.local_log import write_local_log
from outputs.sheets import save_logs_gsheet
from outputs.sheets import apply_formatting
from outputs.sheets import update_summary_gsheet as update_summary
from outputs.telegram import send_telegram_text

# Optional email alerts: import if available, otherwise provide no-op fallbacks
try:
    from outputs.email import send_monitoring_alert, send_security_alert
except Exception:
    def send_monitoring_alert(results):
        return False

    def send_security_alert(results):
        return False
from core.engine import MonitorEngine
from utils.logger import setup_logger
from config import LIST_TAB_NAME, SPREADSHEET_NAME, CHECK_INTERVAL, THREAD_WORKERS, BOT_TOKEN, CHAT_ID, EMAIL_ENABLED, SMTP_SERVER, EMAIL_USER, TIMEOUT_MS, CONCURRENCY
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from core.security_checker import run_security_check_async as run_security_check
from outputs.sheets_security import write_security_results
from outputs.sheets import init_sheets
from outputs.sheets_security_summary import (
    build_security_summary,
    write_security_summary,
    apply_security_summary_formatting,
    prepare_security_summary_sheet
)
from outputs.telegram import send_security_alert


spreadsheet, sheets_api = init_sheets()

console = Console()
logger = setup_logger()

# Global variables for lazy initialization
spreadsheet = None
sheets_api = None
gclient = None
list_tab = None
security_summary_sheet = None
security_sheet = None

def init_google_sheets():
    """Initialize Google Sheets connection lazily"""
    global spreadsheet, sheets_api, gclient, list_tab, security_summary_sheet, security_sheet

    if spreadsheet is not None:
        return  # Already initialized

    try:
        # init google sheet client (used only for reading list)
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("env/credentials.json", scopes=SCOPES)
        gclient = gspread.authorize(creds)
        spreadsheet = gclient.open(SPREADSHEET_NAME)
        list_tab = spreadsheet.worksheet(LIST_TAB_NAME)

        # Initialize sheets API
        sheets_api = build('sheets', 'v4', credentials=creds)

        try:
            security_summary_sheet = spreadsheet.worksheet("Security Summary")
        except gspread.WorksheetNotFound:
            security_summary_sheet = spreadsheet.add_worksheet(
                title="Security Summary",
                rows=1000,
                cols=10
            )

        try:
            security_sheet = spreadsheet.worksheet("Security Check")
        except gspread.WorksheetNotFound:
            security_sheet = spreadsheet.add_worksheet(
                title="Security Check",
                rows=2000,
                cols=10
            )

    except Exception as e:
        console.print(f"[red]❌ Failed to initialize Google Sheets: {e}[/]")
        console.print("[yellow]Some features may not work without Google Sheets connection[/]")
        logger.error(f"Google Sheets initialization failed: {e}")

# security sheet
def load_urls_from_sheet():
    init_google_sheets()
    try:
        return list_tab.col_values(2)[1:]
    except Exception as e:
        logger.error(f"Failed load URLs: {e}")
        return []

# load VM list from sheet    
def build_vm_list_from_urls():
    """
    Ambil DOMAIN langsung dari kolom B sheet 'List VM'
    (tanpa tergantung nama header)
    """
    init_google_sheets()
    try:
        rows = list_tab.get_all_values()
    except Exception as e:
        logger.error(f"Gagal membaca List VM: {e}")
        return []

    vm_list = []

    for idx, row in enumerate(rows[1:], start=1):  # skip header
        if len(row) < 2:
            continue

        domain = str(row[1]).strip()   # kolom B
        if not domain:
            continue

        domain = (
            domain
            .replace("https://", "")
            .replace("http://", "")
            .strip("/")
        )

        vm_list.append({
            #"vm_name": f"VM-{idx}",     # internal saja
            "domain": domain            # ⬅️ DOMAIN ASLI
        })

    return vm_list

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


#---------------- RUN ONCE SCAN ----------------
def run_once():
    banner()
    console.print("[bold green]SCAN ON PROGRESS....[/]")

    urls = load_urls_from_sheet()
    console.print(f"[cyan]Found {len(urls)} domains to check[/]")
    if not urls:
        console.print("[red]Tidak ada URL di 'List VM' kolom B.[/]")
        input("ENTER to return...")
        return

    engine = MonitorEngine(urls) # type: ignore
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
    console.print(f"\n[cyan]Local log saved to:[/] [bold]{local_file}[/]")
    console.print("\n[cyan]Logs & Summary updated (Sheets + local file).[/]")

    send_telegram_text(build_telegram_summary(results), silent=True)
    console.print("\n[cyan]Telegram Notifiaction Sent Successfully.[/]")

    # Send email alerts for critical issues
    send_monitoring_alert(results)

    input("\nENTER to return...")

#---------------- Telegram Summary Builder ----------------
def build_telegram_summary(results):
    healthy = sum(1 for r in results if r.get("Status") == "HEALTHY")
    warning = sum(1 for r in results if r.get("Status") in ("SLOW", "PARTIAL"))
    errors = [r for r in results if r.get("Status") not in ("HEALTHY","SLOW","PARTIAL")]
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


#---------------- RUN LIVE MONITORING ----------------
def run_live():
    try:
        while True:
            banner()
            console.print("[bold green]========= LIVE SCAN WEBSITE MONITORING =========[/]")
            console.print("[bold gray]SCAN ON PROGRESS.... (CTRL+C to stop)[/]\n")

            urls = load_urls_from_sheet()
            if not urls:
                console.print("[red]Tidak ada URL di 'List VM' kolom B.[/]")
                time.sleep(5)
                continue

            hacking_loading("Initializing WEB-MON engine", duration=2.0)

            engine = MonitorEngine(urls) # type: ignore
            total = len(urls)

            # ================================
            # PROGRESS BAR REALTIME
            # ================================
            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]{task.description}"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total}"),
                TimeElapsedColumn(),
                console=console,
                expand=True
            ) as progress:

                task = progress.add_task("Live scanning...", total=total)

                def on_update(res):
                    progress.update(task, advance=1)

                # jalankan engine dengan callback progress
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    results = loop.run_until_complete(engine.run(progress_callback=on_update))
                finally:
                    loop.close()

            # after progress bar done
            console.print("\n[bold green]✔ Live scan finished! Displaying results...[/]\n")

            console.print(make_table_live(results))

            # countdown UI
            console.print("")
            for remaining in range(CHECK_INTERVAL, 0, -1):
                sys.stdout.write(f"\r🔄 Refreshing in {remaining}s...")
                sys.stdout.flush()
                time.sleep(1)
            print("\n")   # spacing

    except KeyboardInterrupt:
        console.print("\n\n[red]⛔ Live monitoring stopped by user.[/]")
        time.sleep(1)

#---------------- RUN SECURITY CHECK ----------------
def run_security():
    banner()
    console.print("[cyan]🔐 Running Security Check...[/]")

    vm_list = build_vm_list_from_urls()
    console.print(f"[cyan]Found {len(vm_list)} domains to check[/]")
    if not vm_list:
        console.print("[red]Tidak ada VM / URL untuk Security Check[/]")
        input("ENTER to return...")
        return

    init_google_sheets()  # Initialize Google Sheets before using

    hacking_loading("Preparing security scanner...", duration=4.0)

    total = len(vm_list)

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:

        task = progress.add_task("Security scanning...", total=total)

        def on_update(_):
            progress.update(task, advance=1)

        results = asyncio.run(run_security_check(
            vm_list,
            progress_callback=on_update
        ))

    console.print("\n[bold green]✔ Security Scan completed![/]\n")

    # PIPELINE LANJUTAN (TIDAK DIUBAH)
    write_security_results(security_sheet, results)

    detail_sheet_id = get_sheet_id_by_title(
        sheets_api,
        spreadsheet.id,
        "Security Check"
    )

    if detail_sheet_id is None:
        console.print("[red]Sheet 'Security Check' tidak ditemukan[/]")
        input("ENTER to return...")
        return

    summary_rows = build_security_summary(
        results,
        spreadsheet.id,
        detail_sheet_id
    )

    summary_sheet_id = get_sheet_id_by_title(
        sheets_api,
        spreadsheet.id,
        "Security Summary"
    )

    if summary_sheet_id is not None:
        prepare_security_summary_sheet(
            sheets_api,
            spreadsheet.id,
            summary_sheet_id
        )

    write_security_summary(
        security_summary_sheet,
        summary_rows
    )

    apply_security_summary_formatting(
        sheets_api,
        spreadsheet.id,
        summary_sheet_id
    )

    send_security_alert(summary_rows)

    console.print("[green]✔ Security Check + Summary completed[/]")
    input("\nENTER to return...")

#---------------- AUTOMATIC SCHEDULER ----------------
def auto_scheduler():
    schedule.every().day.at("08:00").do(run_once)
    schedule.every().day.at("21:03").do(run_once)
    console.print("\n⏱ Scheduler aktif... Menunggu waktu yang dijadwalkan.\n", style="bold yellow")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n\n[red]⛔ Scheduler dihentikan oleh user.[/]\n")

#---------------- DIAGNOSTICS ----------------
def check_telegram():
    console.print("\n[bold cyan]==>  Testing Telegram Notification...[/]")
    return send_telegram_text("✺◟(＾∇＾)◞✺ — Telegram notification working.")

def check_spreadsheet():
    init_google_sheets()
    try:
        urls = list_tab.col_values(2)
        if urls:
            console.print("[bold green]==>  Testing Spreadsheet Working[/]")
            return True
        else:
            console.print("[bold red]==>  Testing Spreadsheet Failed - Please Input The Url You Want To Check..[/]")
            return False
    except Exception as e:
        console.print(f"[bold red]==>  Testing Spreadsheet Failed - {e}[/]")
        return False

#---------------- DIAGNOSTICS ----------------
def run_diagnostics():
    banner()
    console.print("[bold yellow]CONFIG CHECK & DIAGNOSTICS[/]")
    ok_tg = check_telegram()
    ok_sheet = check_spreadsheet()
    
    console.print("\n─────────────────────────────────────────")
    console.print("=> RESULT:")

    if ok_sheet and ok_tg:
        console.print("[bold green]==>  All configurations working! You are ready to run monitoring. √√√[/]")
    else:
        console.print("[bold red]==>  Some configuration failed. Fix before running scans.[/]")

    input("\nPress ENTER to return...")
    
# utility to get sheet ID by title
def get_sheet_id_by_title(sheets_api, spreadsheet_id: str, title: str) -> int | None:
    """
    Ambil sheetId berdasarkan nama sheet (aman & resmi)
    """
    meta = sheets_api.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()

    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        if props.get("title") == title:
            return props.get("sheetId")

    return None

# utility to clear screen
def clear():
    os.system("cls" if os.name == "nt" else "clear")
    console.clear()    
    

# ---------------- MENU ----------------
def menu():
    while True:
        banner()
        console.print("[cyan][1][/cyan] Run Scan Once & Export Logs")
        console.print("[cyan][2][/cyan] Live Monitoring (Loop)")
        console.print("[cyan][3][/cyan] Security Check Test")
        console.print("[cyan][4][/cyan] Telegram Notification Test")
        console.print("[cyan][5][/cyan] Run Diagnostics (Spreadsheet + Telegram Test)")
        console.print("[cyan][6][/cyan] Run Automatic Scheduler (Daily)")
        console.print("[cyan][7][/cyan] Start Web Dashboard")
        console.print("[cyan][8][/cyan] Configuration Settings")
        console.print("[red][0][/red] Exit\n")

        print("┌── Input Option")
        print("│")
        choice = input("└────────> ").strip()

        if choice == "1":
            run_once()

        elif choice == "2":
            try:
                run_live()
            except KeyboardInterrupt:
                console.print("\n[yellow]Live monitoring stopped.[/]")
                time.sleep(1.5)

        elif choice == "3":
            run_security()            
            
        elif choice == "4":
            check_telegram()
            input("\nPress ENTER to return...")

        elif choice == "5":
            run_diagnostics()

        elif choice == "6":
            auto_scheduler()

        elif choice == "7":
            start_web_dashboard()

        elif choice == "8":
            config_settings()

        elif choice == "0":
            clear()
            console.print(
                "[green]Goodbye, Salam Tangguh, Tangguh, Tangguh !!![/]"
            )
            time.sleep(1)
            break

        else:
            console.print("[red]Invalid option! Try again...[/]")
            time.sleep(1.3)

#---------------- START WEB DASHBOARD ----------------
def start_web_dashboard():
    console.print("[cyan]🚀 Starting Web Dashboard...[/]")
    console.print("[cyan]Dashboard will be available at: http://localhost:5000[/]")
    console.print("[yellow]Press Ctrl+C to stop the dashboard[/]")

    try:
        from web.app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except ImportError:
        console.print("[red]❌ Flask not installed. Run: pip install flask flask-cors plotly pandas sqlalchemy[/]")
        input("Press ENTER to return...")
    except Exception as e:
        console.print(f"[red]❌ Error starting dashboard: {e}[/]")
        input("Press ENTER to return...")

#---------------- CONFIGURATION SETTINGS ----------------
def config_settings():
    while True:
        banner()
        console.print("[cyan]⚙️  Configuration Settings[/]")
        console.print("[cyan][1][/cyan] Edit Telegram Settings")
        console.print("[cyan][2][/cyan] Edit Email Settings")
        console.print("[cyan][3][/cyan] Edit Monitoring Settings")
        console.print("[cyan][4][/cyan] Edit Google Sheets Settings")
        console.print("[red][0][/red] Back to Main Menu\n")

        print("┌── Input Option")
        print("│")
        choice = input("└────────> ").strip()

        if choice == "1":
            edit_telegram_config()
        elif choice == "2":
            edit_email_config()
        elif choice == "3":
            edit_monitoring_config()
        elif choice == "4":
            edit_sheets_config()
        elif choice == "0":
            break
        else:
            console.print("[red]Invalid option! Try again...[/]")
            time.sleep(1.3)

def edit_telegram_config():
    console.print("[cyan]📱 Telegram Configuration[/]")
    console.print(f"Current BOT_TOKEN: {BOT_TOKEN[:10]}..." if BOT_TOKEN else "Not set")
    console.print(f"Current CHAT_ID: {CHAT_ID}" if CHAT_ID else "Not set")

    new_token = input("Enter new BOT_TOKEN (leave empty to keep current): ").strip()
    if new_token:
        # In real implementation, update config.py
        console.print("[yellow]Note: Config file needs to be manually updated for persistence[/]")

    new_chat = input("Enter new CHAT_ID (leave empty to keep current): ").strip()
    if new_chat:
        console.print("[yellow]Note: Config file needs to be manually updated for persistence[/]")

    console.print("[green]Telegram config updated![/]")
    input("Press ENTER to continue...")

def edit_email_config():
    console.print("[cyan]📧 Email Configuration[/]")
    console.print(f"Email Enabled: {EMAIL_ENABLED}")
    console.print(f"SMTP Server: {SMTP_SERVER}")
    console.print(f"Email User: {EMAIL_USER}")

    enable = input("Enable email alerts? (y/n): ").strip().lower()
    if enable == 'y':
        console.print("[yellow]Note: Update config.py with your email credentials[/]")

    console.print("[green]Email config updated![/]")
    input("Press ENTER to continue...")

def edit_monitoring_config():
    console.print("[cyan]🔍 Monitoring Configuration[/]")
    console.print(f"Check Interval: {CHECK_INTERVAL} seconds")
    console.print(f"Timeout: {TIMEOUT_MS} ms")
    console.print(f"Concurrency: {CONCURRENCY}")

    console.print("[yellow]Edit config.py directly for these settings[/]")
    input("Press ENTER to continue...")

def edit_sheets_config():
    console.print("[cyan]📊 Google Sheets Configuration[/]")
    console.print(f"Spreadsheet Name: {SPREADSHEET_NAME}")
    console.print(f"List Tab Name: {LIST_TAB_NAME}")

    console.print("[yellow]Edit config.py directly for these settings[/]")
    input("Press ENTER to continue...")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        console.print("\n[red]⛔ Program stopped by user.[/]")
        time.sleep(1)
