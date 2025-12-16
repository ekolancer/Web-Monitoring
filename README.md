
# 🛰️ WEB-MON — Web Monitoring Toolkit (BNPB Edition)

[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)]()
[![License](https://img.shields.io/badge/License-MIT-orange)]()
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)]()

```
██╗    ██╗███████╗██████╗ ███╗   ███╗ ██████╗ ███╗   ██╗
██║    ██║██╔════╝██╔══██╗████╗ ████║██╔═══██╗████╗  ██║
██║ █╗ ██║█████╗  ██████╔╝██╔████╔██║██║   ██║██╔██╗ ██║
██║███╗██║██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║██║╚██╗██║
╚███╔███╔╝███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
 ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

---

## 📌 **Apa itu WEB-MON?**

**WEB-MON** adalah toolkit monitoring website yang modular dan ringan, mendukung:
- Monitoring uptime
- HTTP response time check
- SSL certificate checking (validity & expiry)
- Notifikasi Telegram otomatis
- Integrasi dengan Google Spreadsheet
- Monitoring loop otomatis
- Arsitektur modular untuk pengembangan lanjutan

---

# 📁 **Struktur Proyek**

```
webmon/
├── config.py
├── credentials.json
├── main.py
├── requirements.txt
│
├── core/
│   ├── engine.py
│   ├── http_checker.py
│   └── ssl_checker.py
│
├── outputs/
│   ├── sheets.py
│   ├── telegram.py
│   └── local_log.py
│
├── ui/
│   ├── banner.py
│   └── table_view.py
│
├── utils/
│   ├── logger.py
│   └── normalize.py
│
├── results/
└── logs/
```

---

# 🧩 **Arsitektur Sistem (Diagram ASCII)**

```
          +----------------------+
          |      main.py        |
          |  (User Interface)   |
          +----------+----------+
                     |
                     v
          +----------------------+
          |      engine.py       |
          |  Orchestrator Logic  |
          +----------+-----------+
                     |
     +---------------+-------------------+
     |                                   |
     v                                   v
+------------+                   +----------------+
| http_checker|                   |  ssl_checker  |
+------------+                   +----------------+
     |                                   |
     +---------------+-------------------+
                     |
                     v
          +------------------------+
          |     outputs/          |
          | Sheets / Telegram /   |
          | Local JSON Log        |
          +-----------+-----------+
                      |
                      v
          +------------------------+
          | results/ & logs/      |
          +------------------------+
```

---

# 🚀 **Cara Menjalankan**

### 1. Install dependencies  
```
pip install -r requirements.txt
```

### 2. Siapkan credentials Google Sheets  
Letakkan file:
```
webmon/credentials.json
```

### 3. Jalankan aplikasi  
```
python main.py
```

---

# 🧭 **Menu Aplikasi**

```
[1] Scan Website
[2] Monitoring Loop
[3] Lihat Log
[0] Keluar
```

---

# 🌐 **Konfigurasi Target Website**

Atur di `config.py`:

```python
TARGETS = [
    {"name": "Website BNPB", "url": "https://bnpb.go.id"},
    {"name": "Sistem Informasi", "url": "https://example.com"},
]
```

---

# 📊 **Integrasi Spreadsheet**

Hasil scan dicatat ke Google Sheet dalam format:

| Timestamp | URL | Status | Response Time | SSL Expiry | Notes |
|-----------|------|--------|----------------|-------------|--------|

---

# 📬 **Notifikasi Telegram**

Alert dikirim otomatis ketika:
- Website error / down  
- Slow response  
- SSL mendekati expiry  

---

# 🧱 **Modularitas untuk Pengembangan Lanjutan**

WEB-MON dapat diperluas dengan mudah:
- Security scanning
- DoS early-warning
- DNSSEC checking
- Defacement detection
- Dashboard monitoring (Grafana / Streamlit)

---

# 🤝 **Kontribusi**

Pull request sangat diterima.  
Silakan buat branch baru untuk fitur atau perbaikan bug.

---

# 📜 **Lisensi**
MIT License

---

# 👨‍💻 **Dikembangkan oleh**
ekolancer / BNPB Engineering Team
