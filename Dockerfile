# Multi-stage build for smaller image size
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies (ffmpeg, curl, pgrep from procps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp (pinned)
RUN pip install --no-cache-dir yt-dlp==2024.8.6

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Final stage ----------
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (including procps for pgrep used by healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    procps \
    yt-dlp \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY streaming_bot.py healthcheck.py ./

# Create data directory
RUN mkdir -p /app/data && chmod 755 /app/data

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_PATH=/app/data/stream_manager.db

# Real health check using the dedicated script
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python /app/healthcheck.py || exit 1

# Run as non-root user for security
RUN useradd -r -u 1000 -d /app botuser && chown -R botuser:botuser /app
USER botuser

CMD ["python", "streaming_bot.py"]
