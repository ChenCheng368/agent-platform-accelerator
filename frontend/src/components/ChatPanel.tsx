import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { Message } from '../App'
import './ChatPanel.css'

interface ChatPanelProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  isLoading: boolean
}

const SUGGESTIONS = [
  "Deploy a basic AI Foundry agent platform in Southeast Asia",
  "I need a multi-agent system with async communication between agents",
  "Set up a RAG agent with AI Search and Cosmos DB for document Q&A",
  "Create a production-ready agent platform with VNet isolation",
  "Deploy an agent with an MCP server for tool augmentation",
]

function ChatPanel({ messages, onSendMessage, isLoading }: ChatPanelProps) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    onSendMessage(input.trim())
    setInput('')
  }

  return (
    <div className="chat-panel">
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome">
            <h2>Welcome to Agent Platform Accelerator</h2>
            <p>
              Describe your AI agent platform requirements in natural language, and I'll generate
              production-ready Azure Infrastructure as Code for you.
            </p>
            <div className="suggestions">
              <p className="suggestions-label">Try one of these:</p>
              {SUGGESTIONS.map((suggestion, i) => (
                <button
                  key={i}
                  className="suggestion-btn"
                  onClick={() => onSendMessage(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message message-${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message message-assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Describe your AI agent platform requirements..."
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button type="submit" className="send-btn" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatPanel
