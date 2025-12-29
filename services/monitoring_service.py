"""
Monitoring service for WEB-MON
"""
import time
from typing import List, Dict, Any

from config.settings import settings
from outputs.local_log import write_local_log
from outputs.sheets import save_logs_gsheet, apply_formatting, update_summary_gsheet as update_summary
from outputs.sheets_security import write_security_results
from outputs.sheets_security_summary import (
    build_security_summary,
    write_security_summary,
    apply_security_summary_formatting,
    prepare_security_summary_sheet
)
from outputs.sheets import init_sheets
from utils.logger import setup_logger
from constants import *


class MonitoringService:
    def __init__(self):
        self.logger = setup_logger()
        self.spreadsheet, self.sheets_api = init_sheets()
        self.gclient = None
        self.list_tab = None
        self.security_summary_sheet = None
        self.security_sheet = None

    def init_google_sheets(self):
        """Initialize Google Sheets connection lazily"""
        if self.spreadsheet is not None:
            return  # Already initialized

        try:
            # init google sheet client (used only for reading list)
            SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file("env/credentials.json", scopes=SCOPES)
            self.gclient = gspread.authorize(creds)
            self.spreadsheet = self.gclient.open(settings.google_sheets.spreadsheet_name)
            self.list_tab = self.spreadsheet.worksheet(settings.google_sheets.list_tab_name)

            # Initialize sheets API
            self.sheets_api = build('sheets', 'v4', credentials=creds)

            try:
                self.security_summary_sheet = self.spreadsheet.worksheet("Security Summary")
            except gspread.WorksheetNotFound:
                self.security_summary_sheet = self.spreadsheet.add_worksheet(
                    title="Security Summary",
                    rows=1000,
                    cols=10
                )

            try:
                self.security_sheet = self.spreadsheet.worksheet("Security Logs")
            except gspread.WorksheetNotFound:
                self.security_sheet = self.spreadsheet.add_worksheet(
                    title="Security Logs",
                    rows=2000,
                    cols=10
                )

        except Exception as e:
            self.logger.error(f"Google Sheets initialization failed: {e}")

    def load_urls_from_sheet(self) -> List[str]:
        """Load URLs from Google Sheets"""
        self.init_google_sheets()
        try:
            return self.list_tab.col_values(2)[1:]  # Skip header
        except Exception as e:
            self.logger.error(f"Failed load URLs: {e}")
            return []

    def build_vm_list_from_urls(self) -> List[Dict[str, str]]:
        """
        Build VM list from URLs in sheet
        """
        self.init_google_sheets()
        try:
            rows = self.list_tab.get_all_values()
        except Exception as e:
            self.logger.error(f"Failed to read List VM: {e}")
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
                "domain": domain
            })

        return vm_list

    def save_scan_results(self, results: List[Dict[str, Any]]):
        """Save monitoring scan results"""
        self.init_google_sheets()
        save_logs_gsheet(results)
        update_summary(results)
        apply_formatting()

        local_file = write_local_log(results)
        return local_file

    def save_security_results(self, results: List[Dict[str, Any]]):
        """Save security scan results"""
        self.init_google_sheets()

        write_security_results(self.security_sheet, results)

        detail_sheet_id = self._get_sheet_id_by_title("Security Logs")
        if detail_sheet_id is None:
            return

        summary_rows = build_security_summary(
            results,
            self.spreadsheet.id,
            detail_sheet_id
        )

        summary_sheet_id = self._get_sheet_id_by_title("Security Summary")
        if summary_sheet_id is not None:
            prepare_security_summary_sheet(
                self.sheets_api,
                self.spreadsheet.id,
                summary_sheet_id
            )

        write_security_summary(
            self.security_summary_sheet,
            summary_rows
        )

        apply_security_summary_formatting(
            self.sheets_api,
            self.spreadsheet.id,
            summary_sheet_id
        )

    def build_telegram_summary(self, results: List[Dict[str, Any]]) -> str:
        """Build telegram summary message"""
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

    def test_spreadsheet_connection(self) -> bool:
        """Test Google Sheets connection"""
        self.init_google_sheets()
        try:
            urls = self.list_tab.col_values(2)
            return bool(urls)
        except Exception as e:
            self.logger.error(f"Spreadsheet test failed: {e}")
            return False

    def _get_sheet_id_by_title(self, title: str) -> int | None:
        """
        Get sheet ID by title
        """
        meta = self.sheets_api.spreadsheets().get(
            spreadsheetId=self.spreadsheet.id
        ).execute()

        for sheet in meta.get("sheets", []):
            props = sheet.get("properties", {})
            if props.get("title") == title:
                return props.get("sheetId")

        return None
