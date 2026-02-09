from datetime import datetime, date, timedelta
from db import get_conn

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def add_habit(user_id: int, name: str):
    name = (name or "").strip()
    if not name:
        return False, "اكتب اسم العادة/المهمة."
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO habits (user_id, name, active, created_at) VALUES (?, ?, 1, ?)",
            (user_id, name, now_iso()),
        )
    return True, "تمت إضافة العادة."

def set_habit_active(user_id: int, habit_id: int, active: bool):
    with get_conn() as conn:
        conn.execute(
            "UPDATE habits SET active=? WHERE id=? AND user_id=?",
            (1 if active else 0, habit_id, user_id)
        )

def list_habits(user_id: int, active_only: bool = False):
    q = "SELECT id, name, active, created_at FROM habits WHERE user_id=?"
    params = [user_id]
    if active_only:
        q += " AND active=1"
    q += " ORDER BY id DESC"
    with get_conn() as conn:
        return conn.execute(q, params).fetchall()

def mark_done(user_id: int, habit_id: int, day: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO completions (user_id, habit_id, day, completed_at) VALUES (?, ?, ?, ?)",
            (user_id, habit_id, day, now_iso()),
        )

def unmark_done(user_id: int, habit_id: int, day: str):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM completions WHERE user_id=? AND habit_id=? AND day=?",
            (user_id, habit_id, day)
        )

def done_habits_for_day(user_id: int, day: str):
    with get_conn() as conn:
        return conn.execute("""
            SELECT h.id, h.name
            FROM completions c
            JOIN habits h ON h.id = c.habit_id
            WHERE c.user_id = ? AND c.day = ?
            ORDER BY h.name COLLATE NOCASE
        """, (user_id, day)).fetchall()

def is_habit_done(user_id: int, habit_id: int, day: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM completions WHERE user_id=? AND habit_id=? AND day=?",
            (user_id, habit_id, day)
        ).fetchone()
    return row is not None

def active_habit_ids(user_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id FROM habits WHERE user_id=? AND active=1",
            (user_id,)
        ).fetchall()
    return [r["id"] for r in rows]

def is_perfect_day(user_id: int, day: str) -> bool:
    """
    Perfect Day = كل العادات النشطة (لهذا اليوزر) تم إنجازها في ذلك اليوم.
    """
    ids = active_habit_ids(user_id)
    if not ids:
        return False

    placeholders = ",".join(["?"] * len(ids))
    with get_conn() as conn:
        count_done = conn.execute(
            f"""
            SELECT COUNT(*) as n
            FROM completions
            WHERE user_id=? AND day=? AND habit_id IN ({placeholders})
            """,
            (user_id, day, *ids)
        ).fetchone()["n"]

    return count_done == len(ids)

def compute_streak(user_id: int, ending_day: str) -> int:
    """
    Streak = عدد أيام Perfect المتتالية (تنتهي بـ ending_day)
    """
    d = date.fromisoformat(ending_day)
    streak = 0
    while True:
        if is_perfect_day(user_id, d.isoformat()):
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    return streak
