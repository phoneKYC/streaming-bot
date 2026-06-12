# 📦 Streaming Bot - Project Documentation

## 📋 Project Structure

```
streaming-bot/
├── 📄 streaming_bot.py          # Main bot application
├── 📄 requirements.txt          # Python dependencies
├── 📄 Dockerfile                # Docker image configuration
├── 📄 docker-compose.yml        # Docker Compose configuration
├── 📄 README.md                 # Main documentation (EN/AR)
├── 📄 DEPLOYMENT.md             # Deployment guides (EN/AR)
├── 📄 CONTRIBUTING.md           # Contribution guidelines
├── 📄 SECURITY.md               # Security policies
├── 📄 CHANGELOG.md              # Version history
├── 📄 LICENSE                   # MIT License
├── 📄 .env.example              # Environment template
├── 📄 .gitignore                # Git ignore rules
└── 📁 data/                     # Data directory (created on runtime)
    └── stream_manager.db        # SQLite database
```

---

## 📚 File Descriptions

### Core Application

#### `streaming_bot.py`
- **Purpose**: Main bot application
- **Size**: ~15 KB
- **Language**: Python 3.9+
- **Dependencies**: python-telegram-bot v21, yt-dlp, sqlite3
- **Features**:
  - Telegram bot command handlers
  - FFmpeg process management
  - SQLite database operations
  - Environment variable support
  - Comprehensive logging
  - Error handling and recovery
  - Multi-stream type support
  - Automatic stream resumption

### Configuration Files

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Key Packages**:
  - python-telegram-bot==21.0.1 (Telegram Bot API)
  - yt-dlp==2024.1.1 (YouTube video extraction)
  - python-dotenv==1.0.0 (Environment variables)

#### `.env.example`
- **Purpose**: Template for environment variables
- **Variables**:
  - BOT_TOKEN (Telegram bot token)
  - LOG_LEVEL (Logging verbosity)
  - DATABASE_PATH (SQLite database location)
  - FFMPEG_TIMEOUT (Connection timeout)
  - RECONNECT_DELAY (Reconnection interval)
  - DEBUG (Debug mode flag)

#### `.gitignore`
- **Purpose**: Exclude files from version control
- **Excluded Items**:
  - Python cache (__pycache__, *.pyc)
  - Virtual environments (venv/)
  - Environment files (.env)
  - Database files (*.db)
  - IDE settings (.vscode/, .idea/)
  - OS files (.DS_Store, Thumbs.db)

### Documentation

#### `README.md`
- **Purpose**: Main project documentation
- **Languages**: English & Arabic
- **Sections**:
  - Project overview
  - Feature list
  - Installation instructions
  - Quick start guide
  - Usage documentation
  - How it works (architecture)
  - Docker deployment
  - Troubleshooting
  - Support information

#### `DEPLOYMENT.md`
- **Purpose**: Comprehensive deployment guide
- **Languages**: English & Arabic
- **Deployment Methods**:
  - Local development setup
  - VPS deployment (Ubuntu/Debian)
  - Docker deployment
  - Cloud platforms (Railway, Render)
  - Performance optimization
  - Troubleshooting guide

#### `CONTRIBUTING.md`
- **Purpose**: Guidelines for contributors
- **Contents**:
  - Code of conduct
  - How to report bugs
  - How to suggest features
  - Pull request guidelines
  - Development setup
  - Code style guidelines
  - Testing procedures

#### `SECURITY.md`
- **Purpose**: Security policies and best practices
- **Topics**:
  - Vulnerability reporting process
  - Security best practices
  - Token protection
  - Environment variables
  - Database security
  - API security
  - Firewall configuration
  - FFmpeg security
  - Access control
  - Logging security
  - Dependency management
  - Docker security

#### `CHANGELOG.md`
- **Purpose**: Version history and release notes
- **Format**: Keep a Changelog standard
- **Contents**:
  - Release notes
  - Feature additions
  - Bug fixes
  - Planned features
  - Migration guides
  - Known issues

#### `LICENSE`
- **Purpose**: MIT License text
- **Terms**: 
  - Free use, modification, and distribution
  - Attribution required
  - No warranty provided
  - Liability limitations

### Docker Files

#### `Dockerfile`
- **Purpose**: Docker image definition
- **Base Image**: python:3.9-slim
- **Features**:
  - Multi-stage build for smaller size
  - FFmpeg installation
  - yt-dlp installation
  - Python dependencies
  - Non-root user support
  - Health checks
  - Optimized layers

#### `docker-compose.yml`
- **Purpose**: Docker Compose orchestration
- **Features**:
  - Service definition
  - Environment variables
  - Volume management
  - Restart policy
  - Resource limits
  - Health checks
  - Logging configuration
  - Network setup

---

## 🔑 Key Features

### Multi-Source Streaming
- ✅ YouTube live streams
- ✅ M3U playlists (radio, audio)
- ✅ IPTV streams
- ✅ HTTP/HTTPS streams

### Reliability
- 🔄 Auto-reconnection on failure
- 💾 Persistent session storage
- 📊 Real-time status monitoring
- 🚀 Automatic stream resumption on restart

### User Experience
- 📱 Telegram bot interface
- 🌐 Bilingual support (AR/EN)
- ⚡ Simple command-based setup
- 📈 Permission verification

### Operational
- 🐳 Docker support
- 📖 Comprehensive documentation
- 🔒 Security best practices
- 🛠️ Easy deployment options

---

## 🚀 Quick Start

### Option 1: Direct Execution
```bash
# Setup
git clone https://github.com/IIDZII/streaming-bot.git
cd streaming-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
export BOT_TOKEN="your_token"

# Run
python streaming_bot.py
```

### Option 2: Docker
```bash
# Build
docker build -t streaming-bot:latest .

# Run
docker run -e BOT_TOKEN="your_token" streaming-bot:latest
```

### Option 3: Docker Compose
```bash
# Setup
docker-compose up -d

# Check
docker-compose logs -f
```

---

## 🌐 Telegram Commands

| Command | Description | Parameters |
|---------|-------------|-----------|
| `/start` | Welcome message | None |
| `/setup` | Configure streaming | M3U URL, Server, Key, Channel ID |
| `/start_stream` | Begin streaming | None |
| `/stop_stream` | Stop streaming | None |
| `/status` | Check status | None |

---

## 📊 Database Schema

```sql
CREATE TABLE settings (
    user_id INTEGER PRIMARY KEY,
    m3u_url TEXT,
    server_url TEXT,
    stream_key TEXT,
    channel_id TEXT,
    is_running INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔒 Security Features

- ✅ Environment variable protection
- ✅ Input validation
- ✅ Permission checking
- ✅ Secure logging
- ✅ Database security
- ✅ Firewall configuration support
- ✅ Docker security best practices
- ✅ Vulnerability disclosure process

---

## 📈 System Requirements

### Minimum
- **CPU**: 1 core
- **RAM**: 512 MB
- **Disk**: 100 MB
- **Python**: 3.9+
- **OS**: Linux, macOS, Windows

### Recommended
- **CPU**: 2 cores
- **RAM**: 1 GB
- **Disk**: 1 GB
- **Python**: 3.10+
- **OS**: Linux (Ubuntu 20.04+)

---

## 🎯 Use Cases

1. **Live Stream Relaying**
   - Forward YouTube streams to your server
   - Relay IPTV channels to multiple platforms

2. **Radio Broadcasting**
   - Stream radio stations to your platform
   - Broadcast M3U playlists

3. **Media Distribution**
   - Centralized streaming management
   - Multi-platform delivery

4. **Content Delivery**
   - Stream aggregation
   - Format conversion
   - Quality optimization

---

## 🛠️ Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Bot not responding | Token invalid | Verify BOT_TOKEN |
| FFmpeg not found | Not installed | Install FFmpeg |
| Permission denied | Not admin | Add bot as channel admin |
| Stream disconnects | Network issue | Check firewall and RTMP server |
| High CPU usage | High bitrate | Reduce encoding settings |
| Database locked | Concurrent access | Restart bot service |

---

## 📞 Support

### Getting Help
1. **Documentation**: Check README.md and DEPLOYMENT.md
2. **Issues**: GitHub Issues page
3. **Discussions**: GitHub Discussions
4. **Security**: security@iidzii.dev

### Reporting Issues
Include:
- Clear title and description
- Steps to reproduce
- Error logs/messages
- Environment details (OS, Python version)
- Relevant configuration

---

## 📄 License

This project is licensed under the MIT License.
- **Commercial Use**: ✅ Allowed
- **Modification**: ✅ Allowed
- **Distribution**: ✅ Allowed
- **Private Use**: ✅ Allowed
- **Liability**: ❌ Not included
- **Warranty**: ❌ Not provided

See [LICENSE](LICENSE) file for full details.

---

## 👨‍💻 Author & Credits

**IIDZII Dev** - Lead Developer and Maintainer
- GitHub: https://github.com/IIDZII
- Email: contact@iidzii.dev

### Technologies
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)

---

## 🔗 Useful Links

- **Repository**: https://github.com/IIDZII/streaming-bot
- **Issues**: https://github.com/IIDZII/streaming-bot/issues
- **Discussions**: https://github.com/IIDZII/streaming-bot/discussions
- **Releases**: https://github.com/IIDZII/streaming-bot/releases

---

## 📊 Project Statistics

- **Language**: Python 3.9+
- **Files**: 12
- **Total Lines**: ~2,000+
- **Dependencies**: 4 primary
- **License**: MIT
- **Status**: Active Development

---

<div align="center">

**Show your support by starring the repository! ⭐**

Made with ❤️ by [IIDZII Dev](https://github.com/IIDZII)

</div>
