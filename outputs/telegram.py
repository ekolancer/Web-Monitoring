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
