# 🎬 Streaming Bot | بوت البث المباشر

<div align="center">

![Streaming Bot Banner](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active%20%26%20Maintained-success?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram&logoColor=white)

[![GitHub Stars](https://img.shields.io/github/stars/phoneKYC/streaming-bot?style=social)](https://github.com/phoneKYC/streaming-bot)
[![GitHub Forks](https://img.shields.io/github/forks/phoneKYC/streaming-bot?style=social)](https://github.com/phoneKYC/streaming-bot)
[![GitHub Issues](https://img.shields.io/github/issues/phoneKYC/streaming-bot?style=social)](https://github.com/phoneKYC/streaming-bot)

<p>
  <a href="#english">🌍 English</a> •
  <a href="#العربية">🇸🇦 العربية</a> •
  <a href="#features">✨ Features</a> •
  <a href="#installation">📥 Installation</a> •
  <a href="#documentation">📖 Docs</a>
</p>

</div>

---

## 🌍 English

### 📋 About

**Streaming Bot** is a production-ready Telegram bot designed for managing live streams across multiple platforms. It supports YouTube streams, M3U playlists, and IPTV with intelligent auto-reconnection and persistent session management.

Perfect for content creators, streaming platforms, and media distribution networks.

### ✨ Key Features

<table>
  <tr>
    <td>🎥 Multi-Source Support</td>
    <td>📺 YouTube, M3U, IPTV</td>
  </tr>
  <tr>
    <td>🔄 Smart Auto-Reconnect</td>
    <td>⚡ Configurable Delays</td>
  </tr>
  <tr>
    <td>💾 Persistent Storage</td>
    <td>📊 SQLite Database</td>
  </tr>
  <tr>
    <td>🛡️ Permission Validation</td>
    <td>✅ Auto Channel Checks</td>
  </tr>
  <tr>
    <td>📱 Real-time Control</td>
    <td>💬 Telegram Commands</td>
  </tr>
  <tr>
    <td>🚀 Production Ready</td>
    <td>🐳 Docker Support</td>
  </tr>
  <tr>
    <td>⚙️ Optimized Encoding</td>
    <td>📉 Low Resource Usage</td>
  </tr>
  <tr>
    <td>🌐 Bilingual Interface</td>
    <td>🇸🇦 Arabic & English</td>
  </tr>
</table>

### 🔧 Technical Stack

```
┌─────────────────────────────────┐
│  Framework & Libraries          │
├─────────────────────────────────┤
│ • Python 3.9+                   │
│ • python-telegram-bot v20+      │
│ • FFmpeg (Video Processing)     │
│ • yt-dlp (YouTube Extraction)   │
│ • SQLite3 (Database)            │
│ • Docker & Docker Compose       │
└─────────────────────────────────┘
```

### 🚀 Quick Start

#### 1. Prerequisites
```bash
# System dependencies
sudo apt-get install -y python3.9 ffmpeg git

# Python requirements
pip install python-telegram-bot yt-dlp python-dotenv
```

#### 2. Clone & Setup
```bash
git clone https://github.com/phoneKYC/streaming-bot.git
cd streaming-bot

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Configure
```bash
# Get bot token from @BotFather on Telegram
export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"

# Or use .env file
cp .env.example .env
nano .env  # Edit your token
```

#### 4. Run
```bash
python streaming_bot.py
```

### 📖 Command Reference

| Command | Purpose | Usage |
|---------|---------|-------|
| `/start` | Welcome & help | `/start` |
| `/setup` | Configure streaming | `/setup <m3u_url> <server_url> <key> <channel_id>` |
| `/start_stream` | Begin streaming | `/start_stream` |
| `/stop_stream` | Stop streaming | `/stop_stream` |
| `/status` | Check session status | `/status` |

### 📚 Usage Examples

```bash
# Example 1: YouTube Stream
/setup "https://youtu.be/dQw4w9WgXcQ" "rtmp://server.com/live/" "key123" "-1001234567890"

# Example 2: M3U Playlist (Radio)
/setup "http://radio.playlist.m3u" "rtmp://server.com/live/" "radio_key" "-1001234567890"

# Example 3: IPTV Stream
/setup "http://iptv.stream.url" "rtmp://server.com/live/" "iptv_key" "-1001234567890"
```

### 🏗️ Architecture

```
User (Telegram)
      ↓
   /start_stream
      ↓
Telegram Bot ←→ SQLite Database
      ↓
 FFmpeg Process
      ↓
   RTMP Server
      ↓
   YouTube/OBS/etc
```

### 📊 How It Works

**1. YouTube Streams**
- Extracts live URL using yt-dlp
- Pipes to FFmpeg for encoding
- Auto-reconnects on failure

**2. M3U Playlists**
- Overlays black video (saves bandwidth)
- Preserves audio quality
- Low CPU usage mode

**3. IPTV Streams**
- Direct stream copy
- 15-second timeout with auto-reconnect
- Optimized for stability

### 🐳 Docker Deployment

```bash
# Build image
docker build -t streaming-bot:latest .

# Run container
docker run -d \
  --name streaming-bot \
  -e BOT_TOKEN="your_token" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  streaming-bot:latest

# Or use Docker Compose
docker-compose up -d
```

### 🚀 Production Deployment

#### VPS (Recommended)
```bash
# Ubuntu/Debian setup
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip ffmpeg git

# Clone & install
git clone https://github.com/phoneKYC/streaming-bot.git
cd streaming-bot
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/streaming-bot.service
sudo systemctl enable streaming-bot
sudo systemctl start streaming-bot
```

#### Cloud Platforms
- **Railway.app** (Recommended - Easy & Affordable)
- **Render.com** (Good Alternative)
- **Heroku** (Paid Alternative)

### 🔐 Security

- ✅ Bot token in environment variables only
- ✅ Regular database backups
- ✅ Input validation on all commands
- ✅ Permission verification before streaming
- ✅ Secure logging (no sensitive data)

### 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Verify `BOT_TOKEN` and internet connection |
| FFmpeg not found | `sudo apt-get install ffmpeg` |
| Permission denied | Ensure bot is channel admin |
| Stream disconnects | Check firewall & RTMP server status |
| High CPU usage | Reduce bitrate or resolution |

### 📖 Full Documentation

- 📘 [Installation Guide](./DEPLOYMENT.md)
- 🔐 [Security Guide](./SECURITY.md)
- 🤝 [Contributing](./CONTRIBUTING.md)
- 📝 [Changelog](./CHANGELOG.md)

### 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

### 📝 License

This project is licensed under the **MIT License** - see [LICENSE](./LICENSE) file for details.

### 💬 Support & Contact

- 📧 **Email**: contact@iidzii.dev
- 🐛 **Issues**: [GitHub Issues](https://github.com/phoneKYC/streaming-bot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/phoneKYC/streaming-bot/discussions)

### 👨‍💻 Development

**Created & Maintained by:** [IIDZII Dev](https://github.com/IIDZII) ♕

**Repository:** [phoneKYC/streaming-bot](https://github.com/phoneKYC/streaming-bot)

---

## 🇸🇦 العربية

### 📋 نبذة عن المشروع

**بوت البث** هو بوت Telegram احترافي وجاهز للإنتاج يُدير البث المباشر إلى منصات متعددة. يدعم بثات YouTube وقوائم M3U وIPTV مع إعادة اتصال ذكية وإدارة جلسات دائمة.

مثالي لمنشئي المحتوى والمنصات البثية وشبكات توزيع الوسائط.

### ✨ المميزات الرئيسية

<table>
  <tr>
    <td>🎥 دعم مصادر متعددة</td>
    <td>📺 YouTube, M3U, IPTV</td>
  </tr>
  <tr>
    <td>🔄 إعادة اتصال ذكية</td>
    <td>⚡ تأخيرات قابلة للتكوين</td>
  </tr>
  <tr>
    <td>💾 تخزين دائم</td>
    <td>📊 قاعدة بيانات SQLite</td>
  </tr>
  <tr>
    <td>🛡️ التحقق من الأذونات</td>
    <td>✅ فحص تلقائي للقنوات</td>
  </tr>
  <tr>
    <td>📱 التحكم في الوقت الفعلي</td>
    <td>💬 أوامر Telegram</td>
  </tr>
  <tr>
    <td>🚀 جاهز للإنتاج</td>
    <td>🐳 دعم Docker</td>
  </tr>
  <tr>
    <td>⚙️ ترميز محسّن</td>
    <td>📉 استهلاك موارد منخفض</td>
  </tr>
  <tr>
    <td>🌐 واجهة ثنائية اللغة</td>
    <td>🇸🇦 عربي وإنجليزي</td>
  </tr>
</table>

### 🔧 التقنيات المستخدمة

```
┌─────────────────────────────────┐
│  الأطر العمل والمكتبات          │
├─────────────────────────────────┤
│ • Python 3.9+                   │
│ • python-telegram-bot v20+      │
│ • FFmpeg (معالجة الفيديو)      │
│ • yt-dlp (استخراج YouTube)     │
│ • SQLite3 (قاعدة البيانات)     │
│ • Docker & Docker Compose       │
└─────────────────────────────────┘
```

### 🚀 البدء السريع

#### 1. المتطلبات
```bash
# مكتبات النظام
sudo apt-get install -y python3.9 ffmpeg git

# مكتبات Python
pip install python-telegram-bot yt-dlp python-dotenv
```

#### 2. الاستنساخ والإعداد
```bash
git clone https://github.com/phoneKYC/streaming-bot.git
cd streaming-bot

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. التكوين
```bash
# احصل على توكن البوت من @BotFather على Telegram
export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"

# أو استخدم ملف .env
cp .env.example .env
nano .env  # عدّل توكنك
```

#### 4. التشغيل
```bash
python streaming_bot.py
```

### 📖 مرجع الأوامر

| الأمر | الغرض | الاستخدام |
|------|-------|-----------|
| `/start` | الترحيب والمساعدة | `/start` |
| `/setup` | تكوين البث | `/setup <m3u_url> <server_url> <key> <channel_id>` |
| `/start_stream` | بدء البث | `/start_stream` |
| `/stop_stream` | إيقاف البث | `/stop_stream` |
| `/status` | التحقق من حالة الجلسة | `/status` |

### 📚 أمثلة الاستخدام

```bash
# مثال 1: بث YouTube
/setup "https://youtu.be/dQw4w9WgXcQ" "rtmp://server.com/live/" "key123" "-1001234567890"

# مثال 2: قائمة M3U (راديو)
/setup "http://radio.playlist.m3u" "rtmp://server.com/live/" "radio_key" "-1001234567890"

# مثال 3: بث IPTV
/setup "http://iptv.stream.url" "rtmp://server.com/live/" "iptv_key" "-1001234567890"
```

### 🏗️ البنية المعمارية

```
المستخدم (Telegram)
      ↓
   /start_stream
      ↓
بوت Telegram ←→ قاعدة بيانات SQLite
      ↓
 عملية FFmpeg
      ↓
   خادم RTMP
      ↓
   YouTube/OBS/إلخ
```

### 📊 كيفية العمل

**1. بثات YouTube**
- استخراج رابط البث الحي باستخدام yt-dlp
- نقل البيانات إلى FFmpeg للترميز
- إعادة اتصال تلقائية عند الفشل

**2. قوائم M3U**
- إضافة فيديو أسود (يوفر النطاق الترددي)
- الحفاظ على جودة الصوت
- وضع استهلاك CPU منخفض

**3. بثات IPTV**
- نسخ البث المباشر
- مهلة زمنية 15 ثانية مع إعادة اتصال تلقائية
- محسّنة للاستقرار

### 🐳 نشر Docker

```bash
# بناء الصورة
docker build -t streaming-bot:latest .

# تشغيل الحاوية
docker run -d \
  --name streaming-bot \
  -e BOT_TOKEN="your_token" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  streaming-bot:latest

# أو استخدام Docker Compose
docker-compose up -d
```

### 🚀 نشر الإنتاج

#### VPS (موصى به)
```bash
# إعداد Ubuntu/Debian
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip ffmpeg git

# الاستنساخ والتثبيت
git clone https://github.com/phoneKYC/streaming-bot.git
cd streaming-bot
pip install -r requirements.txt

# إنشاء خدمة systemd
sudo nano /etc/systemd/system/streaming-bot.service
sudo systemctl enable streaming-bot
sudo systemctl start streaming-bot
```

#### منصات سحابية
- **Railway.app** (موصى به - سهل وبأسعار معقولة)
- **Render.com** (بديل جيد)
- **Heroku** (بديل مدفوع)

### 🔐 الأمان

- ✅ توكن البوت في متغيرات البيئة فقط
- ✅ نسخ احتياطية منتظمة لقاعدة البيانات
- ✅ التحقق من صحة جميع الأوامر
- ✅ التحقق من الأذونات قبل البث
- ✅ تسجيل آمن (بدون بيانات حساسة)

### 🐛 استكشاف الأخطاء

| المشكلة | الحل |
|--------|------|
| البوت لا يرد | تحقق من `BOT_TOKEN` والاتصال بالإنترنت |
| FFmpeg غير موجود | `sudo apt-get install ffmpeg` |
| رفض الأذونات | تأكد من أن البوت هو مسؤول القناة |
| انقطاع البث | تحقق من جدار الحماية وحالة خادم RTMP |
| استهلاك CPU مرتفع | قلل معدل ترميز أو الدقة |

### 📖 التوثيق الكامل

- 📘 [دليل التثبيت](./DEPLOYMENT.md)
- 🔐 [دليل الأمان](./SECURITY.md)
- 🤝 [المساهمة](./CONTRIBUTING.md)
- 📝 [سجل التغييرات](./CHANGELOG.md)

### 🤝 المساهمة

نرحب بالمساهمات! إليك كيفية المساهمة:

1. Fork المستودع
2. أنشئ فرع ميزة: `git checkout -b feature/AmazingFeature`
3. Commit التغييرات: `git commit -m 'Add AmazingFeature'`
4. Push إلى الفرع: `git push origin feature/AmazingFeature`
5. فتح Pull Request

### 📝 الترخيص

هذا المشروع مرخص تحت ترخيص **MIT** - انظر ملف [LICENSE](./LICENSE) للتفاصيل.

### 💬 الدعم والتواصل

- 📧 **البريد الإلكتروني**: contact@iidzii.dev
- 🐛 **المشاكل**: [GitHub Issues](https://github.com/phoneKYC/streaming-bot/issues)
- 💬 **النقاشات**: [GitHub Discussions](https://github.com/phoneKYC/streaming-bot/discussions)

### 👨‍💻 التطوير

**تم الإنشاء والصيانة بواسطة:** [IIDZII Dev](https://github.com/IIDZII) ♕

**المستودع:** [phoneKYC/streaming-bot](https://github.com/phoneKYC/streaming-bot)

---

<div align="center">

### 🌟 دعم المشروع

إذا أعجبك هذا المشروع، أعطه ⭐ وشاركه مع الآخرين!

---

## 📊 إحصائيات المشروع

![Python](https://img.shields.io/badge/Language-Python%2094.8%25-blue)
![Docker](https://img.shields.io/badge/Docker-5.2%25-blue)
![Code Quality](https://img.shields.io/badge/Code%20Quality-Production%20Ready-brightgreen)
![Maintenance](https://img.shields.io/badge/Maintenance-Active-brightgreen)

---

### 🙏 شكر خاص

شكر خاص للمساهمين والمستخدمين الذين يدعمون هذا المشروع!

### 💝 الدعم المالي

إذا كنت تستخدم هذا المشروع بشكل احترافي، يرجى التفكير في دعم التطوير المستمر.

---

Made with ❤️ by **[IIDZII Dev](https://github.com/IIDZII)** ♕

**Last Updated**: June 2026

</div>
