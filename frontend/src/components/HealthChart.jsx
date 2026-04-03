import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const HealthChart = ({ userId }) => {
  const [chartData, setChartData] = useState(null);
  const [activeMetric, setActiveMetric] = useState('bp_systolic');

  useEffect(() => {
    if (userId) {
      fetch(`http://localhost:8000/health-data/user/${userId}`)
        .then(res => res.json())
        .then(data => {
          const labels = data.slice().reverse().map(r => new Date(r.recorded_at).toLocaleDateString());
          const bpSys = data.slice().reverse().map(r => r.bp_systolic);
          const bpDia = data.slice().reverse().map(r => r.bp_diastolic);
          const heartRate = data.slice().reverse().map(r => r.heart_rate);
          const bloodSugar = data.slice().reverse().map(r => r.blood_sugar);
          const weight = data.slice().reverse().map(r => r.weight);

          setChartData({
            labels,
            datasets: {
              bp_systolic: {
                label: 'BP Systolic',
                data: bpSys,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239,68,68,0.1)',
                fill: true,
                tension: 0.4
              },
              bp_diastolic: {
                label: 'BP Diastolic',
                data: bpDia,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245,158,11,0.1)',
                fill: true,
                tension: 0.4
              },
              heart_rate: {
                label: 'Heart Rate',
                data: heartRate,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16,185,129,0.1)',
                fill: true,
                tension: 0.4
              },
              blood_sugar: {
                label: 'Blood Sugar',
                data: bloodSugar,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139,92,246,0.1)',
                fill: true,
                tension: 0.4
              },
              weight: {
                label: 'Weight (kg)',
                data: weight,
                borderColor: '#06b6d4',
                backgroundColor: 'rgba(6,182,212,0.1)',
                fill: true,
                tension: 0.4
              }
            }
          });
        });
    }
  }, [userId]);

  if (!chartData) return null;

  const metrics = [
    { key: 'bp_systolic', label: 'BP Systolic', icon: '❤️' },
    { key: 'bp_diastolic', label: 'BP Diastolic', icon: '💙' },
    { key: 'heart_rate', label: 'Heart Rate', icon: '💓' },
    { key: 'blood_sugar', label: 'Blood Sugar', icon: '🩸' },
    { key: 'weight', label: 'Weight', icon: '⚖️' }
  ];

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Health Trends Over Time' }
    },
    scales: { y: { beginAtZero: false } }
  };

  return (
    <div style={{ marginTop: '20px', padding: '20px', background: 'white', borderRadius: '16px' }}>
      <h3 style={{ marginBottom: '15px', color: '#1f2937' }}>📈 Health Analytics</h3>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {metrics.map(m => (
          <button
            key={m.key}
            onClick={() => setActiveMetric(m.key)}
            style={{
              padding: '8px 16px',
              background: activeMetric === m.key ? 'linear-gradient(135deg, #667eea, #764ba2)' : '#f3f4f6',
              color: activeMetric === m.key ? 'white' : '#374151',
              border: 'none',
              borderRadius: '50px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500',
              transition: 'all 0.3s'
            }}
          >
            {m.icon} {m.label}
          </button>
        ))}
      </div>
      <div style={{ height: '300px' }}>
        <Line data={{ labels: chartData.labels, datasets: [chartData.datasets[activeMetric]] }} options={options} />
      </div>
    </div>
  );
};

export default HealthChart;
