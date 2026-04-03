import React, { useState, useEffect } from 'react'

interface TrendAnalysis {
  trend_analysis: string
  recommendations?: string
  provider?: string
}

function HealthTrendAnalyzer() {
  const [analysis, setAnalysis] = useState<TrendAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [healthHistory, setHealthHistory] = useState<any[]>([])

  useEffect(() => {
    loadHealthHistory()
  }, [])

  const loadHealthHistory = () => {
    const saved = localStorage.getItem('healthData')
    if (saved) {
      const data = JSON.parse(saved)
      setHealthHistory(data)
    }
  }

  const analyzeTrends = async () => {
    if (healthHistory.length < 3) {
      alert('Need at least 3 health records for trend analysis. Please add more health data.')
      return
    }
    
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/ai/trend-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ health_history: healthHistory })
      })
      
      const data = await response.json()
      setAnalysis(data)
    } catch (error) {
      alert('Failed to analyze trends')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mt-4">
      <h2 className="text-xl font-bold mb-2 text-blue-600">?? AI Health Trend Analyzer</h2>
      <p className="text-sm text-gray-500 mb-4">Get AI-powered insights on your health trends over time</p>
      
      <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
        <div className="flex justify-between items-center">
          <span className="font-semibold">Health Records: {healthHistory.length}</span>
          {healthHistory.length > 0 && (
            <span className="text-sm text-gray-500">
              Latest: {new Date(healthHistory[healthHistory.length - 1]?.date).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>
      
      <button
        onClick={analyzeTrends}
        disabled={loading || healthHistory.length < 3}
        className="w-full bg-blue-600 text-white px-4 py-3 rounded hover:bg-blue-700 disabled:opacity-50 mb-4"
      >
        {loading ? 'Analyzing with Gemini AI...' : '?? Analyze Health Trends'}
      </button>
      
      {analysis && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200">
          <h3 className="font-bold mb-2">Trend Analysis Results:</h3>
          <div className="whitespace-pre-wrap">{analysis.trend_analysis}</div>
          {analysis.provider && (
            <div className="text-xs mt-2 text-gray-500">Powered by {analysis.provider}</div>
          )}
        </div>
      )}
    </div>
  )
}

export default HealthTrendAnalyzer
