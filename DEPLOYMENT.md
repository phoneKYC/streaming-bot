# 🚀 Deployment Guide | دليل النشر

<div align="center">

[🌍 English](#-english) • [🌍 العربية](#-العربية)

</div>

---

## 🌍 English

### Table of Contents
1. [Local Development](#local-development)
2. [VPS Deployment](#vps-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Troubleshooting](#troubleshooting)

---

### Local Development

#### Setup

```bash
# Clone repository
git clone https://github.com/IIDZII/streaming-bot.git
cd streaming-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure bot token
export BOT_TOKEN="your_telegram_bot_token"

# Run bot
python streaming_bot.py
```

#### Testing Commands

```bash
# Test bot connectivity
curl -X GET "https://api.telegram.org/botYOUR_BOT_TOKEN/getMe"

# Send test message
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" \
  -d "chat_id=YOUR_CHAT_ID" \
  -d "text=Test message"
```

---

### VPS Deployment

#### Prerequisites
- Ubuntu 20.04 LTS or Debian 11+
- Root or sudo access
- Static IP address
- Domain name (optional)

#### Step-by-Step Installation

##### 1. Server Setup

```bash
# SSH into server
ssh root@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.9 \
    python3-pip \
    python3-venv \
    ffmpeg \
    git \
    curl \
    wget \
    nano \
    supervisor

# Verify installations
python3 --version
ffmpeg -version
```

##### 2. Clone and Setup Application

```bash
# Create application directory
mkdir -p /opt/streaming-bot
cd /opt/streaming-bot

# Clone repository
git clone https://github.com/IIDZII/streaming-bot.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

##### 3. Configure Bot Token

```bash
# Method 1: Using environment variable
echo 'export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"' >> ~/.bashrc
source ~/.bashrc

# Method 2: Using .env file
cat > /opt/streaming-bot/.env << EOF
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
EOF

# Update streaming_bot.py to use environment variable
# At the beginning of the file, add:
# from dotenv import load_dotenv
# load_dotenv()
# BOT_TOKEN = os.getenv('BOT_TOKEN')
```

##### 4. Create Systemd Service

```bash
sudo nano /etc/systemd/system/streaming-bot.service
```

Paste this content:

```ini
[Unit]
Description=Streaming Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/streaming-bot
Environment="PATH=/opt/streaming-bot/venv/bin"
Environment="BOT_TOKEN=YOUR_BOT_TOKEN"
ExecStart=/opt/streaming-bot/venv/bin/python /opt/streaming-bot/streaming_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

##### 5. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable streaming-bot

# Start service
sudo systemctl start streaming-bot

# Check status
sudo systemctl status streaming-bot

# View logs
sudo journalctl -u streaming-bot -f

# Stop service
sudo systemctl stop streaming-bot

# Restart service
sudo systemctl restart streaming-bot
```

##### 6. Configure Firewall (UFW)

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP (if needed)
sudo ufw allow 80/tcp

# Allow HTTPS (if needed)
sudo ufw allow 443/tcp

# Check status
sudo ufw status

# Delete a rule
sudo ufw delete allow 80/tcp
```

##### 7. Database Backup

```bash
# Create backup directory
mkdir -p /opt/streaming-bot/backups

# Automated backup script
cat > /opt/streaming-bot/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/streaming-bot/backups"
DB_FILE="/opt/streaming-bot/stream_manager.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp $DB_FILE $BACKUP_DIR/stream_manager_$TIMESTAMP.db
echo "Backup created: stream_manager_$TIMESTAMP.db"
EOF

chmod +x /opt/streaming-bot/backup.sh

# Add cron job for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/streaming-bot/backup.sh") | crontab -
```

##### 8. Monitor Service (Optional)

```bash
# Install monitoring tools
sudo apt install -y htop iotop

# Monitor bot process
htop -p $(pgrep -f "streaming_bot.py")
```

---

### Docker Deployment

#### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN pip install yt-dlp

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application
COPY streaming_bot.py .

# Run bot
CMD ["python", "streaming_bot.py"]
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  streaming-bot:
    build: .
    container_name: streaming-bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
    volumes:
      - ./data:/app/data
      - ./stream_manager.db:/app/stream_manager.db
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Build and Run

```bash
# Build image
docker build -t streaming-bot:latest .

# Run container
docker run -d \
  --name streaming-bot \
  -e BOT_TOKEN="YOUR_BOT_TOKEN" \
  -v $(pwd)/data:/app/data \
  --restart always \
  streaming-bot:latest

# Or using Docker Compose
docker-compose up -d

# View logs
docker logs -f streaming-bot

# Stop container
docker stop streaming-bot

# Remove container
docker rm streaming-bot
```

#### Docker Commands

```bash
# List containers
docker ps -a

# View logs
docker logs streaming-bot

# Execute command in container
docker exec -it streaming-bot bash

# Copy file from container
docker cp streaming-bot:/app/stream_manager.db ./

# Monitor resources
docker stats streaming-bot
```

---

### Cloud Platforms

#### Railway.app (Recommended)

Railway.app is a modern platform with generous free tier.

##### Setup Steps

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your streaming-bot repository

3. **Configure Environment Variables**
   - Go to Variables tab
   - Add: `BOT_TOKEN` = your_telegram_bot_token

4. **Deploy**
   - Railway automatically deploys from main branch
   - Check deployment logs in the dashboard

5. **Monitor**
   - View logs in Railway dashboard
   - Monitor resource usage

##### Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# View logs
railway logs

# Set environment variable
railway variables set BOT_TOKEN="your_token"
```

---

#### Render.com

##### Setup Steps

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Background Worker**
   - New → Background Worker
   - Connect GitHub repository
   - Build command: `pip install -r requirements.txt`
   - Start command: `python streaming_bot.py`

3. **Set Environment Variables**
   - Environment → Add environment variable
   - Key: `BOT_TOKEN`
   - Value: your_telegram_bot_token

4. **Deploy and Monitor**
   - Render automatically deploys
   - View logs in Logs tab

---

#### Heroku (Legacy - Paid)

Note: Heroku free tier was discontinued. Use Railway or Render instead.

---

### Performance Optimization

#### Reduce CPU Usage

```bash
# Lower video bitrate in streaming_bot.py
# Change: -b:v 100k
# To: -b:v 50k  # Lower bitrate

# Reduce resolution
# Change: s=640x360
# To: s=320x240  # Lower resolution
```

#### Monitor Resource Usage

```bash
# CPU and Memory
top -b -n 1 | head -n 20

# Disk usage
df -h

# Database size
du -h stream_manager.db

# FFmpeg process
ps aux | grep ffmpeg
```

---

### Troubleshooting

#### Bot Not Responding

```bash
# Check if service is running
sudo systemctl status streaming-bot

# Check logs
sudo journalctl -u streaming-bot -n 50

# Restart service
sudo systemctl restart streaming-bot

# Verify bot token
curl -X GET "https://api.telegram.org/botYOUR_BOT_TOKEN/getMe"
```

#### FFmpeg Errors

```bash
# Test FFmpeg directly
ffmpeg -re -i "test_stream_url" -c:v copy -c:a copy -f flv rtmp://test-server/live/test_key

# Check FFmpeg installation
ffmpeg -version

# Install missing codecs
sudo apt-get install -y libavcodec-extra
```

#### Database Issues

```bash
# Check database integrity
sqlite3 stream_manager.db "PRAGMA integrity_check;"

# Optimize database
sqlite3 stream_manager.db "VACUUM;"

# Backup database
cp stream_manager.db stream_manager.db.backup
```

---

## 🌍 العربية

### جدول المحتويات
1. [التطوير المحلي](#التطوير-المحلي)
2. [نشر VPS](#نشر-vps)
3. [نشر Docker](#نشر-docker)
4. [منصات السحابة](#منصات-السحابة)
5. [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

### التطوير المحلي

#### الإعداد

```bash
# استنساخ المستودع
git clone https://github.com/IIDZII/streaming-bot.git
cd streaming-bot

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements.txt

# تكوين توكن البوت
export BOT_TOKEN="your_telegram_bot_token"

# تشغيل البوت
python streaming_bot.py
```

#### اختبار الأوامر

```bash
# اختبار اتصال البوت
curl -X GET "https://api.telegram.org/botYOUR_BOT_TOKEN/getMe"

# إرسال رسالة اختبار
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" \
  -d "chat_id=YOUR_CHAT_ID" \
  -d "text=Test message"
```

---

### نشر VPS

#### المتطلبات
- Ubuntu 20.04 LTS أو Debian 11+
- وصول جذر أو sudo
- عنوان IP ثابت
- نطاق (اختياري)

#### التثبيت خطوة بخطوة

##### 1. إعداد الخادم

```bash
# الاتصال عبر SSH
ssh root@your-server-ip

# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المكتبات
sudo apt install -y \
    python3.9 \
    python3-pip \
    python3-venv \
    ffmpeg \
    git \
    curl \
    wget \
    nano \
    supervisor

# التحقق من التثبيتات
python3 --version
ffmpeg -version
```

##### 2. استنساخ وإعداد التطبيق

```bash
# إنشاء دليل التطبيق
mkdir -p /opt/streaming-bot
cd /opt/streaming-bot

# استنساخ المستودع
git clone https://github.com/IIDZII/streaming-bot.git .

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements.txt
pip install gunicorn
```

##### 3. تكوين توكن البوت

```bash
# الطريقة 1: استخدام متغير البيئة
echo 'export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"' >> ~/.bashrc
source ~/.bashrc

# الطريقة 2: استخدام ملف .env
cat > /opt/streaming-bot/.env << EOF
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
EOF

# تحديث streaming_bot.py لاستخدام متغير البيئة
# أضف في بداية الملف:
# from dotenv import load_dotenv
# load_dotenv()
# BOT_TOKEN = os.getenv('BOT_TOKEN')
```

##### 4. إنشاء خدمة Systemd

```bash
sudo nano /etc/systemd/system/streaming-bot.service
```

ألصق هذا المحتوى:

```ini
[Unit]
Description=Streaming Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/streaming-bot
Environment="PATH=/opt/streaming-bot/venv/bin"
Environment="BOT_TOKEN=YOUR_BOT_TOKEN"
ExecStart=/opt/streaming-bot/venv/bin/python /opt/streaming-bot/streaming_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

##### 5. تفعيل وتشغيل الخدمة

```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل عند الإقلاع
sudo systemctl enable streaming-bot

# تشغيل الخدمة
sudo systemctl start streaming-bot

# التحقق من الحالة
sudo systemctl status streaming-bot

# عرض السجلات
sudo journalctl -u streaming-bot -f

# إيقاف الخدمة
sudo systemctl stop streaming-bot

# إعادة تشغيل الخدمة
sudo systemctl restart streaming-bot
```

##### 6. تكوين جدار الحماية (UFW)

```bash
# تفعيل جدار الحماية
sudo ufw enable

# السماح بـ SSH
sudo ufw allow 22/tcp

# السماح بـ HTTP (إذا لزم الأمر)
sudo ufw allow 80/tcp

# السماح بـ HTTPS (إذا لزم الأمر)
sudo ufw allow 443/tcp

# التحقق من الحالة
sudo ufw status

# حذف قاعدة
sudo ufw delete allow 80/tcp
```

##### 7. النسخ الاحتياطي لقاعدة البيانات

```bash
# إنشاء دليل النسخ الاحتياطية
mkdir -p /opt/streaming-bot/backups

# سكريبت النسخ الاحتياطية الآلي
cat > /opt/streaming-bot/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/streaming-bot/backups"
DB_FILE="/opt/streaming-bot/stream_manager.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp $DB_FILE $BACKUP_DIR/stream_manager_$TIMESTAMP.db
echo "تم إنشاء نسخة احتياطية: stream_manager_$TIMESTAMP.db"
EOF

chmod +x /opt/streaming-bot/backup.sh

# إضافة مهمة cron لنسخ احتياطية يومية
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/streaming-bot/backup.sh") | crontab -
```

##### 8. مراقبة الخدمة (اختياري)

```bash
# تثبيت أدوات المراقبة
sudo apt install -y htop iotop

# مراقبة عملية البوت
htop -p $(pgrep -f "streaming_bot.py")
```

---

### نشر Docker

#### Dockerfile

أنشئ `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# تعيين دليل العمل
WORKDIR /app

# تثبيت مكتبات النظام
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# تثبيت yt-dlp
RUN pip install yt-dlp

# نسخ requirements
COPY requirements.txt .

# تثبيت مكتبات Python
RUN pip install -r requirements.txt

# نسخ التطبيق
COPY streaming_bot.py .

# تشغيل البوت
CMD ["python", "streaming_bot.py"]
```

#### Docker Compose

أنشئ `docker-compose.yml`:

```yaml
version: '3.8'

services:
  streaming-bot:
    build: .
    container_name: streaming-bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
    volumes:
      - ./data:/app/data
      - ./stream_manager.db:/app/stream_manager.db
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### البناء والتشغيل

```bash
# بناء الصورة
docker build -t streaming-bot:latest .

# تشغيل الحاوية
docker run -d \
  --name streaming-bot \
  -e BOT_TOKEN="YOUR_BOT_TOKEN" \
  -v $(pwd)/data:/app/data \
  --restart always \
  streaming-bot:latest

# أو استخدام Docker Compose
docker-compose up -d

# عرض السجلات
docker logs -f streaming-bot

# إيقاف الحاوية
docker stop streaming-bot

# حذف الحاوية
docker rm streaming-bot
```

#### أوامر Docker

```bash
# قائمة الحاويات
docker ps -a

# عرض السجلات
docker logs streaming-bot

# تنفيذ أمر في الحاوية
docker exec -it streaming-bot bash

# نسخ ملف من الحاوية
docker cp streaming-bot:/app/stream_manager.db ./

# مراقبة الموارد
docker stats streaming-bot
```

---

### منصات السحابة

#### Railway.app (موصى به)

Railway.app هي منصة حديثة مع طبقة مجانية كريمة.

##### خطوات الإعداد

1. **إنشاء حساب Railway**
   - اذهب إلى [railway.app](https://railway.app)
   - سجل باستخدام GitHub

2. **إنشاء مشروع جديد**
   - انقر على "New Project"
   - اختر "Deploy from GitHub repo"
   - ربط حسابك على GitHub
   - اختر مستودع streaming-bot

3. **تكوين متغيرات البيئة**
   - اذهب إلى علامة تبويب Variables
   - أضف: `BOT_TOKEN` = توكنك

4. **نشر**
   - Railway تنشر تلقائياً من فرع main
   - تحقق من سجلات النشر في لوحة التحكم

5. **مراقبة**
   - اعرض السجلات في لوحة تحكم Railway
   - راقب استخدام الموارد

##### Railway CLI

```bash
# تثبيت Railway CLI
npm i -g @railway/cli

# تسجيل الدخول
railway login

# ربط المشروع
railway link

# نشر
railway up

# عرض السجلات
railway logs

# تعيين متغير البيئة
railway variables set BOT_TOKEN="your_token"
```

---

#### Render.com

##### خطوات الإعداد

1. **إنشاء حساب Render**
   - اذهب إلى [render.com](https://render.com)
   - سجل باستخدام GitHub

2. **إنشاء Background Worker**
   - New → Background Worker
   - ربط مستودع GitHub
   - Build command: `pip install -r requirements.txt`
   - Start command: `python streaming_bot.py`

3. **تعيين متغيرات البيئة**
   - Environment → Add environment variable
   - Key: `BOT_TOKEN`
   - Value: توكنك

4. **النشر والمراقبة**
   - Render تنشر تلقائياً
   - اعرض السجلات في علامة تبويب Logs

---

#### Heroku (قديم - مدفوع)

ملاحظة: تم إيقاف الطبقة المجانية من Heroku. استخدم Railway أو Render بدلاً منها.

---

### تحسين الأداء

#### تقليل استهلاك CPU

```bash
# خفض معدل ترميز الفيديو في streaming_bot.py
# غيّر: -b:v 100k
# إلى: -b:v 50k  # معدل أقل

# تقليل الدقة
# غيّر: s=640x360
# إلى: s=320x240  # دقة أقل
```

#### مراقبة استخدام الموارد

```bash
# وحدة المعالجة والذاكرة
top -b -n 1 | head -n 20

# استخدام القرص
df -h

# حجم قاعدة البيانات
du -h stream_manager.db

# عملية FFmpeg
ps aux | grep ffmpeg
```

---

### استكشاف الأخطاء

#### البوت لا يرد

```bash
# التحقق مما إذا كانت الخدمة تعمل
sudo systemctl status streaming-bot

# عرض السجلات
sudo journalctl -u streaming-bot -n 50

# إعادة تشغيل الخدمة
sudo systemctl restart streaming-bot

# التحقق من توكن البوت
curl -X GET "https://api.telegram.org/botYOUR_BOT_TOKEN/getMe"
```

#### أخطاء FFmpeg

```bash
# اختبار FFmpeg مباشرة
ffmpeg -re -i "test_stream_url" -c:v copy -c:a copy -f flv rtmp://test-server/live/test_key

# التحقق من تثبيت FFmpeg
ffmpeg -version

# تثبيت الترميزات المفقودة
sudo apt-get install -y libavcodec-extra
```

#### مشاكل قاعدة البيانات

```bash
# التحقق من سلامة قاعدة البيانات
sqlite3 stream_manager.db "PRAGMA integrity_check;"

# تحسين قاعدة البيانات
sqlite3 stream_manager.db "VACUUM;"

# النسخ الاحتياطي لقاعدة البيانات
cp stream_manager.db stream_manager.db.backup
```

---

<div align="center">

Made with ❤️ by [IIDZII Dev](https://github.com/IIDZII)

</div>
