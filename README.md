# 🛡️ Streaming Bot | بوت البث المباشر - النسخة المُحصَّنة

<div align="center">

![Streaming Bot Banner](https://img.shields.io/badge/Version-2.0.0%20Hardened-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram&logoColor=white)
![Security](https://img.shields.io/badge/Security-Hardened-red?style=for-the-badge)

[![Security Audited](https://img.shields.io/badge/Security-Audited%20%E2%9C%93-brightgreen?style=for-the-badge)](#-security-hardening)
[![No shell=True](https://img.shields.io/badge/subprocess-shell%3DFalse-brightgreen?style=for-the-badge)](#-security-hardening)
[![Non-root Docker](https://img.shields.io/badge/Docker-Non--root%20User-brightgreen?style=for-the-badge)](#-docker-deployment)

<p>
  <a href="#english">🌍 English</a> •
  <a href="#العربية">🇸🇦 العربية</a> •
  <a href="#-features">✨ Features</a> •
  <a href="#-installation">📥 Installation</a> •
  <a href="#-security-hardening">🔐 Security</a> •
  <a href="#-documentation">📖 Docs</a>
</p>

</div>

---

## 🌍 English

### 📋 About

**Streaming Bot (Hardened Edition)** is a production-ready Telegram bot for relaying live streams (YouTube / M3U / IPTV / Radio) to RTMP destinations with **enterprise-grade security hardening**. Built on top of the original `phoneKYC/streaming-bot`, this version completely eliminates the critical RCE vulnerability, adds per-user stream isolation, real bilingual i18n, and a conversational setup wizard replacing the error-prone 4-argument command.

Designed for broadcasters who need a **secure, multi-tenant, maintainable** stream-relay bot.

### 🔥 What's New in v2.0.0 (Hardened Edition)

This is a **complete security-focused rewrite** addressing 10 critical issues from the original:

| # | Original Issue | Severity | Fix |
|---|----------------|----------|-----|
| 1 | RCE via `shell=True` + f-string interpolation | 🔴 Critical | All subprocess calls use **list args** (`create_subprocess_exec`) |
| 2 | No authentication | 🔴 Critical | `ADMIN_IDS` env whitelist + DB `users` table |
| 3 | Single global `process_pointer` (one stream max) | 🟠 High | Per-user `dict[StreamProcess]` with `asyncio.Lock` |
| 4 | No inline buttons (text commands only) | 🟡 Medium | `ConversationHandler` + `InlineKeyboardMarkup` everywhere |
| 5 | False bilingual claim (Arabic only at runtime) | 🟡 Medium | Real i18n with 50+ keys per language, switchable per user |
| 6 | Fragile Markdown (no escaping) | 🟡 Medium | `MarkdownV2` + `md_escape()` for all dynamic values |
| 7 | Anti-circumvention headers (`Referer: x.com`) | 🟠 High | Removed; neutral `User-Agent` only |
| 8 | Broken Docker healthcheck (curl /health on polling bot) | 🟠 High | Real `healthcheck.py` with 4 actual checks |
| 9 | Running as root in container | 🟡 Medium | Dedicated `botuser` (UID 1000) + `cap_drop: ALL` |
| 10 | No `channel_id` validation | 🟠 High | Strict validators for URL / server / channel_id |

> 📄 **Full fix report:** see [`FIXES_REPORT.md`](./FIXES_REPORT.md)

### ✨ Features

<table>
  <tr>
    <td>🎥 <b>Multi-Source Support</b></td>
    <td>YouTube Live, M3U/M3U8, IPTV, Radio (with auto-detection)</td>
  </tr>
  <tr>
    <td>🔐 <b>Authentication Layer</b></td>
    <td>ADMIN_IDS env whitelist + DB authorization + <code>/authorize</code> admin command</td>
  </tr>
  <tr>
    <td>👥 <b>True Multi-tenancy</b></td>
    <td>Per-user isolated FFmpeg processes (<code>dict[StreamProcess]</code> + asyncio.Lock)</td>
  </tr>
  <tr>
    <td>💬 <b>Conversational Setup Wizard</b></td>
    <td>5-step <code>ConversationHandler</code> with inline Cancel/Confirm buttons</td>
  </tr>
  <tr>
    <td>🌐 <b>Real Bilingual i18n</b></td>
    <td>Arabic & English with 50+ translation keys, switchable per user via <code>/language</code></td>
  </tr>
  <tr>
    <td>📝 <b>MarkdownV2 Safe Formatting</b></td>
    <td>Proper <code>md_escape()</code> on all dynamic values; no broken formatting</td>
  </tr>
  <tr>
    <td>🔄 <b>Python-side Reconnect Loop</b></td>
    <td>No bash <code>while true</code>; <code>asyncio</code> task per user with stop event</td>
  </tr>
  <tr>
    <td>💾 <b>Persistent Storage</b></td>
    <td>SQLite with <code>settings</code> + <code>users</code> tables, thread-safe access</td>
  </tr>
  <tr>
    <td>🛡️ <b>Permission Validation</b></td>
    <td>Auto-checks bot admin status + <code>can_post_messages</code> in target channel</td>
  </tr>
  <tr>
    <td>🐳 <b>Hardened Docker</b></td>
    <td>Non-root user, <code>cap_drop: ALL</code>, <code>no-new-privileges</code>, real healthcheck</td>
  </tr>
  <tr>
    <td>♻️ <b>Auto-resume on Restart</b></td>
    <td>Active streams are restored on bot restart (<code>post_init</code>)</td>
  </tr>
  <tr>
    <td>⚙️ <b>Optimized Encoding</b></td>
    <td>Black-canvas overlay for radio (low CPU), stream copy for IPTV (low bandwidth)</td>
  </tr>
</table>

### 🔧 Technical Stack

```
┌─────────────────────────────────────────────┐
│  Framework & Libraries                      │
├─────────────────────────────────────────────┤
│ • Python 3.11+                              │
│ • python-telegram-bot v21.6 (async)         │
│ • FFmpeg (video processing, list args)      │
│ • yt-dlp 2024.8.6 (YouTube extraction)      │
│ • SQLite3 (settings + users tables)         │
│ • asyncio (per-user stream workers)         │
│ • Docker (non-root, hardened)               │
└─────────────────────────────────────────────┘
```

### 🚀 Quick Start

#### 1. Prerequisites

```bash
# System dependencies
sudo apt-get install -y python3.11 python3.11-venv ffmpeg git

# Python requirements
pip install -r requirements.txt
# yt-dlp installed via Dockerfile or: pip install yt-dlp==2024.8.6
```

#### 2. Get Your Telegram IDs

1. Create a bot via **[@BotFather](https://t.me/BotFather)** → get `BOT_TOKEN`
2. Get your user ID via **[@userinfobot](https://t.me/userinfobot)** → this is your `ADMIN_ID`

#### 3. Clone & Configure

```bash
git clone <your-fork-url> streaming-bot
cd streaming-bot

python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
nano .env
```

Edit `.env`:
```env
BOT_TOKEN=123456:ABC-DEF...your_token_from_botfather
ADMIN_IDS=123456789           # your Telegram user ID (comma-separated for multiple)
DEFAULT_LANGUAGE=ar           # ar or en
```

#### 4. Run

```bash
python streaming_bot.py
```

Or with Docker (recommended for production):
```bash
docker compose up -d --build
docker compose logs -f
```

### 📖 Command Reference

| Command | Purpose | Auth |
|---------|---------|------|
| `/start` | Show main menu with inline buttons | All authorized users |
| `/setup` | Launch 5-step setup wizard (conversational) | All authorized users |
| `/start_stream` | Start streaming (also via button) | All authorized users |
| `/stop_stream` | Stop your active stream (also via button) | All authorized users |
| `/status` | Show your stream status + FFmpeg PID | All authorized users |
| `/language` | Switch interface language (AR/EN) | All authorized users |
| `/help` | Show help with legal notice | All authorized users |
| `/authorize <user_id>` | Authorize a new user | **Admins only** |

### 💬 Conversation Flow (Setup Wizard)

The error-prone `/setup "url" "server" "key" "channel_id"` is replaced by a guided 5-step wizard:

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Stream URL                                         │
│  📡 Send the stream URL (e.g. https://youtu.be/xxx)         │
│  [❌ Cancel]                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓ (validated)
┌─────────────────────────────────────────────────────────────┐
│  Step 2: RTMP Server URL                                    │
│  🖥️ Send the RTMP server URL (e.g. rtmp://server.com/live/) │
│  [❌ Cancel]                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓ (validated)
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Stream Key                                         │
│  🔑 Send the stream key                                     │
│  [❌ Cancel]                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓ (validated)
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Channel ID                                         │
│  📣 Send the channel ID (-100xxxx or @username)             │
│  [❌ Cancel]                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓ (validated)
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Review & Confirm                                   │
│  📋 Review settings before saving:                          │
│     📡 Stream URL: https://...                              │
│     🖥️ Server: rtmp://...                                   │
│     🔑 Key: ••••••••••••                                    │
│     📣 Channel: -1001234567890                              │
│     📡 Stream type: 🎬 YouTube Live                         │
│  [✅ Confirm & Save]  [❌ Cancel]                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ✅ Settings saved!
```

### 🏗️ Architecture

```
                       ┌──────────────────────┐
                       │  Telegram User (DM)  │
                       └──────────┬───────────┘
                                  │ /start or button click
                                  ▼
                       ┌──────────────────────┐
                       │  python-telegram-bot │
                       │  (async, polling)    │
                       └──────────┬───────────┘
                                  │
              ┌───────────────────┼────────────────────┐
              ▼                   ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │  Auth Layer     │  │  SQLite DB      │  │  i18n Layer     │
    │  ADMIN_IDS +    │  │  settings +     │  │  AR / EN dict   │
    │  users table    │  │  users tables   │  │  per-user lang  │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
                                  │
                                  ▼
              ┌───────────────────────────────────────┐
              │  Per-User Stream Manager              │
              │  dict[user_id, StreamProcess]         │
              │  + asyncio.Lock                       │
              │                                       │
              │  For each active user:                │
              │    asyncio.Task → _stream_worker()    │
              │       ├─ yt-dlp (list args)           │
              │       └─ ffmpeg (list args)           │
              └───────────────────┬───────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │  RTMP Destination    │
                       │  (YouTube Live /     │
                       │   Custom RTMP / OBS) │
                       └──────────────────────┘
```

### 📊 How It Works

**1. YouTube Live streams**
- `yt-dlp` extracts the live URL (called via `create_subprocess_exec` with list args — no shell)
- FFmpeg copies video + audio to RTMP destination
- Python-side `while not stop_event.is_set()` re-extracts every 15s to refresh expiring tickets
- Per-user asyncio task; stopping one user does not affect others

**2. Radio / Audio streams**
- Black canvas overlay (`color=c=black:s=640x360:r=10`) — minimal CPU
- Audio re-encoded to AAC 128k
- Suitable for 24/7 radio / Quran stations

**3. IPTV streams**
- Direct stream copy (`-c:v copy -c:a copy`) — minimal CPU
- Python-side reconnect with configurable delay
- No anti-circumvention headers (just a standard User-Agent)

### 🔐 Security Hardening

This is the **most important section** — read it carefully.

#### ✅ RCE Prevention
- **Zero** `shell=True` calls (verified via AST analysis)
- **Zero** `subprocess.Popen(bash_command, shell=True)` patterns
- **Zero** `asyncio.create_subprocess_shell` calls
- All FFmpeg and yt-dlp invocations use **list args**: `["ffmpeg", "-i", url, ...]`
- A malicious input like `"; rm -rf / #` as a stream URL is treated as a single argv element — it cannot execute as a shell command

#### ✅ Authentication
- Bot refuses all commands from unauthorized users
- Two-tier authorization:
  1. `ADMIN_IDS` env variable (Telegram user IDs, comma-separated)
  2. `users.is_authorized = 1` in DB (set via `/authorize <user_id>` by an admin)
- `@authorized_only` decorator wraps every handler

#### ✅ Input Validation
Strict validators on every user input:
- `is_valid_stream_url()` — only `http/https/rtmp/rtmps/rtsp` schemes (blocks `javascript:`, `file:`, etc.)
- `is_valid_server_url()` — only `rtmp/rtmps/http/https` for destination
- `is_valid_channel_id()` — only `-100xxxxxxxxxx`, `@username`, or numeric IDs (blocks `"; rm -rf /`, `$(whoami)`)

#### ✅ Per-User Isolation
- Each user has their own `StreamProcess` (Popen + asyncio.Task + stop_event)
- `asyncio.Lock` protects the `_processes` dict
- User B cannot stop User A's stream

#### ✅ Markdown Safety
- `MarkdownV2` parse mode (not legacy `Markdown`)
- `md_escape()` on every dynamic value (URLs, channel IDs, error messages)
- Escapes all 12 special characters: `_*[]()~\`>#+-=|{}.!`

#### ✅ Docker Hardening
- Runs as `botuser` (UID 1000), not root
- `cap_drop: ALL` (drops all Linux capabilities)
- `cap_add: SETUID, SETGID` only (needed for subprocess management)
- `security_opt: no-new-privileges:true`
- `restart: unless-stopped` (not `always` — won't restart on intentional stop)

#### ✅ Real Healthcheck
The original `python -c "import sys; sys.exit(0)"` always returned 0 (useless). The new `healthcheck.py` runs 4 actual checks:

| Check | What it verifies |
|-------|------------------|
| DB file exists | SQLite file is present and non-empty |
| DB tables present | Both `settings` and `users` tables exist |
| Active streams consistent | If DB says a stream is running, an `ffmpeg` process actually exists |
| Python process alive | The bot's main Python process is running |

If any check fails → exit 1 → Docker restarts the container.

### 🐳 Docker Deployment

#### Option A: Docker Compose (recommended)

```bash
cp .env.example .env
# Edit .env with BOT_TOKEN and ADMIN_IDS
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down
```

#### Option B: Plain Docker

```bash
docker build -t streaming-bot:hardened .

docker run -d \
  --name streaming-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  --cap-add SETUID \
  --cap-add SETGID \
  streaming-bot:hardened
```

### 🚀 Production Deployment

#### VPS with systemd (without Docker)

```bash
# Ubuntu/Debian setup
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3.11 python3.11-venv ffmpeg git

# Clone & install
git clone <your-fork-url> /opt/streaming-bot
cd /opt/streaming-bot
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install yt-dlp==2024.8.6

# Configure
cp .env.example .env
nano .env  # Set BOT_TOKEN and ADMIN_IDS

# Create systemd service
sudo tee /etc/systemd/system/streaming-bot.service <<EOF
[Unit]
Description=Streaming Bot (Hardened)
After=network.target

[Service]
Type=simple
User=streambot
Group=streambot
WorkingDirectory=/opt/streaming-bot
EnvironmentFile=/opt/streaming-bot/.env
ExecStart=/opt/streaming-bot/venv/bin/python streaming_bot.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo useradd -r -s /bin/false streambot
sudo chown -R streambot:streambot /opt/streaming-bot
sudo systemctl daemon-reload
sudo systemctl enable --now streaming-bot
sudo systemctl status streaming-bot
```

#### Cloud Platforms
- **Hetzner Cloud** (recommended VPS — €5/month, 1 vCPU/2GB is enough)
- **Railway.app** (container deployment)
- **Render.com** (alternative)

### 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot says "🚫 Not authorized" | Add your user ID to `ADMIN_IDS` in `.env`, or ask an admin to run `/authorize <your_id>` |
| `ADMIN_IDS is empty` warning in logs | Set `ADMIN_IDS=123456789` in `.env` (get your ID from `@userinfobot`) |
| Bot not responding | Verify `BOT_TOKEN` and internet connection; check `docker compose logs` |
| FFmpeg not found | `sudo apt-get install ffmpeg` (or use Docker image which includes it) |
| Permission denied in channel | Make the bot an **admin** of the target channel with **Post Messages** permission |
| Stream disconnects | Check firewall & RTMP server status; check `RECONNECT_DELAY` |
| High CPU usage | Reduce bitrate in `_build_ffmpeg_cmd_radio()` or use radio mode for audio-only |
| MarkdownV2 parse error | All dynamic values should go through `md_escape()` — report if you see this |
| Container restarts constantly | Run `python healthcheck.py` manually to see which check fails |
| `yt-dlp` fails on YouTube | Update: `pip install --upgrade yt-dlp==2024.8.6` |

### 📖 Documentation

- 📘 **[FIXES_REPORT.md](./FIXES_REPORT.md)** — Full security fix report (10 issues addressed)
- 📘 [Installation Guide](./DEPLOYMENT.md)
- 🔐 [Security Guide](./SECURITY.md)
- 🤝 [Contributing](./CONTRIBUTING.md)
- 📝 [Changelog](./CHANGELOG.md)

### ⚖️ Legal Notice

This bot is a **neutral technical tool** for stream relay. The operator is solely responsible for:

- ✅ Owning the rights to redistribute the source stream
- ✅ Complying with the source platform's Terms of Service (YouTube ToS, IPTV provider terms, etc.)
- ✅ Complying with local broadcast redistribution laws in their jurisdiction

The Hardened Edition **removed** the original's anti-circumvention features (`Referer: x.com` spoofing, "Anti-Block" headers). Using the bot to redistribute copyrighted content without a license may expose the operator to legal liability.

### 🤝 Contributing

We welcome contributions! Please ensure your PR:

1. Does **not** reintroduce `shell=True` anywhere
2. Does **not** add anti-circumvention headers (Referer spoofing, etc.)
3. Validates all user inputs through the existing validators
4. Uses `MarkdownV2` with `md_escape()` for any dynamic text
5. Passes the existing test suite (`python -c "from streaming_bot import *; ..."`)

```bash
# Standard workflow
git checkout -b feature/AmazingFeature
git commit -m 'Add AmazingFeature'
git push origin feature/AmazingFeature
# Open PR
```

### 📝 License

This project is licensed under the **MIT License** — see [LICENSE](./LICENSE) file for details.

### 💬 Support & Contact

- 🐛 **Issues**: [GitHub Issues](https://github.com/phoneKYC/streaming-bot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/phoneKYC/streaming-bot/discussions)

### 👨‍💻 Development

**Hardened Edition by:** Security audit & rewrite
**Original project:** [phoneKYC/streaming-bot](https://github.com/phoneKYC/streaming-bot)

---

## 🇸🇦 العربية

### 📋 نبذة عن المشروع

**بوت البث - النسخة المُحصَّنة** هو بوت Telegram جاهز للإنتاج لإدارة ترحيل البث المباشر (YouTube / M3U / IPTV / الراديو) إلى وجهات RTMP مع **تحصين أمني بمستوى المؤسسات**. بُني هذا الإصدار على البوت الأصلي `phoneKYC/streaming-bot`، لكنه يُعالج بالكامل ثغرة RCE الحرجة، ويضيف عزل بث لكل مستخدم، وثنائية لغة حقيقية، ومعالج ضبط تفاعلي يحل محل الأمر النصي المُعرَّض للأخطاء بأربع وسائط.

مُصمَّم للمذيعين الذين يحتاجون بوت ترحيل بث **آمن ومتعدد المستخدمين وقابل للصيانة**.

### 🔥 ما الجديد في الإصدار 2.0.0 (النسخة المُحصَّنة)

هذه **إعادة كتابة كاملة مُركَّزة على الأمان** تُعالج 10 مشاكل حرجة من النسخة الأصلية:

| # | المشكلة الأصلية | الخطورة | الإصلاح |
|---|----------------|---------|---------|
| 1 | ثغرة RCE عبر `shell=True` + f-strings | 🔴 حرجة | كل استدعاءات subprocess تستخدم **قائمة وسائط** (`create_subprocess_exec`) |
| 2 | لا مصادقة | 🔴 حرجة | قائمة `ADMIN_IDS` البيئية + جدول `users` في DB |
| 3 | متغير عام `process_pointer` واحد (بث واحد فقط) | 🟠 عالية | `dict[StreamProcess]` لكل مستخدم مع `asyncio.Lock` |
| 4 | لا أزرار تفاعلية (أوامر نصية فقط) | 🟡 متوسطة | `ConversationHandler` + `InlineKeyboardMarkup` في كل مكان |
| 5 | ادّعاء ثنائية اللغة كاذب (عربي فقط وقت التشغيل) | 🟡 متوسطة | i18n حقيقي بـ 50+ مفتاح لكل لغة، قابل للتبديل لكل مستخدم |
| 6 | Markdown هش (بدون escaping) | 🟡 متوسطة | `MarkdownV2` + `md_escape()` لكل القيم الديناميكية |
| 7 | ترويسات تخطّي حماية (`Referer: x.com`) | 🟠 عالية | أُزيلت؛ فقط `User-Agent` قياسية ومحايدة |
| 8 | Docker healthcheck مكسور (curl /health على بوت polling) | 🟠 عالية | `healthcheck.py` حقيقي بـ 4 فحوصات فعلية |
| 9 | تشغيل كـ root في الحاوية | 🟡 متوسطة | مستخدم مخصص `botuser` (UID 1000) + `cap_drop: ALL` |
| 10 | لا تحقق من `channel_id` | 🟠 عالية |.validators صارمة لـ URL / server / channel_id |

> 📄 **تقرير الإصلاحات الكامل:** راجع [`FIXES_REPORT.md`](./FIXES_REPORT.md)

### ✨ المميزات الرئيسية

<table>
  <tr>
    <td>🎥 <b>دعم مصادر متعددة</b></td>
    <td>YouTube Live, M3U/M3U8, IPTV, الراديو (مع كشف تلقائي)</td>
  </tr>
  <tr>
    <td>🔐 <b>طبقة مصادقة</b></td>
    <td>قائمة ADMIN_IDS بيئية + تخويل في DB + أمر <code>/authorize</code> للمدراء</td>
  </tr>
  <tr>
    <td>👥 <b>تعدد مستخدمين حقيقي</b></td>
    <td>عمليات FFmpeg معزولة لكل مستخدم (<code>dict[StreamProcess]</code> + asyncio.Lock)</td>
  </tr>
  <tr>
    <td>💬 <b>معالج ضبط تفاعلي</b></td>
    <td><code>ConversationHandler</code> من 5 خطوات مع أزرار Cancel/Confirm</td>
  </tr>
  <tr>
    <td>🌐 <b>ثنائية لغة حقيقية</b></td>
    <td>عربي وإنجليزي بـ 50+ مفتاح ترجمة، قابل للتبديل لكل مستخدم عبر <code>/language</code></td>
  </tr>
  <tr>
    <td>📝 <b>تنسيق MarkdownV2 آمن</b></td>
    <td><code>md_escape()</code> صحيح على كل القيم الديناميكية؛ لا تنسيق مكسور</td>
  </tr>
  <tr>
    <td>🔄 <b>حلقة إعادة اتصال في Python</b></td>
    <td>لا <code>while true</code> bash؛ مهمة <code>asyncio</code> لكل مستخدم مع stop event</td>
  </tr>
  <tr>
    <td>💾 <b>تخزين دائم</b></td>
    <td>SQLite مع جدولي <code>settings</code> و<code>users</code>، وصول آمن من thread</td>
  </tr>
  <tr>
    <td>🛡️ <b>التحقق من الأذونات</b></td>
    <td>فحص تلقائي لحالة آدمن البوت + <code>can_post_messages</code> في القناة</td>
  </tr>
  <tr>
    <td>🐳 <b>Docker مُحصَّن</b></td>
    <td>مستخدم غير root، <code>cap_drop: ALL</code>، <code>no-new-privileges</code>، healthcheck حقيقي</td>
  </tr>
  <tr>
    <td>♻️ <b>استئناف تلقائي عند إعادة التشغيل</b></td>
    <td>يُستعاد البث النشط عند إعادة إقلاع البوت (<code>post_init</code>)</td>
  </tr>
  <tr>
    <td>⚙️ <b>ترميز محسَّن</b></td>
    <td>طبقة سوداء للراديو (CPU منخفض)، نسخ مباشر للبث لـ IPTV (نطاق ترددي منخفض)</td>
  </tr>
</table>

### 🔧 التقنيات المستخدمة

```
┌─────────────────────────────────────────────┐
│  الأطر والمكتبات                             │
├─────────────────────────────────────────────┤
│ • Python 3.11+                              │
│ • python-telegram-bot v21.6 (تزامني)        │
│ • FFmpeg (معالجة فيديو، قائمة وسائط)        │
│ • yt-dlp 2024.8.6 (استخراج YouTube)         │
│ • SQLite3 (جداول settings + users)          │
│ • asyncio (عمليات بث لكل مستخدم)            │
│ • Docker (غير root، مُحصَّن)                 │
└─────────────────────────────────────────────┘
```

### 🚀 البدء السريع

#### 1. المتطلبات

```bash
# مكتبات النظام
sudo apt-get install -y python3.11 python3.11-venv ffmpeg git

# مكتبات Python
pip install -r requirements.txt
# yt-dlp يُثبَّت عبر Dockerfile أو: pip install yt-dlp==2024.8.6
```

#### 2. احصل على معرّفات Telegram

1. أنشئ بوت عبر **[@BotFather](https://t.me/BotFather)** ← احصل على `BOT_TOKEN`
2. احصل على معرّفك عبر **[@userinfobot](https://t.me/userinfobot)** ← هذا هو `ADMIN_ID` الخاص بك

#### 3. الاستنساخ والتكوين

```bash
git clone <your-fork-url> streaming-bot
cd streaming-bot

python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
nano .env
```

حرّر `.env`:
```env
BOT_TOKEN=123456:ABC-DEF...توكنك_من_botfather
ADMIN_IDS=123456789           # معرّفك على Telegram (مفصول بفواصل لعدة مدراء)
DEFAULT_LANGUAGE=ar           # ar أو en
```

#### 4. التشغيل

```bash
python streaming_bot.py
```

أو مع Docker (موصى به للإنتاج):
```bash
docker compose up -d --build
docker compose logs -f
```

### 📖 مرجع الأوامر

| الأمر | الغرض | الصلاحية |
|------|-------|----------|
| `/start` | عرض القائمة الرئيسية بأزرار inline | كل المستخدمين المصرّح لهم |
| `/setup` | بدء معالج الضبط من 5 خطوات (تفاعلي) | كل المستخدمين المصرّح لهم |
| `/start_stream` | بدء البث (أو عبر الزر) | كل المستخدمين المصرّح لهم |
| `/stop_stream` | إيقاف بثك النشط (أو عبر الزر) | كل المستخدمين المصرّح لهم |
| `/status` | عرض حالة البث + PID لـ FFmpeg | كل المستخدمين المصرّح لهم |
| `/language` | تبديل لغة الواجهة (AR/EN) | كل المستخدمين المصرّح لهم |
| `/help` | عرض المساعدة مع التحذير القانوني | كل المستخدمين المصرّح لهم |
| `/authorize <user_id>` | تخويل مستخدم جديد | **المدراء فقط** |

### 💬 مسار المحادثة (معالج الضبط)

الأمر المُعرَّض للأخطاء `/setup "url" "server" "key" "channel_id"` استُبدل بمعالج تفاعلي من 5 خطوات:

```
┌─────────────────────────────────────────────────────────────┐
│  الخطوة 1: رابط البث                                        │
│  📡 أرسل رابط البث (مثال: https://youtu.be/xxx)             │
│  [❌ إلغاء]                                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ (تحقق)
┌─────────────────────────────────────────────────────────────┐
│  الخطوة 2: عنوان خادم RTMP                                  │
│  🖥️ أرسل عنوان الخادم (مثال: rtmp://server.com/live/)       │
│  [❌ إلغاء]                                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ (تحقق)
┌─────────────────────────────────────────────────────────────┐
│  الخطوة 3: مفتاح البث                                       │
│  🔑 أرسل مفتاح البث                                         │
│  [❌ إلغاء]                                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ (تحقق)
┌─────────────────────────────────────────────────────────────┐
│  الخطوة 4: معرّف القناة                                     │
│  📣 أرسل معرّف القناة (-100xxxx أو @username)               │
│  [❌ إلغاء]                                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ (تحقق)
┌─────────────────────────────────────────────────────────────┐
│  الخطوة 5: المراجعة والتأكيد                                │
│  📋 مراجعة الإعدادات قبل الحفظ:                             │
│     📡 رابط البث: https://...                               │
│     🖥️ الخادم: rtmp://...                                   │
│     🔑 المفتاح: ••••••••••••                                │
│     📣 القناة: -1001234567890                               │
│     📡 نوع البث: 🎬 يوتيوب مباشر                            │
│  [✅ تأكيد وحفظ]  [❌ إلغاء]                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ✅ تم حفظ الإعدادات!
```

### 🏗️ البنية المعمارية

```
                       ┌──────────────────────┐
                       │  مستخدم Telegram (DM)│
                       └──────────┬───────────┘
                                  │ /start أو نقر زر
                                  ▼
                       ┌──────────────────────┐
                       │  python-telegram-bot │
                       │  (تزامني، polling)   │
                       └──────────┬───────────┘
                                  │
              ┌───────────────────┼────────────────────┐
              ▼                   ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │  طبقة المصادقة  │  │  قاعدة SQLite   │  │  طبقة i18n      │
    │  ADMIN_IDS +    │  │  جداول settings │  │  قاموس AR/EN    │
    │  جدول users     │  │  و users        │  │  لكل مستخدم     │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
                                  │
                                  ▼
              ┌───────────────────────────────────────┐
              │  مدير البث لكل مستخدم                 │
              │  dict[user_id, StreamProcess]         │
              │  + asyncio.Lock                      │
              │                                       │
              │  لكل مستخدم نشط:                      │
              │    asyncio.Task → _stream_worker()    │
              │       ├─ yt-dlp (قائمة وسائط)         │
              │       └─ ffmpeg (قائمة وسائط)         │
              └───────────────────┬───────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │  وجهة RTMP           │
                       │  (YouTube Live /     │
                       │   RTMP مخصص / OBS)   │
                       └──────────────────────┘
```

### 📊 كيفية العمل

**1. بثات YouTube المباشرة**
- `yt-dlp` يستخرج رابط البث الحي (يُستدعى عبر `create_subprocess_exec` بقائمة وسائط — لا shell)
- FFmpeg ينسخ الفيديو + الصوت إلى وجهة RTMP
- حلقة Python-side `while not stop_event.is_set()` تُجدِّد الاستخراج كل 15 ثانية لتحديث التذاكر المنتهية
- مهمة asyncio لكل مستخدم؛ إيقاف مستخدم لا يؤثر على الآخرين

**2. بثات الراديو / الصوت**
- طبقة سوداء (`color=c=black:s=640x360:r=10`) — استهلاك CPU أدنى
- الصوت يُعاد ترميزه إلى AAC 128k
- مناسب لإذاعات 24/7 / راديو القرآن

**3. بثات IPTV**
- نسخ مباشر للبث (`-c:v copy -c:a copy`) — استهلاك CPU أدنى
- إعادة اتصال Python-side مع تأخير قابل للإعداد
- لا ترويسات تخطّي حماية (فقط User-Agent قياسي)

### 🔐 التحصين الأمني

هذا **أهم قسم** — اقرأه بعناية.

#### ✅ منع RCE
- **صفر** استدعاءات `shell=True` (تم التحقق عبر تحليل AST)
- **صفر** أنماط `subprocess.Popen(bash_command, shell=True)`
- **صفر** استدعاءات `asyncio.create_subprocess_shell`
- كل استدعاءات FFmpeg و yt-dlp تستخدم **قائمة وسائط**: `["ffmpeg", "-i", url, ...]`
- مدخل خبيث مثل `"; rm -rf / #` كرابط بث يُعامل كعنصر argv واحد — لا يمكن تنفيذه كأمر shell

#### ✅ المصادقة
- البوت يرفض كل الأوامر من المستخدمين غير المصرّح لهم
- تخويل من طبقتين:
  1. متغير `ADMIN_IDS` البيئي (معرّفات Telegram، مفصولة بفواصل)
  2. `users.is_authorized = 1` في DB (يُضبط عبر `/authorize <user_id>` من مدير)
- Decorator باسم `@authorized_only` يغلِّف كل handler

#### ✅ التحقق من المدخلات
validators صارمة على كل مدخل مستخدم:
- `is_valid_stream_url()` — فقط بروتوكولات `http/https/rtmp/rtmps/rtsp` (يحظر `javascript:`، `file:`، إلخ)
- `is_valid_server_url()` — فقط `rtmp/rtmps/http/https` للوجهة
- `is_valid_channel_id()` — فقط `-100xxxxxxxxxx`، `@username`، أو معرّفات رقمية (يحظر `"; rm -rf /`، `$(whoami)`)

#### ✅ العزل لكل مستخدم
- كل مستخدم يملك `StreamProcess` خاصاً به (Popen + asyncio.Task + stop_event)
- `asyncio.Lock` يحمي الـ dict `_processes`
- المستخدم "ب" لا يستطيع إيقاف بث المستخدم "أ"

#### ✅ أمان Markdown
- وضع `MarkdownV2` للتحليل (وليس `Markdown` القديم)
- `md_escape()` على كل قيمة ديناميكية (URLs، معرّفات القنوات، رسائل الأخطاء)
- يهرب كل الرموز الخاصة الـ 12: `_*[]()~\`>#+-=|{}.!`

#### ✅ تحصين Docker
- يعمل كـ `botuser` (UID 1000)، وليس root
- `cap_drop: ALL` (يحذف كل صلاحيات Linux)
- `cap_add: SETUID, SETGID` فقط (ضرورية لإدارة subprocess)
- `security_opt: no-new-privileges:true`
- `restart: unless-stopped` (ليس `always` — لا يُعاد التشغيل عند الإيقاف المتعمَّد)

#### ✅ Healthcheck حقيقي
الأصلي `python -c "import sys; sys.exit(0)"` كان يرجع 0 دائماً (عديم الفائدة). الـ `healthcheck.py` الجديد يجرى 4 فحوصات فعلية:

| الفحص | ما يتحقق منه |
|-------|--------------|
| وجود ملف DB | ملف SQLite موجود وغير فارغ |
| وجود الجداول | جدولا `settings` و `users` موجودان |
| تزامن البث النشط | إذا قالت DB إن بثاً يعمل، فعلاً هناك عملية `ffmpeg` |
| عملية Python حية | عملية Python الرئيسية للبوت تعمل |

إذا فشل أي فحص → exit 1 → Docker يُعيد تشغيل الحاوية.

### 🐳 نشر Docker

#### الخيار أ: Docker Compose (موصى به)

```bash
cp .env.example .env
# حرّر .env بـ BOT_TOKEN و ADMIN_IDS
docker compose up -d --build

# عرض السجلات
docker compose logs -f

# إيقاف
docker compose down
```

#### الخيار ب: Docker مباشر

```bash
docker build -t streaming-bot:hardened .

docker run -d \
  --name streaming-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  --cap-add SETUID \
  --cap-add SETGID \
  streaming-bot:hardened
```

### 🚀 نشر الإنتاج

#### VPS مع systemd (بدون Docker)

```bash
# إعداد Ubuntu/Debian
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3.11 python3.11-venv ffmpeg git

# الاستنساخ والتثبيت
git clone <your-fork-url> /opt/streaming-bot
cd /opt/streaming-bot
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install yt-dlp==2024.8.6

# التكوين
cp .env.example .env
nano .env  # اضبط BOT_TOKEN و ADMIN_IDS

# إنشاء خدمة systemd
sudo tee /etc/systemd/system/streaming-bot.service <<EOF
[Unit]
Description=Streaming Bot (Hardened)
After=network.target

[Service]
Type=simple
User=streambot
Group=streambot
WorkingDirectory=/opt/streaming-bot
EnvironmentFile=/opt/streaming-bot/.env
ExecStart=/opt/streaming-bot/venv/bin/python streaming_bot.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo useradd -r -s /bin/false streambot
sudo chown -R streambot:streambot /opt/streaming-bot
sudo systemctl daemon-reload
sudo systemctl enable --now streaming-bot
sudo systemctl status streaming-bot
```

#### منصات سحابية
- **Hetzner Cloud** (VPS موصى به — €5/شهر، 1 vCPU/2GB كافية)
- **Railway.app** (نشر حاويات)
- **Render.com** (بديل)

### 🐛 استكشاف الأخطاء

| المشكلة | الحل |
|--------|------|
| البوت يقول "🚫 غير مصرّح لك" | أضف معرّفك إلى `ADMIN_IDS` في `.env`، أو اطلب من مدير تشغيل `/authorize <your_id>` |
| تحذير `ADMIN_IDS is empty` في السجلات | اضبط `ADMIN_IDS=123456789` في `.env` (احصل على معرّفك من `@userinfobot`) |
| البوت لا يرد | تحقق من `BOT_TOKEN` والاتصال؛ راجع `docker compose logs` |
| FFmpeg غير موجود | `sudo apt-get install ffmpeg` (أو استخدم صورة Docker التي تتضمنه) |
| رفض الأذونات في القناة | اجعل البوت **آدمن** في القناة المستهدفة مع صلاحية **نشر الرسائل** |
| انقطاع البث | تحقق من جدار الحماية وحالة خادم RTMP؛ راجع `RECONNECT_DELAY` |
| استهلاك CPU مرتفع | قلّل الـ bitrate في `_build_ffmpeg_cmd_radio()` أو استخدم وضع الراديو للصوت فقط |
| خطأ MarkdownV2 parse | كل القيم الديناميكية يجب أن تمر عبر `md_escape()` — أبلغ عنها إن رأيتها |
| الحاوية تُعاد تشغيلها باستمرار | شغّل `python healthcheck.py` يدوياً لمعرفة أي فحص فشل |
| `yt-dlp` يفشل على يوتيوب | حدّث: `pip install --upgrade yt-dlp==2024.8.6` |

### 📖 التوثيق

- 📘 **[FIXES_REPORT.md](./FIXES_REPORT.md)** — تقرير الإصلاحات الأمنية الكامل (10 مشاكل عُولجت)
- 📘 [دليل التثبيت](./DEPLOYMENT.md)
- 🔐 [دليل الأمان](./SECURITY.md)
- 🤝 [المساهمة](./CONTRIBUTING.md)
- 📝 [سجل التغييرات](./CHANGELOG.md)

### ⚖️ إشعار قانوني

هذا البوت **أداة تقنية محايدة** لترحيل البث. المشغّل مسؤول وحده عن:

- ✅ امتلاك حقوق إعادة توزيع البث المصدر
- ✅ الالتزام بشروط استخدام المنصة المصدر (شروط YouTube، شروط مزوّد IPTV، إلخ)
- ✅ الالتزام بقوانين إعادة البث المحلية في بلده

النسخة المُحصَّنة **أزالت** ميزات التخطّي الموجودة في الأصل (تزييف `Referer: x.com`، ترويسات "Anti-Block"). استخدام البوت لإعادة توزيع محتوى محمي بحقوق ملكية دون ترخيص قد يُعرّض المشغّل للمسؤولية القانونية.

### 🤝 المساهمة

نرحب بالمساهمات! يُرجى التأكد من أن PR الخاص بك:

1. **لا** يُعيد إدخال `shell=True` في أي مكان
2. **لا** يضيف ترويسات تخطّي (تزييف Referer، إلخ)
3. يتحقق من كل مدخلات المستخدم عبر الـ validators الموجودة
4. يستخدم `MarkdownV2` مع `md_escape()` لأي نص ديناميكي
5. يجتاز مجموعة الاختبارات الموجودة

```bash
# سير العمل القياسي
git checkout -b feature/AmazingFeature
git commit -m 'Add AmazingFeature'
git push origin feature/AmazingFeature
# افتح PR
```

### 📝 الترخيص

هذا المشروع مرخص تحت ترخيص **MIT** — انظر ملف [LICENSE](./LICENSE) للتفاصيل.

### 💬 الدعم والتواصل

- 🐛 **المشاكل**: [GitHub Issues](https://github.com/phoneKYC/streaming-bot/issues)
- 💬 **النقاشات**: [GitHub Discussions](https://github.com/phoneKYC/streaming-bot/discussions)

### 👨‍💻 التطوير

**النسخة المُحصَّنة بواسطة:** مراجعة أمنية وإعادة كتابة
**المشروع الأصلي:** [phoneKYC/streaming-bot](https://github.com/phoneKYC/streaming-bot)

---

<div align="center">

### 🌟 دعم المشروع

إذا أعجبك هذا المشروع، أعطه ⭐ وشاركه مع الآخرين!

---

## 📊 إحصائيات المشروع

![Python](https://img.shields.io/badge/Language-Python%2095%25-blue)
![Docker](https://img.shields.io/badge/Docker-Hardened-blue)
![Code Quality](https://img.shields.io/badge/Code%20Quality-Security%20Audited-brightgreen)
![Maintenance](https://img.shields.io/badge/Maintenance-Active-brightgreen)
![Security](https://img.shields.io/badge/Security-RCE%20Fixed-red)

---

### 🙏 شكر خاص

شكر خاص للمساهمين والمستخدمين الذين يدعمون هذا المشروع!

### 💝 الدعم المالي

إذا كنت تستخدم هذا المشروع بشكل احترافي، يُرجى التفكير في دعم التطوير المستمر.

---

Made with ❤️ and 🔐 by the Hardened Edition contributors

**Last Updated**: July 2026 · **Version**: 2.0.0 Hardened

</div>
