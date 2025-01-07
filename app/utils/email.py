from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks
from app.config import settings

def send_email_verification(background_tasks: BackgroundTasks, email_to: str, token: str):
    verification_link = f"{settings.EMAIL_VERIFICATION_LINK}/verify-email?token={token}"
    subject = "Verify Your Email"
    html_content = f"<strong>Click <a href='{verification_link}'>here</a> to verify your email address.</strong>"
    background_tasks.add_task(_send_email, subject, email_to, html_content)


def send_password_reset_email(background_tasks: BackgroundTasks, email_to: str, token: str):
    reset_link = f"{settings.PASSWORD_RESET_LINK}/reset-password?token={token}"
    subject = "Reset Your Password"
    html_content = f"<strong>Click <a href='{reset_link}'>here</a> to reset your password.</strong>"
    background_tasks.add_task(_send_email, subject, email_to, html_content)


def _send_email(subject: str, recipient: str, html_content: str):
    sender = settings.SMTP_USER
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    # Connect to Gmail SMTP server
    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(sender, recipient, msg.as_string())


