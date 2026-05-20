import './Header.css'

interface HeaderProps {
  iacFormat: 'bicep' | 'terraform'
  onFormatChange: (format: 'bicep' | 'terraform') => void
}

function Header({ iacFormat, onFormatChange }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">Agent Platform Accelerator</h1>
        <span className="header-subtitle">Azure AI Agent Infrastructure Generator</span>
      </div>
      <div className="header-right">
        <div className="format-toggle">
          <label className="format-label">IaC Format:</label>
          <button
            className={`format-btn ${iacFormat === 'bicep' ? 'active' : ''}`}
            onClick={() => onFormatChange('bicep')}
          >
            Bicep
          </button>
          <button
            className={`format-btn ${iacFormat === 'terraform' ? 'active' : ''}`}
            onClick={() => onFormatChange('terraform')}
          >
            Terraform
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
