from .config import *


class LoggingSettings:
    level = "INFO"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    file = f"{LOG_DIR}/webmon.log"


class TelegramSettings:
    bot_token = BOT_TOKEN
    chat_id = CHAT_ID


class EmailSettings:
    enabled = EMAIL_ENABLED
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    user = EMAIL_USER
    password = EMAIL_PASS
    to = EMAIL_TO
    from_addr = EMAIL_FROM


class GoogleSheetsSettings:
    spreadsheet_name = SPREADSHEET_NAME
    list_tab_name = LIST_TAB_NAME


class Settings:
    logging = LoggingSettings()
    telegram = TelegramSettings()
    email = EmailSettings()
    google_sheets = GoogleSheetsSettings()
    check_interval = CHECK_INTERVAL
    timeout_ms = TIMEOUT_MS
    concurrency = CONCURRENCY


settings = Settings()