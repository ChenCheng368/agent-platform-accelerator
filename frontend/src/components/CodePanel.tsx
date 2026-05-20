import { useState } from 'react'
import { GeneratedCode } from '../App'
import './CodePanel.css'

interface CodePanelProps {
  generatedCode: GeneratedCode | null
}

function CodePanel({ generatedCode }: CodePanelProps) {
  const [activeFile, setActiveFile] = useState<number>(0)
  const [copied, setCopied] = useState(false)

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownloadAll = () => {
    if (!generatedCode?.files) return
    generatedCode.files.forEach(file => {
      const blob = new Blob([file.content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.filename
      a.click()
      URL.revokeObjectURL(url)
    })
  }

  if (!generatedCode) {
    return (
      <div className="code-panel">
        <div className="code-empty">
          <div className="code-empty-icon">📄</div>
          <p>Generated IaC code will appear here</p>
          <p className="code-empty-hint">
            Describe your requirements in the chat to generate Azure infrastructure code
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="code-panel">
      <div className="code-header">
        <div className="code-header-left">
          {generatedCode.pattern && (
            <span className="pattern-badge">{generatedCode.pattern}</span>
          )}
        </div>
        <div className="code-header-actions">
          <button className="action-btn" onClick={() => handleCopy(generatedCode.code)}>
            {copied ? '✓ Copied' : '📋 Copy All'}
          </button>
          {generatedCode.files && (
            <button className="action-btn" onClick={handleDownloadAll}>
              ⬇ Download
            </button>
          )}
        </div>
      </div>

      {generatedCode.files && generatedCode.files.length > 1 && (
        <div className="file-tabs">
          {generatedCode.files.map((file, i) => (
            <button
              key={i}
              className={`file-tab ${i === activeFile ? 'active' : ''}`}
              onClick={() => setActiveFile(i)}
            >
              {file.filename}
            </button>
          ))}
        </div>
      )}

      <div className="code-content">
        <pre>
          <code>
            {generatedCode.files
              ? generatedCode.files[activeFile]?.content
              : generatedCode.code}
          </code>
        </pre>
      </div>
    </div>
  )
}

export default CodePanel
