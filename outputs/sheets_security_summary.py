from collections import defaultdict
from datetime import datetime

def build_security_summary(results: list) -> list:
    summary = defaultdict(lambda: {
        "headers": "OK",
        "methods": "OK",
        "files": "OK",
        "ports": "OK",
        "notes": []
    })

    for r in results:
        domain = r.get("domain")   # ⬅️ PAKAI DOMAIN
        if not domain:
            continue

        check = r["check_type"]
        status = r["status"]

        if check == "Security Headers":
            summary[domain]["headers"] = status
        elif check == "HTTP Methods":
            summary[domain]["methods"] = status
        elif check == "Sensitive Files":
            summary[domain]["files"] = status
        elif check == "Open Ports":
            summary[domain]["ports"] = status

        if status in ("WARN", "FAIL", "CRITICAL"):
            summary[domain]["notes"].append(f"{check}: {status}")

    rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for domain, data in summary.items():
        severities = [
            data["headers"],
            data["methods"],
            data["files"],
            data["ports"],
        ]

        if "CRITICAL" in severities or "FAIL" in severities:
            risk = "HIGH"
        elif severities.count("WARN") >= 1:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        rows.append([
            timestamp,
            domain,   # ⬅️ DOMAIN TAMPIL DI SUMMARY
            data["headers"],
            data["methods"],
            data["files"],
            data["ports"],
            risk,
            "; ".join(data["notes"]) if data["notes"] else "-"
        ])

    return rows


def write_security_summary(sheet, rows: list):
    sheet.append_rows(rows, value_input_option="USER_ENTERED")


def apply_security_summary_formatting(sheets_api, spreadsheet_id, sheet_id):
    requests = [
        # HEADER BOLD
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True}
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold"
            }
        },
        # RISK LEVEL COLOR
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "HIGH"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1, "green": 0.6, "blue": 0.6}
                        }
                    }
                },
                "index": 0
            }
        },
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "MEDIUM"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1, "green": 1, "blue": 0.6}
                        }
                    }
                },
                "index": 1
            }
        },
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "LOW"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 0.8, "green": 1, "blue": 0.8}
                        }
                    }
                },
                "index": 2
            }
        }
    ]

    sheets_api.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()

def prepare_security_summary_sheet(
    sheets_api,
    spreadsheet_id: str,
    sheet_id: int
) -> None:
    """
    Bersihkan sheet, set header, freeze row, dan UX formatting dasar
    (TIDAK mengatur lebar kolom)
    """

    requests = [
        # CLEAR SHEET CONTENT
        {
            "updateCells": {
                "range": {
                    "sheetId": sheet_id
                },
                "fields": "userEnteredValue"
            }
        },

        # SET HEADER
        {
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1
                },
                "rows": [{
                    "values": [
                        {"userEnteredValue": {"stringValue": "Timestamp"}},
                        {"userEnteredValue": {"stringValue": "Domain"}},
                        {"userEnteredValue": {"stringValue": "Security Headers"}},
                        {"userEnteredValue": {"stringValue": "HTTP Methods"}},
                        {"userEnteredValue": {"stringValue": "Sensitive Files"}},
                        {"userEnteredValue": {"stringValue": "Open Ports"}},
                        {"userEnteredValue": {"stringValue": "Risk Level"}},
                        {"userEnteredValue": {"stringValue": "Notes"}},
                    ]
                }],
                "fields": "userEnteredValue"
            }
        },

        # FREEZE HEADER
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        },

        # HEADER STYLE
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.9,
                            "green": 0.9,
                            "blue": 0.9
                        },
                        "horizontalAlignment": "CENTER",
                        "textFormat": {
                            "bold": True
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        }
    ]

    sheets_api.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()

