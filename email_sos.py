import smtplib
from email.message import EmailMessage
import os

def send_sos_alert(message=None):
    if message is None:
        message = "🚨 EMERGENCY SOS ALERT! 🚨\n\nPatient needs immediate medical attention!\n\nPlease check on them immediately."
    
    # Your email configuration
    EMAIL_ADDRESS = "sndpsrinivasan@gmail.com"
    EMAIL_PASSWORD = "your_app_password"  # You need to create this
    
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = '🚨 SOS ALERT - Medical Emergency!'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS  # Send to yourself
        
        # Send via Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        
        print("✅ Email SOS Sent to:", EMAIL_ADDRESS)
        return {"status": "sent", "method": "email", "to": EMAIL_ADDRESS}
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return {"status": "failed", "error": str(e)}
