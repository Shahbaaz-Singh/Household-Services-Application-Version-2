from flask_mail import Message
from app import mail

def send_email(recipient, subject, body, html_content=None):
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body
        )
        if html_content:
            msg.html = html_content
        mail.send(msg)
        print(f"Email sent to {recipient}")
        return True
    
    except Exception as e:
        print(f"Email error: {str(e)}")
        return False