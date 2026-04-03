import React, { useState, useEffect } from 'react'

interface RiskPrediction {
  risk_level: string
  risks: string[]
  recommendations: string[]
  summary: string
  ai_analysis?: string
}

function HealthRiskPredictor() {
  const [prediction, setPrediction] = useState<RiskPrediction | null>(null)
  const [loading, setLoading] = useState(false)
  const [healthData, setHealthData] = useState<any>(null)

  useEffect(() => {
    loadLatestHealthData()
  }, [])

  const loadLatestHealthData = () => {
    const saved = localStorage.getItem('healthData')
    if (saved) {
      const data = JSON.parse(saved)
      if (data.length > 0) {
        setHealthData(data[data.length - 1])
      }
    }
  }

  const analyzeHealthRisk = async () => {
    if (!healthData) {
      alert('No health data available. Please save some health data first.')
      return
    }
    
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/ai/health-risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ health_data: healthData })
      })
      
      const data = await response.json()
      setPrediction(data)
    } catch (error) {
      alert('Failed to analyze health risk. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch(level?.toUpperCase()) {
      case 'HIGH': return 'bg-red-100 border-red-500 text-red-800'
      case 'MODERATE': return 'bg-yellow-100 border-yellow-500 text-yellow-800'
      default: return 'bg-green-100 border-green-500 text-green-800'
    }
  }

  const getRiskIcon = (level: string) => {
    switch(level?.toUpperCase()) {
      case 'HIGH': return '??'
      case 'MODERATE': return '??'
      default: return '??'
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mt-4">
      <h2 className="text-xl font-bold mb-2 text-purple-600">?? AI Health Risk Predictor</h2>
      <p className="text-sm text-gray-500 mb-4">Powered by Google Gemini AI - Analyzes your health data for potential risks</p>
      
      {healthData && (
        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
          <h3 className="font-semibold mb-2">Current Health Data:</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span>BP: {healthData.bp_systolic}/{healthData.bp_diastolic}</span>
            <span>Heart Rate: {healthData.heart_rate} BPM</span>
            <span>Blood Sugar: {healthData.blood_sugar} mg/dL</span>
            <span>Weight: {healthData.weight} kg</span>
          </div>
        </div>
      )}
      
      <button
        onClick={analyzeHealthRisk}
        disabled={loading || !healthData}
        className="w-full bg-purple-600 text-white px-4 py-3 rounded hover:bg-purple-700 disabled:opacity-50 mb-4"
      >
        {loading ? 'Analyzing with Gemini AI...' : '?? Analyze Health Risk with AI'}
      </button>
      
      {prediction && (
        <div className={'p-4 rounded-lg border-2 ' + getRiskColor(prediction.risk_level)}>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-2xl">{getRiskIcon(prediction.risk_level)}</span>
            <h3 className="font-bold text-lg">Risk Level: {prediction.risk_level}</h3>
          </div>
          
          <p className="mb-3">{prediction.summary}</p>
          
          {prediction.risks && prediction.risks.length > 0 && (
            <div className="mb-3">
              <strong className="block mb-1">?? Identified Risks:</strong>
              <ul className="list-disc list-inside space-y-1">
                {prediction.risks.map((risk, i) => (
                  <li key={i}>{risk}</li>
                ))}
              </ul>
            </div>
          )}
          
          {prediction.recommendations && prediction.recommendations.length > 0 && (
            <div>
              <strong className="block mb-1">?? Recommendations:</strong>
              <ul className="list-disc list-inside space-y-1">
                {prediction.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
          
          {prediction.ai_analysis && (
            <div className="mt-3 pt-2 border-t text-sm italic">
              <strong>AI Analysis:</strong> {prediction.ai_analysis}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default HealthRiskPredictor
