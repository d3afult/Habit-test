import streamlit as st
from datetime import date
from logic import (
    add_habit, list_habits, mark_done, unmark_done,
    done_habits_for_day, is_habit_done, compute_streak, is_perfect_day,
    set_habit_active
)

def header_section(user_id: int, selected_day: str):
    st.title("Habit Tracker ✅")
    streak = compute_streak(user_id, selected_day)
    col1, col2, col3 = st.columns(3)
    col1.metric("📅 التاريخ", selected_day)
    col2.metric("🔥 الستريك", streak)
    col3.metric("⭐ Perfect Day?", "نعم" if is_perfect_day(user_id, selected_day) else "لا")

def add_habit_section(user_id: int):
    st.subheader("➕ إضافة عادة/مهمة")
    with st.form("add_habit_form", clear_on_submit=True):
        name = st.text_input("اسم العادة/المهمة")
        submitted = st.form_submit_button("إضافة")
    if submitted:
        ok, msg = add_habit(user_id, name)
        (st.success if ok else st.warning)(msg)
        st.rerun()

def checklist_section(user_id: int, selected_day: str):
    st.subheader("🧾 قائمة العادات (علّم المنجَز اليوم)")
    habits = list_habits(user_id, active_only=True)

    if not habits:
        st.info("ما في عادات نشطة. أضف عادة من فوق.")
        return

    for h in habits:
        hid = int(h["id"])
        checked = is_habit_done(user_id, hid, selected_day)
        new_val = st.checkbox(
            h["name"],
            value=checked,
            key=f"habit_{user_id}_{hid}_{selected_day}"
        )

        # ✅ الإصلاح الأساسي للستريك: نحفظ ثم rerun فورًا
        if new_val and not checked:
            mark_done(user_id, hid, selected_day)
            st.toast(f"تم إنجاز: {h['name']}", icon="✅")
            st.rerun()

        elif (not new_val) and checked:
            unmark_done(user_id, hid, selected_day)
            st.toast(f"تم إلغاء إنجاز: {h['name']}", icon="↩️")
            st.rerun()

def done_today_section(user_id: int, selected_day: str):
    st.subheader("✅ المهام المنجزة لهذا اليوم")
    done = done_habits_for_day(user_id, selected_day)
    if not done:
        st.write("لا يوجد منجَزات اليوم بعد.")
        return

    for row in done:
        st.write(f"- {row['name']}")

def manage_habits_section(user_id: int):
    st.subheader("⚙️ إدارة العادات (تفعيل/إيقاف)")
    all_habits = list_habits(user_id, active_only=False)
    if not all_habits:
        return

    with st.expander("عرض الإدارة"):
        for h in all_habits:
            hid = int(h["id"])
            active = bool(h["active"])
            cols = st.columns([6, 2])
            cols[0].write(h["name"])
            new_active = cols[1].toggle(
                "نشطة",
                value=active,
                key=f"active_{user_id}_{hid}"
            )
            if new_active != active:
                set_habit_active(user_id, hid, new_active)
                st.toast("تم التحديث", icon="🔧")
                st.rerun()
