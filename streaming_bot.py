import logging
import subprocess
import os
import signal
import sqlite3
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# إعداد نظام السجلات (Logs) لمراقبة تيار العمليات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إعدادات قاعدة البيانات وإدارة العمليات
DB_NAME = os.getenv("DATABASE_PATH", "stream_manager.db")
process_pointer = None

# إعدادات الـ FFmpeg المستوردة من البيئة
FFMPEG_TIMEOUT = int(os.getenv("FFMPEG_TIMEOUT", "15000000"))
RECONNECT_DELAY = int(os.getenv("RECONNECT_DELAY", "5"))

# امتدادات الملفات الصوتية التي تشير إلى أن البث راديو/صوت فقط
AUDIO_EXTENSIONS = ('.mp3', '.aac', '.ogg', '.opus', '.m3u', '.m3u8', '.pls', '.asx', '.xspf')

# نطاقات خوادم الإذاعات الدينية وراديو القرآن الكريم الشهيرة
RADIO_DOMAINS = ('aymane.xyz', 'qurango.net', 'radiojar.com', 'radiocoast.com', 'listenradio.org')


def is_valid_url(url):
    """التحقق من صحة الرابط المدخل ودعم البروتوكولات المستخدمة للبث"""
    try:
        result = urlparse(url)
        return result.scheme in ('http', 'https', 'rtmp', 'rtmps', 'rtsp')
    except Exception:
        return False


def detect_stream_type(url):
    """الكشف التلقائي عن نوع تيار البث المدخل"""
    # 1. كشف روابط يوتيوب
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    
    # 2. كشف نطاقات الراديو المعروفة
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()
    
    for radio_domain in RADIO_DOMAINS:
        if radio_domain in domain:
            return 'radio'
    
    # 3. التحقق من وجود كلمة /radio/ في مسار الرابط
    if '/radio/' in path:
        return 'radio'
    
    # 4. إذا كان رابط m3u8 ويحتوي على كلمة 'live'، فغالباً هو ملف بث حي مرئي (IPTV)
    if url.lower().endswith('.m3u8') and 'live' in url.lower():
        return 'iptv'
    
    # 5. التحقق من الامتدادات الصوتية المباشرة
    if url.lower().endswith(AUDIO_EXTENSIONS):
        return 'radio'
    
    # الافتراضي: بث مرئي IPTV
    return 'iptv'

def init_db():
    """تهيئة قاعدة بيانات SQLite وبناء جدول الإعدادات بالصيغة الكاملة"""
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
    """حفظ وتحديث الإعدادات باستخدام REPLACE الآمنة لتفادي أخطاء التصادم"""
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
    """تحديث حالة تشغيل البث للمستخدم في قاعدة البيانات"""
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
    """جلب إعدادات البث الخاصة بالمستخدم"""
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
    """جلب الجلسات النشطة التي كانت تعمل لاستعادتها تلقائياً عند الإقلاع"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, m3u_url, server_url, stream_key FROM settings WHERE is_running = 1')
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"❌ Error retrieving active streams: {e}")
        return []


def launch_ffmpeg_process(m3u_url, server_url, stream_key):
    """إطلاق عملية الـ FFmpeg بالتهيئة والترويسات المخصصة لتخطي جدران الحماية"""
    global process_pointer
    
    try:
        if not server_url.endswith('/'):
            server_url += '/'
            
        full_rtmp_destination = f"{server_url}{stream_key}"
        
        # كشف نوع البث تلقائياً
        stream_type = detect_stream_type(m3u_url)
        logger.info(f"🔍 Detected stream type: {stream_type} for URL: {m3u_url}")
        
        # 🌟 الحالة الأولى: تيار يوتيوب المباشر (استخلاص مستمر لمنع انتهاء صلاحية تذكرة البث)
        if stream_type == 'youtube':
            bash_command = (
                f'while true; do '
                f'LIVE_URL=$(yt-dlp --no-update -f "b" -g "{m3u_url}"); '
                f'ffmpeg -http_persistent 0 -headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" '
                f'-timeout {FFMPEG_TIMEOUT} -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
                f'-re -i "$LIVE_URL" -c:v copy -c:a copy -f flv "{full_rtmp_destination}"; '
                f'sleep 15; ' # مهلة أمان للتهدئة قبل تحديث الرابط التالي من يوتيوب
                f'done'
            )
            logger.info("🎬 YouTube streaming configured with safety loop")
            
        # 🌟 الحالة الثانية: الراديو أو الصوتيات الثابتة (القرآن الكريم)
        elif stream_type == 'radio':
            # توليد شاشة سوداء منخفضة الدقة والإطارات لتوفير استهلاك المعالج وتلبية شروط تلغرام
            bash_command = (
                f'while true; do '
                f'ffmpeg '
                f'-f lavfi -i color=c=black:s=640x360:r=10 '
                f'-timeout {FFMPEG_TIMEOUT} -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
                f'-re -i "{m3u_url}" '
                f'-c:v libx264 -pix_fmt yuv420p -b:v 100k -g 20 '
                f'-c:a aac -b:a 128k '
                f'-shortest -f flv "{full_rtmp_destination}"; '
                f'sleep {RECONNECT_DELAY}; '
                f'done'
            )
            logger.info("🎵 Radio/Audio streaming configured with virtual video canvas")
            
        # 🌟 الحالة الثالثة: البث المباشر المعتاد IPTV ومحاولات كسر الحظر (YCN & Cloudflare Bypass)
        else:
            # ترويسة المتصفح وموقع الإحالة من إكس (تويتر سابقاً) لخداع جدران الحماية
            custom_headers = (
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36\\r\\n"
                "Referer: https://x.com/\\r\\n"
            )
            # ضبط reconnect_at_eof إلى 0 مع sleep 15 لمنع حلقات التكرار الميتة عند انقطاع ملفات الـ ts المتغيرة
            bash_command = (
                f'while true; do '
                f'ffmpeg -timeout {FFMPEG_TIMEOUT} -reconnect 1 -reconnect_at_eof 0 -reconnect_streamed 1 -reconnect_delay_max 10 '
                f'-headers "{custom_headers}" '
                f'-live_start_index -1 -i "{m3u_url}" -c:v copy -c:a copy -f flv "{full_rtmp_destination}"; '
                f'echo "FFmpeg exited, waiting 15 seconds to prevent rate limits..."; '
                f'sleep 15; ' # حماية قصوى ومقاومة لعمليات حظر الـ IP المؤقت من السيرفرات الحساسة
                f'done'
            )
            logger.info("📺 IPTV streaming configured with custom anti-blocking headers")
        
        # إطلاق العملية الفرعية في مجلد مستقل خلف الكود
        process_pointer = subprocess.Popen(bash_command, shell=True, preexec_fn=os.setsid)
        logger.info(f"🚀 FFmpeg process launched with PID: {process_pointer.pid}")
        return process_pointer
        
    except Exception as e:
        logger.error(f"❌ Error launching FFmpeg: {e}")
        raise


async def resume_active_streams(application: Application):
    """استئناف البث التلقائي لجميع الجلسات التي كانت تعمل قبل إعادة التشغيل"""
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
    """التحقق من صلاحيات البوت الإدارية وصلاحية نشر الرسائل داخل القناة"""
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
    """الاستجابة لأمر الترحيب وعرض الواجهة التعليمية"""
    welcome = (
        "👋 أهلاً بك في بوت إدارة البث المباشر المرن والمعدل!\n\n"
        "**الأوامر الحالية:**\n"
        "1️⃣ `/setup [رابط_البث] [عنوان_الخادم] [مفتاح_البث] [معرف_القناة]`\n"
        "2️⃣ `/start_stream` - لبدء البث المباشر\n"
        "3️⃣ `/stop_stream` - لإيقاف البث فوراً\n"
        "4️⃣ `/status` - لعرض حالة الجلسة وتفاصيل الاتصال\n\n"
        "**أنواع البث المدعومة والمحسنة:**\n"
        "🎬 يوتيوب المباشر | 🎵 إذاعات وراديو القرآن | 📺 قنوات IPTV والـ TS (المحمية والمفتوحة)\n\n"
        "📖 للمزيد من المعلومات، انظر التوثيق: https://github.com/phoneKYC/streaming-bot"
    )
    logger.info(f"👋 User {update.effective_user.id} started the bot")
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def setup_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الاستجابة لأمر ضبط الإعدادات وحفظها"""
    user_id = update.effective_user.id
    if len(context.args) < 4:
        await update.message.reply_text(
            "❌ الاستخدام الصحيح للمتغيرات الأربعة:\n`/setup [رابط_البث] [عنوان_الخادم] [مفتاح_البث] [معرف_القناة]`", 
            parse_mode="Markdown"
        )
        logger.warning(f"❌ Invalid setup command from user {user_id}")
        return

    m3u_url = context.args[0]
    server_url = context.args[1]
    stream_key = context.args[2]
    channel_id = context.args[3]
    
    # التحقق من صحة صياغة رابط البث
    if not is_valid_url(m3u_url):
        await update.message.reply_text(
            "❌ رابط البث غير صالح! تأكد من استخدام رابط يبدأ بـ http:// أو https://"
        )
        logger.warning(f"❌ Invalid stream URL from user {user_id}: {m3u_url}")
        return
    
    # التحقق من صحة صياغة رابط خادم البث
    if not is_valid_url(server_url):
        await update.message.reply_text(
            "❌ رابط الخادم غير صالح! تأكد من استخدام رابط يبدأ بـ rtmp:// أو https://"
        )
        logger.warning(f"❌ Invalid server URL from user {user_id}: {server_url}")
        return
    
    # الكشف عن نوع البث ديناميكياً لإعلام المشرف
    stream_type = detect_stream_type(m3u_url)
    type_labels = {'youtube': '🎬 يوتيوب المباشر', 'radio': '🎵 إذاعة/راديو القرآن', 'iptv': '📺 IPTV القنوات'}
    type_label = type_labels.get(stream_type, '📺 IPTV القنوات')
    
    await update.message.reply_text(
        f"🔄 جاري التحقق من صلاحيات البوت في القناة المستهدفة...\n"
        f"📡 نوع البث المكتشف تلقائياً: {type_label}"
    )
    logger.info(f"🔍 Checking permissions for user {user_id}")
    
    if not await check_bot_permissions(context, channel_id):
        await update.message.reply_text(
            "❌ فشل التحقق! تأكد من رفع البوت آدمن في القناة ومنحه صلاحية 'نشر الرسائل' (Post Messages)."
        )
        logger.error(f"❌ Permission check failed for user {user_id}")
        return

    try:
        save_settings(user_id, m3u_url, server_url, stream_key, channel_id)
        await update.message.reply_text(
            f"✅ تم حفظ الإعدادات بنجاح وتفادي أخطاء التضارب!\n"
            f"📡 نوع البث المعتمد: {type_label}\n"
            f"أرسل الآن أمر البدء `/start_stream` لإطلاق البث البصري في قناتك.",
            parse_mode="Markdown"
        )
        logger.info(f"✅ Settings saved successfully for user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ غير متوقع أثناء حفظ الإعدادات: {str(e)}")
        logger.error(f"❌ Error saving settings for user {user_id}: {e}")

async def start_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الاستجابة لأمر إطلاق البث والتحقق من حالته"""
    global process_pointer
    user_id = update.effective_user.id
    
    if process_pointer and process_pointer.poll() is None:
        await update.message.reply_text("⚠️ منظومة البث والمراقبة تعمل بالفعل بالخلفية!")
        logger.warning(f"⚠️ Stream already running for user {user_id}")
        return

    settings = get_settings(user_id)
    if not settings:
        await update.message.reply_text(
            "❌ لم يتم ضبط الإعدادات بعد، استخدم أمر ضبط المعايير أولاً:\n`/setup [رابط] [خادم] [مفتاح] [معرف]`",
            parse_mode="Markdown"
        )
        logger.warning(f"❌ No settings found for user {user_id}")
        return

    m3u_url, server_url, stream_key, _, _ = settings
    await update.message.reply_text("🚀 جاري معالجة تيار البيانات وحقن الترويسات الأمنية لتشغيل البث...")
    logger.info(f"🚀 Starting stream for user {user_id}")
    
    try:
        launch_ffmpeg_process(m3u_url, server_url, stream_key)
        update_status(user_id, 1)
        await update.message.reply_text("🟢 تم تفعيل البث بنجاح وهو محمي ومراقب 24/7!")
        logger.info(f"🟢 Stream started successfully for user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ أثناء بدء البث: {str(e)}")
        logger.error(f"❌ Error starting stream for user {user_id}: {e}")

async def stop_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الاستجابة لأمر إيقاف البث وتحرير العمليات المعلقة بالخلفية"""
    global process_pointer
    user_id = update.effective_user.id
    
    if process_pointer and process_pointer.poll() is None:
        try:
            os.killpg(os.getpgid(process_pointer.pid), signal.SIGTERM)
            process_pointer = None
            update_status(user_id, 0)
            await update.message.reply_text("⏹️ تم إيقاف عملية البث وتحرير الموارد بنجاح.")
            logger.info(f"⏹️ Stream stopped for user {user_id}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ أثناء تجميد العمليات الفرعية: {str(e)}")
            logger.error(f"❌ Error stopping stream for user {user_id}: {e}")
    else:
        await update.message.reply_text("⚪ لا يوجد بث يعمل حالياً في الخلفية لإيقافه.")
        logger.info(f"ℹ️ No active stream to stop for user {user_id}")

async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الاستجابة لأمر تقرير الحالة الكاملة للجلسة الحالية"""
    global process_pointer
    user_id = update.effective_user.id
    settings = get_settings(user_id)
    
    db_status = "🔴 متوقف" if not settings or settings[4] == 0 else "🟢 قيد العمل والمراقبة"
    script_status = "🟢 نشط" if process_pointer and process_pointer.poll() is None else "🔴 غير نشط"
    
    # جلب نوع البث الحالي المسجل لعرضه
    stream_url = settings[0] if settings else ''
    stream_type = detect_stream_type(stream_url) if stream_url else 'iptv'
    type_labels = {'youtube': '🎬 يوتيوب المباشر', 'radio': '🎵 إذاعة/راديو القرآن', 'iptv': '📺 IPTV القنوات'}
    type_label = type_labels.get(stream_type, '📺 IPTV القنوات')
    
    status_message = (
        f"📊 **تقرير حالة المنظومة الحالية:**\n\n"
        f"▪️ الحالة بقاعدة البيانات: {db_status}\n"
        f"▪️ خادم البث المستهدف: `{settings[1] if settings else 'غير محدد'}`\n"
        f"▪️ نوع البث المسجل: {type_label}\n"
        f"▪️ عملية FFmpeg الفرعية: {script_status}"
    )
    
    await update.message.reply_text(status_message, parse_mode="Markdown")
    logger.info(f"📊 Status checked for user {user_id}")

def main():
    """نقطة الدخول والتشغيل الأساسية للبوت"""
    # تهيئة قاعدة البيانات وإنشاء الجدول المحدث
    init_db()

    # استدعاء توكن البوت من المتغيرات البيئية بأمان
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        raise ValueError("BOT_TOKEN environment variable is required")
    
    logger.info("🤖 Starting Streaming Bot with Anti-Block features...")

    # بناء كود تطبيق البوت
    application = Application.builder().token(BOT_TOKEN).build()

    # تسجيل مستقبلي الأوامر داخل بيئة تلغرام
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setup", setup_stream))
    application.add_handler(CommandHandler("start_stream", start_stream))
    application.add_handler(CommandHandler("stop_stream", stop_stream))
    application.add_handler(CommandHandler("status", get_status))

    # ربط دالة الاستعادة التلقائية لتعمل فور ربط البوت
    application.post_init = resume_active_streams

    # تشغيل سحب التحديثات المستمر (Polling)
    logger.info("🤖 البوت يعمل الآن ويراقب المجموعات والقنوات...")
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error in bot session: {e}")
        raise
