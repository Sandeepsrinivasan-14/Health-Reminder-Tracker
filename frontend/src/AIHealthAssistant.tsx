import React, { useState, useEffect } from 'react'

interface Message {
  text: string
  isUser: boolean
  provider?: string
  timestamp?: string
}

function AIHealthAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    { text: 'Hello! I am your AI Health Assistant powered by Google Gemini. How can I help you today?', isUser: false }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [aiStatus, setAiStatus] = useState<any>(null)

  useEffect(() => {
    checkAIStatus()
  }, [])

  const checkAIStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ai/status')
      const data = await response.json()
      setAiStatus(data)
    } catch (error) {
      console.error('AI status check failed')
    }
  }

  const sendMessage = async () => {
    if (!input.trim()) return
    
    const userMessage = input.trim()
    setMessages(prev => [...prev, { text: userMessage, isUser: true, timestamp: new Date().toLocaleTimeString() }])
    setInput('')
    setIsLoading(true)
    
    try {
      const healthData = localStorage.getItem('healthData')
      const parsedHealth = healthData ? JSON.parse(healthData) : []
      const latestHealth = parsedHealth.length > 0 ? parsedHealth[parsedHealth.length - 1] : null
      
      const response = await fetch('http://localhost:8000/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage,
          health_data: latestHealth
        })
      })
      
      const data = await response.json()
      setMessages(prev => [...prev, { 
        text: data.response, 
        isUser: false,
        provider: data.provider,
        timestamp: new Date().toLocaleTimeString()
      }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        text: 'Sorry, I am having trouble connecting. Please check your connection and try again.', 
        isUser: false 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mt-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-green-600">?? AI Health Assistant</h2>
        {aiStatus && (
          <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
            {aiStatus.gemini_available ? 'Gemini AI Active' : 'Fallback Mode'}
          </span>
        )}
      </div>
      <p className="text-sm text-gray-500 mb-4">Ask me anything about BP, sugar, heart rate, medicines, diet, or exercise!</p>
      
      <div className="h-80 overflow-y-auto mb-4 border rounded p-3 bg-gray-50 dark:bg-gray-900">
        {messages.map((msg, i) => (
          <div key={i} className={'mb-3 ' + (msg.isUser ? 'text-right' : 'text-left')}>
            <div className={'inline-block max-w-[85%] p-3 rounded-lg ' + 
              (msg.isUser 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 dark:bg-gray-700 dark:text-white')}>
              <div className="whitespace-pre-wrap">{msg.text}</div>
              {msg.provider && !msg.isUser && (
                <div className="text-xs mt-1 opacity-70">Powered by {msg.provider}</div>
              )}
              {msg.timestamp && (
                <div className="text-xs mt-1 opacity-50">{msg.timestamp}</div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="text-left">
            <div className="inline-block p-3 rounded-lg bg-gray-200 dark:bg-gray-700">
              <div className="flex gap-1">
                <span className="animate-bounce">?</span>
                <span className="animate-bounce delay-100">?</span>
                <span className="animate-bounce delay-200">?</span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about BP, sugar, medicines, diet..."
          className="flex-1 p-3 border rounded dark:bg-gray-700 dark:text-white"
        />
        <button
          onClick={sendMessage}
          disabled={isLoading}
          className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default AIHealthAssistant
