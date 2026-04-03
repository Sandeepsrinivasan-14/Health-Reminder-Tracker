class NotificationService {
  private static instance: NotificationService;
  
  static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  sendNotification(title: string, body: string) {
    console.log(`Notification: ${title} - ${body}`);
  }

  getMedicationReminders(userId: number) {
    return fetch(`http://localhost:8000/api/notifications/medication-reminders/${userId}`);
  }
}

export default NotificationService.getInstance();
