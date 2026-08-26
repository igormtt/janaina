# Jira SLA Automation

Automação para consulta de chamados do Jira,
identificação de SLA e envio de lembretes
aos responsáveis pelo Microsoft Teams.

## Tecnologias

- Python
- Jira REST API
- Microsoft Graph API
- Pandas
- OpenPyXL
- MSAL

## Estrutura

```text
jira-sla-automation/
│
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── config.py
├── main.py
│
├── jira/
│   ├── __init__.py
│   ├── client.py
│   └── service.py
│
├── teams/
│   ├── __init__.py
│   └── service.py
│
├── export/
│   ├── __init__.py
│   └── excel.py
│
└── output/
```
