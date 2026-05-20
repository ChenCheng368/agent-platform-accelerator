# Foundry Agent Basic Pattern

## Architecture

```
┌─────────────────────────────────────────────────┐
│                Resource Group                    │
│                                                 │
│  ┌───────────────┐     ┌──────────────────┐    │
│  │  AI Foundry   │────▶│  Azure OpenAI    │    │
│  │  Hub + Project│     │  (GPT-4o)        │    │
│  └───────────────┘     └──────────────────┘    │
│          │                                      │
│          ├──▶ Key Vault (secrets)               │
│          ├──▶ Storage Account (data)            │
│          └──▶ App Insights (monitoring)         │
│                                                 │
│  ┌───────────────────────────────────────┐     │
│  │  User-Assigned Managed Identity       │     │
│  │  (RBAC: OpenAI User, KV Secrets)     │     │
│  └───────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

## When to Use

- Getting started with a single AI agent
- Prototyping and development
- Simple agent scenarios without complex networking
- When you want minimal infrastructure overhead

## Components

| Resource | Purpose |
|----------|---------|
| AI Foundry Hub | Central management for AI projects |
| AI Foundry Project | Workspace for agent development |
| Azure OpenAI | LLM inference (GPT-4o default) |
| Key Vault | Secure secrets management |
| Storage Account | Data and artifact storage |
| App Insights | Monitoring and telemetry |
| Managed Identity | Passwordless authentication |

## Prerequisites

- Azure subscription with OpenAI access
- Contributor + User Access Administrator on resource group
- Azure OpenAI model quota in target region

## Estimated Cost

- **Dev**: ~$150/month (low usage)
- **Prod**: ~$400/month (moderate usage)
- Primary cost driver: Azure OpenAI token consumption
