"""
Command implementations for WEB-MON CLI
"""
import asyncio
import time
import sys
import os
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from core.engine import MonitorEngine
from core.security_checker import run_security_check_async
from services.monitoring_service import MonitoringService
from services.notification_service import NotificationService
from ui.banner import banner
from ui.table_view import make_table_live
from outputs.sheets import init_sheets
from outputs.sheets_security import write_security_results
from outputs.sheets_security_summary import (
    build_security_summary,
    write_security_summary,
    apply_security_summary_formatting,
    prepare_security_summary_sheet
)
from config.settings import settings
from utils.logger import setup_logger
from constants import *


class Commands:
    def __init__(self):
        self.console = Console()
        self.logger = setup_logger()
        self.monitoring_service = MonitoringService()
        self.notification_service = NotificationService()

    def run_once(self):
        """Run one-time monitoring scan"""
        banner()
        self.console.print("[cyan]🖥️  Running Monitoring Check....[/]")

        urls = self.monitoring_service.load_urls_from_sheet()
        self.console.print(f"[cyan]Found {len(urls)} domains to check[/]")

        if not urls:
            self.console.print("[red]Tidak ada URL di 'List VM' kolom B.[/]")
            input("ENTER to return...")
            return

        engine = MonitorEngine(urls)
        total = len(urls)

        # Progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=self.console,
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

        self.console.print("\n[bold green]✔ Scan completed![/]\n")

        # Save results
        self.monitoring_service.save_scan_results(results)

        # Send notifications
        telegram_summary = self.monitoring_service.build_telegram_summary(results)
        self.notification_service.send_telegram(telegram_summary, silent=True)

        self.console.print("\n[green]🚀 Telegram notification sent successfully.[/]")
        input("\nENTER to return...")

    def run_live(self):
        """Run live monitoring"""
        try:
            while True:
                banner()
                self.console.print("[bold green]========= LIVE SCAN WEBSITE MONITORING =========[/]")
                self.console.print("[bold gray]SCAN ON PROGRESS.... (CTRL+C to stop)[/]\n")

                urls = self.monitoring_service.load_urls_from_sheet()
                if not urls:
                    self.console.print("[red]Tidak ada URL di 'List VM' kolom B.[/]")
                    time.sleep(5)
                    continue

                engine = MonitorEngine(urls)
                total = len(urls)

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[cyan]{task.description}"),
                    BarColumn(),
                    TextColumn("{task.completed}/{task.total}"),
                    TimeElapsedColumn(),
                    console=self.console,
                    expand=True
                ) as progress:
                    task = progress.add_task("Live scanning...", total=total)

                    def on_update(res):
                        progress.update(task, advance=1)

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        results = loop.run_until_complete(engine.run(progress_callback=on_update))
                    finally:
                        loop.close()

                self.console.print("\n[bold green]✔ Live scan finished! Displaying results...[/]\n")
                self.console.print(make_table_live(results))

                # Countdown
                self.console.print("")
                for remaining in range(settings.check_interval, 0, -1):
                    sys.stdout.write(f"\r🔄 Refreshing in {remaining}s...")
                    sys.stdout.flush()
                    time.sleep(1)
                print("\n")

        except KeyboardInterrupt:
            self.console.print("\n\n[red]⛔ Live monitoring stopped by user.[/]")
            time.sleep(1)

    def run_security(self):
        """Run security check"""
        banner()
        self.console.print("[cyan]🔐 Running Security Check...[/]")

        vm_list = self.monitoring_service.build_vm_list_from_urls()
        self.console.print(f"[cyan]Found {len(vm_list)} domains to check[/]")

        if not vm_list:
            self.console.print("[red]Tidak ada VM / URL untuk Security Check[/]")
            input("ENTER to return...")
            return

        total = len(vm_list)

        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=self.console,
            expand=True
        ) as progress:
            task = progress.add_task("Security scanning...", total=total)

            def on_update(_):
                progress.update(task, advance=1)

            results = asyncio.run(run_security_check_async(
                vm_list,
                progress_callback=on_update
            ))

        self.console.print("\n[bold green]✔ Security Scan completed![/]\n")

        # Save security results
        self.monitoring_service.save_security_results(results)

        # Send security notifications
        self.notification_service.send_security_alert(results)

        self.console.print("[green]✅ Security Check + Summary completed[/]")
        input("\nENTER to return...")

    def check_telegram(self):
        """Test Telegram notification"""
        self.console.print("\n[bold cyan]==>  Testing Telegram Notification...[/]")
        success = self.notification_service.test_telegram()
        if success:
            self.console.print("[bold green]==>  Telegram working![/]")
        else:
            self.console.print("[bold red]==>  Telegram failed![/]")

    def check_spreadsheet(self):
        """Test Google Sheets connection"""
        success = self.monitoring_service.test_spreadsheet_connection()
        if success:
            self.console.print("[bold green]==>  Spreadsheet working![/]")
        else:
            self.console.print("[bold red]==>  Spreadsheet failed![/]")
        return success

    def run_diagnostics(self):
        """Run diagnostics"""
        banner()
        self.console.print("[bold yellow]CONFIG CHECK & DIAGNOSTICS[/]")
        self.console.print("\n─────────────────────────────────────────")
        self.console.print("=> RESULT:")

        ok_tg = self.notification_service.test_telegram()
        ok_sheet = self.check_spreadsheet()

        if ok_sheet and ok_tg:
            self.console.print("[bold green]==>  All configurations working! You are ready to run monitoring. √√√[/]")
        else:
            self.console.print("[bold red]==>  Some configuration failed. Fix before running scans.[/]")

        input("\nPress ENTER to return...")

    def start_web_dashboard(self):
        """Start web dashboard"""
        self.console.print("[cyan]🚀 Starting Web Dashboard...[/]")
        self.console.print("[cyan]Dashboard will be available at: http://localhost:5000[/]")
        self.console.print("[yellow]Press Ctrl+C to stop the dashboard[/]")

        try:
            from web.app import app
            app.run(host='0.0.0.0', port=5000, debug=False)
        except ImportError:
            self.console.print("[red]❌ Flask not installed. Run: pip install flask flask-cors plotly pandas sqlalchemy[/]")
            input("Press ENTER to return...")
        except Exception as e:
            self.console.print(f"[red]❌ Error starting dashboard: {e}[/]")
            input("Press ENTER to return...")

    def edit_telegram_config(self):
        """Edit Telegram configuration"""
        self.console.print("[cyan]📱 Telegram Configuration[/]")
        self.console.print(f"Current BOT_TOKEN: {settings.telegram.bot_token[:10]}..." if settings.telegram.bot_token else "Not set")
        self.console.print(f"Current CHAT_ID: {settings.telegram.chat_id}" if settings.telegram.chat_id else "Not set")

        new_token = input("Enter new BOT_TOKEN (leave empty to keep current): ").strip()
        if new_token:
            self.console.print("[yellow]Note: Config file needs to be manually updated for persistence[/]")

        new_chat = input("Enter new CHAT_ID (leave empty to keep current): ").strip()
        if new_chat:
            self.console.print("[yellow]Note: Config file needs to be manually updated for persistence[/]")

        self.console.print("[green]Telegram config updated![/]")
        input("Press ENTER to continue...")

    def edit_email_config(self):
        """Edit email configuration"""
        self.console.print("[cyan]📧 Email Configuration[/]")
        self.console.print(f"Email Enabled: {settings.email.enabled}")
        self.console.print(f"SMTP Server: {settings.email.smtp_server}")
        self.console.print(f"Email User: {settings.email.user}")

        enable = input("Enable email alerts? (y/n): ").strip().lower()
        if enable == 'y':
            self.console.print("[yellow]Note: Update config.py with your email credentials[/]")

        self.console.print("[green]Email config updated![/]")
        input("Press ENTER to continue...")

    def edit_monitoring_config(self):
        """Edit monitoring configuration"""
        self.console.print("[cyan]🔍 Monitoring Configuration[/]")
        self.console.print(f"Check Interval: {settings.check_interval} seconds")
        self.console.print(f"Timeout: {settings.timeout_ms} ms")
        self.console.print(f"Concurrency: {settings.concurrency}")

        self.console.print("[yellow]Edit config.py directly for these settings[/]")
        input("Press ENTER to continue...")

    def edit_sheets_config(self):
        """Edit Google Sheets configuration"""
        self.console.print("[cyan]📊 Google Sheets Configuration[/]")
        self.console.print(f"Spreadsheet Name: {settings.google_sheets.spreadsheet_name}")
        self.console.print(f"List Tab Name: {settings.google_sheets.list_tab_name}")

        self.console.print("[yellow]Edit config.py directly for these settings[/]")
        input("Press ENTER to continue...")
