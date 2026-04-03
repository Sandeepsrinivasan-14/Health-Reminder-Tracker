// HealthMetricsAlert.ts
import NotificationService from '../services/NotificationService';

export const checkHealthMetricsAndAlert = async (userId: number, healthData: any) => {
  const alerts = [];
  
  // Check Blood Pressure
  if (healthData.bp_systolic > 140 || healthData.bp_diastolic > 90) {
    const alertMessage = ⚠️ High Blood Pressure Alert: / mmHg;
    await NotificationService.createHealthAlert(userId, 'Blood Pressure', 'warning', alertMessage);
    alerts.push(alertMessage);
    console.log(alertMessage);
  } else if (healthData.bp_systolic < 90 || healthData.bp_diastolic < 60) {
    const alertMessage = ⚠️ Low Blood Pressure Alert: / mmHg;
    await NotificationService.createHealthAlert(userId, 'Blood Pressure', 'warning', alertMessage);
    alerts.push(alertMessage);
    console.log(alertMessage);
  }
  
  // Check Heart Rate
  if (healthData.heart_rate > 100) {
    const alertMessage = 💓 High Heart Rate Alert:  BPM;
    await NotificationService.createHealthAlert(userId, 'Heart Rate', 'warning', alertMessage);
    alerts.push(alertMessage);
    console.log(alertMessage);
  } else if (healthData.heart_rate < 60) {
    const alertMessage = 💓 Low Heart Rate Alert:  BPM;
    await NotificationService.createHealthAlert(userId, 'Heart Rate', 'warning', alertMessage);
    alerts.push(alertMessage);
    console.log(alertMessage);
  }
  
  // Check Blood Sugar
  if (healthData.blood_sugar > 140) {
    const alertMessage = 🍬 CRITICAL: High Blood Sugar Alert:  mg/dL;
    await NotificationService.createHealthAlert(userId, 'Blood Sugar', 'danger', alertMessage);
    alerts.push(alertMessage);
    console.log(alertMessage);
  } else if (healthData.blood_sugar < 70) {
    const alertMessage = 🍬 CRITICAL: Low Blood Sugar Alert:  mg/dL;
    await NotificationService.createHealthAlert(userId, 'Blood Sugar', 'danger', alertMessage);
    alerts.push(alertMessage);
    console.log(alertMessage);
  }
  
  return alerts;
};

export default checkHealthMetricsAndAlert;
