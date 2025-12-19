import requests
from config import BOT_TOKEN, CHAT_ID
from utils.logger import setup_logger
from rich.console import Console

console = Console()
logger = setup_logger()

def send_telegram_text(text: str, silent: bool = False):
    """
    Kirim pesan Telegram.
    - Jika silent=True → tidak print apa pun ke console.
    - Logger tetap mencatat (tanpa emoji).
    """

    if not BOT_TOKEN or not CHAT_ID:
        if not silent:
            console.print("[yellow]⚠ Telegram not configured. Skipping...[/]")
        logger.info("Telegram not configured; skipping send.")
        return False

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )

        if r.status_code == 200:
            if not silent:
                console.print("[green]✔ Telegram message sent successfully.[/]")
            logger.info("Telegram message sent successfully.")
            return True
        
        else:
            if not silent:
                console.print(f"[red]❌ Telegram API returned HTTP {r.status_code}[/]")
            logger.warning(f"Telegram API returned HTTP {r.status_code}")
            return False

    except Exception as e:
        if not silent:
            console.print(f"[red]❌ Telegram send FAILED:[/] {e}")
        logger.error(f"Telegram send failed: {e}")
        return False


def send_security_alert(summary_rows: list):
    """
    Kirim Telegram alert hanya untuk HIGH risk
    (AMAN: tanpa formula Sheets)
    """
    high_risk = []

    for r in summary_rows:
        if len(r) < 8:
            continue
        if r[6] == "HIGH":
            high_risk.append(r)

    if not high_risk:
        return False

    lines = [
        "🚨 SECURITY ALERT — HIGH RISK DETECTED",
        ""
    ]

    for r in high_risk:
        domain_cell = r[1]

        # ⬅️ STRIP FORMULA HYPERLINK → AMBIL DOMAIN SAJA
        if isinstance(domain_cell, str) and domain_cell.startswith('=HYPERLINK'):
            # ambil teks setelah koma terakhir
            domain = domain_cell.split('","')[-1].rstrip('")')
        else:
            domain = str(domain_cell)

        notes = r[7] if r[7] else "-"

        lines.append(f"🌐 {domain}")
        lines.append(f"⚠️ {notes}")
        lines.append("")

    message = "\n".join(lines)

    # 🔐 Telegram SAFE payload
    return send_telegram_text(message)
