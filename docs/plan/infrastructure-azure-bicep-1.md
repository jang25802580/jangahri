---
goal: Implement Azure Infrastructure with Bicep for PDF Chatbot
version: 1.0
date_created: 2026-03-17
last_updated: 2026-03-17
owner: KAIST Big Data Analysis Team
status: 'Planned'
tags: [infrastructure, azure, bicep, iac]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan defines the tasks to provision the Azure infrastructure for the KAIST PDF Chatbot Agent. It focuses on setting up the `kaist-ai-infra` directory with Bicep templates for Azure Functions, Cosmos DB (Serverless), Blob Storage, and Key Vault, managed by `azd`.

## 1. Requirements & Constraints

- **REQ-001**: Deploy resources to `koreacentral` region.
- **REQ-002**: Use Bicep for all infrastructure definitions.
- **REQ-003**: Manage deployment with Azure Developer CLI (`azd`).
- **REQ-004**: Resource Group: `kaist-ai-agent-rg`.
- **REQ-005**: Cosmos DB: Serverless mode with Hybrid Search (NoSQL).
- **REQ-006**: Storage: Standard_LRS, Hot tier for PDF storage.
- **REQ-007**: Compute: Azure Functions (Python 3.11, Consumption) & Static Web Apps (Free).
- **SEC-001**: Use Managed Identities for service-to-service authentication.
- **SEC-002**: Use Key Vault for secrets (e.g., future GCP keys).

## 2. Implementation Steps

### Implementation Phase 1: Project Setup & Base Infrastructure

- GOAL-001: Initialize the infrastructure project structure and base Bicep files.

| Task     | Description                                                                 | Completed | Date |
| -------- | --------------------------------------------------------------------------- | --------- | ---- |
| TASK-001 | Create `kaist-ai-infra` directory and `infra` subdirectory.                |           |      |
| TASK-002 | Initialize `azure.yaml` in root for `azd` configuration.                   |           |      |
| TASK-003 | Create `infra/main.bicep` and `infra/main.parameters.json`.                |           |      |
| TASK-004 | Create `infra/modules/naming.bicep` for consistent resource naming.       |           |      |
| TASK-005 | Create `infra/modules/keyvault.bicep` for secrets management.             |           |      |

### Implementation Phase 2: Data & Storage Layer

- GOAL-002: Provision storage and database resources.

| Task     | Description                                                                                     | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-006 | Create `infra/modules/storage.bicep` (Blob Storage, Hot tier, Containers).                    |           |      |
| TASK-007 | Create `infra/modules/cosmos.bicep` (Serverless, NoSQL, Vector Search).                       |           |      |
| TASK-008 | Define Cosmos DB database `knowledgebase` and containers (`documents`, `chunks`, `sessions`). |           |      |

### Implementation Phase 3: Compute & Web Hosting

- GOAL-003: Provision compute resources for API and generic web hosting.

| Task     | Description                                                                                          | Completed | Date |
| -------- | ---------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-009 | Create `infra/modules/functions.bicep` (Python 3.11, Consumption Plan, App Insights).              |           |      |
| TASK-010 | Create `infra/modules/staticwebapp.bicep` (Free tier, for React app host).                         |           |      |
| TASK-011 | Wire up modules in `main.bicep` and configure outputs (endpoints, keys, identities).               |           |      |

## 3. Alternatives

- **ALT-001**: **Terraform** - Rejected in favor of Bicep for native Azure integration and `azd` support.
- **ALT-002**: **Azure SQL** - Rejected; Cosmos DB chosen for vector search and schema flexibility.
- **ALT-003**: **Container Apps** - Rejected; Functions Consumption plan is more cost-effective for low-traffic/startup phase.

## 4. Dependencies

- **DEP-001**: Azure Subscription with `Contributor` access.
- **DEP-002**: `azd` (Azure Developer CLI) installed.
- **DEP-003**: `bicep` CLI installed.

## 5. Files

- **FILE-001**: `azure.yaml`
- **FILE-002**: `kaist-ai-infra/infra/main.bicep`
- **FILE-003**: `kaist-ai-infra/infra/main.parameters.json`
- **FILE-004**: `kaist-ai-infra/infra/modules/naming.bicep`
- **FILE-005**: `kaist-ai-infra/infra/modules/storage.bicep`
- **FILE-006**: `kaist-ai-infra/infra/modules/cosmos.bicep`
- **FILE-007**: `kaist-ai-infra/infra/modules/functions.bicep`
- **FILE-008**: `kaist-ai-infra/infra/modules/staticwebapp.bicep`
- **FILE-009**: `kaist-ai-infra/infra/modules/keyvault.bicep`

## 6. Testing

- **TEST-001**: Run `az bicep build --file infra/main.bicep` to validate syntax.
- **TEST-002**: Run `azd up` (or `provision`) to deploy and verify resource creation in the portal.
- **TEST-003**: Verify Cosmos DB is in Serverless mode.
- **TEST-004**: Verify Key Vault and Storage Account are created in `koreacentral`.

## 7. Risks & Assumptions

- **RISK-001**: `koreacentral` might not have Static Web Apps free tier available (might need to use `eastasia` for SWAs).
- **ASSUMPTION-001**: User has valid Azure credentials.
- **ASSUMPTION-002**: Resource group name `kaist-ai-agent-rg` is available/unique within the subscription scope constraints.

## 8. Related Specifications / Further Reading

- [docs/spec/spec-architecture-pdf-chatbot-agent.md](docs/spec/spec-architecture-pdf-chatbot-agent.md)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
