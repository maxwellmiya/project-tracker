from flask_mail import Message
from app import mail

def send_email_alert(subject, recipients, body):
    """Send email notifications."""
    msg = Message(subject, recipients=recipients, body=body)
    mail.send(msg)
