// Notification Service for medication reminders
export class NotificationService {
  static requestPermission() {
    if ('Notification' in window) {
      Notification.requestPermission();
    }
  }

  static sendNotification(title: string, body: string, tag?: string) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: body,
        icon: '/favicon.svg',
        tag: tag || 'medication-reminder'
      });
    }
  }

  static scheduleReminder(medName: string, time: string) {
    // Simple reminder scheduling
    const now = new Date();
    const [hour, minute] = time.split(':');
    const reminderTime = new Date();
    reminderTime.setHours(parseInt(hour), parseInt(minute), 0);
    
    const timeDiff = reminderTime.getTime() - now.getTime();
    if (timeDiff > 0) {
      setTimeout(() => {
        this.sendNotification('Medication Reminder', Time to take );
      }, timeDiff);
    }
  }
}
