import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_sos_alert(message=None):
    if message is None:
        message = "🚨 EMERGENCY SOS ALERT! Patient needs immediate medical attention!"
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')
    to_number = os.getenv('CARETAKER_PHONE')
    
    # Print debug info
    print(f"Account SID: {account_sid[:10]}...")
    print(f"From: {from_number}")
    print(f"To: {to_number}")
    
    if not account_sid or not auth_token:
        return {"status": "failed", "error": "Twilio credentials missing"}
    
    if not to_number:
        return {"status": "failed", "error": "Caretaker number missing"}
    
    try:
        client = Client(account_sid, auth_token)
        sms = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        print(f"✅ SOS Sent! SID: {sms.sid}")
        return {"status": "sent", "sid": sms.sid}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "failed", "error": str(e)}
