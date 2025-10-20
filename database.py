# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from loguru import logger
from config import DB_URL

engine = create_engine(DB_URL, poolclass=QueuePool, pool_size=5, max_overflow=10)

def create_tables():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS professors (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            university TEXT,
            department TEXT,
            research_area TEXT,
            country TEXT,
            timezone TEXT,
            email_subject TEXT,
            email_body TEXT,
            email_status TEXT DEFAULT 'pending',
            gpt_model TEXT,
            batch_id UUID,
            error_log TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """))
        logger.info("✅ Tables ensured.")

def insert_professor_record(p):
    with engine.begin() as conn:
        conn.execute(text("""
        INSERT INTO professors (
            name, email, university, department, research_area, country,
            timezone, email_subject, email_body, email_status, gpt_model, batch_id
        ) VALUES (
            :name, :email, :university, :department, :research_area, :country,
            :timezone, :email_subject, :email_body, 'pending', :gpt_model, gen_random_uuid()
        )
        ON CONFLICT (email) DO NOTHING;
        """), p)
