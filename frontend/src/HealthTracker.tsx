import React, { useState, useEffect } from 'react'
import HealthChart from './HealthChart'
import { PDFExportService } from './pdfExport'

interface HealthData {
  id: number
  date: string
  bp_systolic: number
  bp_diastolic: number
  heart_rate: number
  blood_sugar: number
  weight: number
}

interface HealthTrackerProps {
  selectedUser: any
}

function HealthTracker({ selectedUser }: HealthTrackerProps) {
  const [healthData, setHealthData] = useState<HealthData[]>([])
  const [bpSystolic, setBpSystolic] = useState('')
  const [bpDiastolic, setBpDiastolic] = useState('')
  const [heartRate, setHeartRate] = useState('')
  const [bloodSugar, setBloodSugar] = useState('')
  const [weight, setWeight] = useState('')

  useEffect(() => {
    const saved = localStorage.getItem('healthData')
    if (saved) {
      setHealthData(JSON.parse(saved))
    }
  }, [])

  const saveHealthData = () => {
    if (!bpSystolic || !bpDiastolic || !heartRate || !bloodSugar || !weight) {
      alert('Please fill all fields')
      return
    }
    
    const newEntry: HealthData = {
      id: Date.now(),
      date: new Date().toLocaleString(),
      bp_systolic: parseInt(bpSystolic),
      bp_diastolic: parseInt(bpDiastolic),
      heart_rate: parseInt(heartRate),
      blood_sugar: parseInt(bloodSugar),
      weight: parseInt(weight)
    }
    
    const updated = [...healthData, newEntry]
    setHealthData(updated)
    localStorage.setItem('healthData', JSON.stringify(updated))
    
    setBpSystolic('')
    setBpDiastolic('')
    setHeartRate('')
    setBloodSugar('')
    setWeight('')
    
    alert('Health data saved!')
  }

  const analyzeHealth = () => {
    if (healthData.length === 0) {
      alert('No health data available')
      return
    }
    
    const latest = healthData[healthData.length - 1]
    let warnings = []
    
    if (latest.bp_systolic > 140) warnings.push('High BP')
    if (latest.bp_systolic < 90) warnings.push('Low BP')
    if (latest.heart_rate > 100) warnings.push('High Heart Rate')
    if (latest.heart_rate < 60) warnings.push('Low Heart Rate')
    if (latest.blood_sugar > 140) warnings.push('High Blood Sugar')
    if (latest.blood_sugar < 70) warnings.push('Low Blood Sugar')
    
    if (warnings.length > 0) {
      alert('Health Alert: ' + warnings.join(', ') + '\nPlease consult doctor if symptoms persist.')
    } else {
      alert('All vitals are in normal range. Good job!')
    }
  }

  const exportToPDF = () => {
    if (healthData.length === 0) {
      alert('No health data to export')
      return
    }
    if (!selectedUser) {
      alert('Please select a user first')
      return
    }
    PDFExportService.exportHealthReport(healthData, selectedUser.name)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-purple-700 dark:text-purple-400">Health Parameter Tracker</h2>
        <button 
          onClick={exportToPDF}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm"
        >
          Export PDF Report
        </button>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium mb-1 dark:text-white">BP Systolic (mmHg)</label>
          <input type="number" value={bpSystolic} onChange={(e) => setBpSystolic(e.target.value)}
            className="w-full p-2 border rounded dark:bg-gray-700 dark:text-white" placeholder="e.g., 120" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1 dark:text-white">BP Diastolic (mmHg)</label>
          <input type="number" value={bpDiastolic} onChange={(e) => setBpDiastolic(e.target.value)}
            className="w-full p-2 border rounded dark:bg-gray-700 dark:text-white" placeholder="e.g., 80" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1 dark:text-white">Heart Rate (BPM)</label>
          <input type="number" value={heartRate} onChange={(e) => setHeartRate(e.target.value)}
            className="w-full p-2 border rounded dark:bg-gray-700 dark:text-white" placeholder="e.g., 72" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1 dark:text-white">Blood Sugar (mg/dL)</label>
          <input type="number" value={bloodSugar} onChange={(e) => setBloodSugar(e.target.value)}
            className="w-full p-2 border rounded dark:bg-gray-700 dark:text-white" placeholder="e.g., 110" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1 dark:text-white">Weight (kg)</label>
          <input type="number" value={weight} onChange={(e) => setWeight(e.target.value)}
            className="w-full p-2 border rounded dark:bg-gray-700 dark:text-white" placeholder="e.g., 70" />
        </div>
      </div>
      
      <div className="flex gap-2 mb-4">
        <button onClick={saveHealthData} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Save Health Data
        </button>
        <button onClick={analyzeHealth} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
          Analyze Health Status
        </button>
      </div>
      
      <h3 className="font-semibold mb-2 dark:text-white">Recent Health Records</h3>
      <div className="max-h-48 overflow-y-auto">
        {healthData.length === 0 ? (
          <p className="text-gray-500 text-center py-4 dark:text-gray-400">No health data recorded yet</p>
        ) : (
          healthData.slice().reverse().slice(0, 5).map((data) => (
            <div key={data.id} className="border rounded p-2 mb-2 dark:border-gray-600">
              <div className="font-semibold text-gray-700 dark:text-white">{data.date}</div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mt-1 text-xs">
                <span className="dark:text-gray-300">BP: {data.bp_systolic}/{data.bp_diastolic}</span>
                <span className="dark:text-gray-300">HR: {data.heart_rate}</span>
                <span className="dark:text-gray-300">Sugar: {data.blood_sugar}</span>
                <span className="dark:text-gray-300">Weight: {data.weight}kg</span>
              </div>
            </div>
          ))
        )}
      </div>
      
      {healthData.length > 0 && <HealthChart healthData={healthData} />}
    </div>
  )
}

export default HealthTracker
