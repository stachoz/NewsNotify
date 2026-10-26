import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def _get_email_credentials() -> tuple[str, str]:
    sender_email = os.getenv("GMAIL_EMAIL")
    app_password = os.getenv("GMAIL_PASSWORD")

    if not sender_email or not app_password:
        raise RuntimeError("GMAIL_EMAIL and GMAIL_PASSWORD must be set to send email.")

    return sender_email, app_password


def _build_report_email(
    file_path: Path, sender_email: str, receiver_email: str
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = "Finance report"
    message["From"] = sender_email
    message["To"] = receiver_email
    message.set_content("Hi,\n\nPlease find the report Markdown file attached.\n")

    with file_path.open("rb") as attachment_file:
        message.add_attachment(
            attachment_file.read(),
            maintype="text",
            subtype="markdown",
            filename=file_path.name,
        )

    return message


def send_report(file_path: Path, receiver_email: str) -> None:
    sender_email, app_password = _get_email_credentials()
    message = _build_report_email(file_path, sender_email, receiver_email)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(message)

    print("Report email sent successfully.")
