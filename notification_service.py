import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

def send_email_alert(to_email, subject, message):
    """Send email alert using Gmail SMTP"""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return {"success": False, "message": "Email not configured"}
    
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return {"success": True, "message": "Email sent"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_push_notification_script(title, body):
    """Get JavaScript for browser push notification"""
    return f"""
    <script>
    if ("Notification" in window) {{
        if (Notification.permission === "granted") {{
            new Notification("{title}", {{ body: "{body}" }});
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(permission => {{
                if (permission === "granted") {{
                    new Notification("{title}", {{ body: "{body}" }});
                }}
            }});
        }}
    }}
    </script>
    """
