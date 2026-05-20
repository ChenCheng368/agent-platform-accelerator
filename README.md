# Agent Platform Accelerator

An AI-powered platform accelerator that helps enterprise customers quickly deploy Azure infrastructure for AI agent solutions using natural language.

## Overview

This application provides a conversational interface where users describe their AI agent platform requirements in natural language, and the accelerator agent generates production-ready Infrastructure as Code (Bicep/Terraform) tailored for Azure AI agent workloads.

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  React Frontend │────▶│  FastAPI Backend      │────▶│  Azure OpenAI       │
│  (Chat UI)      │◀────│  (Orchestrator)       │◀────│  (GPT-4o)           │
└─────────────────┘     └──────────┬───────────┘     └─────────────────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  IaC Generation      │
                        │  Engine              │
                        │  ┌─────────────────┐ │
                        │  │ Template Library │ │
                        │  │ (Bicep/TF)      │ │
                        │  └─────────────────┘ │
                        └──────────────────────┘
```

## Key Features

- **Natural Language to IaC**: Describe your requirements, get production-ready Bicep or Terraform
- **Pre-built Patterns**: Reusable architecture patterns for common AI agent scenarios
- **Enterprise-Ready**: Networking, identity, security, and compliance built-in
- **Singapore Region Optimized**: Default configurations for Southeast Asia deployments
- **Modular Design**: Mix and match components for your specific use case

## Supported Patterns

| Pattern | Description |
|---------|-------------|
| `foundry-agent-basic` | Azure AI Foundry + Managed Identity + Key Vault |
| `foundry-agent-vnet` | Above + VNet integration + Private Endpoints |
| `multi-agent-orchestrator` | Multi-agent with Service Bus + Container Apps |
| `rag-agent` | AI Search + OpenAI + Cosmos DB for RAG agents |
| `agent-with-mcp` | Agent with MCP server on Container Apps |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Azure CLI (`az`) logged in
- Azure OpenAI resource with GPT-4o deployed

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Configuration

Set the following environment variables in `backend/.env`:

```
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview
DEFAULT_AZURE_REGION=southeastasia
```

## Project Structure

```
agent-platform-accelerator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/                 # API routes
│   │   ├── agent/               # Agent orchestration logic
│   │   ├── iac_engine/          # IaC generation engine
│   │   └── templates/           # Bicep/Terraform templates
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   └── services/
│   ├── package.json
│   └── vite.config.ts
├── patterns/                    # Reusable architecture patterns
│   ├── foundry-agent-basic/
│   ├── foundry-agent-vnet/
│   ├── multi-agent-orchestrator/
│   └── rag-agent/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## License

Internal use - Singapore Enterprise Commercial Team
