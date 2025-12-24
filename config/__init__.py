# Config package
from .config import (
    # Google credentials
    GOOGLE_CREDENTIALS_FILE,

    # Spreadsheet config
    SPREADSHEET_NAME,
    LIST_TAB_NAME,

    # Timing and performance
    TIMEOUT_MS,
    SSL_WARNING_DAYS,
    SLA_WINDOW_DAYS,
    CHECK_INTERVAL,
    CONCURRENCY,
    THREAD_WORKERS,

    # Telegram
    BOT_TOKEN,
    CHAT_ID,

    # Email
    EMAIL_ENABLED,
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_USER,
    EMAIL_PASS,
    EMAIL_TO,
    EMAIL_FROM,

    # Local paths
    LOG_DIR,
    OUTPUT_DIR,

    # Headers
    LOG_HEADERS,
    SUMMARY_HEADERS,
)
