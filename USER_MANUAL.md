# 📖 **WEB-MON User Manual**

Panduan lengkap penggunaan sistem monitoring website BNPB.

---

## 🎯 **Overview**

WEB-MON adalah toolkit monitoring website yang komprehensif untuk BNPB dengan fitur:
- ✅ **Real-time monitoring** website status
- 🔐 **Security assessment** otomatis
- 📊 **Google Sheets integration** untuk logging
- 📱 **Telegram notifications** untuk alerts
- 📧 **Email alerts** untuk monitoring issues
- 🌐 **Web dashboard** untuk real-time monitoring
- ⚡ **Async processing** untuk performa tinggi

---

## 🚀 **Quick Start**

### **1. Persiapan Environment**
```bash
# Clone atau download project
cd D:\Python\webmon

# Install dependencies
pip install -r requirements.txt

# Setup virtual environment (recommended)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Konfigurasi**
Edit file `config.py`:
```python
# Google Sheets Setup
SPREADSHEET_ID = "your_google_sheets_id"
SERVICE_ACCOUNT_FILE = "env/credentials.json"

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

# Email Setup
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# Monitoring Settings
MONITORING_INTERVAL = 30  # minutes
SECURITY_CHECK_INTERVAL = 1440  # 24 hours
```

### **3. Setup Google Sheets**
1. Buat Google Spreadsheet baru
2. Bagikan dengan service account email
3. Copy spreadsheet ID ke `config.py`
4. Pastikan `credentials.json` ada di folder `env/`

### **4. Setup Telegram Bot**
1. Chat dengan [@BotFather](https://t.me/botfather)
2. Buat bot baru: `/newbot`
3. Copy token ke `config.py`
4. Start bot dan dapatkan chat ID
5. Copy chat ID ke `config.py`

### **5. Setup Email (Opsional)**
1. Enable 2FA di Gmail
2. Generate App Password
3. Copy app password ke `config.py`

### **6. Jalankan Program**
```bash
python main.py
```

---

## 📋 **Menu Utama**

Setelah menjalankan `python main.py`, Anda akan melihat menu:

```
╔══════════════════════════════════════════════════════════════╗
║                      WEB-MON v2.0                           ║
║                   Website Monitoring Tool                   ║
║                        for BNPB                             ║
╚══════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│                           MENU                              │
├─────────────────────────────────────────────────────────────┤
│  1. 📊 View Dashboard                                       │
│  2. 🔍 Run Monitoring                                       │
│  3. 🔐 Run Security Check                                   │
│  4. 📋 View Results                                         │
│  5. ⚙️  Configuration                                       │
│  6. 📧 Test Email                                           │
│  7. 📱 Test Telegram                                        │
│  8. 🌐 Start Web Dashboard                                  │
│  9. 📊 View Spreadsheet                                     │
│ 10. 🚪 Exit                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 **Fitur Utama**

### **1. View Dashboard**
Menampilkan status real-time semua domain yang dimonitoring dalam format tabel.

### **2. Run Monitoring**
Melakukan monitoring website dengan:
- HTTP status check
- Response time measurement
- SSL certificate validation
- Server information gathering

### **3. Run Security Check**
Melakukan security assessment komprehensif:
- Security headers analysis
- HTTP methods testing
- Sensitive files scanning
- Open ports detection
- Vulnerability assessment
- SSL security evaluation

### **4. View Results**
Melihat hasil monitoring terakhir dari file JSON di folder `results/`.

### **5. Configuration**
Interface untuk mengubah konfigurasi:
- Monitoring intervals
- Alert thresholds
- Notification settings

### **6. Test Email**
Test pengiriman email alerts.

### **7. Test Telegram**
Test pengiriman pesan Telegram.

### **8. Start Web Dashboard**
Menjalankan web server untuk dashboard real-time.

### **9. View Spreadsheet**
Membuka Google Sheets untuk melihat data lengkap.

---

## 🌐 **Web Dashboard**

### **Cara Menggunakan:**
1. Pilih menu "8. 🌐 Start Web Dashboard"
2. Buka browser ke `http://localhost:5000`
3. Dashboard akan menampilkan:
   - Status real-time semua websites
   - Charts uptime dan latency
   - Security summary
   - Recent alerts

### **Fitur Dashboard:**
- **Real-time Updates**: Data refresh setiap 30 detik
- **Interactive Charts**: Plotly charts untuk trends
- **Color Coding**: Status visual dengan warna
- **Responsive Design**: Compatible dengan mobile

---

## 📊 **Google Sheets Integration**

### **Struktur Sheets:**
1. **List VM**: Daftar domain yang dimonitoring
2. **Monitoring Log**: Detail setiap scan
3. **Summary**: Ringkasan status per domain
4. **Security Check**: Hasil security assessment
5. **Security Summary**: Ringkasan security

### **Cara Input Domain:**
1. Buka sheet "List VM"
2. Masukkan domain di kolom B (mulai baris 2)
3. Format: satu domain per baris, tanpa http/https
4. Contoh:
   ```
   bnpb.go.id
   sub.bnpb.go.id
   api.bnpb.go.id
   ```

### **Conditional Formatting:**
- **Hijau**: Status baik
- **Kuning**: Warning
- **Merah**: Critical/Error

---

## 📱 **Telegram Notifications**

### **Jenis Alerts:**
- **Monitoring Alerts**: Website down atau slow
- **Security Alerts**: Critical security issues
- **SSL Alerts**: Certificate expiring soon

### **Format Pesan:**
```
🚨 CRITICAL: 3 sites down
🌐 site1.com - HTTP 500
🌐 site2.com - SSL expired
🌐 site3.com - Timeout
```

### **Test Telegram:**
Gunakan menu "7. 📱 Test Telegram" untuk memastikan setup benar.

---

## 📧 **Email Alerts**

### **Konfigurasi SMTP:**
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Not regular password!
```

### **Jenis Email:**
- **Monitoring Alerts**: HTML table dengan detail issues
- **Security Reports**: Weekly security summary
- **SSL Warnings**: Certificate expiration alerts

### **Test Email:**
Gunakan menu "6. 📧 Test Email" untuk memastikan setup benar.

---

## ⚙️ **Konfigurasi Lanjutan**

### **File config.py:**

```python
# Monitoring Settings
MONITORING_INTERVAL = 30          # Minutes between checks
SECURITY_CHECK_INTERVAL = 1440    # 24 hours in minutes
MAX_CONCURRENT_CHECKS = 10        # Max parallel requests

# Alert Thresholds
LATENCY_WARNING = 2000            # ms
LATENCY_CRITICAL = 5000           # ms
SSL_WARNING_DAYS = 30             # Days before expiry
SSL_CRITICAL_DAYS = 7             # Days before expiry

# Web Dashboard
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 5000
DASHBOARD_REFRESH = 30            # Seconds

# Logging
LOG_LEVEL = "INFO"
LOG_MAX_SIZE = 10*1024*1024       # 10MB
LOG_BACKUP_COUNT = 5
```

### **Environment Variables:**
Bisa menggunakan environment variables untuk sensitive data:
```bash
export TELEGRAM_BOT_TOKEN="your_token"
export EMAIL_PASSWORD="your_password"
```

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. Google Sheets Error**
```
Error: gspread.exceptions.APIError
```
**Solution:**
- Pastikan `credentials.json` valid
- Check spreadsheet sharing permissions
- Verify spreadsheet ID

#### **2. Telegram HTTP 400**
```
Error: Bad Request
```
**Solution:**
- Check bot token format
- Verify chat ID
- Ensure bot is started

#### **3. Email Authentication Failed**
```
Error: SMTP Authentication Error
```
**Solution:**
- Use App Password instead of regular password
- Enable 2FA on Gmail
- Check SMTP server settings

#### **4. Import Errors**
```
ModuleNotFoundError
```
**Solution:**
- Install missing packages: `pip install -r requirements.txt`
- Check Python version (3.9+ required)
- Activate virtual environment

#### **5. Web Dashboard Not Loading**
```
Connection refused
```
**Solution:**
- Check if port 5000 is available
- Verify Flask installation
- Check firewall settings

### **Logs Location:**
- **Application Logs**: `logs/webmon.log.YYYY-MM-DD`
- **Results**: `results/scan_YYYYMMDD_HHMM.json`

### **Debug Mode:**
Jalankan dengan debug:
```bash
python -c "import logging; logging.basicConfig(level=logging.DEBUG); import main; main.main()"
```

---

## 📈 **Performance Optimization**

### **Async Processing:**
- Security checks menggunakan asyncio untuk concurrency
- Max 10 concurrent requests untuk menghindari rate limiting
- Timeout individual per check (30 detik)

### **Memory Management:**
- Results disimpan dalam file JSON
- Logs di-rotate otomatis (10MB max per file)
- Lazy loading untuk Google Sheets

### **Monitoring Best Practices:**
- **Critical sites**: 5-15 menit interval
- **Important sites**: 30-60 menit interval
- **Standard sites**: 2-4 jam interval

---

## 🔐 **Security Considerations**

### **Credentials Management:**
- Jangan commit `credentials.json` ke git
- Gunakan environment variables untuk sensitive data
- Regular rotation bot tokens dan passwords

### **Network Security:**
- Monitor hanya domain yang authorized
- Avoid scanning sensitive internal systems
- Respect robots.txt dan rate limits

### **Data Privacy:**
- Logs berisi informasi teknis saja
- Tidak menyimpan sensitive user data
- SSL certificates info untuk monitoring saja

---

## 📚 **Additional Resources**

### **Documentation:**
- `README.md`: Quick overview
- `README_ALL.md`: Comprehensive documentation
- `USER_GUIDE_SPREADSHEET.md`: Spreadsheet interpretation guide

### **Support:**
- Check logs di `logs/` folder
- Review `results/` untuk troubleshooting
- Contact tim IT BNPB untuk technical issues

### **Development:**
- Source code di GitHub
- Issues dan feature requests via GitHub
- Contributing guidelines di `CONTRIBUTING.md`

---

## 🎯 **Quick Reference**

### **Start Monitoring:**
```bash
python main.py
# Choose option 2: Run Monitoring
```

### **Start Security Check:**
```bash
python main.py
# Choose option 3: Run Security Check
```

### **Start Web Dashboard:**
```bash
python main.py
# Choose option 8: Start Web Dashboard
# Open http://localhost:5000
```

### **View Logs:**
```bash
tail -f logs/webmon.log.2025-12-23
```

### **Backup Data:**
```bash
cp -r results/ backup/
cp logs/webmon.log.* backup/
```

---

**🚀 WEB-MON siap membantu Anda memantau website BNPB dengan efisien dan andal!**