# 📊 **WEB-MON Spreadsheet Results Guide**

Panduan lengkap untuk memahami dan menginterpretasi hasil monitoring di Google Sheets.

---

## 🎯 **Overview Sheets**

WEB-MON menggunakan 4 sheet utama di Google Spreadsheet:

1. **List VM** → Daftar domain yang dimonitoring
2. **Monitoring Log** → Detail hasil setiap scan
3. **Summary** → Ringkasan status per domain
4. **Security Check** → Hasil security assessment detail
5. **Security Summary** → Ringkasan security per domain

---

## 📋 **Sheet "List VM"**

### **Struktur:**
- **Kolom A**: Nomor urut (opsional)
- **Kolom B**: Domain/URL yang akan dimonitoring
- **Baris 1**: Header (biasanya kosong atau "Domain")

### **Format Input:**
```
| No | Domain          |
|----|-----------------|
| 1  | bnpb.go.id      |
| 2  | sub.bnpb.go.id  |
| 3  | api.bnpb.go.id  |
```

### **Catatan:**
- Masukkan domain tanpa `http://` atau `https://`
- Satu domain per baris
- Sistem akan otomatis test HTTPS dulu, lalu fallback ke HTTP

---

## 📈 **Sheet "Monitoring Log"**

### **Header Columns:**

| Column | Name | Description |
|--------|------|-------------|
| A | Timestamp | Waktu scan (YYYY-MM-DD HH:MM:SS) |
| B | URL | Domain yang di-scan |
| C | Status | Status kesehatan website |
| D | HTTP | HTTP status code |
| E | Latency | Response time (ms) |
| F | SSL Status | Status sertifikat SSL |
| G | SSL Days | Hari sebelum SSL expired |
| H | TLS Version | Versi TLS yang digunakan |
| I | SSL Error | Detail error SSL |
| J | Protocol | Protokol HTTP |
| K | Server | Web server software |
| L | Cache | Cache status |
| M | CDN | CDN provider |
| N | Content | Content-Type |
| O | Alerts | Pesan alert khusus |

### **Status Code Meanings:**

#### **Status (Column C)**
```
✅ HEALTHY   = Website berfungsi normal (HTTP 200, latency OK)
⚠️  SLOW      = Response lambat (>2000ms)
❌ ERROR     = Website tidak dapat diakses
🔶 PARTIAL   = Sebagian bermasalah
🔄 UNREACHABLE = Tidak dapat dihubungi
```

#### **HTTP Status (Column D)**
```
200 = OK (berhasil)
301 = Moved Permanently (redirect)
302 = Found (redirect)
400 = Bad Request
401 = Unauthorized
403 = Forbidden
404 = Not Found
500 = Internal Server Error
502 = Bad Gateway
503 = Service Unavailable
504 = Gateway Timeout
```

#### **SSL Status (Column F)**
```
✅ VALID      = SSL valid dan trusted
⚠️  EXPIRING  = Akan expired dalam 30 hari
❌ INVALID    = SSL bermasalah atau expired
🔄 NO_SSL     = Tidak menggunakan HTTPS
```

#### **SSL Days (Column G)**
```
🟢 > 30 hari  = Aman
🟡 7-30 hari  = Warning (segera renew)
🔴 < 7 hari   = Critical (renew segera)
❌ Negative   = Sudah expired
```

#### **TLS Version (Column H)**
```
🟢 TLS 1.3    = Excellent (terbaru)
🟢 TLS 1.2    = Good (recommended)
🟡 TLS 1.1    = Deprecated (update server)
🔴 TLS 1.0    = Insecure (update urgent)
```

### **Contoh Data:**

```
| 2025-12-23 08:00:01 | bnpb.go.id | ✅ HEALTHY | 200 | 245 | ✅ VALID | 89 | TLS 1.3 | - | HTTP/2 | nginx/1.20.1 | MISS | Cloudflare | text/html | - |
| 2025-12-23 08:00:02 | api.bnpb.go.id | ⚠️ SLOW | 200 | 3240 | ✅ VALID | 45 | TLS 1.2 | - | HTTP/1.1 | Apache/2.4.41 | HIT | - | application/json | High latency detected |
| 2025-12-23 08:00:03 | old.bnpb.go.id | ❌ ERROR | 502 | - | ❌ INVALID | -5 | - | CERT_EXPIRED | - | - | - | - | - | SSL certificate expired |
```

---

## 📊 **Sheet "Summary"**

### **Header Columns:**

| Column | Name | Description |
|--------|------|-------------|
| A | Website | Domain dengan hyperlink ke detail |
| B | Last Check | Timestamp check terakhir |
| C | Last Status | Status terakhir |
| D | HTTP | HTTP status code terakhir |
| E | Latency (ms) | Latency terakhir |
| F | Server | Web server software |
| G | Avg Latency (50 scans) | Rata-rata dari 50 scan terakhir |
| H | SLA % (7d) | Persentase uptime dalam 7 hari |
| I | SSL Status | Status SSL saat ini |
| J | SSL Expiry Days | Hari sebelum SSL expired |
| K | TLS | Versi TLS |
| L | Protocol | Protokol HTTP |
| M | SSL Error | Error SSL jika ada |
| N | Alerts | Alert messages |

### **Cara Membaca SLA % (Column H):**
```
🟢 99.9%+   = Excellent (downtime minimal)
🟢 99.0%+   = Good
🟡 95-99%   = Fair (perlu perhatian)
🟠 90-95%   = Poor (perlu investigasi)
🔴 <90%     = Critical (immediate action needed)
```

### **Formula SLA Calculation:**
```excel
=COUNTIFS(range_status, "HEALTHY") / COUNTIFS(range_timestamp, ">=" & TODAY()-7) * 100
```

### **Contoh Data:**

```
| =HYPERLINK("https://docs.google.com/spreadsheets/d/.../edit#gid=...", "bnpb.go.id") | 2025-12-23 08:00:01 | ✅ HEALTHY | 200 | 245 | nginx/1.20.1 | 312 | 99.8% | ✅ VALID | 89 | TLS 1.3 | HTTP/2 | - | - |
| =HYPERLINK("https://docs.google.com/spreadsheets/d/.../edit#gid=...", "api.bnpb.go.id") | 2025-12-23 08:00:02 | ⚠️ SLOW | 200 | 3240 | Apache/2.4.41 | 2890 | 97.2% | ✅ VALID | 45 | TLS 1.2 | HTTP/1.1 | - | High latency trend |
```

---

## 🔐 **Sheet "Security Check"**

### **Header Columns:**

| Column | Name | Description |
|--------|------|-------------|
| A | Timestamp | Waktu security check |
| B | Domain | Domain yang di-check |
| C | Check Type | Tipe security check |
| D | Status | Hasil check |
| E | Severity | Tingkat keparahan |
| F | Detail | Detail hasil check |

### **Check Types (Column C):**
```
🔒 Security Headers   = Analisis header keamanan
🌐 HTTP Methods       = Test metode HTTP berbahaya
📁 Sensitive Files    = Scan file sensitif
🔌 Open Ports         = Scan port terbuka
🛡️  Vulnerabilities   = Assessment kerentanan
🔐 SSL Security       = Analisis keamanan SSL
```

### **Status Codes (Column D):**
```
✅ OK         = Aman/tidak ada issue
⚠️  WARN       = Peringatan (perlu perhatian)
🚨 CRITICAL   = Kritis (perlu segera diperbaiki)
❌ ERROR      = Error dalam pengecekan
```

### **Severity Levels (Column E):**
```
🟢 Low        = Issue minor
🟡 Medium     = Perlu diperhatikan
🟠 High       = Rekomendasi segera diperbaiki
🔴 Critical   = Harus segera diperbaiki
```

### **Contoh Data:**

```
| 2025-12-23 09:00:00 | bnpb.go.id | Security Headers | ⚠️ WARN | Medium | Missing headers: X-Content-Type-Options, Referrer-Policy |
| 2025-12-23 09:00:00 | bnpb.go.id | HTTP Methods | ✅ OK | Low | Allowed methods: GET, HEAD, POST |
| 2025-12-23 09:00:00 | bnpb.go.id | Sensitive Files | ✅ OK | Low | No sensitive files exposed |
| 2025-12-23 09:00:00 | bnpb.go.id | Open Ports | ⚠️ WARN | Medium | Open ports detected: 22, 80, 443 |
| 2025-12-23 09:00:00 | bnpb.go.id | Vulnerabilities | ✅ OK | Low | No critical vulnerabilities detected |
| 2025-12-23 09:00:00 | bnpb.go.id | SSL Security | ✅ OK | Low | SSL configuration appears secure |
```

---

## 📋 **Sheet "Security Summary"**

### **Header Columns:**

| Column | Name | Description |
|--------|------|-------------|
| A | Domain | Domain dengan hyperlink |
| B | Security Headers | Status header keamanan |
| C | HTTP Methods | Status metode HTTP |
| D | Sensitive Files | Status file sensitif |
| E | Open Ports | Status port terbuka |
| F | Vulnerabilities | Status kerentanan |
| G | SSL Security | Status keamanan SSL |
| H | Overall Risk | Risiko keseluruhan |
| I | Last Check | Timestamp terakhir |
| J | Notes | Catatan tambahan |

### **Status Interpretation:**

#### **Individual Checks (B-G):**
```
✅ OK         = Pass (hijau)
⚠️  WARN       = Warning (kuning)
🚨 CRITICAL   = Critical (merah)
❌ ERROR      = Error (merah)
```

#### **Overall Risk (Column H):**
```
🟢 LOW        = Risiko rendah (semua OK atau warning minor)
🟡 MEDIUM     = Risiko sedang (ada beberapa warning)
🟠 HIGH       = Risiko tinggi (ada critical issues)
🔴 CRITICAL   = Risiko kritis (multiple critical issues)
```

### **Contoh Data:**

```
| =HYPERLINK("https://docs.google.com/spreadsheets/d/.../edit#gid=...", "bnpb.go.id") | ⚠️ WARN | ✅ OK | ✅ OK | ⚠️ WARN | ✅ OK | ✅ OK | 🟡 MEDIUM | 2025-12-23 09:00:00 | Review security headers and open ports |
| =HYPERLINK("https://docs.google.com/spreadsheets/d/.../edit#gid=...", "api.bnpb.go.id") | ❌ ERROR | ✅ OK | ✅ OK | ✅ OK | 🚨 CRITICAL | ✅ OK | 🔴 CRITICAL | 2025-12-23 09:00:00 | Critical vulnerability found - immediate action required |
```

---

## 🎨 **Conditional Formatting**

### **Monitoring Log:**
- **Status Column**: Hijau untuk HEALTHY, Merah untuk ERROR
- **Latency Column**: Hijau <1000ms, Kuning 1000-2000ms, Merah >2000ms
- **SSL Days Column**: Hijau >30, Kuning 7-30, Merah <7

### **Summary:**
- **SLA % Column**: Hijau >99%, Kuning 95-99%, Merah <95%
- **SSL Days Column**: Sama dengan Monitoring Log

### **Security Sheets:**
- **Status Columns**: Hijau untuk OK, Kuning untuk WARN, Merah untuk CRITICAL/ERROR
- **Severity Column**: Hijau untuk Low, Kuning untuk Medium, Merah untuk High/Critical

---

## 📊 **Charts & Analytics**

### **Uptime Chart:**
- **X-Axis**: Time (tanggal)
- **Y-Axis**: Uptime Percentage (0-100%)
- **Data Source**: Summary sheet, SLA % column

### **Latency Trend:**
- **X-Axis**: Time
- **Y-Axis**: Average Latency (ms)
- **Data Source**: Summary sheet, Avg Latency column

### **Security Risk Distribution:**
- **Pie Chart**: Distribusi risiko keseluruhan
- **Data Source**: Security Summary sheet, Overall Risk column

---

## 🔍 **Advanced Queries**

### **Find Failing Sites:**
```excel
=FILTER('Monitoring Log'!A:O, 'Monitoring Log'!C:C <> "✅ HEALTHY")
```

### **Sites with SSL Expiring Soon:**
```excel
=FILTER('Summary'!A:N, 'Summary'!J:J <= 30)
```

### **High Risk Security Sites:**
```excel
=FILTER('Security Summary'!A:J, 'Security Summary'!H:H = "🔴 CRITICAL")
```

### **Average Uptime by Domain:**
```excel
=AVERAGEIFS('Summary'!H:H, 'Summary'!A:A, "domain.com")
```

---

## 🚨 **Alert Interpretation**

### **Telegram Alerts:**
```
🚨 CRITICAL: 3 sites down
🌐 site1.com - HTTP 500
🌐 site2.com - SSL expired
🌐 site3.com - Timeout
```

### **Email Alerts:**
- **Subject**: "5 Website(s) Down or Having Issues"
- **Body**: HTML table dengan detail lengkap
- **Recipients**: Konfigurasi di `config.py`

### **Dashboard Alerts:**
- **Real-time**: Status updates setiap 30 detik
- **Color Coding**: Hijau=OK, Merah=Issues
- **Charts**: Uptime trends dan latency graphs

---

## 💡 **Tips & Best Practices**

### **Monitoring Frequency:**
- **Critical Sites**: Setiap 5-15 menit
- **Important Sites**: Setiap 30-60 menit
- **Standard Sites**: Setiap 2-4 jam

### **Alert Thresholds:**
- **Latency**: >2000ms = Warning, >5000ms = Critical
- **Uptime SLA**: <99% = Warning, <95% = Critical
- **SSL Days**: <30 = Warning, <7 = Critical

### **Security Priorities:**
1. **Critical**: SSL expired, server down
2. **High**: Missing security headers, dangerous HTTP methods
3. **Medium**: Open ports, outdated software
4. **Low**: Minor configuration issues

### **Maintenance Tasks:**
- **Weekly**: Review security summary
- **Monthly**: Check SSL renewal dates
- **Quarterly**: Update monitoring configurations

---

## 📞 **Support**

Untuk bantuan dalam menginterpretasi hasil:
- Referensi ke dokumentasi ini
- Check logs di folder `results/`
- Contact tim IT BNPB untuk technical issues

---

**📊 Understanding your monitoring data is key to maintaining reliable web services!**