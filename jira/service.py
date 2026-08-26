from jira.client import JiraClient


JQL = """
project IN (CNI, CDAU)
AND status IN (
    Aberto,
    Agendado,
    "Aguardando Aprovação",
    "Aguardando Aprovação Aplicação",
    "Aguardando Aprovação Banco de Dados",
    "Aguardando Aprovação Cibersegurança",
    "Aguardando Aprovação Demandante",
    "Aguardando Aprovação Do Demandante",
    "Aguardando Aprovação do Negócio",
    "Aguardando Aprovação Infraestrutura",
    "Aguardando Aprovação Inicial",
    "Aguardando Cliente",
    "Aguardando Fornecedor",
    "Aguardando Reunião De Estratégia",
    Aprovado,
    Briefing,
    Discovery,
    "Em Análise",
    "Em Atendimento",
    "Em Desenvolvimento",
    "Em Execução",
    "EM EXECUÇÃO N3",
    "Em Execução NOC",
    "Em Homologação",
    Encaminhado,
    "Encaminhado N1/N2",
    "ENCAMINHADO N3",
    "Encaminhado NOC",
    "Entrega e Documentação",
    "Escritório De Projetos",
    Ideação,
    "Projeto Em Execução",
    Prototipagem,
    "Aberto N3",
    "Aberto N1/N2",
    "Aberto NOC"
)
AND statusCategory != done
ORDER BY "cf[10599]" DESC, created ASC, updated ASC
""".strip()


def collect_issues():

    client = JiraClient()

    fields = [
        "summary",
        "status",
        "assignee",
    ]

    response = client.search_issues(
        jql=JQL,
        fields=fields,
    )

    issues = []

    for issue in response.get(
        "issues",
        []
    ):

        fields = issue.get(
            "fields",
            {}
        )

        status = fields.get(
            "status"
        ) or {}

        assignee = fields.get(
            "assignee"
        ) or {}

        issues.append({
            "key": issue.get(
                "key"
            ),

            "summary": fields.get(
                "summary"
            ),

            "status": status.get(
                "name"
            ),

            "assignee_name": assignee.get(
                "displayName"
            ),

            "assignee_account_id": assignee.get(
                "accountId"
            ),
        })

    return issues