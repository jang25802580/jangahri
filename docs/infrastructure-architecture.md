# Infrastructure Architecture

Diagram: (add architecture diagram here)

Components

- Resource Group: `kaist-ai-agent-rg` (koreacentral)
- Storage: Blob Storage for PDFs
- Cosmos DB: NoSQL serverless with vector search
- Function App: Python 3.11 API
- Static Web App: React frontend (East Asia)
- Key Vault: secrets and managed identity bindings
- Monitoring: Log Analytics, Application Insights, Workbooks, Alerts

Deployment

Deployed via `azd up` using Bicep templates in `kaist-ai-infra/infra`.
