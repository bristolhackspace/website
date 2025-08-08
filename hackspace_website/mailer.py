from email.mime.text import MIMEText
from flask import current_app
import smtplib
import ssl

def send_internal(reply_to: str | None, subject: str, text: str):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(current_app.config["SMTP_SERVER"], current_app.config["SMTP_PORT"], context=context) as smtp_client:
        smtp_client.login(current_app.config["SMTP_EMAIL"], current_app.config["SMTP_PASSWORD"])
        sender_email = current_app.config["SMTP_EMAIL"]
        receiver_email = current_app.config["SMTP_EMAIL"]

        message = MIMEText(text, "plain")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email
        if reply_to:
            message['reply-to'] = reply_to
        smtp_client.sendmail(sender_email, receiver_email, message.as_string())