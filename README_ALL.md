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

### � **4. Email Alerts (Opsional)**
- Kirim alert ke email untuk issues kritis
- HTML formatted email dengan detail lengkap
- Konfigurasi SMTP untuk berbagai provider

### 🌐 **5. Web Dashboard**
- Interface web real-time untuk monitoring
- Charts uptime history
- Status table dengan auto-refresh
- Accessible via browser di `http://localhost:5000`

### 📑 **6. Integrasi Google Sheets**
- Semua hasil scan disimpan pada tab **Logs**
- Ringkasan otomatis dihasilkan pada tab **Summary**
- Security check results di tab **Security Check** dan **Security Summary**
- Dilengkapi format otomatis & emoji indikator status

### 🛡️ **7. Security Checks**
- Security Headers analysis (CSP, HSTS, X-Frame-Options, dll.)
- HTTP Methods testing (PUT, DELETE detection)
- Sensitive files scanning (.env, .git, backup.zip)
- Port scanning (common ports 21, 22, 25, 80, 443, 3306, 6379)
- Vulnerability assessment (outdated software, directory listing)

### 🧠 **8. Mode Live Monitoring**
- Menjalankan scan terus-menerus dengan interval tertentu
- Dilengkapi tabel real-time dan penghitung waktu refresh

### 🗂️ **9. Modular Architecture**
- Struktur kode rapi dan mudah dijaga
- Setiap fungsi berada di modul terpisah (**core**, **outputs**, **ui**, **utils**)

### 📆 **10. Automatic Scheduler**
- Scan otomatis pada waktu terjadwal (contoh: 08:00 & 21:03)
- Cocok untuk monitoring harian

### ⚙️ **11. Configuration Management**
- Menu interaktif untuk edit settings
- Konfigurasi Telegram, Email, Monitoring, dan Google Sheets
- Tanpa perlu edit file manual

### 💾 **12. Local Logging**
- Semua hasil tersimpan juga dalam file `.json` di folder `results/`

---

## 📦 **Instalasi & Setup**

### **Persyaratan Sistem**
- Python 3.9 atau lebih tinggi
- Google Cloud Project dengan Google Sheets API enabled
- Service Account credentials (JSON file)
- Telegram Bot Token (opsional)
- Email account untuk SMTP (opsional)

### **Langkah Instalasi**

1. **Clone Repository**
```bash
git clone <repository-url>
cd webmon
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Google Sheets API**
   - Buat Google Cloud Project
   - Enable Google Sheets API
   - Buat Service Account dan download credentials JSON
   - Share spreadsheet dengan service account email
   - Rename file JSON menjadi `credentials.json` dan letakkan di folder `env/`

4. **Konfigurasi Aplikasi**
   - Edit `config.py` untuk mengatur:
     - `SPREADSHEET_NAME`: Nama Google Spreadsheet
     - `BOT_TOKEN`: Telegram bot token
     - `CHAT_ID`: Telegram chat ID
     - `EMAIL_*`: Email settings (opsional)

5. **Setup Domain List**
   - Di Google Spreadsheet, buat sheet bernama "List VM"
   - Masukkan domain/website di kolom B (mulai baris 2)
   - Format: `domain.com` atau `subdomain.domain.com`

### **Menjalankan Aplikasi**
```bash
python main.py
```

---

## 🎯 **Panduan Penggunaan**

### **Menu Utama**

```
[1] Run Scan Once & Export Logs          → Scan sekali dan simpan ke Sheets
[2] Live Monitoring (Loop)               → Monitoring terus menerus
[3] Security Check Test                  → Jalankan security assessment
[4] Telegram Notification Test           → Test notifikasi Telegram
[5] Run Diagnostics                      → Periksa koneksi Sheets & Telegram
[6] Run Automatic Scheduler              → Jalankan scheduler otomatis
[7] Start Web Dashboard                  → Buka dashboard web
[8] Configuration Settings               → Edit konfigurasi
[0] Exit                                 → Keluar aplikasi
```

### **1. Run Scan Once & Export Logs**
- Melakukan scan satu kali terhadap semua domain
- Menampilkan progress bar real-time
- Menyimpan hasil ke Google Sheets (tab "Monitoring Log")
- Mengirim notifikasi Telegram
- Menyimpan log lokal di folder `results/`

### **2. Live Monitoring**
- Scan terus menerus dengan interval 60 detik
- Menampilkan tabel hasil real-time
- Countdown timer untuk refresh berikutnya
- Tekan Ctrl+C untuk berhenti

### **3. Security Check**
- Menjalankan comprehensive security assessment
- Mengecek 6 aspek keamanan per domain
- Menyimpan hasil ke tab "Security Check" dan "Security Summary"
- Mengirim alert untuk issues kritis

### **4. Web Dashboard**
- Jalankan server web di `http://localhost:5000`
- Interface modern dengan charts dan tables
- Auto-refresh setiap 30 detik
- Tidak memerlukan Google Sheets untuk berjalan

### **5. Configuration Settings**
- Edit Telegram settings (BOT_TOKEN, CHAT_ID)
- Konfigurasi Email alerts
- Atur monitoring parameters
- Edit Google Sheets settings

---

## 📊 **Panduan Membaca Hasil di Google Sheets**

### **Tab "Monitoring Log"**

| Kolom | Penjelasan | Cara Membaca |
|-------|------------|--------------|
| **Timestamp** | Waktu scan dilakukan | Format: YYYY-MM-DD HH:MM:SS |
| **URL** | Domain yang di-scan | Nama domain atau subdomain |
| **Status** | Status kesehatan website | ✅ HEALTHY = OK<br>❌ ERROR = Problem<br>⚠️ SLOW = Lambat<br>🔶 PARTIAL = Sebagian OK |
| **HTTP** | Kode status HTTP | 200 = OK<br>404 = Not Found<br>500 = Server Error<br>301/302 = Redirect |
| **Latency** | Waktu respon (ms) | <1000ms = Cepat<br>1000-3000ms = Sedang<br>>3000ms = Lambat |
| **SSL Status** | Status sertifikat SSL | ✅ VALID = OK<br>❌ INVALID = Problem<br>⚠️ EXPIRING = Akan expired |
| **SSL Days** | Sisa hari sebelum expired | >30 hari = Aman<br>7-30 hari = Warning<br><7 hari = Critical |
| **TLS Version** | Versi TLS yang digunakan | TLS 1.3 = Terbaik<br>TLS 1.2 = OK<br>TLS 1.1/1.0 = Deprecated |
| **SSL Error** | Detail error SSL | HANDSHAKE_FAIL, INVALID_CERT, dll. |
| **Protocol** | Protokol yang digunakan | HTTP/1.1, HTTP/2, HTTP/3 |
| **Server** | Server software | Apache, Nginx, IIS, dll. |
| **Cache** | Status caching | HIT/MISS |
| **CDN** | CDN provider | Cloudflare, Akamai, dll. |
| **Content** | Tipe konten | text/html, application/json, dll. |
| **Alerts** | Pesan alert khusus | Error messages atau warnings |

### **Tab "Summary"**

| Kolom | Penjelasan |
|-------|------------|
| **Website** | Nama domain dengan hyperlink |
| **Last Check** | Timestamp check terakhir |
| **Last Status** | Status terakhir |
| **HTTP** | HTTP status code terakhir |
| **Latency (ms)** | Rata-rata latency |
| **Server** | Server software |
| **Avg Latency (50 scans)** | Rata-rata dari 50 scan terakhir |
| **SLA % (7d)** | Persentase uptime dalam 7 hari |
| **SSL Status** | Status SSL saat ini |
| **SSL Expiry Days** | Hari sebelum SSL expired |
| **TLS** | Versi TLS |
| **Protocol** | Protokol HTTP |
| **SSL Error** | Error SSL jika ada |
| **Alerts** | Alert messages |

### **Tab "Security Check"**

| Kolom | Penjelasan | Status Codes |
|-------|------------|--------------|
| **Timestamp** | Waktu check | YYYY-MM-DD HH:MM:SS |
| **Domain** | Domain yang di-check | domain.com |
| **Check Type** | Tipe security check | Security Headers, HTTP Methods, dll. |
| **Status** | Hasil check | OK, WARN, CRITICAL, ERROR |
| **Severity** | Tingkat keparahan | Low, Medium, High, Critical |
| **Detail** | Detail hasil check | Deskripsi spesifik issue |

### **Tab "Security Summary"**

| Kolom | Penjelasan |
|-------|------------|
| **Domain** | Domain dengan hyperlink |
| **Security Headers** | Status header keamanan |
| **HTTP Methods** | Status metode HTTP |
| **Sensitive Files** | Status file sensitif |
| **Open Ports** | Status port terbuka |
| **Vulnerabilities** | Status kerentanan |
| **SSL Security** | Status keamanan SSL |
| **Overall Risk** | Risiko keseluruhan |
| **Last Check** | Timestamp terakhir |
| **Notes** | Catatan tambahan |

### **Interpretasi Status**

#### **Status Monitoring:**
- 🟢 **HEALTHY**: Website berfungsi normal
- 🟡 **SLOW**: Response lambat (>2000ms)
- 🔴 **ERROR**: Website tidak dapat diakses
- 🟠 **PARTIAL**: Sebagian fitur bermasalah

#### **Status SSL:**
- 🟢 **VALID**: SSL valid dan aman
- 🟡 **EXPIRING**: Akan expired dalam 30 hari
- 🔴 **INVALID**: SSL bermasalah atau expired
- ⚪ **NO_SSL**: Tidak menggunakan HTTPS

#### **Severity Security:**
- 🟢 **Low**: Issue minor, tidak kritis
- 🟡 **Medium**: Perlu diperhatikan
- 🟠 **High**: Rekomendasi segera diperbaiki
- 🔴 **Critical**: Harus segera diperbaiki

---

## 🔧 **Troubleshooting**

### **Error: ModuleNotFoundError**
```
pip install -r requirements.txt
```

### **Error: Google Sheets Connection**
- Pastikan `credentials.json` ada di folder `env/`
- Pastikan Service Account email memiliki akses ke spreadsheet
- Check nama spreadsheet di `config.py`

### **Error: Telegram Not Working**
- Verify BOT_TOKEN dan CHAT_ID di `config.py`
- Test dengan menu [4] Telegram Notification Test
- Pastikan bot sudah di-add ke group/channel

### **Error: Email Not Working**
- Check SMTP settings di `config.py`
- Verify email credentials
- Test koneksi SMTP

### **Performance Issues**
- Kurangi CONCURRENCY di `config.py`
- Tingkatkan CHECK_INTERVAL
- Monitor memory usage

---

## 🚀 **Development & Customization**

### **Menambah Security Check Baru**
1. Buat function di `utils/` (contoh: `utils/custom_check.py`)
2. Import dan tambahkan ke `core/security_checker.py`
3. Update `run_checks_for_domain()` function

### **Menambah Output Format Baru**
1. Buat module di `outputs/` (contoh: `outputs/slack.py`)
2. Implement send function
3. Import dan panggil dari `main.py`

### **Menambah Menu Baru**
1. Tambah option di `menu()` function
2. Buat handler function
3. Update elif chain

---

## 📞 **Support & Contact**

Untuk pertanyaan atau dukungan teknis:
- Buat issue di repository GitHub
- Contact tim development BNPB
- Dokumentasi lengkap tersedia di folder `docs/`

---

## 📝 **Changelog**

### **v2.0.0 (Latest)**
- ✅ Web Dashboard interface
- ✅ Email alerts support
- ✅ Advanced security checks
- ✅ Configuration management UI
- ✅ Improved error handling
- ✅ Async/await implementation

### **v1.0.0**
- ✅ Basic monitoring features
- ✅ Google Sheets integration
- ✅ Telegram notifications
- ✅ Local logging
- ✅ Modular architecture

---

**Powered by Salam Tangguh, Tangguh, Tangguh! 💪**

*WEB-MON BNPB — Reliable Website Monitoring for Disaster Management*

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

## � **Dokumentasi Lengkap**

### **📖 User Manual**
Untuk panduan lengkap penggunaan WEB-MON, silakan baca:
- **[USER_MANUAL.md](USER_MANUAL.md)** - Panduan lengkap setup, konfigurasi, dan penggunaan

### **📊 Spreadsheet Guide**
Untuk memahami hasil monitoring di Google Sheets:
- **[USER_GUIDE_SPREADSHEET.md](USER_GUIDE_SPREADSHEET.md)** - Panduan lengkap interpretasi data spreadsheet

### **🔧 Troubleshooting**
- Check folder `logs/` untuk log aplikasi
- Check folder `results/` untuk hasil scan JSON
- Gunakan menu "View Results" untuk melihat hasil terakhir

### **💡 Tips Penggunaan**
- Jalankan security check mingguan
- Monitor SLA >99% untuk critical services
- Setup alerts untuk SSL expiry <30 hari
- Backup folder `results/` dan `logs/` secara berkala

---

## �🛡️ **Keamanan & Privasi**

- Berjalan lokal, tidak mengirimkan data selain ke Google Sheets internal
- Telegram hanya untuk notifikasi internal BNPB
- Tidak menyimpan data sensitif website

---

> _Salam Tangguh, Tangguh, Tangguh!_ 💪💪💪
