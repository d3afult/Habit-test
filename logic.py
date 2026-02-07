# logic.py
from datetime import datetime, date, timedelta
from db import get_conn

def today_str() -> str:
    return date.today().isoformat()

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def add_habit(name: str):
    name = (name or "").strip()
    if not name:
        return False, "اكتب اسم العادة/المهمة."
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO habits (name, active, created_at) VALUES (?, 1, ?)",
            (name, now_iso()),
        )
    return True, "تمت إضافة العادة."

def set_habit_active(habit_id: int, active: bool):
    with get_conn() as conn:
        conn.execute("UPDATE habits SET active=? WHERE id=?", (1 if active else 0, habit_id))

def list_habits(active_only=False):
    q = "SELECT id, name, active, created_at FROM habits"
    params = ()
    if active_only:
        q += " WHERE active=1"
    q += " ORDER BY id DESC"
    with get_conn() as conn:
        return conn.execute(q, params).fetchall()

def mark_done(habit_id: int, day: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO completions (habit_id, day, completed_at) VALUES (?, ?, ?)",
            (habit_id, day, now_iso()),
        )

def unmark_done(habit_id: int, day: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM completions WHERE habit_id=? AND day=?", (habit_id, day))

def done_habits_for_day(day: str):
    with get_conn() as conn:
        return conn.execute("""
            SELECT h.id, h.name
            FROM completions c
            JOIN habits h ON h.id = c.habit_id
            WHERE c.day = ?
            ORDER BY h.name COLLATE NOCASE
        """, (day,)).fetchall()

def is_habit_done(habit_id: int, day: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM completions WHERE habit_id=? AND day=?",
            (habit_id, day)
        ).fetchone()
    return row is not None

def active_habit_ids():
    with get_conn() as conn:
        rows = conn.execute("SELECT id FROM habits WHERE active=1").fetchall()
    return [r["id"] for r in rows]

def is_perfect_day(day: str) -> bool:
    """
    اليوم يعتبر "Perfect" إذا:
    - يوجد عادات نشطة
    - وكل عادة نشطة مسجّل لها completion في ذلك اليوم
    """
    ids = active_habit_ids()
    if not ids:
        return False
    with get_conn() as conn:
        count_done = conn.execute(
            f"SELECT COUNT(*) as n FROM completions WHERE day=? AND habit_id IN ({','.join(['?']*len(ids))})",
            (day, *ids)
        ).fetchone()["n"]
    return count_done == len(ids)

def compute_streak(ending_day: str) -> int:
    """
    يحسب الستريك كعدد أيام Perfect متتالية تنتهي بـ ending_day.
    """
    d = date.fromisoformat(ending_day)
    streak = 0
    while True:
        if is_perfect_day(d.isoformat()):
            streak += 1
            d = d - timedelta(days=1)
        else:
            break
    return streak
