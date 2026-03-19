# kaist-ai-infra

This directory contains the Azure infrastructure-as-code for the KAIST PDF Knowledge Base Chatbot.

Quick commands

- Create environment and provision:

```bash
cd kaist-ai-infra
azd env new dev --location koreacentral
azd up --environment dev
```

- Tear down:

```bash
azd down --environment dev
```

Parameter files

- `.azure/dev.parameters.json` contains default parameters for `dev`.
- `.azure/dev/.env` is populated by `azd` with deployment outputs; use it for local testing values.

Diagnostics & Monitoring

- Application Insights and Log Analytics are provisioned as part of the deployment.
- To view logs and workbooks, open the Azure Portal and navigate to the created resources.

Notes

- Static Web App is deployed to `eastasia` because Static Web Apps are not available in `koreacentral`.
