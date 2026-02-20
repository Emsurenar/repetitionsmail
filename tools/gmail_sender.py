"""
Gmail sender – copied and adapted from Morgonmeddelande project.
Sends HTML email via Gmail SMTP with app password.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import config

logger = logging.getLogger(__name__)


class GmailSender:
    def __init__(self):
        self.sender_email = config.GMAIL_SENDER
        self.app_password  = config.GMAIL_APP_PASSWORD
        self.smtp_server   = "smtp.gmail.com"
        self.smtp_port     = 587

    def send_email(self, recipient: str, subject: str, html_content: str) -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From']    = self.sender_email
            msg['To']      = recipient
            msg['Date']    = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)

            logger.info(f"✅ Email sent to {recipient} – {subject!r}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Gmail auth failed. Check app password.")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
