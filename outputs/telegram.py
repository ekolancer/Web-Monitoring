import requests
from config import BOT_TOKEN, CHAT_ID
from utils.logger import setup_logger
from rich.console import Console

console = Console()
logger = setup_logger()

def send_telegram_text(text: str, silent: bool = False):
    """
    Kirim pesan Telegram dengan validasi dan error handling yang lebih baik.
    - Jika silent=True → tidak print apa pun ke console.
    - Logger tetap mencatat (tanpa emoji).
    """

    if not BOT_TOKEN or not CHAT_ID:
        if not silent:
            console.print("[yellow]⚠ Telegram not configured. Skipping...[/]")
        logger.info("Telegram not configured; skipping send.")
        return False

    # Validate and sanitize message
    if not text or not isinstance(text, str):
        if not silent:
            console.print("[red]❌ Invalid message content[/]")
        logger.error("Invalid message content for Telegram")
        return False

    # Telegram has a 4096 character limit per message
    if len(text) > 4000:
        text = text[:4000] + "\n\n[Message truncated due to length limit]"

    # Remove or replace problematic characters
    text = text.replace('\r', '')  # Remove carriage returns

    try:
        payload = {
            "chat_id": str(CHAT_ID).strip(),
            "text": text.strip(),
            "parse_mode": "HTML"  # Try HTML parsing for better formatting
        }

        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=payload,
            timeout=10
        )

        if r.status_code == 200:
            response_data = r.json()
            if response_data.get("ok"):
                if not silent:
                    console.print("[green]✔ Telegram message sent successfully.[/]")
                logger.info("Telegram message sent successfully.")
                return True
            else:
                error_description = response_data.get("description", "Unknown error")
                if not silent:
                    console.print(f"[red]❌ Telegram API error: {error_description}[/]")
                logger.error(f"Telegram API error: {error_description}")
                return False

        elif r.status_code == 400:
            # Bad Request - usually malformed message
            try:
                error_data = r.json()
                error_desc = error_data.get("description", "Bad Request")
            except:
                error_desc = "Malformed message"

            if not silent:
                console.print(f"[red]❌ Telegram HTTP 400 - {error_desc}[/]")
                console.print(f"[yellow]Message length: {len(text)} characters[/]")
            logger.error(f"Telegram HTTP 400: {error_desc}")
            return False

        elif r.status_code == 401:
            if not silent:
                console.print("[red]❌ Telegram unauthorized - check BOT_TOKEN[/]")
            logger.error("Telegram unauthorized - invalid bot token")
            return False

        elif r.status_code == 403:
            if not silent:
                console.print("[red]❌ Telegram forbidden - check CHAT_ID[/]")
            logger.error("Telegram forbidden - invalid chat ID")
            return False

        else:
            if not silent:
                console.print(f"[red]❌ Telegram API returned HTTP {r.status_code}[/]")
            logger.warning(f"Telegram API returned HTTP {r.status_code}")
            return False

    except requests.exceptions.Timeout:
        if not silent:
            console.print("[red]❌ Telegram request timed out[/]")
        logger.error("Telegram request timed out")
        return False

    except requests.exceptions.RequestException as e:
        if not silent:
            console.print(f"[red]❌ Telegram network error: {e}[/]")
        logger.error(f"Telegram network error: {e}")
        return False

    except Exception as e:
        if not silent:
            console.print(f"[red]❌ Telegram send FAILED: {e}[/]")
        logger.error(f"Telegram send failed: {e}")
        return False


def send_security_alert(summary_rows: list):
    """
    Kirim Telegram alert untuk security issues dengan format yang lebih aman
    """
    if not summary_rows:
        return False

    # Filter for high/critical severity issues
    high_risk = []
    for r in summary_rows:
        if isinstance(r, dict):
            severity = r.get('severity', '').lower()
            if severity in ['high', 'critical']:
                high_risk.append(r)
        elif isinstance(r, list) and len(r) >= 8:
            # Legacy format support
            if str(r[6]).upper() == "HIGH":
                high_risk.append(r)

    if not high_risk:
        logger.info("No high-risk security issues found")
        return False

    # Build message with length limits
    lines = [
        "🚨 SECURITY ALERT — HIGH RISK DETECTED",
        f"Found {len(high_risk)} critical security issues",
        ""
    ]

    for i, risk in enumerate(high_risk[:10]):  # Limit to 10 issues to avoid message too long
        if isinstance(risk, dict):
            domain = risk.get('domain', 'Unknown')
            check_type = risk.get('check_type', 'Unknown')
            detail = risk.get('detail', 'No details')
            severity = risk.get('severity', 'High')
        else:
            # Legacy format
            domain = str(risk[1]) if len(risk) > 1 else 'Unknown'
            if isinstance(domain, str) and domain.startswith('=HYPERLINK'):
                domain = domain.split('","')[-1].rstrip('")')
            check_type = 'Security Check'  # Default for legacy format
            detail = str(risk[7]) if len(risk) > 7 else 'No details'
            severity = 'High'

        lines.extend([
            f"🌐 {domain}",
            f"⚠️ {check_type}: {detail[:100]}",  # Limit detail length
            ""
        ])

    # Add footer
    lines.append("Please review security issues immediately.")
    lines.append(f"Total domains checked: {len(summary_rows)}")

    message = "\n".join(lines)

    # Ensure message is not too long
    if len(message) > 4000:
        message = message[:3950] + "\n\n[Message truncated]"

    return send_telegram_text(message)
