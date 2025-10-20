# app.py
import streamlit as st
import json
import openai
from sqlalchemy import create_engine, text
from loguru import logger

# Import project modules
from database import create_tables, insert_professor_record
from config import OPENAI_API_KEY, GPT_MODEL, SECRET_KEY, DB_URL
from scheduler import run_smart_scheduler
# from utils import setup_logging

# ✅ Initialize logging safely (no multiprocessing)
# setup_logging()

# ✅ Configure OpenAI key
openai.api_key = OPENAI_API_KEY

# ✅ Initialize database engine
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

# ✅ Streamlit configuration
st.set_page_config(page_title="🎓 AI Outreach", layout="wide")
st.sidebar.title("📍 Navigation")
page = st.sidebar.radio("Go to", ["📤 Upload Professors", "📊 Dashboard", "⚙️ Logs"])

# ===============================================================
# ✅ Quick Supabase Connection Health Check
# ===============================================================
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT NOW()"))
    st.sidebar.success("✅ Connected to Supabase!")
    logger.info("✅ Database connection successful.")
except Exception as e:
    st.sidebar.error("❌ Database connection failed.")
    st.error(f"Cannot connect to Supabase. Check DATABASE_URL or if project is sleeping.\n\nError: {e}")
    logger.error(f"❌ Database connection failed: {e}")
    st.stop()

# ===============================================================
# ✅ Load custom email template
# ===============================================================
def load_template():
    try:
        with open("template.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "Subject: Collaboration on {{research_area}} Research\n\n"
            "Dear {{name}},\n"
            "I found your research at {{university}} inspiring.\n"
            "Would you be open to discussing potential collaboration?\n\n"
            "Best regards,\n"
            "Sadaqat Hunzai\n"
            "AI Researcher | Sadaqat Labs\n"
            "sadaqatdev@gmail.com"
        )

# ===============================================================
# ✅ GPT Function: Fill email template dynamically
# ===============================================================
def gpt_fill_template(template, professor):
    prompt = f"""
    You are an academic outreach assistant.
    You will fill placeholders like {{name}}, {{university}}, {{research_area}} 
    in this email template with the given professor data and ensure a natural tone.

    Professor data:
    {json.dumps(professor, indent=2)}

    Template:
    {template}

    Output only valid JSON:
    {{
      "subject": "...",
      "body": "..."
    }}
    """
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        return data.get("subject"), data.get("body")
    except Exception as e:
        logger.error(f"GPT error: {e}")
        return (
            f"Collaboration Opportunity in {professor.get('research_area', '')}",
            f"Dear {professor.get('name', '')},\nHope you are well.\nBest,\nSadaqat Hunzai"
        )

# ===============================================================
# ✅ Cloudflare scheduler endpoint
# ===============================================================
if st.query_params.get("run") == "scheduler":
    auth = st.query_params.get("auth")
    if auth == SECRET_KEY:
        result = run_smart_scheduler()
        st.json(result)
    else:
        st.error("Unauthorized access.")
    st.stop()

# ===============================================================
# 📤 PAGE 1: Upload Professors
# ===============================================================
if page == "📤 Upload Professors":
    st.title("📤 Upload Professor Data & Generate Emails")
    create_tables()

    json_input = st.text_area("Paste JSON array of professors:", height=300)

    if st.button("Process & Save"):
        try:
            professors = json.loads(json_input)
            template = load_template()
            saved = 0
            for prof in professors:
                subject, body = gpt_fill_template(template, prof)
                record = {
                    **prof,
                    "email_subject": subject,
                    "email_body": body,
                    "gpt_model": GPT_MODEL,
                }
                insert_professor_record(record)
                saved += 1
            st.success(f"✅ Processed & saved {saved} records successfully.")
            logger.info(f"✅ Saved {saved} professor records.")
        except Exception as e:
            st.error(f"Error processing input: {e}")
            logger.error(f"Upload error: {e}")

# ===============================================================
# 📊 PAGE 2: Dashboard
# ===============================================================
elif page == "📊 Dashboard":
    import pandas as pd
    st.title("📊 Outreach Dashboard")
    try:
        df = pd.read_sql("SELECT * FROM professors ORDER BY updated_at DESC", engine)
        if df.empty:
            st.info("No professor data yet.")
        else:
            total, sent, pending, failed = (
                len(df),
                len(df[df.email_status == "sent"]),
                len(df[df.email_status == "pending"]),
                len(df[df.email_status == "failed"]),
            )
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", total)
            c2.metric("Sent", sent)
            c3.metric("Pending", pending)
            c4.metric("Failed", failed)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        logger.error(f"Dashboard error: {e}")

# ===============================================================
# ⚙️ PAGE 3: Logs
# ===============================================================
elif page == "⚙️ Logs":
    st.title("📜 System Logs")
    try:
        with open("app.log", "r") as f:
            st.text(f.read()[-8000:])
    except FileNotFoundError:
        st.warning("No logs yet.")
