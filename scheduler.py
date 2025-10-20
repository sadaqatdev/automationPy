# scheduler.py
import datetime, pytz, time
from database import engine
from sqlalchemy import text
from email_sender import gmail_service, send_email
from config import GMAIL_TOKEN, DAILY_EMAIL_LIMIT, MAX_PER_DEPARTMENT
from loguru import logger
from datetime import date

def run_smart_scheduler():
    logger.info("🚀 Scheduler triggered by Cloudflare")

    with engine.connect() as conn:
        records = conn.execute(text("""
            SELECT * FROM professors
            WHERE email_status='pending'
            ORDER BY timezone, created_at ASC
            LIMIT :limit
        """), {"limit": DAILY_EMAIL_LIMIT}).fetchall()

    if not records:
        logger.info("No pending records.")
        return {"sent": 0}

    service = gmail_service(GMAIL_TOKEN)
    sent_today = 0
    sent_today_depts = set()

    for r in records:
        tz = pytz.timezone(r["timezone"] or "UTC")
        local = datetime.datetime.now(pytz.utc).astimezone(tz)
        if local.weekday() >= 5 or local.hour != 9:
            continue

        key = (r["university"], r["department"], date.today())
        if key in sent_today_depts:
            continue
        sent_today_depts.add(key)

        try:
            send_email(service, r["email"], r["email_subject"], r["email_body"])
            with engine.begin() as conn:
                conn.execute(text("""
                    UPDATE professors SET email_status='sent', updated_at=NOW()
                    WHERE id=:id
                """), {"id": r["id"]})
            sent_today += 1
        except Exception as e:
            with engine.begin() as conn:
                conn.execute(text("""
                    UPDATE professors SET email_status='failed', error_log=:err, updated_at=NOW()
                    WHERE id=:id
                """), {"id": r["id"], "err": str(e)})
            logger.error(f"❌ Failed: {r['email']} | {e}")

    logger.success(f"✅ Sent {sent_today} emails successfully.")
    return {"sent": sent_today}
