import React, { useState } from 'react'

interface VoiceInputProps {
  onResult: (text: string) => void
}

function VoiceInput({ onResult }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false)

  const startListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('Speech recognition not supported in this browser')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onresult = (event: any) => {
      const text = event.results[0][0].transcript
      onResult(text)
      setIsListening(false)
    }
    recognition.start()
  }

  return (
    <button
      onClick={startListening}
      className={"px-3 py-1 rounded " + (isListening ? "bg-red-600 animate-pulse" : "bg-purple-600") + " text-white"}
    >
      {isListening ? '?? Listening...' : '?? Voice Input'}
    </button>
  )
}

export default VoiceInput
