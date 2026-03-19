---
goal: Setup API Backend with Azure Functions and Google Gemini 3 Pro
version: 1.0
date_created: 2026-03-17
status: 'Planned'
tags: [backend, azure-functions, python, gemini, langchain, gcp]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan details the setup of the Python 3.11 based API backend using Azure Functions. It includes the integration of Google Gemini 3 Pro for LLM and embedding capabilities via `langchain-google-genai`, replacing the initial Azure OpenAI plan. It also covers the necessary GCP project setup and security configuration using Azure Key Vault.

## 1. Requirements & Constraints

- **REQ-001**: Runtime envrionment must be Azure Functions with Python 3.11.
- **REQ-002**: Storage must use Azure Blob Storage (Cloud) even for development, bypassing Azurite.
- **REQ-003**: AI Model must be Google Gemini 3 Pro (`gemini-3-pro`) for Chat and Embeddings.
- **REQ-004**: Integration library must be `langchain-google-genai`.
- **SEC-001**: GCP API Keys must be stored in Azure Key Vault and referenced via Key Vault references.
- **INF-001**: GCP Project must be created and configured for Generative AI API usage.

## 2. Implementation Steps

### Implementation Phase 1: Cloud Provider Setup (GCP & Azure)

- GOAL-001: Configure Google Cloud Platform project and secure credentials in Azure Key Vault.

| Task     | Description                                                                 | Completed | Date |
| -------- | --------------------------------------------------------------------------- | --------- | ---- |
| TASK-001 | Create GCP Project `kaist-ai-agent` and enable "Google Generative AI API".  |           |      |
| TASK-002 | Generate GCP API Key for accessing Gemini models.                           |           |      |
| TASK-003 | Add secret `GOOGLE-API-KEY` to Azure Key Vault `kaist-kv-dev`.              |           |      |
| TASK-004 | Grant `Key Vault Secrets User` role to the Azure Function Managed Identity. |           |      |

### Implementation Phase 2: Project Scaffolding & Configuration

- GOAL-002: Initialize Azure Functions project structure and dependency management.

| Task     | Description                                                                                     | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-005 | Initialize `kaist-ai-functions` as Python V2 model Azure Functions project.                     |           |      |
| TASK-006 | Create `kaist-ai-functions/requirements.txt` with `azure-functions`, `langchain-google-genai`.  |           |      |
| TASK-007 | Configure `kaist-ai-functions/local.settings.json` to use Azure Storage connection string.      |           |      |
| TASK-008 | Set `GOOGLE_API_KEY` in Function App Settings to `@Microsoft.KeyVault(...)` reference.          |           |      |

### Implementation Phase 3: Core AI Integration

- GOAL-003: Implement Gemini 3 Pro integration for Chat and Embeddings using LangChain.

| Task     | Description                                                                                                   | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-009 | Implement `kaist-ai-functions/shared/llm.py`: Factory for `ChatGoogleGenerativeAI(model="gemini-3-pro")`.    |           |      |
| TASK-010 | Implement `kaist-ai-functions/shared/embeddings.py`: Factory for `GoogleGenerativeAIEmbeddings`.              |           |      |
| TASK-011 | Implement `kaist-ai-functions/function_app.py`: Basic HTTP trigger `/api/health` to verify LLM connectivity.  |           |      |

## 3. Alternatives

- **ALT-001**: Using `langchain-google-vertexai`. Rejected to reduce complexity of GCP Service Account management (`google-genai` uses simple API Key).
- **ALT-002**: Using Azurite for local storage. Rejected per requirements to use cloud storage directly.

## 4. Dependencies

- **DEP-001**: `langchain-google-genai` package for Gemini integration.
- **DEP-002**: Azure Key Vault resource provisioned in Infrastructure layer.
- **DEP-003**: Google Cloud Platform account with billing enabled.

## 5. Files

- **FILE-001**: `kaist-ai-functions/requirements.txt` - Python dependencies.
- **FILE-002**: `kaist-ai-functions/function_app.py` - Main function entry point.
- **FILE-003**: `kaist-ai-functions/shared/llm.py` - LLM client factory.
- **FILE-004**: `kaist-ai-functions/local.settings.json` - Local config (gitignored).

## 6. Testing

- **TEST-001**: Verify GCP API Key works by invoking a simple generation call locally.
- **TEST-002**: Verify Key Vault reference resolution in Azure Portal Configuration blade.
- **TEST-003**: Verify `pip install -r requirements.txt` succeeds without conflicts on Python 3.11.

## 7. Risks & Assumptions

- **RISK-001**: "Gemini 3 Pro" model name might differ (e.g., `gemini-3.0-pro`). Will need to verify exact model string upon release.
- **ASSUMPTION-001**: Azure Function App Identity has already been created or will be created during infra deployment.

## 8. Related Specifications / Further Reading

- [LangChain Google GenAI Integration](https://docs.langchain.com/oss/python/integrations/providers/google#google-generative-ai)
- [Azure Key Vault References for App Service](https://learn.microsoft.com/azure/app-service/app-service-key-vault-references)
