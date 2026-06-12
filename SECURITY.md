# 🔒 Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes   |

## Reporting a Vulnerability

**Please do not open public issues for security vulnerabilities.**

If you discover a security vulnerability in Streaming Bot, please email us at:
- **security@iidzii.dev**
- Or create a private security advisory on GitHub

Please include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if available)

We will acknowledge receipt of your report within 48 hours and will keep you informed of our progress.

## Security Best Practices

### 1. Bot Token Protection

**Never** commit your bot token to version control:

```bash
# ❌ DON'T DO THIS
BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

# ✅ DO THIS INSTEAD
export BOT_TOKEN="your_token_here"
# Or use .env file with python-dotenv
```

### 2. Environment Variables

Always use environment variables for sensitive data:

```python
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
```

Create a `.env` file (never commit it):
```bash
BOT_TOKEN=your_actual_token
```

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
```

### 3. Database Security

#### Backup Regular Backups
```bash
# Create automated backups
0 2 * * * cp /opt/streaming-bot/stream_manager.db /backup/stream_manager_$(date +\%Y\%m\%d).db
```

#### Encrypt Sensitive Data
For production deployments, consider encrypting the database:

```python
from cryptography.fernet import Fernet

# Generate key (store safely)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt stream key
encrypted_key = cipher.encrypt(stream_key.encode())
```

### 4. API Security

#### Use HTTPS Only
For any API endpoints, always use HTTPS:

```python
# ❌ Avoid HTTP
url = "http://streaming-server.com/live/"

# ✅ Use HTTPS
url = "https://streaming-server.com/live/"
```

#### Validate Input
Always validate and sanitize user inputs:

```python
import urllib.parse

def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
```

### 5. Firewall Configuration

Restrict access to necessary ports only:

```bash
# Allow only SSH and necessary services
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp        # SSH
sudo ufw allow 80/tcp        # HTTP (if needed)
sudo ufw allow 443/tcp       # HTTPS (if needed)
sudo ufw enable
```

### 6. FFmpeg Security

#### Validate Stream URLs
```python
def is_valid_stream_url(url: str) -> bool:
    """Validate stream URL to prevent injection attacks."""
    forbidden_chars = [';', '|', '&', '`', '$', '(', ')', '<', '>', '\n', '\r']
    return not any(char in url for char in forbidden_chars)
```

#### Use Quotes in Shell Commands
```python
# ❌ Vulnerable to injection
f'ffmpeg -i {url} ...'

# ✅ Safe with proper escaping
subprocess.Popen([
    'ffmpeg', '-i', url, ...
], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
```

### 7. Access Control

#### Telegram User ID Verification
Implement user verification in production:

```python
AUTHORIZED_USERS = [123456789, 987654321]  # Admin user IDs

async def admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    # Admin command logic
```

### 8. Logging and Monitoring

#### Secure Logging
```python
import logging

# Never log sensitive information
logger.info(f"User {user_id} setup stream")  # ✅ Safe
logger.info(f"Bot token: {BOT_TOKEN}")        # ❌ Dangerous
```

#### Monitor Suspicious Activity
```python
# Log failed attempts
failed_attempts = {}

async def track_failed_setup(user_id):
    failed_attempts[user_id] = failed_attempts.get(user_id, 0) + 1
    if failed_attempts[user_id] > 5:
        logger.warning(f"⚠️ Multiple failed attempts from user {user_id}")
```

### 9. Dependencies

#### Keep Dependencies Updated
```bash
# Check for security vulnerabilities
pip install --upgrade pip
pip install safety
safety check

# Update requirements
pip list --outdated
pip install -r requirements.txt --upgrade
```

#### Use Specific Versions
Instead of loose version constraints:

```
# ❌ Avoid
python-telegram-bot
yt-dlp

# ✅ Specify versions
python-telegram-bot==21.0.1
yt-dlp==2024.1.1
```

### 10. Docker Security

#### Run as Non-Root User
```dockerfile
FROM python:3.9-slim

RUN useradd -m -u 1000 botuser
USER botuser

WORKDIR /app
COPY --chown=botuser:botuser . .
```

#### Read-Only Filesystem
```bash
docker run --read-only \
  --tmpfs /tmp \
  -e BOT_TOKEN="your_token" \
  streaming-bot:latest
```

## Vulnerability Disclosure Timeline

1. **Report received**: Acknowledgment within 24 hours
2. **Assessment**: Initial assessment within 48 hours
3. **Fix**: Target 7 days for patch release
4. **Disclosure**: Public disclosure after patch release
5. **Credit**: You will be credited (if desired) in release notes

## Security Checklist

Before deploying to production:

- [ ] Bot token stored in environment variables
- [ ] Database backed up regularly
- [ ] Firewall properly configured
- [ ] HTTPS enabled for all external connections
- [ ] Input validation implemented
- [ ] Logging doesn't include sensitive data
- [ ] Dependencies are up to date
- [ ] HTTPS used for Telegram API calls
- [ ] Regular security audits scheduled
- [ ] Incident response plan in place

## Additional Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [Telegram Bot Security](https://core.telegram.org/bots/tutorials/bot-security)
- [Python Security](https://docs.python.org/3/library/security_warnings.html)
- [Docker Security](https://docs.docker.com/engine/security/)

## Contact

For security concerns, please contact:
- **Email**: security@iidzii.dev
- **GitHub**: [IIDZII Dev](https://github.com/IIDZII)

---

Made with ❤️ by [IIDZII Dev](https://github.com/IIDZII)
