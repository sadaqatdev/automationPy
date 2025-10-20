# app.py
import streamlit as st
import json
import openai
from database import create_tables, insert_professor_record
from config import OPENAI_API_KEY, GPT_MODEL, SECRET_KEY
from utils import setup_logging
from scheduler import run_smart_scheduler
from loguru import logger
from sqlalchemy import create_engine
from config import DB_URL

openai.api_key = OPENAI_API_KEY
engine = create_engine(DB_URL)
setup_logging()

st.set_page_config(page_title="🎓 AI Outreach", layout="wide")
st.sidebar.title("📍 Navigation")
page = st.sidebar.radio("Go to", ["📤 Upload Professors", "📊 Dashboard", "⚙️ Logs"])

# --- Load custom email template
def load_template():
    with open("template.txt", "r") as f:
        return f.read()

def gpt_fill_template(template, professor):
    prompt = f"""
    You are a helpful academic email assistant.
    You are given an email template with placeholders like {{name}}, {{university}}, {{research_area}}.
    Fill them with this professor's data and lightly rewrite for politeness and fluency.

    Professor data:
    {json.dumps(professor, indent=2)}

    Template:
    {template}

    Output only JSON:
    {{
      "subject": "...",
      "body": "..."
    }}
    """
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        return data.get("subject"), data.get("body")
    except Exception as e:
        logger.error(f"GPT error: {e}")
        return ("Research Collaboration", f"Dear {professor['name']},\nHope you are well.\nBest,\nSadaqat Hunzai")

# --- Cloudflare scheduler trigger ---
if st.query_params.get("run") == "scheduler":
    auth = st.query_params.get("auth")
    if auth == SECRET_KEY:
        result = run_smart_scheduler()
        st.json(result)
    else:
        st.error("Unauthorized access.")
    st.stop()

# --- Page 1: Upload Professors ---
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
                    "gpt_model": GPT_MODEL
                }
                insert_professor_record(record)
                saved += 1
            st.success(f"✅ Processed & saved {saved} records successfully.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Page 2: Dashboard ---
elif page == "📊 Dashboard":
    st.title("📊 Outreach Dashboard")
    import pandas as pd
    df = pd.read_sql("SELECT * FROM professors ORDER BY updated_at DESC", engine)
    if df.empty:
        st.info("No data yet.")
    else:
        total, sent, pending, failed = len(df), len(df[df.email_status == "sent"]), len(df[df.email_status == "pending"]), len(df[df.email_status == "failed"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", total)
        c2.metric("Sent", sent)
        c3.metric("Pending", pending)
        c4.metric("Failed", failed)
        st.dataframe(df, use_container_width=True)

# --- Page 3: Logs ---
elif page == "⚙️ Logs":
    st.title("📜 System Logs")
    try:
        with open("logs/app.log", "r") as f:
            st.text(f.read()[-5000:])
    except FileNotFoundError:
        st.warning("No logs found.")
