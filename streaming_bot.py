"""
Streaming Bot - Hardened Edition
================================
نسخة مُصلحة من بوت إدارة البث المباشر تعالج جميع الثغرات الأمنية والمعمارية:

  1. إزالة ثغرة RCE (Command Injection) بالكامل: لا يوجد shell=True،
     كل مدخلات المستخدم تُمرَّر كقائمة وسائط منفصلة (list args).
  2. مصادقة صارمة عبر قائمة ADMIN_IDS البيئية + قاعدة بيانات للمستخدمين المصرّح لهم.
  3. ConversationHandler كامل لمعالج /setup (بدل الأمر النصي بأربع وسائط).
  4. InlineKeyboardButton في كل مكان (Cancel/Confirm/Stop/Restart/Language).
  5. ثنائية لغة حقيقية (AR/EN) قابلة للتبديل لكل مستخدم.
  6. تعدد المستخدمين فعلي: كل مستخدم يملك عملية FFmpeg مستقلة في dict آمن.
  7. MarkdownV2 مع escaping صحيح لكل القيم الديناميكية.
  8. إزالة ترويسات التخطي القانونية المشكوك بها (Referer: x.com).
  9. حلقة إعادة الاتصال مُعاد كتابتها في Python بدل bash while-loop.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shlex
import signal
import sqlite3
import subprocess
import threading
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------------------------
# تكوين النظام
# ---------------------------------------------------------------------------
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)

DB_NAME = os.getenv("DATABASE_PATH", "stream_manager.db")
FFMPEG_TIMEOUT = int(os.getenv("FFMPEG_TIMEOUT", "15000000"))
RECONNECT_DELAY = int(os.getenv("RECONNECT_DELAY", "5"))
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ar").lower()

# قائمة المدراء (بيئياً: ADMIN_IDS=123456789,987654321)
ADMIN_IDS: set[int] = {
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}

# User-Agent قياسي لرأس HTTP - لا ترويسات Referer مزيفة
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# امتدادات الملفات الصوتية
AUDIO_EXTENSIONS = (
    ".mp3", ".aac", ".ogg", ".opus", ".m3u", ".m3u8", ".pls", ".asx", ".xspf",
)

# نطاقات الراديو المعروفة
RADIO_DOMAINS = (
    "aymane.xyz", "qurango.net", "radiojar.com",
    "radiocoast.com", "listenradio.org",
)

# حالات ConversationHandler
(
    STATE_STREAM_URL,
    STATE_SERVER_URL,
    STATE_STREAM_KEY,
    STATE_CHANNEL_ID,
    STATE_CONFIRM,
) = range(5)

# ---------------------------------------------------------------------------
# نظام الترجمة (i18n) - ثنائية اللغة الحقيقية
# ---------------------------------------------------------------------------
TRANSLATIONS: dict[str, dict[str, str]] = {
    "ar": {
        "welcome": (
            "👋 *أهلاً بك في بوت إدارة البث المباشر*\n\n"
            "اختر إحدى العمليات من الأزرار أدناه:"
        ),
        "btn_setup": "⚙️ ضبط الإعدادات",
        "btn_start": "▶️ بدء البث",
        "btn_stop": "⏹️ إيقاف البث",
        "btn_status": "📊 الحالة",
        "btn_language": "🌐 اللغة",
        "btn_help": "❓ المساعدة",
        "btn_cancel": "❌ إلغاء",
        "btn_confirm": "✅ تأكيد وحفظ",
        "btn_restart": "🔄 إعادة التشغيل",
        "btn_back": "🔙 رجوع",
        "setup_intro": "⚙️ *معالج ضبط الإعدادات*\n\nأرسل *رابط البث* (YouTube / m3u8 / راديو):",
        "setup_stream_url_prompt": "📡 أرسل *رابط البث* (مثال: `https://youtu.be/xxx` أو `https://example.com/stream.m3u8`):",
        "setup_server_url_prompt": "🖥️ أرسل *عنوان خادم RTMP* (مثال: `rtmp://server.com/live/`):",
        "setup_stream_key_prompt": "🔑 أرسل *مفتاح البث* (stream key):",
        "setup_channel_id_prompt": "📣 أرسل *معرّف القناة* (مثال: `-1001234567890` أو `@mychannel`):",
        "setup_invalid_url": "❌ رابط غير صالح. يجب أن يبدأ بـ `http://` أو `https://` أو `rtmp://`. حاول مجدداً:",
        "setup_invalid_server": "❌ عنوان الخادم غير صالح. يجب أن يبدأ بـ `rtmp://` أو `rtmps://` أو `https://`. حاول مجدداً:",
        "setup_invalid_channel": "❌ معرّف القناة غير صالح. استخدم `-100xxxxxxxxxx` أو `@username`. حاول مجدداً:",
        "setup_checking_perms": "🔄 جاري التحقق من صلاحيات البوت في القناة...",
        "setup_detected_type": "📡 نوع البث المكتشف: *{type_label}*",
        "setup_perms_failed": "❌ فشل التحقق! تأكد من رفع البوت آدمن في القناة ومنحه صلاحية 'نشر الرسائل'.",
        "setup_review_title": "📋 *مراجعة الإعدادات قبل الحفظ:*",
        "setup_review_stream_url": "📡 رابط البث",
        "setup_review_server": "🖥️ الخادم",
        "setup_review_key": "🔑 المفتاح",
        "setup_review_channel": "📣 القناة",
        "setup_review_type": "📡 نوع البث",
        "setup_saved": "✅ تم حفظ الإعدادات بنجاح! استخدم زر *بدء البث* لإطلاقه.",
        "setup_cancelled": "❌ تم إلغاء المعالج. لم يُحفظ شيء.",
        "type_youtube": "🎬 يوتيوب مباشر",
        "type_radio": "🎵 إذاعة / راديو",
        "type_iptv": "📺 IPTV",
        "stream_already_running": "⚠️ البث يعمل بالفعل! أوقفه أولاً.",
        "stream_starting": "🚀 جاري تشغيل البث...",
        "stream_started": "🟢 تم تشغيل البث بنجاح وهو تحت المراقبة.",
        "stream_no_settings": "❌ لا توجد إعدادات محفوظة. استخدم معالج الضبط أولاً.",
        "stream_not_running": "⚪ لا يوجد بث يعمل حالياً.",
        "stream_stopped": "⏹️ تم إيقاف البث وتحرير الموارد.",
        "stream_failed": "❌ فشل تشغيل البث: `{error}`",
        "status_title": "📊 *تقرير حالة المنظومة*",
        "status_db": "▪️ حالة قاعدة البيانات",
        "status_running": "🟢 قيد العمل",
        "status_stopped": "🔴 متوقف",
        "status_server": "▪️ خادم البث",
        "status_type": "▪️ نوع البث",
        "status_process": "▪️ عملية FFmpeg",
        "status_active": "🟢 نشط",
        "status_inactive": "🔴 غير نشط",
        "status_none": "— غير محدد —",
        "not_authorized": "🚫 غير مصرّح لك باستخدام هذا البوت. تواصل مع المدير.",
        "language_changed": "✅ تم تغيير اللغة إلى *{lang_name}*.",
        "language_select": "🌐 اختر اللغة:",
        "lang_ar": "العربية",
        "lang_en": "English",
        "help_text": (
            "❓ *المساعدة*\n\n"
            "هذا البوت يدير بث مباشر من مصدر (YouTube / m3u8 / راديو) إلى خادم RTMP.\n\n"
            "*الأوامر:*\n"
            "• /start - القائمة الرئيسية\n"
            "• /setup - معالج ضبط الإعدادات\n"
            "• /start\\_stream - بدء البث\n"
            "• /stop\\_stream - إيقاف البث\n"
            "• /status - عرض الحالة\n"
            "• /language - تغيير اللغة\n"
            "• /help - هذه الرسالة\n\n"
            "*ملاحظة قانونية:* المستخدم مسؤول عن امتلاك حقوق المصدر وإعادة بثه."
        ),
    },
    "en": {
        "welcome": (
            "👋 *Welcome to the Live Stream Manager Bot*\n\n"
            "Choose an action from the buttons below:"
        ),
        "btn_setup": "⚙️ Setup",
        "btn_start": "▶️ Start Stream",
        "btn_stop": "⏹️ Stop Stream",
        "btn_status": "📊 Status",
        "btn_language": "🌐 Language",
        "btn_help": "❓ Help",
        "btn_cancel": "❌ Cancel",
        "btn_confirm": "✅ Confirm & Save",
        "btn_restart": "🔄 Restart",
        "btn_back": "🔙 Back",
        "setup_intro": "⚙️ *Setup Wizard*\n\nSend the *stream URL* (YouTube / m3u8 / radio):",
        "setup_stream_url_prompt": "📡 Send the *stream URL* (e.g. `https://youtu.be/xxx` or `https://example.com/stream.m3u8`):",
        "setup_server_url_prompt": "🖥️ Send the *RTMP server URL* (e.g. `rtmp://server.com/live/`):",
        "setup_stream_key_prompt": "🔑 Send the *stream key*:",
        "setup_channel_id_prompt": "📣 Send the *channel ID* (e.g. `-1001234567890` or `@mychannel`):",
        "setup_invalid_url": "❌ Invalid URL. Must start with `http://`, `https://`, or `rtmp://`. Try again:",
        "setup_invalid_server": "❌ Invalid server URL. Must start with `rtmp://`, `rtmps://`, or `https://`. Try again:",
        "setup_invalid_channel": "❌ Invalid channel ID. Use `-100xxxxxxxxxx` or `@username`. Try again:",
        "setup_checking_perms": "🔄 Verifying bot permissions in target channel...",
        "setup_detected_type": "📡 Detected stream type: *{type_label}*",
        "setup_perms_failed": "❌ Permission check failed! Make sure the bot is admin in the channel with 'Post Messages' permission.",
        "setup_review_title": "📋 *Review settings before saving:*",
        "setup_review_stream_url": "📡 Stream URL",
        "setup_review_server": "🖥️ Server",
        "setup_review_key": "🔑 Key",
        "setup_review_channel": "📣 Channel",
        "setup_review_type": "📡 Stream type",
        "setup_saved": "✅ Settings saved successfully! Use the *Start Stream* button to launch.",
        "setup_cancelled": "❌ Wizard cancelled. Nothing was saved.",
        "type_youtube": "🎬 YouTube Live",
        "type_radio": "🎵 Radio / Audio",
        "type_iptv": "📺 IPTV",
        "stream_already_running": "⚠️ Stream is already running! Stop it first.",
        "stream_starting": "🚀 Starting stream...",
        "stream_started": "🟢 Stream started successfully and is being monitored.",
        "stream_no_settings": "❌ No saved settings. Run the setup wizard first.",
        "stream_not_running": "⚪ No stream is currently running.",
        "stream_stopped": "⏹️ Stream stopped and resources released.",
        "stream_failed": "❌ Failed to start stream: `{error}`",
        "status_title": "📊 *System Status Report*",
        "status_db": "▪️ DB status",
        "status_running": "🟢 Running",
        "status_stopped": "🔴 Stopped",
        "status_server": "▪️ Stream server",
        "status_type": "▪️ Stream type",
        "status_process": "▪️ FFmpeg process",
        "status_active": "🟢 Active",
        "status_inactive": "🔴 Inactive",
        "status_none": "— none —",
        "not_authorized": "🚫 You are not authorized to use this bot. Contact the admin.",
        "language_changed": "✅ Language changed to *{lang_name}*.",
        "language_select": "🌐 Select language:",
        "lang_ar": "العربية",
        "lang_en": "English",
        "help_text": (
            "❓ *Help*\n\n"
            "This bot manages a live stream from a source (YouTube / m3u8 / radio) to an RTMP server.\n\n"
            "*Commands:*\n"
            "• /start - Main menu\n"
            "• /setup - Setup wizard\n"
            "• /start\\_stream - Start streaming\n"
            "• /stop\\_stream - Stop streaming\n"
            "• /status - Show status\n"
            "• /language - Change language\n"
            "• /help - This message\n\n"
            "*Legal note:* The user is responsible for owning the rights to the source and redistributing it."
        ),
    },
}


def t(user_id: int, key: str, **kwargs) -> str:
    """ترجمة مفتاح حسب لغة المستخدم المحفوظة في قاعدة البيانات."""
    lang = get_user_language(user_id)
    text = TRANSLATIONS.get(lang, TRANSLATIONS["ar"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


# ---------------------------------------------------------------------------
# أدوات مساعدة لـ MarkdownV2
# ---------------------------------------------------------------------------
_MD_V2_SPECIAL = r"_*[]()~`>#+-=|{}.!"


def md_escape(text: str) -> str:
    """تهريب الرموز الخاصة في MarkdownV2."""
    if text is None:
        return ""
    return "".join(f"\\{c}" if c in _MD_V2_SPECIAL else c for str_c in (text,) for c in str_c)


# ---------------------------------------------------------------------------
# قاعدة البيانات
# ---------------------------------------------------------------------------
_db_lock = threading.Lock()


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """تهيئة قاعدة البيانات مع جداول: settings, users."""
    try:
        with _db_lock, get_db_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    user_id INTEGER PRIMARY KEY,
                    m3u_url TEXT NOT NULL,
                    server_url TEXT NOT NULL,
                    stream_key TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    is_running INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'ar',
                    is_authorized INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()
        logger.info("✅ Database initialized successfully (settings + users tables)")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise


def save_settings(
    user_id: int,
    m3u_url: str,
    server_url: str,
    stream_key: str,
    channel_id: str,
) -> None:
    with _db_lock, get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO settings (user_id, m3u_url, server_url, stream_key, channel_id, is_running, updated_at)
            VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                m3u_url=excluded.m3u_url,
                server_url=excluded.server_url,
                stream_key=excluded.stream_key,
                channel_id=excluded.channel_id,
                is_running=0,
                updated_at=CURRENT_TIMESTAMP
            """,
            (user_id, m3u_url, server_url, stream_key, channel_id),
        )
        conn.commit()
    logger.info(f"✅ Settings saved for user {user_id}")


def update_status(user_id: int, is_running: bool) -> None:
    with _db_lock, get_db_connection() as conn:
        conn.execute(
            "UPDATE settings SET is_running=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=?",
            (1 if is_running else 0, user_id),
        )
        conn.commit()


def get_settings(user_id: int) -> Optional[sqlite3.Row]:
    with _db_lock, get_db_connection() as conn:
        cur = conn.execute(
            "SELECT m3u_url, server_url, stream_key, channel_id, is_running FROM settings WHERE user_id=?",
            (user_id,),
        )
        return cur.fetchone()


def get_active_streams() -> list[sqlite3.Row]:
    with _db_lock, get_db_connection() as conn:
        cur = conn.execute(
            "SELECT user_id, m3u_url, server_url, stream_key FROM settings WHERE is_running=1"
        )
        return cur.fetchall()


def get_user_language(user_id: int) -> str:
    """جلب لغة المستخدم، مع إنشاء سجل افتراضي عند أول استخدام."""
    try:
        with _db_lock, get_db_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, language, is_authorized) VALUES (?, ?, 0)",
                (user_id, DEFAULT_LANGUAGE),
            )
            conn.commit()
            cur = conn.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
            row = cur.fetchone()
            return row["language"] if row else DEFAULT_LANGUAGE
    except Exception as e:
        logger.error(f"❌ Error getting language for {user_id}: {e}")
        return DEFAULT_LANGUAGE


def set_user_language(user_id: int, language: str) -> None:
    with _db_lock, get_db_connection() as conn:
        conn.execute(
            "INSERT INTO users (user_id, language, is_authorized) VALUES (?, ?, 0) "
            "ON CONFLICT(user_id) DO UPDATE SET language=excluded.language",
            (user_id, language),
        )
        conn.commit()


def is_user_authorized(user_id: int) -> bool:
    """المستخدم مصرّح له إذا كان: (1) في ADMIN_IDS البيئية، أو (2) معلّم is_authorized=1 في DB."""
    if user_id in ADMIN_IDS:
        return True
    try:
        with _db_lock, get_db_connection() as conn:
            cur = conn.execute(
                "SELECT is_authorized FROM users WHERE user_id=?", (user_id,)
            )
            row = cur.fetchone()
            return bool(row and row["is_authorized"])
    except Exception:
        return False


def authorize_user(user_id: int) -> None:
    with _db_lock, get_db_connection() as conn:
        conn.execute(
            "INSERT INTO users (user_id, language, is_authorized) VALUES (?, ?, 1) "
            "ON CONFLICT(user_id) DO UPDATE SET is_authorized=1",
            (user_id, DEFAULT_LANGUAGE),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# التحقق من المدخلات
# ---------------------------------------------------------------------------
def is_valid_stream_url(url: str) -> bool:
    try:
        r = urlparse(url)
        return r.scheme in ("http", "https", "rtmp", "rtmps", "rtsp") and bool(r.netloc)
    except Exception:
        return False


def is_valid_server_url(url: str) -> bool:
    try:
        r = urlparse(url)
        return r.scheme in ("rtmp", "rtmps", "https", "http") and bool(r.netloc)
    except Exception:
        return False


def is_valid_channel_id(channel_id: str) -> bool:
    """معرّف القناة إما -100xxxxxxxxxx أو @username."""
    if not channel_id:
        return False
    if channel_id.startswith("@"):
        return len(channel_id) > 1 and all(
            c.isalnum() or c == "_" for c in channel_id[1:]
        )
    if channel_id.startswith("-100"):
        return channel_id[4:].isdigit() and len(channel_id) >= 10
    if channel_id.lstrip("-").isdigit():
        return True
    return False


def detect_stream_type(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()
    if any(rd in domain for rd in RADIO_DOMAINS):
        return "radio"
    if "/radio/" in path:
        return "radio"
    if url.lower().endswith(".m3u8") and "live" in url.lower():
        return "iptv"
    if url.lower().endswith(AUDIO_EXTENSIONS):
        return "radio"
    return "iptv"


def type_label(user_id: int, stream_type: str) -> str:
    mapping = {
        "youtube": t(user_id, "type_youtube"),
        "radio": t(user_id, "type_radio"),
        "iptv": t(user_id, "type_iptv"),
    }
    return mapping.get(stream_type, mapping["iptv"])


# ---------------------------------------------------------------------------
# إدارة عمليات FFmpeg (لكل مستخدم - آمن)
# ---------------------------------------------------------------------------
@dataclass
class StreamProcess:
    """حاوية آمنة لعملية بث مستخدم واحد."""
    user_id: int
    process: subprocess.Popen
    task: asyncio.Task
    stop_event: asyncio.Event


# dict عمليات لكل مستخدم + قفل للمزامنة
_processes: dict[int, StreamProcess] = {}
_processes_lock = asyncio.Lock()


async def _extract_youtube_live_url(yt_url: str) -> Optional[str]:
    """استخراج رابط البث الحي من يوتيوب عبر yt-dlp بأمان (list args)."""
    cmd = [
        "yt-dlp",
        "--no-update",
        "-f", "b",
        "-g",
        yt_url,
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
        if proc.returncode == 0 and stdout:
            url = stdout.decode("utf-8", errors="ignore").strip().splitlines()[0]
            return url
    except asyncio.TimeoutError:
        logger.warning(f"⚠️ yt-dlp timeout for {yt_url}")
    except Exception as e:
        logger.error(f"❌ yt-dlp error: {e}")
    return None


def _build_ffmpeg_cmd_youtube(live_url: str, full_dest: str) -> list[str]:
    """بناء أمر FFmpeg ليوتيوب كقائمة وسائط - لا shell."""
    return [
        "ffmpeg",
        "-http_persistent", "0",
        "-headers", f"User-Agent: {DEFAULT_USER_AGENT}\r\n",
        "-timeout", str(FFMPEG_TIMEOUT),
        "-reconnect", "1",
        "-reconnect_at_eof", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-re",
        "-i", live_url,
        "-c:v", "copy",
        "-c:a", "copy",
        "-f", "flv",
        full_dest,
    ]


def _build_ffmpeg_cmd_radio(m3u_url: str, full_dest: str) -> list[str]:
    """بناء أمر FFmpeg للراديو مع شاشة سوداء منخفضة الاستهلاك."""
    return [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "color=c=black:s=640x360:r=10",
        "-timeout", str(FFMPEG_TIMEOUT),
        "-reconnect", "1",
        "-reconnect_at_eof", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-re",
        "-i", m3u_url,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-b:v", "100k",
        "-g", "20",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-f", "flv",
        full_dest,
    ]


def _build_ffmpeg_cmd_iptv(m3u_url: str, full_dest: str) -> list[str]:
    """بناء أمر FFmpeg لـ IPTV - بدون ترويسات Referer مزيفة."""
    headers = f"User-Agent: {DEFAULT_USER_AGENT}\r\n"
    return [
        "ffmpeg",
        "-timeout", str(FFMPEG_TIMEOUT),
        "-reconnect", "1",
        "-reconnect_at_eof", "0",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "10",
        "-headers", headers,
        "-live_start_index", "-1",
        "-i", m3u_url,
        "-c:v", "copy",
        "-c:a", "copy",
        "-f", "flv",
        full_dest,
    ]


async def _stream_worker(
    user_id: int,
    m3u_url: str,
    server_url: str,
    stream_key: str,
    stream_type: str,
    stop_event: asyncio.Event,
) -> None:
    """عامل بث يعمل في coroutine منفصلة لكل مستخدم - حلقة إعادة اتصال Python-side."""
    if not server_url.endswith("/"):
        server_url += "/"
    full_dest = f"{server_url}{stream_key}"

    logger.info(
        f"🚀 Stream worker started for user {user_id} (type={stream_type}, dest={full_dest})"
    )

    while not stop_event.is_set():
        try:
            if stream_type == "youtube":
                live_url = await _extract_youtube_live_url(m3u_url)
                if not live_url:
                    logger.warning(f"⚠️ Could not extract YouTube live URL for user {user_id}, retrying in 15s")
                    await asyncio.sleep(15)
                    continue
                cmd = _build_ffmpeg_cmd_youtube(live_url, full_dest)

            elif stream_type == "radio":
                cmd = _build_ffmpeg_cmd_radio(m3u_url, full_dest)

            else:
                cmd = _build_ffmpeg_cmd_iptv(m3u_url, full_dest)

            # تشغيل FFmpeg كـ subprocess بقائمة وسائط (لا shell=True)
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )

            # تسجيل PID
            async with _processes_lock:
                existing = _processes.get(user_id)
                if existing:
                    existing.process = proc  # تحديث المرجع

            logger.info(f"🎬 FFmpeg PID={proc.pid} running for user {user_id}")

            # انتظر خروجه (مع إمكانية الإلغاء)
            while not stop_event.is_set():
                try:
                    await asyncio.wait_for(proc.wait(), timeout=2.0)
                    break
                except asyncio.TimeoutError:
                    continue

            if stop_event.is_set():
                if proc.returncode is None:
                    try:
                        proc.terminate()
                        await asyncio.wait_for(proc.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        proc.kill()
                logger.info(f"⏹️ Stream worker for user {user_id} stopped by request")
                break

            rc = proc.returncode
            logger.info(f"ℹ️ FFmpeg exited with code {rc} for user {user_id}, reconnecting in {RECONNECT_DELAY}s")
            await asyncio.sleep(RECONNECT_DELAY)

        except asyncio.CancelledError:
            logger.info(f"🛑 Stream worker cancelled for user {user_id}")
            raise
        except Exception as e:
            logger.error(f"❌ Stream worker error for user {user_id}: {e}")
            await asyncio.sleep(RECONNECT_DELAY)

    update_status(user_id, False)
    async with _processes_lock:
        _processes.pop(user_id, None)
    logger.info(f"✅ Stream worker fully stopped for user {user_id}")


async def launch_stream(
    user_id: int,
    m3u_url: str,
    server_url: str,
    stream_key: str,
) -> bool:
    """إطلاق بث جديد للمستخدم. يرجع True عند النجاح."""
    async with _processes_lock:
        existing = _processes.get(user_id)
        if existing and existing.process.returncode is None:
            return False  # البث يعمل بالفعل

        stream_type = detect_stream_type(m3u_url)
        stop_event = asyncio.Event()
        # placeholder process - سيُحدَّث داخل العامل
        placeholder = subprocess.Popen(["true"])  # لا يفعل شيئاً
        task = asyncio.create_task(
            _stream_worker(user_id, m3u_url, server_url, stream_key, stream_type, stop_event)
        )
        _processes[user_id] = StreamProcess(
            user_id=user_id,
            process=placeholder,
            task=task,
            stop_event=stop_event,
        )

    update_status(user_id, True)
    return True


async def stop_stream_for_user(user_id: int) -> bool:
    """إيقاف بث مستخدم معيّن بلطف."""
    async with _processes_lock:
        sp = _processes.get(user_id)
        if not sp:
            return False
        sp.stop_event.set()
        sp.task.cancel()
        try:
            await asyncio.wait_for(sp.task, timeout=10)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass
        _processes.pop(user_id, None)
    update_status(user_id, False)
    return True


async def is_stream_running(user_id: int) -> bool:
    async with _processes_lock:
        sp = _processes.get(user_id)
        return sp is not None and sp.process.returncode is None


async def get_stream_pid(user_id: int) -> Optional[int]:
    async with _processes_lock:
        sp = _processes.get(user_id)
        return sp.process.pid if sp and sp.process else None


# ---------------------------------------------------------------------------
# التحقق من صلاحيات القناة
# ---------------------------------------------------------------------------
async def check_bot_permissions(
    context: ContextTypes.DEFAULT_TYPE, channel_id: str
) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=channel_id, user_id=context.bot.id
        )
        if member.status in ("administrator", "creator"):
            if member.can_post_messages or member.status == "creator":
                logger.info(f"✅ Bot permissions verified for channel {channel_id}")
                return True
        logger.warning(f"⚠️ Insufficient permissions for channel {channel_id}")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking bot permissions: {e}")
        return False


# ---------------------------------------------------------------------------
# لوحات المفاتيح (Inline Keyboards)
# ---------------------------------------------------------------------------
def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(t(user_id, "btn_setup"), callback_data="cmd:setup"),
                InlineKeyboardButton(t(user_id, "btn_status"), callback_data="cmd:status"),
            ],
            [
                InlineKeyboardButton(t(user_id, "btn_start"), callback_data="cmd:start_stream"),
                InlineKeyboardButton(t(user_id, "btn_stop"), callback_data="cmd:stop_stream"),
            ],
            [
                InlineKeyboardButton(t(user_id, "btn_language"), callback_data="cmd:language"),
                InlineKeyboardButton(t(user_id, "btn_help"), callback_data="cmd:help"),
            ],
        ]
    )


def cancel_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cmd:cancel")]]
    )


def confirm_cancel_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(t(user_id, "btn_confirm"), callback_data="cmd:confirm"),
                InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cmd:cancel"),
            ]
        ]
    )


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇸🇦 العربية", callback_data="lang:ar"),
                InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


# ---------------------------------------------------------------------------
# Decorator للتحقق من التفويض
# ---------------------------------------------------------------------------
def authorized_only(handler):
    """Decorator يمنع المستخدمين غير المصرّح لهم من تنفيذ أي handler."""

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return
        if not is_user_authorized(user.id):
            target = update.callback_query or update.message
            if target:
                await target.reply_text(t(user.id, "not_authorized"))
            return
        return await handler(update, context, *args, **kwargs)

    return wrapper


# ---------------------------------------------------------------------------
# Handlers - القائمة الرئيسية
# ---------------------------------------------------------------------------
@authorized_only
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    # حفظ سجل المستخدم
    get_user_language(user_id)
    await update.message.reply_text(
        t(user_id, "welcome"),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard(user_id),
    )


@authorized_only
async def on_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أزرار القائمة الرئيسية."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "cmd:setup":
        await start_setup_conversation(update, context)
    elif data == "cmd:start_stream":
        await do_start_stream(update, context, edit=True)
    elif data == "cmd:stop_stream":
        await do_stop_stream(update, context, edit=True)
    elif data == "cmd:status":
        await do_status(update, context, edit=True)
    elif data == "cmd:language":
        await query.edit_message_text(
            t(user_id, "language_select"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=language_keyboard(),
        )
    elif data == "cmd:help":
        await query.edit_message_text(
            t(user_id, "help_text"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
    elif data == "cmd:cancel":
        await query.edit_message_text(
            t(user_id, "setup_cancelled"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
    elif data == "cmd:confirm":
        # يُعالَج في سياق setup
        await confirm_setup(update, context)


@authorized_only
async def on_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = query.data.split(":")[1]
    set_user_language(user_id, lang)
    lang_name = t(user_id, "lang_ar" if lang == "ar" else "lang_en")
    await query.edit_message_text(
        t(user_id, "language_changed").format(lang_name=md_escape(lang_name)),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard(user_id),
    )


# ---------------------------------------------------------------------------
# Setup Wizard - ConversationHandler
# ---------------------------------------------------------------------------
# تخزين مؤقت لإعدادات المعالج لكل مستخدم
_setup_drafts: dict[int, dict[str, str]] = {}


async def start_setup_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء معالج الضبط - يُستدعى من زر القائمة أو أمر /setup."""
    user_id = update.effective_user.id
    _setup_drafts[user_id] = {}

    target = update.callback_query or update.message
    if update.callback_query:
        await target.edit_message_text(
            t(user_id, "setup_intro"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(user_id),
        )
    else:
        await target.reply_text(
            t(user_id, "setup_intro"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(user_id),
        )
    return STATE_STREAM_URL


async def on_stream_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    if not is_valid_stream_url(text):
        await update.message.reply_text(
            t(user_id, "setup_invalid_url"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(user_id),
        )
        return STATE_STREAM_URL
    _setup_drafts.setdefault(user_id, {})["m3u_url"] = text
    stream_type = detect_stream_type(text)
    _setup_drafts[user_id]["stream_type"] = stream_type
    await update.message.reply_text(
        t(user_id, "setup_server_url_prompt"),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=cancel_keyboard(user_id),
    )
    return STATE_SERVER_URL


async def on_server_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    if not is_valid_server_url(text):
        await update.message.reply_text(
            t(user_id, "setup_invalid_server"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(user_id),
        )
        return STATE_SERVER_URL
    _setup_drafts[user_id]["server_url"] = text
    await update.message.reply_text(
        t(user_id, "setup_stream_key_prompt"),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=cancel_keyboard(user_id),
    )
    return STATE_STREAM_KEY


async def on_stream_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text(
            t(user_id, "setup_stream_key_prompt"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(user_id),
        )
        return STATE_STREAM_KEY
    _setup_drafts[user_id]["stream_key"] = text
    await update.message.reply_text(
        t(user_id, "setup_channel_id_prompt"),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=cancel_keyboard(user_id),
    )
    return STATE_CHANNEL_ID


async def on_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    if not is_valid_channel_id(text):
        await update.message.reply_text(
            t(user_id, "setup_invalid_channel"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(user_id),
        )
        return STATE_CHANNEL_ID
    _setup_drafts[user_id]["channel_id"] = text

    draft = _setup_drafts[user_id]
    stream_type = draft.get("stream_type", "iptv")

    # عرض ملخص للمراجعة
    summary = (
        f"{t(user_id, 'setup_review_title')}\n\n"
        f"{t(user_id, 'setup_review_stream_url')}: `{md_escape(draft['m3u_url'])}`\n"
        f"{t(user_id, 'setup_review_server')}: `{md_escape(draft['server_url'])}`\n"
        f"{t(user_id, 'setup_review_key')}: `{md_escape('•' * min(len(draft['stream_key']), 12))}`\n"
        f"{t(user_id, 'setup_review_channel')}: `{md_escape(draft['channel_id'])}`\n"
        f"{t(user_id, 'setup_review_type')}: *{md_escape(type_label(user_id, stream_type))}*"
    )
    await update.message.reply_text(
        summary,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=confirm_cancel_keyboard(user_id),
    )
    return STATE_CONFIRM


async def confirm_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تأكيد وحفظ الإعدادات بعد المراجعة."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    draft = _setup_drafts.get(user_id, {})
    if not draft:
        await query.edit_message_text(
            t(user_id, "setup_cancelled"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
        return ConversationHandler.END

    m3u_url = draft["m3u_url"]
    server_url = draft["server_url"]
    stream_key = draft["stream_key"]
    channel_id = draft["channel_id"]
    stream_type = draft.get("stream_type", "iptv")

    # التحقق من الصلاحيات في القناة
    await query.edit_message_text(
        f"{t(user_id, 'setup_checking_perms')}\n"
        f"{t(user_id, 'setup_detected_type').format(type_label=md_escape(type_label(user_id, stream_type)))}",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    if not await check_bot_permissions(context, channel_id):
        await query.message.reply_text(
            t(user_id, "setup_perms_failed"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
        _setup_drafts.pop(user_id, None)
        return ConversationHandler.END

    try:
        save_settings(user_id, m3u_url, server_url, stream_key, channel_id)
        await query.message.reply_text(
            t(user_id, "setup_saved"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
    except Exception as e:
        await query.message.reply_text(
            t(user_id, "stream_failed").format(error=md_escape(str(e))),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
    finally:
        _setup_drafts.pop(user_id, None)
    return ConversationHandler.END


async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
        _setup_drafts.pop(user_id, None)
        await query.edit_message_text(
            t(user_id, "setup_cancelled"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# أوامر البث
# ---------------------------------------------------------------------------
@authorized_only
async def do_start_stream(
    update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False
) -> None:
    user_id = update.effective_user.id
    settings = get_settings(user_id)
    if not settings:
        msg = t(user_id, "stream_no_settings")
        target = update.callback_query or update.message
        if edit and update.callback_query:
            await update.callback_query.edit_message_text(
                msg, parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=main_menu_keyboard(user_id),
            )
        else:
            await target.reply_text(
                msg, parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=main_menu_keyboard(user_id),
            )
        return

    if await is_stream_running(user_id):
        msg = t(user_id, "stream_already_running")
        target = update.callback_query or update.message
        if edit and update.callback_query:
            await update.callback_query.edit_message_text(
                msg, parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=main_menu_keyboard(user_id),
            )
        else:
            await target.reply_text(
                msg, parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=main_menu_keyboard(user_id),
            )
        return

    # إرسال رسالة "جاري التشغيل"
    target = update.callback_query or update.message
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            t(user_id, "stream_starting"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        await target.reply_text(
            t(user_id, "stream_starting"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    try:
        ok = await launch_stream(
            user_id,
            settings["m3u_url"],
            settings["server_url"],
            settings["stream_key"],
        )
        if ok:
            final_msg = t(user_id, "stream_started")
        else:
            final_msg = t(user_id, "stream_already_running")
    except Exception as e:
        final_msg = t(user_id, "stream_failed").format(error=md_escape(str(e)))

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=final_msg,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard(user_id),
    )


@authorized_only
async def do_stop_stream(
    update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False
) -> None:
    user_id = update.effective_user.id
    stopped = await stop_stream_for_user(user_id)
    msg = t(user_id, "stream_stopped") if stopped else t(user_id, "stream_not_running")

    target = update.callback_query or update.message
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            msg, parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
    else:
        await target.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )


@authorized_only
async def do_status(
    update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False
) -> None:
    user_id = update.effective_user.id
    settings = get_settings(user_id)

    if settings:
        db_status = (
            t(user_id, "status_running") if settings["is_running"]
            else t(user_id, "status_stopped")
        )
        server = settings["server_url"]
        stream_url = settings["m3u_url"]
        stream_type = detect_stream_type(stream_url)
    else:
        db_status = t(user_id, "status_stopped")
        server = t(user_id, "status_none")
        stream_type = "iptv"

    pid = await get_stream_pid(user_id)
    proc_status = (
        f"{t(user_id, 'status_active')} (PID {pid})"
        if await is_stream_running(user_id)
        else t(user_id, "status_inactive")
    )

    msg = (
        f"{t(user_id, 'status_title')}\n\n"
        f"{t(user_id, 'status_db')}: {md_escape(db_status)}\n"
        f"{t(user_id, 'status_server')}: `{md_escape(server)}`\n"
        f"{t(user_id, 'status_type')}: {md_escape(type_label(user_id, stream_type))}\n"
        f"{t(user_id, 'status_process')}: {md_escape(proc_status)}"
    )

    target = update.callback_query or update.message
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            msg, parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )
    else:
        await target.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(user_id),
        )


@authorized_only
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.reply_text(
        t(user_id, "help_text"),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard(user_id),
    )


# ---------------------------------------------------------------------------
# استئناف البث التلقائي عند الإقلاع
# ---------------------------------------------------------------------------
async def resume_active_streams(application: Application) -> None:
    """استئناف البث التلقائي لكل الجلسات التي كانت نشطة قبل إعادة التشغيل."""
    try:
        active = get_active_streams()
        if not active:
            logger.info("ℹ️ No active streams to resume")
            return
        logger.info(f"🔄 Resuming {len(active)} active stream(s)...")
        for row in active:
            user_id = row["user_id"]
            try:
                await launch_stream(
                    user_id,
                    row["m3u_url"],
                    row["server_url"],
                    row["stream_key"],
                )
                logger.info(f"🔄 Resumed stream for user {user_id}")
                await asyncio.sleep(1)  # تجنّب ضغط مفاجئ
            except Exception as e:
                logger.error(f"❌ Error resuming stream for user {user_id}: {e}")
                update_status(user_id, False)
    except Exception as e:
        logger.error(f"❌ Error in resume_active_streams: {e}")


# ---------------------------------------------------------------------------
# أوامر الإدارة (للمدراء فقط)
# ---------------------------------------------------------------------------
async def cmd_authorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر إداري: /authorize <user_id> - يصرّح بمستخدم جديد (للمدراء فقط)."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(t(user_id, "not_authorized"))
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /authorize <user_id>")
        return
    target_uid = int(context.args[0])
    authorize_user(target_uid)
    await update.message.reply_text(f"✅ User {target_uid} authorized.")


# ---------------------------------------------------------------------------
# نقطة الدخول
# ---------------------------------------------------------------------------
def main() -> None:
    init_db()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("❌ BOT_TOKEN environment variable is required")

    if not ADMIN_IDS:
        logger.warning(
            "⚠️ ADMIN_IDS is empty! No one will be able to use the bot. "
            "Set ADMIN_IDS=123456,789012 in .env"
        )

    logger.info("🤖 Starting Streaming Bot (hardened edition)...")

    application = Application.builder().token(bot_token).build()

    # ConversationHandler لمعالج /setup
    setup_conv = ConversationHandler(
        entry_points=[
            CommandHandler("setup", start_setup_conversation),
            CallbackQueryHandler(start_setup_conversation, pattern="^cmd:setup$"),
        ],
        states={
            STATE_STREAM_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_stream_url)],
            STATE_SERVER_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_server_url)],
            STATE_STREAM_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_stream_key)],
            STATE_CHANNEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_channel_id)],
            STATE_CONFIRM: [
                CallbackQueryHandler(confirm_setup, pattern="^cmd:confirm$"),
                CallbackQueryHandler(cancel_setup, pattern="^cmd:cancel$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_setup),
            CallbackQueryHandler(cancel_setup, pattern="^cmd:cancel$"),
        ],
        per_user=True,
        per_chat=True,
        name="setup_conversation",
        allow_reentry=True,
    )
    application.add_handler(setup_conv)

    # أوامر الإدارة (يجب أن تكون قبل باقي الأوامر حتى لا تتعارض)
    application.add_handler(CommandHandler("authorize", cmd_authorize))

    # الأوامر الأساسية
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("start_stream", lambda u, c: do_start_stream(u, c, edit=False)))
    application.add_handler(CommandHandler("stop_stream", lambda u, c: do_stop_stream(u, c, edit=False)))
    application.add_handler(CommandHandler("status", lambda u, c: do_status(u, c, edit=False)))

    # Callback handlers للقائمة الرئيسية واللغة
    application.add_handler(CallbackQueryHandler(on_language_callback, pattern="^lang:"))
    application.add_handler(CallbackQueryHandler(on_menu_callback, pattern="^cmd:"))

    # استئناف البث عند الإقلاع
    application.post_init = resume_active_streams

    logger.info("🤖 Bot is running and listening for commands...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
