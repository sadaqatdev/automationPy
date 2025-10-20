# config.py
import streamlit as st

DB_URL = st.secrets["DATABASE_URL"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SECRET_KEY = st.secrets["SECRET_KEY"]
GMAIL_TOKEN = st.secrets["GMAIL_TOKEN_PATH"]

DAILY_EMAIL_LIMIT = 400
MAX_PER_DEPARTMENT = 3
LOG_FILE = "logs/app.log"
GPT_MODEL = "gpt-4-turbo"


# DB Pass
# VazP3RsjQiwxHcrN
# postgresql://postgres:VazP3RsjQiwxHcrN@db.ilaovjedbffkwfngqsrs.supabase.co:5432/postgres
# postgresql://postgres.ilaovjedbffkwfngqsrs:VazP3RsjQiwxHcrN@aws-1-us-east-2.pooler.supabase.com:6543/postgres
