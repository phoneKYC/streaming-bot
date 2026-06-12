# 🎬 Streaming Bot - بوت إدارة البث المباشر

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)

[![Contributors](https://img.shields.io/github/contributors/IIDZII/streaming-bot?style=flat-square)](../../graphs/contributors)
[![Forks](https://img.shields.io/github/forks/IIDZII/streaming-bot?style=flat-square)](../../network/members)
[![Stars](https://img.shields.io/github/stars/IIDZII/streaming-bot?style=flat-square)](../../stargazers)
[![Issues](https://img.shields.io/github/issues/IIDZII/streaming-bot?style=flat-square)](../../issues)

<p>
  <a href="#-english">English</a> •
  <a href="#-العربية">العربية</a>
</p>

</div>

---

## 🌍 English

### 📋 Overview

**Streaming Bot** is a powerful Telegram bot that manages live streaming to multiple platforms. It supports YouTube streams, M3U playlists, and IPTV streams with automatic reconnection and persistent session management.

### ✨ Features

- 🎥 **Multi-Source Streaming**: Support for YouTube, M3U playlists, and IPTV streams
- 🔄 **Auto-Reconnection**: Intelligent reconnection mechanism with configurable delays
- 💾 **Persistent Storage**: SQLite database for storing user settings and stream status
- 🛡️ **Permission Checking**: Automatic verification of bot permissions in Telegram channels
- 📊 **Session Management**: Monitor and control streaming status in real-time
- 🚀 **Easy Setup**: Simple command-based configuration via Telegram
- ⚡ **Optimized Encoding**: FFmpeg optimization for minimal resource consumption
- 🌐 **Bilingual Support**: Arabic and English interface

### 🔧 Technical Stack

- **Language**: Python 3.9+
- **Telegram API**: python-telegram-bot v21
- **Streaming**: FFmpeg, yt-dlp
- **Database**: SQLite3
- **Dependencies**: See requirements.txt

### 📥 Installation

#### Prerequisites
```bash
# System requirements
- Python 3.9 or higher
- FFmpeg
- yt-dlp
- Telegram Bot Token

# Install FFmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg -y

# Install yt-dlp
pip install yt-dlp
```

#### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/IIDZII/streaming-bot.git
cd streaming-bot
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure your bot token**
```bash
# Edit streaming_bot.py
nano streaming_bot.py

# Find and replace BOT_TOKEN with your Telegram bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```

### 🚀 Quick Start

1. **Start the bot**
```bash
python streaming_bot.py
```

2. **In Telegram, use these commands**

```
/start          - Display welcome message and available commands
/setup [args]   - Configure streaming settings
/start_stream   - Begin streaming
/stop_stream    - Stop streaming
/status         - Check current session status
```

### 📖 Usage Guide

#### Setup Command Syntax
```
/setup <m3u_url> <server_url> <stream_key> <channel_id>
```

**Parameters:**
- `m3u_url`: Source stream URL (YouTube, M3U playlist, or IPTV link)
- `server_url`: RTMP server address (e.g., rtmp://your-server.com/live/)
- `stream_key`: Stream key for the RTMP server
- `channel_id`: Telegram channel ID where the bot will post

**Example:**
```
/setup https://youtu.be/dQw4w9WgXcQ rtmp://streaming-server.com/live/ stream_key_123 -1001234567890
```

#### Complete Workflow
1. Add bot to your Telegram channel as administrator
2. Grant "Post Messages" permission
3. Send `/setup` command with your streaming parameters
4. Send `/start_stream` to begin streaming
5. Monitor with `/status`
6. Use `/stop_stream` to stop

### 🏗️ How It Works

```
┌─────────────────────────────────────────────────┐
│         Telegram Bot (python-telegram-bot)      │
├─────────────────────────────────────────────────┤
│                                                  │
│  User Commands:                                  │
│  /setup → Save to SQLite DB                     │
│  /start_stream → Launch FFmpeg Process          │
│  /stop_stream → Terminate FFmpeg                │
│  /status → Check DB & Process Status            │
│                                                  │
├─────────────────────────────────────────────────┤
│            SQLite Database                       │
│  ┌──────────────────────────────────────┐       │
│  │ user_id | m3u_url | server_url | ... │       │
│  │ settings | streaming status          │       │
│  └──────────────────────────────────────┘       │
│                                                  │
├─────────────────────────────────────────────────┤
│        FFmpeg Process Management                 │
│                                                  │
│  YouTube Support:                                │
│  YouTube URL → yt-dlp (Extract Live URL)        │
│              → FFmpeg (Encode & Stream)          │
│                                                  │
│  M3U Playlists:                                  │
│  M3U URL → FFmpeg (Black video overlay)          │
│         → Low bitrate encoding                   │
│         → Minimal resource consumption           │
│                                                  │
│  IPTV Streams:                                   │
│  IPTV URL → FFmpeg (Direct stream copy)          │
│          → Auto-reconnection on failure          │
│                                                  │
├─────────────────────────────────────────────────┤
│      Output to RTMP Server                       │
│      (OBS, Nginx RTMP, or other platforms)      │
└─────────────────────────────────────────────────┘
```

### 🔄 Streaming Logic

#### YouTube Streams
- Uses `yt-dlp` to extract the actual streaming URL
- FFmpeg connects to the extracted URL
- Auto-reconnect every 5 seconds on failure
- Includes Mozilla User-Agent headers for compatibility

#### M3U Playlists (Radio/Audio)
- Overlays a black video stream (10 FPS, 640x360)
- Low bitrate encoding (100k) to save server resources
- Preserves audio quality without re-encoding
- Shortest stream mode (video ends when audio ends)

#### IPTV Streams
- Direct stream copy without re-encoding
- 15-second read timeout with reconnection
- 10-second retry delay on connection loss
- Optimized for continuous, stable streams

### 🐳 Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install yt-dlp

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY streaming_bot.py .

CMD ["python", "streaming_bot.py"]
```

#### Build and Run
```bash
# Build image
docker build -t streaming-bot:latest .

# Run container
docker run -d \
  --name streaming-bot \
  --env BOT_TOKEN="YOUR_BOT_TOKEN" \
  -v $(pwd)/data:/app/data \
  streaming-bot:latest
```

### 🚀 Production Deployment

#### Option 1: VPS Deployment (Ubuntu/Debian)

```bash
# 1. SSH into your server
ssh root@your-server-ip

# 2. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 3. Install dependencies
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg git

# 4. Clone repository
git clone https://github.com/IIDZII/streaming-bot.git
cd streaming-bot

# 5. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 6. Install Python dependencies
pip install -r requirements.txt

# 7. Configure bot token
nano streaming_bot.py
# Edit BOT_TOKEN = "YOUR_TOKEN"

# 8. Create systemd service
sudo nano /etc/systemd/system/streaming-bot.service
```

#### Systemd Service File
```ini
[Unit]
Description=Streaming Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/streaming-bot
Environment="PATH=/root/streaming-bot/venv/bin"
ExecStart=/root/streaming-bot/venv/bin/python streaming_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable streaming-bot
sudo systemctl start streaming-bot

# Check status
sudo systemctl status streaming-bot

# View logs
sudo journalctl -u streaming-bot -f
```

#### Option 2: Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Option 3: Cloud Platform Deployment

**Heroku** (Free tier deprecated)
**Railway.app** (Recommended)
**Render.com**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.

### 🔐 Security Best Practices

1. **Protect your bot token**
   ```bash
   # Use environment variables
   export BOT_TOKEN="your_token_here"
   
   # Or use .env file with python-dotenv
   ```

2. **Database backup**
   ```bash
   # Regular SQLite backups
   cp stream_manager.db stream_manager.db.backup
   ```

3. **Firewall configuration**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

### 📊 Database Schema

```sql
CREATE TABLE settings (
    user_id INTEGER PRIMARY KEY,
    m3u_url TEXT,
    server_url TEXT,
    stream_key TEXT,
    channel_id TEXT,
    is_running INTEGER DEFAULT 0
);
```

### 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Check bot token and internet connection |
| FFmpeg not found | Install FFmpeg: `sudo apt-get install ffmpeg` |
| Permission denied | Verify bot is admin in the channel |
| Stream keeps disconnecting | Check firewall rules and RTMP server status |
| High CPU usage | Reduce encoding bitrate or video resolution |
| Database locked | Restart the bot service |

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/streaming-bot.git
cd streaming-bot

# Create feature branch
git checkout -b feature/AmazingFeature

# Commit changes
git commit -m 'Add some AmazingFeature'

# Push to branch
git push origin feature/AmazingFeature

# Open Pull Request
```

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### ⭐ Show Your Support

Give a ⭐ if this project helps you!

### 📞 Support

- 📧 Email: contact@iidzii.dev
- 🔗 GitHub Issues: [Report a bug](../../issues)
- 💬 Discussions: [Ask a question](../../discussions)

### 👨‍💻 Author

**IIDZII Dev** - [GitHub](https://github.com/IIDZII)

---

## 🌍 العربية

### 📋 نظرة عامة

**بوت البث** هو بوت Telegram قوي يدير البث المباشر إلى منصات متعددة. يدعم بثات YouTube وقوائم تشغيل M3U وبثات IPTV مع إعادة اتصال تلقائية وإدارة جلسات دائمة.

### ✨ المميزات

- 🎥 **البث من مصادر متعددة**: دعم YouTube وقوائم M3U وبثات IPTV
- 🔄 **إعادة اتصال ذكية**: آلية إعادة اتصال ذكية مع تأخيرات قابلة للتكوين
- 💾 **التخزين الدائم**: قاعدة بيانات SQLite لحفظ إعدادات المستخدم وحالة البث
- 🛡️ **فحص الأذونات**: التحقق التلقائي من أذونات البوت في قنوات Telegram
- 📊 **إدارة الجلسات**: المراقبة والتحكم بحالة البث بالوقت الفعلي
- 🚀 **إعداد سهل**: تكوين بسيط قائم على الأوامر عبر Telegram
- ⚡ **ترميز محسّن**: تحسينات FFmpeg لاستهلاك موارد منخفض
- 🌐 **دعم ثنائي اللغة**: واجهة عربية وإنجليزية

### 🔧 التقنيات المستخدمة

- **اللغة**: Python 3.9+
- **واجهة Telegram**: python-telegram-bot v21
- **البث**: FFmpeg, yt-dlp
- **قاعدة البيانات**: SQLite3
- **المكتبات**: انظر requirements.txt

### 📥 التثبيت

#### المتطلبات الأساسية
```bash
# متطلبات النظام
- Python 3.9 أو أحدث
- FFmpeg
- yt-dlp
- توكن بوت Telegram

# تثبيت FFmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg -y

# تثبيت yt-dlp
pip install yt-dlp
```

#### خطوات الإعداد

1. **استنساخ المستودع**
```bash
git clone https://github.com/IIDZII/streaming-bot.git
cd streaming-bot
```

2. **إنشاء بيئة افتراضية**
```bash
python3 -m venv venv
source venv/bin/activate  # على Windows: venv\Scripts\activate
```

3. **تثبيت المكتبات**
```bash
pip install -r requirements.txt
```

4. **تكوين توكن البوت**
```bash
# تحرير الملف
nano streaming_bot.py

# البحث والاستبدال BOT_TOKEN بتوكنك
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```

### 🚀 البدء السريع

1. **تشغيل البوت**
```bash
python streaming_bot.py
```

2. **في Telegram، استخدم الأوامر التالية**

```
/start          - عرض رسالة الترحيب والأوامر المتاحة
/setup [args]   - تكوين إعدادات البث
/start_stream   - بدء البث
/stop_stream    - إيقاف البث
/status         - التحقق من حالة الجلسة
```

### 📖 دليل الاستخدام

#### بناء جملة أمر الإعداد
```
/setup <m3u_url> <server_url> <stream_key> <channel_id>
```

**المعاملات:**
- `m3u_url`: رابط مصدر البث (YouTube أو قائمة M3U أو رابط IPTV)
- `server_url`: عنوان خادم RTMP (مثل rtmp://your-server.com/live/)
- `stream_key`: مفتاح البث لخادم RTMP
- `channel_id`: معرف قناة Telegram حيث سينشر البوت

**مثال:**
```
/setup https://youtu.be/dQw4w9WgXcQ rtmp://streaming-server.com/live/ stream_key_123 -1001234567890
```

#### سير العمل الكامل
1. أضف البوت إلى قناة Telegram الخاصة بك كمسؤول
2. امنحه صلاحية "نشر الرسائل"
3. أرسل أمر `/setup` مع معاملات البث الخاصة بك
4. أرسل `/start_stream` لبدء البث
5. راقب باستخدام `/status`
6. استخدم `/stop_stream` للإيقاف

### 🏗️ كيفية العمل

```
┌─────────────────────────────────────────────────┐
│      بوت Telegram (python-telegram-bot)         │
├─────────────────────────────────────────────────┤
│                                                  │
│  أوامر المستخدم:                                │
│  /setup → حفظ في قاعدة البيانات SQLite          │
│  /start_stream → تشغيل عملية FFmpeg             │
│  /stop_stream → إيقاف FFmpeg                    │
│  /status → فحص قاعدة البيانات وحالة العملية   │
│                                                  │
├─────────────────────────────────────────────────┤
│           قاعدة بيانات SQLite                   │
│  ┌──────────────────────────────────────┐       │
│  │ user_id | m3u_url | server_url | ... │       │
│  │ الإعدادات | حالة البث                  │       │
│  └──────────────────────────────────────┘       │
│                                                  │
├─────────────────────────────────────────────────┤
│         إدارة عملية FFmpeg                      │
│                                                  │
│  دعم YouTube:                                    │
│  رابط YouTube → yt-dlp (استخراج رابط البث)      │
│              → FFmpeg (الترميز والبث)           │
│                                                  │
│  قوائم M3U:                                     │
│  رابط M3U → FFmpeg (إضافة فيديو أسود)          │
│        → ترميز منخفض البث                       │
│        → استهلاك موارد بسيط                     │
│                                                  │
│  بثات IPTV:                                     │
│  رابط IPTV → FFmpeg (نسخ البث مباشرة)           │
│          → إعادة اتصال تلقائية عند الفشل        │
│                                                  │
├─────────────────────────────────────────────────┤
│     الإخراج إلى خادم RTMP                       │
│  (OBS أو Nginx RTMP أو منصات أخرى)             │
└─────────────────────────────────────────────────┘
```

### 🔄 منطق البث

#### بثات YouTube
- يستخدم `yt-dlp` لاستخراج رابط البث الفعلي
- يتصل FFmpeg برابط البث المستخرج
- إعادة اتصال تلقائية كل 5 ثوان عند الفشل
- يتضمن Mozilla User-Agent لتوافق أفضل

#### قوائم M3U (الراديو/الصوت)
- إضافة تدفق فيديو أسود (10 FPS، 640x360)
- ترميز منخفض البث (100k) لتوفير موارد الخادم
- الحفاظ على جودة الصوت بدون إعادة ترميز
- نمط أقصر بث (ينتهي الفيديو عند انتهاء الصوت)

#### بثات IPTV
- نسخ البث المباشر بدون إعادة ترميز
- مهلة قراءة 15 ثانية مع إعادة اتصال
- تأخير إعادة محاولة 10 ثوان عند فقدان الاتصال
- محسّنة للبثات المستمرة والمستقرة

### 🐳 نشر Docker

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install yt-dlp

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY streaming_bot.py .

CMD ["python", "streaming_bot.py"]
```

#### البناء والتشغيل
```bash
# بناء الصورة
docker build -t streaming-bot:latest .

# تشغيل الحاوية
docker run -d \
  --name streaming-bot \
  --env BOT_TOKEN="YOUR_BOT_TOKEN" \
  -v $(pwd)/data:/app/data \
  streaming-bot:latest
```

### 🚀 نشر الإنتاج

#### الخيار 1: نشر على VPS (Ubuntu/Debian)

```bash
# 1. الاتصال عبر SSH بخادمك
ssh root@your-server-ip

# 2. تحديث النظام
sudo apt-get update && sudo apt-get upgrade -y

# 3. تثبيت المكتبات
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg git

# 4. استنساخ المستودع
git clone https://github.com/IIDZII/streaming-bot.git
cd streaming-bot

# 5. إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# 6. تثبيت مكتبات Python
pip install -r requirements.txt

# 7. تكوين توكن البوت
nano streaming_bot.py
# عدل BOT_TOKEN = "YOUR_TOKEN"

# 8. إنشاء خدمة systemd
sudo nano /etc/systemd/system/streaming-bot.service
```

#### ملف خدمة Systemd
```ini
[Unit]
Description=Streaming Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/streaming-bot
Environment="PATH=/root/streaming-bot/venv/bin"
ExecStart=/root/streaming-bot/venv/bin/python streaming_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل وتشغيل الخدمة
sudo systemctl daemon-reload
sudo systemctl enable streaming-bot
sudo systemctl start streaming-bot

# التحقق من الحالة
sudo systemctl status streaming-bot

# عرض السجلات
sudo journalctl -u streaming-bot -f
```

#### الخيار 2: نشر Docker

```bash
# استخدام Docker Compose
docker-compose up -d

# عرض السجلات
docker-compose logs -f
```

#### الخيار 3: نشر على منصات سحابية

**Heroku** (الطبقة المجانية ملغاة)
**Railway.app** (موصى به)
**Render.com**

انظر [DEPLOYMENT.md](DEPLOYMENT.md) للأدلة المفصلة.

### 🔐 أفضل ممارسات الأمان

1. **حماية توكن البوت**
   ```bash
   # استخدام متغيرات البيئة
   export BOT_TOKEN="your_token_here"
   
   # أو استخدم ملف .env مع python-dotenv
   ```

2. **نسخ احتياطي من قاعدة البيانات**
   ```bash
   # نسخ احتياطي منتظمة SQLite
   cp stream_manager.db stream_manager.db.backup
   ```

3. **تكوين جدار الحماية**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

### 📊 مخطط قاعدة البيانات

```sql
CREATE TABLE settings (
    user_id INTEGER PRIMARY KEY,
    m3u_url TEXT,
    server_url TEXT,
    stream_key TEXT,
    channel_id TEXT,
    is_running INTEGER DEFAULT 0
);
```

### 🐛 استكشاف الأخطاء

| المشكلة | الحل |
|--------|------|
| البوت لا يرد | تحقق من توكن البوت والاتصال بالإنترنت |
| FFmpeg غير موجود | ثبت FFmpeg: `sudo apt-get install ffmpeg` |
| رفض الأذونات | تحقق من أن البوت مسؤول في القناة |
| البث ينقطع باستمرار | تحقق من قوانين جدار الحماية وحالة خادم RTMP |
| استهلاك عالي للـ CPU | قلل معدل ترميز الفيديو أو الدقة |
| قاعدة البيانات مقفلة | أعد تشغيل خدمة البوت |

### 🤝 المساهمة

المساهمات مرحب بها! يرجى تقديم Pull Request.

```bash
# Fork واستنساخ
git clone https://github.com/YOUR_USERNAME/streaming-bot.git
cd streaming-bot

# إنشاء فرع ميزة
git checkout -b feature/AmazingFeature

# التزام التغييرات
git commit -m 'Add some AmazingFeature'

# دفع إلى الفرع
git push origin feature/AmazingFeature

# فتح Pull Request
```

### 📝 الترخيص

هذا المشروع مرخص بموجب ترخيص MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

### ⭐ دعم المشروع

أعطِ ⭐ إذا ساعدك هذا المشروع!

### 📞 الدعم

- 📧 البريد الإلكتروني: contact@iidzii.dev
- 🔗 GitHub Issues: [إبلاغ عن خطأ](../../issues)
- 💬 النقاشات: [اسأل سؤال](../../discussions)

### 👨‍💻 المؤلف

**IIDZII Dev** - [GitHub](https://github.com/IIDZII)

---

<div align="center">

**[⬆ back to top](#-streaming-bot---بوت-إدارة-البث-المباشر)**

Made with ❤️ by [IIDZII Dev](https://github.com/IIDZII)

</div>
