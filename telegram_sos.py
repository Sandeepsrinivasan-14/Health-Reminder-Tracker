import requests

TELEGRAM_BOT_TOKEN = "8660692147:AAEwJmsfmm22EKfL8kXnGGFV7izgH1jpSD0"
YOUR_USERNAME = "Lohithvardan"  # Your Telegram username

def send_sos_alert(message=None):
    if message is None:
        message = "🚨 EMERGENCY SOS ALERT! 🚨\n\nPatient needs immediate medical attention!\n\nPlease check on them immediately."
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": f"@{YOUR_USERNAME}",
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ Telegram SOS Sent to @{YOUR_USERNAME}")
            return {"status": "sent", "method": "telegram"}
        else:
            print(f"❌ Failed: {response.text}")
            return {"status": "failed", "error": response.text}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "failed", "error": str(e)}
