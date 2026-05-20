import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import CodePanel from './components/CodePanel'
import Header from './components/Header'
import './App.css'

export interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface GeneratedCode {
  code: string
  pattern: string | null
  files: { filename: string; content: string }[] | null
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [iacFormat, setIacFormat] = useState<'bicep' | 'terraform'>('bicep')

  const sendMessage = async (content: string) => {
    const userMessage: Message = { role: 'user', content }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          iac_format: iacFormat,
        }),
      })

      if (!response.ok) throw new Error('Failed to send message')

      const data = await response.json()
      const assistantMessage: Message = { role: 'assistant', content: data.reply }
      setMessages(prev => [...prev, assistantMessage])

      if (data.iac_code) {
        setGeneratedCode({
          code: data.iac_code,
          pattern: data.pattern_used,
          files: data.files,
        })
      }
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please check that the backend is running.',
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <Header iacFormat={iacFormat} onFormatChange={setIacFormat} />
      <div className="main-content">
        <ChatPanel
          messages={messages}
          onSendMessage={sendMessage}
          isLoading={isLoading}
        />
        <CodePanel generatedCode={generatedCode} />
      </div>
    </div>
  )
}

export default App
