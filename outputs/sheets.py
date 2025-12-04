# outputs/sheets.py
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread
from datetime import datetime, timedelta
from config import (
    GOOGLE_CREDENTIALS_FILE,
    SPREADSHEET_NAME,
    LOG_HEADERS,
    SUMMARY_HEADERS,
    SLA_WINDOW_DAYS,
)

# ----------------------------------------
# INIT GOOGLE SHEETS CLIENT (MODULAR)
# ----------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def init_sheets():
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    g = gspread.authorize(creds)
    sheet = g.open(SPREADSHEET_NAME)
    api = build("sheets", "v4", credentials=creds)
    return sheet, api

spreadsheet, sheets_api = init_sheets()


# ----------------------------------------
# SHEET UTILITIES
# ----------------------------------------

def sheet_get_or_create(spreadsheet, name, header):
    """Create sheet if missing + ensure correct header."""
    try:
        ws = spreadsheet.worksheet(name)
    except Exception:
        ws = spreadsheet.add_worksheet(name, rows=1000, cols=len(header))
        ws.append_row(header)
        return ws

    # Pastikan header benar
    if ws.row_values(1) != header:
        ws.clear()
        ws.append_row(header)

    return ws


# ----------------------------------------
# SAVE LOGS TO GOOGLE SHEETS
# ----------------------------------------

def save_logs_gsheet(results: list):
    """Save scan results to Logs sheet."""
    ws = sheet_get_or_create(spreadsheet, "Logs", LOG_HEADERS)

    # Convert dict results → row list
    rows = [[r.get(h, "") for h in LOG_HEADERS] for r in results]

    ws.append_rows(rows)


# ----------------------------------------
# UPDATE SUMMARY TAB
# ----------------------------------------

def update_summary_gsheet(results: list):
    ws_logs = sheet_get_or_create(spreadsheet, "Logs", LOG_HEADERS)
    ws_sum = sheet_get_or_create(spreadsheet, "Summary", SUMMARY_HEADERS)

    # Ambil semua histori logs
    logs = ws_logs.get_all_records(expected_headers=LOG_HEADERS)

    grouped = {}
    for row in logs:
        grouped.setdefault(row["URL"], []).append(row)

    # Hapus baris lama
    ws_sum.batch_clear(["A2:Z9999"])

    final_rows = []
    now = datetime.now()
    window_cutoff = now - timedelta(days=SLA_WINDOW_DAYS)

    for url, entries in grouped.items():

        # Sort berdasarkan timestamp
        entries.sort(key=lambda x: x["Timestamp"])
        last = entries[-1]  # last scan

        # ---------------------------------------
        # 1) AVG LATENCY (last 50 entries)
        # ---------------------------------------
        latencies = [
            e["Latency"] for e in entries
            if isinstance(e["Latency"], (int, float))
        ]

        avg_latency = (
            round(sum(latencies[-50:]) / len(latencies[-50:]), 2)
            if latencies else "-"
        )

        # ---------------------------------------
        # 2) SLA: HTTP == 200 dalam 7 hari terakhir
        # ---------------------------------------
        def to_dt(ts):
            try:
                return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except:
                return now

        last7 = [e for e in entries if to_dt(e["Timestamp"]) >= window_cutoff]

        if last7:
            http_ok = sum(1 for e in last7 if str(e.get("HTTP")) == "200")
            total = len(last7)
            sla_val = round((http_ok / total) * 100, 2)
            sla_str = f"{sla_val}%"
        else:
            sla_str = "-"

        # ---------------------------------------
        # 3) SSL EXPIRY DAYS (ambil data TERAKHIR)
        # ---------------------------------------
        ssl_days_final = (
            last["SSL Days"]
            if isinstance(last.get("SSL Days"), int)
            else "-"
        )

        # ---------------------------------------
        # 4) Row ke Summary (disesuaikan HEADER)
        # ---------------------------------------
        final_rows.append([
            url,
            last["Timestamp"],
            last["Status"],
            last["HTTP"],
            last["Latency"],
            last["Server"],
            avg_latency,
            sla_str,
            last["SSL Status"],
            ssl_days_final,       # FIX → tidak lagi True/False
            last["TLS Version"],
            last["Protocol"],
            last["Alerts"],
            last.get("SSL Error", "-"),
        ])

    if final_rows:
        ws_sum.append_rows(final_rows)

    # Auto-resize kolom
    sheets_api.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet.id,
        body={
            "requests": [{
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": ws_sum.id,
                        "dimension": "COLUMNS"
                    }
                }
            }]
        }
    )


def apply_formatting():
    """Insert emoji indicators into key Summary fields."""
    ws = sheet_get_or_create(spreadsheet, "Summary", SUMMARY_HEADERS)
    data = ws.get_all_values()

    header = data[0]
    updated_rows = []

    # Column mapping
    col_status = header.index("Last Status")
    col_sla = header.index("SLA % (7d)")
    col_ssl = header.index("SSL Expiry Days")
    col_alert = header.index("Alerts")

    for row in data[1:]:  # skip header
        if not row or all(c == "" for c in row):
            continue

        # ---- Last Status
        status = row[col_status].upper()
        if "HEALTHY" in status:
            row[col_status] = f"🤩   {status}"
        elif "SLOW" in status or "PARTIAL" in status:
            row[col_status] = f"🥺   {status}"
        else:
            row[col_status] = f"😭  {status}"

        # ---- SLA Rating
        try:
            sla_value = float(row[col_sla].replace('%', ''))
        except:
            sla_value = None

        if sla_value is not None:
            if sla_value >= 95:
                row[col_sla] = f"⚡   {row[col_sla]}"
            elif sla_value >= 80:
                row[col_sla] = f"🐌   {row[col_sla]}"
            else:
                row[col_sla] = f"⛔   {row[col_sla]}"

        # ---- SSL Expiry Days
        try:
            ssl_days = int(row[col_ssl])
        except:
            ssl_days = None

        if ssl_days is not None:
            if ssl_days > 30:
                row[col_ssl] = f"🟢   {ssl_days}"
            elif ssl_days >= 7:
                row[col_ssl] = f"🟡   {ssl_days}"
            else:
                row[col_ssl] = f"🔴   {ssl_days}"

        # ---- Alerts
        alert = row[col_alert]
        if alert.strip() == "-" or alert.strip() == "":
            row[col_alert] = "🆗"
        elif "WARNING" in alert:
            row[col_alert] = f"⚠️ {alert}"
        else:
            row[col_alert] = f"🚨 {alert}"

        updated_rows.append(row)

    # Write back to sheet
    #ws.update(f"A2:{chr(65+len(header))}{len(updated_rows)+1}", updated_rows)
    ws.update(
    updated_rows, 
    range_name=f"A2:{chr(65+len(header))}{len(updated_rows)+1}"
    )