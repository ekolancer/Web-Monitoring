"""
Notification service for WEB-MON
"""
from typing import List, Dict, Any

from config.settings import settings
from outputs.telegram import send_telegram_text
from outputs.email import send_monitoring_alert, send_security_alert
from constants import *


class NotificationService:
    def __init__(self):
        pass

    def send_telegram(self, message: str, silent: bool = False):
        """Send Telegram notification"""
        if settings.telegram.bot_token and settings.telegram.chat_id:
            return send_telegram_text(message, silent=silent)
        return False

    def send_monitoring_alert(self, results: List[Dict[str, Any]]):
        """Send monitoring alerts (email)"""
        if settings.email.enabled:
            send_monitoring_alert(results)

    def send_security_alert(self, results: List[Dict[str, Any]]):
        """Send security alerts"""
        # Send Telegram security alert
        # (Assuming there's a security alert function in telegram.py)
        try:
            from outputs.telegram import send_security_alert as send_tg_security_alert
            send_tg_security_alert(results)
        except ImportError:
            pass  # Telegram security alert not implemented

        # Send email security alert
        if settings.email.enabled:
            send_security_alert(results)

    def test_telegram(self) -> bool:
        """Test Telegram connection"""
        test_message = "✺◟(＾∇＾)◞✺ — Telegram notification working."
        return self.send_telegram(test_message)
