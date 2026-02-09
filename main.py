import streamlit as st
from datetime import date
from db import init_db
from auth import create_user, verify_login
from ui import (
    header_section, add_habit_section, checklist_section,
    done_today_section, manage_habits_section
)

def login_ui():
    st.subheader("🔐 تسجيل الدخول")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("دخول", key="login_btn"):
        uid = verify_login(username, password)
        if uid:
            st.session_state["user_id"] = uid
            st.success("تم تسجيل الدخول.")
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة.")

    st.divider()

    st.subheader("🆕 إنشاء حساب")
    new_u = st.text_input("Username جديد", key="new_user")
    new_p = st.text_input("Password جديد (6+)", type="password", key="new_pass")

    if st.button("إنشاء", key="create_btn"):
        ok, msg = create_user(new_u, new_p)
        (st.success if ok else st.error)(msg)

def main():
    st.set_page_config(page_title="Habit Tracker", page_icon="✅", layout="centered")
    init_db()

    if "user_id" not in st.session_state:
        login_ui()
        return

    user_id = int(st.session_state["user_id"])

    top = st.columns([6, 2])
    selected_day = top[0].date_input("اختَر يوم", value=date.today()).isoformat()

    if top[1].button("تسجيل خروج"):
        st.session_state.pop("user_id", None)
        st.rerun()

    header_section(user_id, selected_day)
    st.divider()

    add_habit_section(user_id)
    st.divider()

    checklist_section(user_id, selected_day)
    st.divider()

    done_today_section(user_id, selected_day)
    st.divider()

    manage_habits_section(user_id)

if __name__ == "__main__":
    main()
