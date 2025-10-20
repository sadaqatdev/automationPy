# dashboard.py
import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
from email_sender import gmail_service, send_email
from database import update_email_details
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS

# Database connection
def get_data(query):
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Title
st.set_page_config(page_title="🎓 Outreach Dashboard", layout="wide")
st.title("📊 Professor Outreach Dashboard")

st.markdown("""
This dashboard shows all professors, their email status, and the GPT-generated messages.  
You can filter, view, and retry failed emails directly from here.
""")

# Sidebar filters
st.sidebar.header("🔍 Filters")
status_filter = st.sidebar.multiselect("Email Status", ["pending", "sent", "failed"], default=["pending", "failed"])
country_filter = st.sidebar.text_input("Country (optional)").strip()
university_filter = st.sidebar.text_input("University (optional)").strip()

# Build dynamic query
query = "SELECT * FROM professors WHERE email_status IN %s"
params = [tuple(status_filter)]

if country_filter:
    query += " AND country ILIKE %s"
    params.append(f"%{country_filter}%")

if university_filter:
    query += " AND university ILIKE %s"
    params.append(f"%{university_filter}%")

df = get_data(cur.mogrify(query, params).decode() if 'cur' in locals() else query % tuple(params))

if df.empty:
    st.warning("No records found with current filters.")
else:
    st.success(f"Found {len(df)} records")

    # Display table
    st.dataframe(df[['id', 'name', 'email', 'university', 'department', 'country', 'email_status', 'email_sent_time']], use_container_width=True)

    # Select a professor to view details
    selected_id = st.selectbox("Select a Professor ID to View Email Details", df['id'].tolist())
    selected_prof = df[df['id'] == selected_id].iloc[0]

    st.subheader(f"📧 Email Preview for {selected_prof['name']} ({selected_prof['university']})")
    st.write(f"**Subject:** {selected_prof['email_subject'] or '—'}")
    st.text_area("Email Body", selected_prof['email_body'] or "—", height=250)

    # Retry failed email option
    if selected_prof['email_status'] == 'failed':
        if st.button("🔁 Retry Sending Email"):
            try:
                service = gmail_service()
                send_email(service, selected_prof['email'], selected_prof['email_subject'], selected_prof['email_body'])
                update_email_details(selected_prof['id'], selected_prof['email_subject'], selected_prof['email_body'], status="sent")
                st.success(f"✅ Retried and sent to {selected_prof['email']}")
            except Exception as e:
                st.error(f"❌ Failed to resend: {e}")

st.markdown("---")
st.caption("AI Outreach System © 2025 — Managed by Sadaqat Hunzai")
