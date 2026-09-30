import os
import smtplib
from email.message import EmailMessage


def send_shortlist_email(candidate_email: str, candidate_name: str, score: float):
    """
    Sends a shortlist email using SMTP settings from environment variables.

    Required:
      SMTP_HOST
      SMTP_PORT
      SMTP_USERNAME
      SMTP_PASSWORD
      FROM_EMAIL
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL", username)

    if not all([host, username, password, from_email]):
        return False, "SMTP is not configured. Add SMTP settings to .env."

    message = EmailMessage()
    message["Subject"] = "Application Shortlisted"
    message["From"] = from_email
    message["To"] = candidate_email
    message.set_content(
        f"""Dear {candidate_name},

We are pleased to inform you that your resume has been shortlisted for the position.

Resume match score: {score}%

Our recruitment team will contact you with the next steps.

Regards,
Recruitment Team
"""
    )

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(message)
        return True, f"Shortlist email sent to {candidate_email}."
    except Exception as exc:
        return False, f"Email could not be sent: {exc}"
