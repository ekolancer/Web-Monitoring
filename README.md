# 🛰️ **WEB-MON BNPB — Web Monitoring Tool**

WEB-MON BNPB adalah aplikasi monitoring website yang dikembangkan untuk mendukung kebutuhan operasional **Badan Nasional Penanggulangan Bencana (BNPB)** dalam memantau ketersediaan layanan, kesehatan sistem, kinerja web, dan keamanan SSL seluruh aplikasi dan subdomain BNPB.

Aplikasi ini bersifat modular, mudah dikembangkan, serta terintegrasi dengan Google Sheets dan Telegram untuk pelaporan otomatis.

---

## ✨ **Fitur Utama**

### 🟢 **1. Monitoring Website**
- Mengecek status HTTP (200, 500, 404, dll.)
- Memeriksa kecepatan respon (latency)
- Melakukan validasi konten (content inspection)

### 🔐 **2. Monitoring SSL**
- Menampilkan status validitas SSL
- Menghitung sisa masa berlaku (days-to-expire)
- Menganalisis versi TLS
- Mendeteksi error SSL (HANDSHAKE_FAIL, INVALID_CERT, dsb.)

### 📡 **3. Notifikasi Telegram**
- Mengirim ringkasan hasil scan
- Mengirim alert jika ditemukan error, status buruk, atau perubahan penting
- Dapat diaktifkan/diuji melalui menu

### 📑 **4. Integrasi Google Sheets**
- Semua hasil scan disimpan pada tab **Logs**
- Ringkasan otomatis dihasilkan pada tab **Summary**
- Dilengkapi format otomatis & emoji indikator status

### 🧠 **5. Mode Live Monitoring**
- Menjalankan scan terus-menerus dengan interval tertentu
- Dilengkapi tabel real-time dan penghitung waktu refresh

### 🗂️ **6. Modular Architecture**
- Struktur kode rapi dan mudah dijaga
- Setiap fungsi berada di modul terpisah (**core**, **outputs**, **ui**, **utils**)

### 📆 **7. Automatic Scheduler**
- Scan otomatis pada waktu terjadwal (contoh: 08:00 & 21:03)
- Cocok untuk monitoring harian

### 💾 **8. Local Logging**
- Semua hasil tersimpan juga dalam file `.json` di folder `results/`

---

## 📦 **Instalasi**

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Tambahkan Kredensial Google
- Letakkan `credentials.json` di root folder project
- Pastikan service account memiliki akses ke Google Sheets terkait

### 3. Konfigurasi
Edit file `config.py` untuk mengatur:
- Token & chat ID Telegram
- Nama Google Sheets & nama tab
- Timeout scanning & concurrency
- Jadwal monitoring otomatis

---

## ▶️ **Cara Menjalankan Aplikasi**
```bash
python main.py
```

---

## 📋 **Menu Aplikasi**

| Menu | Fungsi |
|------|--------|
| **1. Run Scan Once & Export Logs** | Menjalankan scan satu kali & ekspor log |
| **2. Live Monitoring (Loop)** | Scan terus-menerus dengan interval |
| **3. Telegram Notification Test** | Menguji koneksi & notifikasi Telegram |
| **4. Run Diagnostics** | Mengecek Google Sheets + Telegram |
| **5. Run Automatic Scheduler (Daily)** | Menjalankan scan otomatis harian |
| **0. Exit** | Keluar aplikasi |

---

## ⚙️ **Konfigurasi Penting**

- `SPREADSHEET_NAME` → Nama Google Sheets
- `LIST_TAB_NAME` → Tab berisi daftar URL
- `CHECK_INTERVAL` → Interval Live Monitoring
- `TIMEOUT_MS` → Batas waktu request
- `SSL_WARNING_DAYS` → Batas peringatan SSL
- `CONCURRENCY` → Jumlah worker scanning
- `BOT_TOKEN` & `CHAT_ID` → Telegram bot config

---

## 📂 **Struktur Project**

```
webmon/
├── config.py
├── credentials.json
├── main.py
├── README.md
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
│   └── *.json
│
└── logs/
    └── webmon.log
```

---

## 📤 **Output Monitoring**

### 🧾 Google Sheets
- **Logs**: data mentah tiap scan
- **Summary**: status terbaru per website + SLA + latency rata-rata + SSL info

### 📨 Telegram
- Ringkasan hasil scan
- Alert jika error, SSL bermasalah, atau status tidak sehat

### 💾 Local JSON
- Backup log untuk kebutuhan audit

---

## 🛡️ **Keamanan & Privasi**

- Berjalan lokal, tidak mengirimkan data selain ke Google Sheets internal
- Telegram hanya untuk notifikasi internal BNPB
- Tidak menyimpan data sensitif website

---

> _Salam Tangguh, Tangguh, Tangguh!_ 💪💪💪
