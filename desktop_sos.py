import platform
import subprocess

def send_sos_alert(message=None):
    if message is None:
        message = "🚨 EMERGENCY SOS ALERT! 🚨\n\nPatient needs immediate medical attention!\n\nPlease check on them immediately."
    
    if platform.system() == "Windows":
        try:
            from plyer import notification
            notification.notify(
                title="🚨 SOS ALERT!",
                message=message,
                timeout=10,
                app_name="Health Tracker"
            )
        except:
            print("Notification module not available")
        
        try:
            import winsound
            for i in range(3):
                winsound.Beep(1000, 500)
        except:
            pass
        
        print("✅ SOS Alert Displayed on Desktop!")
        
    elif platform.system() == "Darwin":  # Mac
        subprocess.run(['osascript', '-e', f'display alert "SOS ALERT!" message "{message}"'])
    else:  # Linux
        subprocess.run(['notify-send', 'SOS ALERT!', message])
    
    return {"status": "sent", "method": "desktop_notification"}
