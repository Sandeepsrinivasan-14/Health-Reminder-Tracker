export default {
  requestPermission: async () => { if ('Notification' in window) return await Notification.requestPermission() === 'granted'; return false; },
  startReminderCheck: (userId) => { console.log('Reminder check started for user', userId); },
  stopReminderCheck: () => { console.log('Reminder check stopped'); }
};
