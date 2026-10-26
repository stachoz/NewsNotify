import os
import smtplib
from email.message import EmailMessage

def send_report(file_path, receiver_email):
    sender_email = str(os.getenv("GMAIL_EMAIL"))
    app_password = str(os.getenv("GMAIL_PASSWORD"))

    msg = EmailMessage()
    msg["Subject"] = "finance report"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Hi,\n\nPlease find the report the Markdown file attached.\n")

    with file_path.open("rb") as file:
        msg.add_attachment(
            file.read(),
            maintype="text",
            subtype="markdown",
            filename=file_path.name
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

    print("Email sent successfully!")