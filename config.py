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

# Google credential file
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# Local paths
LOG_DIR = "logs"
OUTPUT_DIR = "output"


# ---------------- HEADERS ----------------
LOG_HEADERS = [
    "Timestamp", "URL", "Status", "HTTP", "Latency",
    "SSL Status", "SSL Days", "TLS Version", "SSL Error",
    "Protocol", "Server", "Cache", "CDN", "Content", "Alerts"
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
    "SSL Error",
    "Protocol",
    "Alerts",
]