import React from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface HealthChartProps {
  healthData: any[]
}

function HealthChart({ healthData }: HealthChartProps) {
  const last7Days = healthData.slice(-7)
  
  const chartData = {
    labels: last7Days.map(function(d) { return new Date(d.date).toLocaleDateString() }),
    datasets: [
      {
        label: 'BP Systolic',
        data: last7Days.map(function(d) { return d.bp_systolic }),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.1
      },
      {
        label: 'Heart Rate',
        data: last7Days.map(function(d) { return d.heart_rate }),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        tension: 0.1
      }
    ]
  }

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const
      },
      title: {
        display: true,
        text: 'Health Trends (Last 7 Days)'
      }
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mt-4">
      <h3 className="text-lg font-bold mb-4 dark:text-white">?? Health Trends Chart</h3>
      <Line data={chartData} options={options} />
    </div>
  )
}

export default HealthChart
