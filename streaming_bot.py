import logging
import subprocess
import os
import signal
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database and Process Management
DB_NAME = os.getenv("DATABASE_PATH", "stream_manager.db")
process_pointer = None

# FFmpeg Configuration
FFMPEG_TIMEOUT = int(os.getenv("FFMPEG_TIMEOUT", "15000000"))
RECONNECT_DELAY = int(os.getenv("RECONNECT_DELAY", "5"))

def init_db():
    """Initialize SQLite database with required tables."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    user_id INTEGER PRIMARY KEY,
                    m3u_url TEXT,
                    server_url TEXT,
                    stream_key TEXT,
                    channel_id TEXT,
                    is_running INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")

def save_settings(user_id, m3u_url, server_url, stream_key, channel_id):
    """Save user streaming settings to database."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                REPLACE INTO settings (user_id, m3u_url, server_url, stream_key, channel_id, is_running, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
            ''', (user_id, m3u_url, server_url, stream_key, channel_id))
            conn.commit()
            logger.info(f"✅ Settings saved for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Error saving settings: {e}")
        raise

def update_status(user_id, is_running):
    """Update streaming status for a user."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE settings SET is_running = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', 
                (is_running, user_id)
            )
            conn.commit()
            logger.info(f"📊 Status updated for user {user_id}: {'Running' if is_running else 'Stopped'}")
    except Exception as e:
        logger.error(f"❌ Error updating status: {e}")

def get_settings(user_id):
    """Retrieve streaming settings for a user."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT m3u_url, server_url, stream_key, channel_id, is_running FROM settings WHERE user_id = ?', 
                (user_id,)
            )
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"❌ Error retrieving settings: {e}")
        return None

def get_active_streams():
    """Get all active streaming sessions."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, m3u_url, server_url, stream_key FROM settings WHERE is_running = 1')
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"❌ Error retrieving active streams: {e}")
        return []


def launch_ffmpeg_process(m3u_url, server_url, stream_key):
    """Launch FFmpeg process with appropriate streaming configuration."""
    global process_pointer
    
    try:
        if not server_url.endswith('/'):
            server_url += '/'
            
        full_rtmp_destination = f"{server_url}{stream_key}"
        
        # YouTube Streams Configuration
        if "youtube.com" in m3u_url or "youtu.be" in m3u_url:
            bash_command = (
                f'while true; do '
                f'LIVE_URL=$(yt-dlp --no-update -f "b" -g "{m3u_url}"); '
                f'ffmpeg -http_persistent 0 -headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" '
                f'-rw_timeout {FFMPEG_TIMEOUT} -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
                f'-re -i "$LIVE_URL" -c:v copy -c:a copy -f flv "{full_rtmp_destination}"; '
                f'sleep {RECONNECT_DELAY}; '
                f'done'
            )
            logger.info("🎬 YouTube streaming configured")
            
        # M3U Playlists Configuration (Radio/Audio)
        elif "aymane.xyz" in m3u_url or m3u_url.endswith('.m3u8') and not "live" in m3u_url:
            bash_command = (
                f'while true; do '
                f'ffmpeg -rw_timeout {FFMPEG_TIMEOUT} -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
                f'-f lavfi -i color=c=black:s=640x360:r=10 '
                f'-re -i "{m3u_url}" '
                f'-c:v libx264 -pix_fmt yuv420p -b:v 100k -g 20 '
                f'-c:a copy '
                f'-shortest -f flv "{full_rtmp_destination}"; '
                f'sleep {RECONNECT_DELAY}; '
                f'done'
            )
            logger.info("🎵 M3U/Radio streaming configured")
            
        # Standard IPTV Streams Configuration
        else:
            bash_command = (
                f'while true; do '
                f'ffmpeg -rw_timeout {FFMPEG_TIMEOUT} -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
                f'-re -i "{m3u_url}" -c:v copy -c:a copy -f flv "{full_rtmp_destination}"; '
                f'sleep 10; '
                f'done'
            )
            logger.info("📺 IPTV streaming configured")
        
        # Launch FFmpeg process
        process_pointer = subprocess.Popen(bash_command, shell=True, preexec_fn=os.setsid)
        logger.info(f"🚀 FFmpeg process launched with PID: {process_pointer.pid}")
        return process_pointer
        
    except Exception as e:
        logger.error(f"❌ Error launching FFmpeg: {e}")
        raise


async def resume_active_streams(application: Application):
    """Resume all active streams on bot startup."""
    global process_pointer
    try:
        active_streams = get_active_streams()
        if active_streams:
            logger.info(f"🔄 Resuming {len(active_streams)} active stream(s)...")
            for stream in active_streams:
                user_id, m3u_url, server_url, stream_key = stream
                try:
                    logger.info(f"🔄 جاري استئناف البث التلقائي للمستخدم: {user_id}")
                    launch_ffmpeg_process(m3u_url, server_url, stream_key)
                except Exception as e:
                    logger.error(f"❌ Error resuming stream for user {user_id}: {e}")
        else:
            logger.info("ℹ️ No active streams to resume")
    except Exception as e:
        logger.error(f"❌ Error in resume_active_streams: {e}")


async def check_bot_permissions(context: ContextTypes.DEFAULT_TYPE, channel_id: str) -> bool:
    """Verify bot has necessary permissions in the channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=channel_id, user_id=context.bot.id)
        if member.status in ['administrator', 'creator']:
            if member.can_post_messages or member.status == 'creator':
                logger.info(f"✅ Bot permissions verified for channel {channel_id}")
                return True
        logger.warning(f"⚠️ Insufficient permissions for channel {channel_id}")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking bot permissions: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome = (
        "👋 أهلاً بك في بوت إدارة البث المباشر المرن!\n\n"
        "**الأوامر الحالية:**\n"
        "1️⃣ `/setup [رابط_M3U] [عنوان_الخادم] [مفتاح_البث] [معرف_القناة]`\n"
        "2️⃣ `/start_stream` - لبدء البث\n"
        "3️⃣ `/stop_stream` - لإيقاف البث\n"
        "4️⃣ `/status` - لعرض حالة الجلسة\n\n"
        "📖 للمزيد من المعلومات، انظر التوثيق: https://github.com/IIDZII/streaming-bot"
    )
    logger.info(f"👋 User {update.effective_user.id} started the bot")
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def setup_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setup command to configure streaming settings."""
    user_id = update.effective_user.id
    if len(context.args) < 4:
        await update.message.reply_text(
            "❌ الاستخدام الصحيح:\n`/setup [رابط_M3U] [عنوان_الخادم] [مفتاح_البث] [معرف_القناة]`", 
            parse_mode="Markdown"
        )
        logger.warning(f"❌ Invalid setup command from user {user_id}")
        return

    m3u_url = context.args[0]
    server_url = context.args[1]
    stream_key = context.args[2]
    channel_id = context.args[3]
    
    await update.message.reply_text("🔄 جاري التحقق من صلاحيات البوت في القناة...")
    logger.info(f"🔍 Checking permissions for user {user_id}")
    
    if not await check_bot_permissions(context, channel_id):
        await update.message.reply_text(
            "❌ فشل التحقق! تأكد من رفع البوت آدمن في القناة ومنحه صلاحية 'نشر الرسائل'."
        )
        logger.error(f"❌ Permission check failed for user {user_id}")
        return

    try:
        save_settings(user_id, m3u_url, server_url, stream_key, channel_id)
        await update.message.reply_text(
            "✅ تم حفظ الإعدادات بنجاح!\nأرسل الآن `/start_stream` للبدء.",
            parse_mode="Markdown"
        )
        logger.info(f"✅ Settings saved successfully for user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ أثناء حفظ الإعدادات: {str(e)}")
        logger.error(f"❌ Error saving settings for user {user_id}: {e}")

async def start_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start_stream command to begin streaming."""
    global process_pointer
    user_id = update.effective_user.id
    
    if process_pointer and process_pointer.poll() is None:
        await update.message.reply_text("⚠️ منظومة البث تعمل بالفعل!")
        logger.warning(f"⚠️ Stream already running for user {user_id}")
        return

    settings = get_settings(user_id)
    if not settings:
        await update.message.reply_text(
            "❌ لم يتم ضبط الإعدادات بعد، استخدم أمر `/setup` أولاً.",
            parse_mode="Markdown"
        )
        logger.warning(f"❌ No settings found for user {user_id}")
        return

    m3u_url, server_url, stream_key, _, _ = settings
    await update.message.reply_text("🚀 جاري تفعيل سكريبت المراقبة والبث...")
    logger.info(f"🚀 Starting stream for user {user_id}")
    
    try:
        launch_ffmpeg_process(m3u_url, server_url, stream_key)
        update_status(user_id, 1)
        await update.message.reply_text("🟢 تم تفعيل البث بنجاح!")
        logger.info(f"🟢 Stream started successfully for user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")
        logger.error(f"❌ Error starting stream for user {user_id}: {e}")

async def stop_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop_stream command to stop streaming."""
    global process_pointer
    user_id = update.effective_user.id
    
    if process_pointer and process_pointer.poll() is None:
        try:
            os.killpg(os.getpgid(process_pointer.pid), signal.SIGTERM)
            process_pointer = None
            update_status(user_id, 0)
            await update.message.reply_text("⏹️ تم إيقاف عملية البث.")
            logger.info(f"⏹️ Stream stopped for user {user_id}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ أثناء الإيقاف: {str(e)}")
            logger.error(f"❌ Error stopping stream for user {user_id}: {e}")
    else:
        await update.message.reply_text("⚪ لا يوجد بث يعمل حالياً.")
        logger.info(f"ℹ️ No active stream to stop for user {user_id}")

async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command to check streaming status."""
    global process_pointer
    user_id = update.effective_user.id
    settings = get_settings(user_id)
    
    db_status = "🔴 متوقف" if not settings or settings[4] == 0 else "🟢 قيد العمل"
    script_status = "🟢 نشط" if process_pointer and process_pointer.poll() is None else "🔴 غير نشط"
    
    status_message = (
        f"📊 **حالة الجلسة الحالية:**\n"
        f"- في قاعدة البيانات: {db_status}\n"
        f"- خادم البث: `{settings[1] if settings else 'غير محدد'}`\n"
        f"- عملية FFmpeg: {script_status}"
    )
    
    await update.message.reply_text(status_message, parse_mode="Markdown")
    logger.info(f"📊 Status checked for user {user_id}")

def main():
    """Main entry point for the bot."""
    # Initialize database
    init_db()

    # Get bot token from environment
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        raise ValueError("BOT_TOKEN environment variable is required")
    
    logger.info("🤖 Starting Streaming Bot...")

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setup", setup_stream))
    application.add_handler(CommandHandler("start_stream", start_stream))
    application.add_handler(CommandHandler("stop_stream", stop_stream))
    application.add_handler(CommandHandler("status", get_status))

    # Resume active streams on startup
    application.post_init = resume_active_streams

    # Start bot
    logger.info("🤖 البوت يعمل الآن...")
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
