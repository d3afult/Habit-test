import os
import base64
import hashlib
from datetime import datetime
from db import get_conn

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def _hash_password(password: str, salt_b64: str) -> str:
    salt = base64.b64decode(salt_b64.encode())
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return base64.b64encode(dk).decode()

def create_user(username: str, password: str):
    username = (username or "").strip().lower()
    password = password or ""

    if not username or not password:
        return False, "أدخل اسم مستخدم وكلمة مرور."
    if len(password) < 6:
        return False, "كلمة المرور لازم تكون 6 أحرف أو أكثر."

    salt = os.urandom(16)
    salt_b64 = base64.b64encode(salt).decode()
    pw_hash = _hash_password(password, salt_b64)

    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, pw_hash, pw_salt, created_at) VALUES (?, ?, ?, ?)",
                (username, pw_hash, salt_b64, now_iso()),
            )
        return True, "تم إنشاء الحساب. تقدر تسجّل دخول الآن."
    except Exception:
        return False, "اسم المستخدم موجود مسبقًا."

def verify_login(username: str, password: str):
    username = (username or "").strip().lower()
    password = password or ""
    if not username or not password:
        return None

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, pw_hash, pw_salt FROM users WHERE username=?",
            (username,)
        ).fetchone()

    if not row:
        return None

    candidate = _hash_password(password, row["pw_salt"])
    if candidate == row["pw_hash"]:
        return int(row["id"])
    return None
