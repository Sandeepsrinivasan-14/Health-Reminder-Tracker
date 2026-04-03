export const checkHealthMetricsAndAlert = async (userId: number, healthData: any) => {
  const alerts: string[] = [];

  if (healthData.bp_systolic > 140 || healthData.bp_diastolic > 90) {
    const alertMessage = `High Blood Pressure Alert: ${healthData.bp_systolic}/${healthData.bp_diastolic} mmHg`;
    alerts.push(alertMessage);
    console.log(alertMessage);
  } else if (healthData.bp_systolic < 90 || healthData.bp_diastolic < 60) {
    const alertMessage = `Low Blood Pressure Alert: ${healthData.bp_systolic}/${healthData.bp_diastolic} mmHg`;
    alerts.push(alertMessage);
    console.log(alertMessage);
  }

  if (healthData.heart_rate > 100) {
    const alertMessage = `High Heart Rate Alert: ${healthData.heart_rate} BPM`;
    alerts.push(alertMessage);
    console.log(alertMessage);
  } else if (healthData.heart_rate < 60) {
    const alertMessage = `Low Heart Rate Alert: ${healthData.heart_rate} BPM`;
    alerts.push(alertMessage);
    console.log(alertMessage);
  }

  if (healthData.blood_sugar > 140) {
    const alertMessage = `CRITICAL: High Blood Sugar Alert: ${healthData.blood_sugar} mg/dL`;
    alerts.push(alertMessage);
    console.log(alertMessage);
  } else if (healthData.blood_sugar < 70) {
    const alertMessage = `CRITICAL: Low Blood Sugar Alert: ${healthData.blood_sugar} mg/dL`;
    alerts.push(alertMessage);
    console.log(alertMessage);
  }

  return alerts;
};

export default checkHealthMetricsAndAlert;
