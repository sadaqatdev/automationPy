# test_db_connection.py
import psycopg2

DB_HOST = "localhost"
DB_NAME = "ai_outreach"
DB_USER = "postgres"
DB_PASS = "password"

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("✅ Connection successful!")
    print("PostgreSQL version:", version[0])
    cur.close()
    conn.close()
except Exception as e:
    print("❌ Connection failed.")
    print("Error details:", e)
