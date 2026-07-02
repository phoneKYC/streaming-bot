"""
Healthcheck script for the Streaming Bot container.
يُستدعى من Docker HEALTHCHECK للتحقق من صحة البوت.

يجري ثلاثة فحوصات:
  1. وجود ملف قاعدة البيانات وقابليته للقراءة.
  2. وجود عملية ffmpeg فعّالة على الأقل (إن كان هناك بث نشط في DB).
  3. صحة جدول settings/users.

يخرج:
  0 = صحي
  1 = غير صحي (سيُعيد Docker تشغيل الحاوية)
"""

import os
import sqlite3
import subprocess
import sys

DB_PATH = os.getenv("DATABASE_PATH", "stream_manager.db")


def check_db_exists() -> bool:
    return os.path.isfile(DB_PATH) and os.path.getsize(DB_PATH) > 0


def check_db_tables() -> bool:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name IN ('settings', 'users')"
            )
            tables = {row[0] for row in cur.fetchall()}
            return {"settings", "users"}.issubset(tables)
    except Exception:
        return False


def check_active_streams() -> bool:
    """إذا كانت DB تقول إن هناك بث نشط، يجب أن تكون هناك عملية ffmpeg فعلية."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM settings WHERE is_running=1"
            )
            active_count = cur.fetchone()[0]
            if active_count == 0:
                return True  # لا بث متوقع = صحي

            # تحقق من وجود عملية ffmpeg واحدة على الأقل
            result = subprocess.run(
                ["pgrep", "-x", "ffmpeg"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
    except Exception:
        return False


def check_python_alive() -> bool:
    """تأكيد أن عملية python الرئيسية تعمل."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "streaming_bot.py"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def main() -> int:
    checks = [
        ("DB file exists", check_db_exists),
        ("DB tables present", check_db_tables),
        ("Active streams consistent", check_active_streams),
        ("Python process alive", check_python_alive),
    ]
    all_ok = True
    for name, fn in checks:
        try:
            ok = fn()
        except Exception:
            ok = False
        status = "✅" if ok else "❌"
        print(f"{status} {name}", file=sys.stderr)
        if not ok:
            all_ok = False
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
