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
from core.engine import MonitorEngine
from utils.logger import setup_logger
from config import LIST_TAB_NAME, SPREADSHEET_NAME, CHECK_INTERVAL, THREAD_WORKERS
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

console = Console()
logger = setup_logger()

# init google sheet client (used only for reading list)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
gclient = gspread.authorize(creds)
spreadsheet = gclient.open(SPREADSHEET_NAME)
list_tab = spreadsheet.worksheet(LIST_TAB_NAME)

def load_urls_from_sheet():
    try:
        return list_tab.col_values(2)[1:]
    except Exception as e:
        logger.error(f"Failed load URLs: {e}")
        return []

def run_once():
    banner()
    console.print("[bold green]SCAN ON PROGRES....[/]")
    urls = load_urls_from_sheet()
    if not urls:
        console.print("[red]Tidak ada URL di 'List VM' kolom B.[/]")
        input("ENTER to return...")
        return

    # progress UI
    results = []
    engine = MonitorEngine(urls) # pyright: ignore[reportArgumentType]
    hacking_loading("Initializing WEB-MON engine", duration=3.0)

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console, expand=True
    ) as progress:
        task = progress.add_task("Scanning websites...", total=len(urls))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(engine.run())
        finally:
            loop.close()
        for _ in results:
            progress.update(task, advance=1)

    console.print("\n[bold green]✔ Scan completed![/]\n")

    # display table identical to previous UX
    console.print(make_table(results))

    # save to sheets
    save_logs_gsheet(results)
    update_summary(results)
    apply_formatting()
    
    # write local
    local_file = write_local_log(results)
    console.print(f"\n[cyan]Local log saved to:[/] [bold]{local_file}[/]/n")

    # telegram
    send_telegram_text(build_telegram_summary(results), silent=True)
    console.print("\n[cyan]Sending notification to Telegram...[/]")
    
    console.print("\n[cyan]Logs & Summary updated (Sheets + local file).")
    input("\nENTER to return...")

def hacking_loading(message="Initializing engine", duration=2.0):
    frames = ["[=     ]", "[==    ]", "[===   ]", "[====  ]", "[===== ]", "[======]"]
    start = time.time()
    idx = 0
    while time.time() - start < duration:
        frame = frames[idx % len(frames)]
        print(f"\r{message} {frame}", end="", flush=True)
        time.sleep(0.12)
        idx += 1
    print("\r" + " " * (len(message) + 10), end="\r")

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
            f"🔗 {e.get('URL')}",
            f"⚡ Latency : {e.get('Latency')}",
            f"🔐 SSL : {e.get('SSL Status')}",
            f"📌 Status : {e.get('Status')}",
            "━━━━━━━━━━━━━\n"
        ]
    lines.append(f"📝 Logs updated to Google Sheets (Logs & Summary)")
    lines.append(f"⏰ Created_at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("🔗 Powered by WEB-MON BNPB")
    return "\n".join(lines)

def run_live():
    try:
        while True:
            banner()
            console.print("[bold green]=========LIVE SCAN WEBSITE MONITORING (LOOP @60seconds)=========[/]")
            console.print("[bold gray]SCAN ON PROGRESS.... (CTRL+C to stop)[/]")

            urls = load_urls_from_sheet()
            if not urls:
                console.print("[red]Tidak ada URL di 'List VM' kolom B.[/]")
                time.sleep(5)
                continue

            hacking_loading("Initializing WEB-MON engine", duration=1.0)

            engine = MonitorEngine(urls) # pyright: ignore[reportArgumentType]
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(engine.run())
            loop.close()

            console.print(make_table_live(results))

            # Countdown refresh
            for remaining in range(CHECK_INTERVAL, 0, -1):
                sys.stdout.write(f"\r🔄 Refreshing in {remaining}s...")
                sys.stdout.flush()
                time.sleep(1)

            print()  # pindah baris setelah countdown

    except KeyboardInterrupt:
        console.print("\n\n[red]⛔ Live monitoring stopped by user.[/]")
        time.sleep(1)


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

# quick tests from original script
def check_telegram():
    console.print("\n[bold cyan]==>  Testing Telegram Notification...[/]")
    return send_telegram_text("✺◟(＾∇＾)◞✺ — Telegram notification working.")

def check_spreadsheet():
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
    

# utility to clear screen
def clear():
    os.system("cls" if os.name == "nt" else "clear")
    console.clear()    
    

#---------------- MENU ----------------
def menu():
    while True:
        banner()
        console.print("[cyan][1][/cyan] Run Scan Once & Export Logs")
        console.print("[cyan][2][/cyan] Live Monitoring (Loop)")
        console.print("[cyan][3][/cyan] Telegram Notification Test")
        console.print("[cyan][4][/cyan] Run Diagnostics (Spreadsheet + Telegram Test)")
        console.print("[cyan][5][/cyan] Run Automatic Scheduler (Daily)")
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
            check_telegram()
            input("\nPress ENTER to return...")

        elif choice == "4":
            run_diagnostics()
            
        elif choice == "5":
            auto_scheduler()

        elif choice == "0":
            clear()      # <<< clear screen
            console.print("[green]Goodbye, Salam Tangguh, Tangguh, Tangguh !!![/]")
            time.sleep(1)
            break

        else:
            console.print("[red]Invalid option! Try again...[/]")
            time.sleep(1.3)


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        console.print("\n[red]⛔ Program stopped by user.[/]")
        time.sleep(1)
