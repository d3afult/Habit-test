# app.py
import streamlit as st
from datetime import date
from db import init_db
from ui import (
    header_section, add_habit_section, checklist_section,
    done_today_section, manage_habits_section
)

def main():
    st.set_page_config(page_title="Habit Tracker", page_icon="✅", layout="centered")
    init_db()

    selected_day = st.date_input("اختَر يوم", value=date.today()).isoformat()

    header_section(selected_day)
    st.divider()

    add_habit_section()
    st.divider()

    checklist_section(selected_day)
    st.divider()

    done_today_section(selected_day)
    st.divider()

    manage_habits_section()

if __name__ == "__main__":
    main()
