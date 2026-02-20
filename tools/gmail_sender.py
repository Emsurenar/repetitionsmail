"""
Gmail sender – copied and adapted from Morgonmeddelande project.
Sends HTML email via Gmail SMTP with app password.
Supports CID (Content-ID) for inline images.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import logging
import os
import config

logger = logging.getLogger(__name__)


class GmailSender:
    def __init__(self):
        self.sender_email = config.GMAIL_SENDER
        self.app_password  = config.GMAIL_APP_PASSWORD
        self.smtp_server   = "smtp.gmail.com"
        self.smtp_port     = 587

    def send_email(self, recipient: str, subject: str, html_content: str, attachments: list = None) -> bool:
        """
        Sends an HTML email, optionally with inline attachments (CID).
        
        Args:
            recipient: Recipient email address.
            subject: Email subject.
            html_content: HTML body.
            attachments: List of tuples (file_path, cid_name).
        """
        try:
            # 'related' is required for CID images
            msg_root = MIMEMultipart('related')
            msg_root['Subject'] = subject
            msg_root['From']    = self.sender_email
            msg_root['To']      = recipient
            msg_root['Date']    = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

            # Encapsulate the HTML part in 'alternative'
            msg_alternative = MIMEMultipart('alternative')
            msg_root.attach(msg_alternative)

            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg_alternative.attach(html_part)

            # Attach images with CID
            if attachments:
                for file_path, cid_name in attachments:
                    if not os.path.exists(file_path):
                        logger.warning(f"Attachment not found: {file_path}")
                        continue
                        
                    with open(file_path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', f'<{cid_name}>')
                        img.add_header('Content-Disposition', 'inline', filename=cid_name)
                        msg_root.attach(img)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.send_message(msg_root)

            logger.info(f"✅ Email sent to {recipient} – {subject!r} ({len(attachments or [])} attachments)")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Gmail auth failed. Check app password.")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
