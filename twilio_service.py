from twilio.rest import Client

# Your Twilio credentials
import os
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = "+15187194160"
CARETAKER_NUMBER = "+917604950136"

def send_sos_alert(message=None):
    if message is None:
        message = "🚨 EMERGENCY ALERT! Patient needs immediate help!"
    
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=CARETAKER_NUMBER
        )
        print(f'✅ SMS sent! SID: {msg.sid}')
        return {"status": "sent", "sid": msg.sid}
    except Exception as e:
        print(f'❌ Error: {e}')
        return {"status": "failed", "error": str(e)}
