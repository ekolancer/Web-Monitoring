from collections import defaultdict
from datetime import datetime

def build_security_summary(results: list) -> list:
    summary = defaultdict(lambda: {
        "headers": "OK",
        "methods": "OK",
        "files": "OK",
        "ports": "OK",
        "notes": []   # ⬅️ HARUS LIST
    })

    for r in results:
        vm = r["vm_name"]
        check = r["check_type"]
        status = r["status"]

        if check == "Security Headers":
            summary[vm]["headers"] = status
        elif check == "HTTP Methods":
            summary[vm]["methods"] = status
        elif check == "Sensitive Files":
            summary[vm]["files"] = status
        elif check == "Open Ports":
            summary[vm]["ports"] = status

        if status in ("WARN", "FAIL", "CRITICAL"):
            notes = summary[vm]["notes"]
            if isinstance(notes, list):
                notes.append(f"{check}: {status}")


    rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for vm, data in summary.items():
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
            vm,
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
