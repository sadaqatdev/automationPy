# email_sender.py
import base64, time, random
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from loguru import logger

def gmail_service(token_path):
    creds = Credentials.from_authorized_user_file(token_path)
    return build('gmail', 'v1', credentials=creds)

def send_email(service, to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
    logger.info(f"📧 Sent to {to}")
    time.sleep(random.uniform(2, 5))
