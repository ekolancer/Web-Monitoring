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
from core.security_checker import run_security_check
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

# init google sheet client (used only for reading list)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("env/credentials.json", scopes=SCOPES)
gclient = gspread.authorize(creds)
spreadsheet = gclient.open(SPREADSHEET_NAME)
list_tab = spreadsheet.worksheet(LIST_TAB_NAME)
try:
    security_summary_sheet = spreadsheet.worksheet("Security Summary")
except gspread.WorksheetNotFound:
    security_summary_sheet = spreadsheet.add_worksheet(
        title="Security Summary",
        rows=1000,
        cols=10
    )
    
# Sheet DETAIL Security Check
try:
    security_sheet = spreadsheet.worksheet("Security Check")
except gspread.WorksheetNotFound:
    security_sheet = spreadsheet.add_worksheet(
        title="Security Check",
        rows=2000,
        cols=10
    )

# security sheet
def load_urls_from_sheet():
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


#---------------- RUN ONCE SCAN ----------------
def run_once():
    banner()
    console.print("[bold green]SCAN ON PROGRESS....[/]")

    urls = load_urls_from_sheet()
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

    save_logs_gsheet(results)
    update_summary(results)
    apply_formatting()

    local_file = write_local_log(results)
    console.print(f"\n[cyan]Local log saved to:[/] [bold]{local_file}[/]")
    console.print("\n[cyan]Logs & Summary updated (Sheets + local file).[/]")

    send_telegram_text(build_telegram_summary(results), silent=True)
    console.print("\n[cyan]Telegram Notifiaction Sent Successfully.[/]")

    input("\nENTER to return...")


#---------------- Animasi Loading ----------------
def hacking_loading(message="Initializing engine", duration=5.0):
    frames = ["[=     ]", "[==         ]", "[===        ]", "[====       ]", "[=====      ]", "[======     ]", "[=======    ]", "[========   ]", "[=========  ]",
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
            console.print("[cyan]🔐 Running Security Check...[/]")

            vm_list = build_vm_list_from_urls()
            if not vm_list:
                console.print("[red]Tidak ada VM / URL untuk Security Check[/]")
                input("ENTER to return...")
                return

            # 1️⃣ JALANKAN SECURITY CHECK
            results = run_security_check(vm_list)

            # 2️⃣ TULIS DETAIL (Security Check)
            write_security_results(security_sheet, results)

            # 3️⃣ AMBIL SHEET ID DETAIL (UNTUK LINK)
            detail_sheet_id = get_sheet_id_by_title(
                sheets_api,
                spreadsheet.id,
                "Security Check"
            )

            if detail_sheet_id is None:
                console.print("[red]Sheet 'Security Check' tidak ditemukan[/]")
                input("ENTER to return...")
                return

            # 4️⃣ BANGUN SUMMARY (DENGAN LINK KE DETAIL)
            summary_rows = build_security_summary(
                results,
                spreadsheet.id,
                detail_sheet_id
            )

            # 5️⃣ AMBIL SHEET ID SUMMARY
            summary_sheet_id = get_sheet_id_by_title(
                sheets_api,
                spreadsheet.id,
                "Security Summary"
            )

            if summary_sheet_id is not None:
                # 6️⃣ RESET + HEADER SUMMARY
                prepare_security_summary_sheet(
                    sheets_api,
                    spreadsheet.id,
                    summary_sheet_id
                )

                # 7️⃣ TULIS SUMMARY
                write_security_summary(
                    security_summary_sheet,
                    summary_rows
                )

                # 8️⃣ FORMAT WARNA RISK
                apply_security_summary_formatting(
                    sheets_api,
                    spreadsheet.id,
                    summary_sheet_id
                )

            # 9️⃣ TELEGRAM ALERT (HIGH RISK SAJA)
            send_security_alert(summary_rows)

            console.print("[green]✔ Security Check + Summary completed[/]")
            input("\nENTER to return...")


        elif choice == "4":
            check_telegram()
            input("\nPress ENTER to return...")

        elif choice == "5":
            run_diagnostics()

        elif choice == "6":
            auto_scheduler()

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


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        console.print("\n[red]⛔ Program stopped by user.[/]")
        time.sleep(1)
