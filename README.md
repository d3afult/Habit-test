# Habit Tracker (Streamlit)

تطبيق Habit Tracking بسيط:
- إضافة عادة/مهمة
- تعليم المنجزات لليوم
- عرض قائمة المنجَز اليوم
- Daily Streak يزيد إذا أنجزت كل العادات النشطة يوميًا بشكل متتالي

## تشغيل محليًا
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
