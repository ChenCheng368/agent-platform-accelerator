# Multi-Agent Orchestrator Pattern

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Resource Group                            │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            Container Apps Environment                    │ │
│  │                                                         │ │
│  │  ┌─────────────┐   ┌─────────────┐  ┌──────────────┐  │ │
│  │  │Orchestrator │   │ Worker      │  │ Worker       │  │ │
│  │  │Agent (API)  │   │ Agent 1     │  │ Agent 2      │  │ │
│  │  └──────┬──────┘   └──────┬──────┘  └──────┬───────┘  │ │
│  └─────────┼─────────────────┼─────────────────┼──────────┘ │
│            │                 │                 │              │
│            ▼                 ▼                 ▼              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │          Azure Service Bus                            │    │
│  │  ┌────────────┐  ┌────────────┐  ┌───────────────┐  │    │
│  │  │agent-tasks │  │agent-results│  │agent-events   │  │    │
│  │  │(queue)     │  │(queue)     │  │(topic)        │  │    │
│  │  └────────────┘  └────────────┘  └───────────────┘  │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │Azure OpenAI│  │Cosmos DB   │  │Container Registry      │ │
│  │(inference) │  │(state)     │  │(agent images)          │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## When to Use

- Multi-agent systems with specialized worker agents
- Async task distribution and result aggregation
- Systems requiring durable agent state/memory
- Event-driven agent architectures
- Production workloads requiring horizontal scaling

## Components

| Resource | Purpose |
|----------|---------|
| Container Apps | Hosting orchestrator + worker agents |
| Service Bus | Async messaging between agents |
| Cosmos DB | Agent state, memory, conversation history |
| Azure OpenAI | LLM inference for all agents |
| Container Registry | Private agent container images |
| App Insights | Distributed tracing across agents |

## Estimated Cost

- **Dev**: ~$400/month
- **Prod**: ~$1000/month (depends on agent count and traffic)
