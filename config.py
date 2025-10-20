# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --- DATABASE (Supabase) ---
DB_URL = os.getenv("DATABASE_URL")

# --- OPENAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- GMAIL ---
GMAIL_TOKEN = os.getenv("GMAIL_TOKEN_PATH", "token_account1.json")

# --- SECURITY (for Cloudflare trigger auth) ---
SECRET_KEY = os.getenv("SECRET_KEY", "local-dev-key")

# --- LIMITS ---
DAILY_EMAIL_LIMIT = 400
MAX_PER_DEPARTMENT = 3

# --- LOGGING ---
LOG_FILE = "logs/app.log"

# --- GPT MODEL ---
GPT_MODEL = "gpt-4-turbo"

# DB Pass
# VazP3RsjQiwxHcrN
# postgresql://postgres:VazP3RsjQiwxHcrN@db.ilaovjedbffkwfngqsrs.supabase.co:5432/postgres
