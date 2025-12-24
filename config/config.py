# Google credential file
GOOGLE_CREDENTIALS_FILE = "env/credentials.json"

# Konfigurasi global — update sesuai kebutuhan Anda
SPREADSHEET_NAME = "Website Monitoring"
LIST_TAB_NAME = "List VM"

TIMEOUT_MS = 1500
SSL_WARNING_DAYS = 30
SLA_WINDOW_DAYS = 7

CHECK_INTERVAL = 60
CONCURRENCY = 25   # aiohttp concurrency
THREAD_WORKERS = 10

# Telegram
BOT_TOKEN = "8497837842:AAE_NIDqV6ZoQQEQoghQpxYqjF0GQpqJAN0"   # isi jika mau
CHAT_ID = "6618166674"     # isi jika mau

# Email alerts (optional)
EMAIL_ENABLED = False
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASS = "your-app-password"
EMAIL_TO = ["admin@bnpp.go.id"]
EMAIL_FROM = "webmon@bnpp.go.id"

# Local paths
LOG_DIR = "logs"
OUTPUT_DIR = "results"


# ---------------- HEADERS ----------------
LOG_HEADERS = [
    "Timestamp",
    "URL",
    "Status",
    "HTTP",
    "Latency",
    "SSL Status",
    "SSL Days",
    "TLS Version",
    "SSL Error",      # << NEW
    "Protocol",
    "Server",
    "Cache",
    "CDN",
    "Content",
    "Alerts",
]

SUMMARY_HEADERS = [
    "Website",
    "Last Check",
    "Last Status",
    "HTTP",
    "Latency (ms)",
    "Server",
    "Avg Latency (50 scans)",
    "SLA % (7d)",
    "SSL Status",
    "SSL Expiry Days",
    "TLS",
    "Protocol",
    "SSL Error",      # << NEW (optional, tapi kamu minta ada di summary)
    "Alerts",
]