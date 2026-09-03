import requests

from config import (
    JIRA_API_TOKEN,
    JIRA_BASE_URL,
    JIRA_EMAIL,
)

SIMPLE_JQL = """
project IN (CNI, CDAU)
""".strip()


FULL_JQL = """
project IN (CNI, CDAU)
and status IN (
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
and statusCategory != done
ORDER BY "cf[10599]" DESC, created ASC, updated ASC
""".strip()


def create_session():

    session = requests.Session()

    session.auth = (
        JIRA_EMAIL,
        JIRA_API_TOKEN,
    )

    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )

    return session


def test_count(
    session: requests.Session,
    name: str,
    jql: str,
):

    url = f"{JIRA_BASE_URL}" "/rest/api/3/search/approximate-count"

    response = session.post(
        url,
        json={
            "jql": jql,
        },
        timeout=60,
    )

    print()
    print("=" * 60)
    print(f"COUNT - {name}")
    print("=" * 60)

    print(f"HTTP: {response.status_code}")

    print(f"Resposta: {response.text}")


def test_search(
    session: requests.Session,
    name: str,
    jql: str,
):

    url = f"{JIRA_BASE_URL}" "/rest/api/3/search/jql"

    response = session.post(
        url,
        json={
            "jql": jql,
            "maxResults": 5,
            "fields": [
                "summary",
                "status",
            ],
        },
        timeout=60,
    )

    print()
    print("=" * 60)
    print(f"SEARCH - {name}")
    print("=" * 60)

    print(f"HTTP: {response.status_code}")

    try:

        data = response.json()

        issues = data.get("issues", [])

        print(f"Chamados retornados: " f"{len(issues)}")

        print(f"isLast: " f"{data.get('isLast')}")

        print(f"nextPageToken: " f"{data.get('nextPageToken')}")

        for issue in issues:

            print(f"- {issue.get('key')}")

        if not issues:

            print(f"Resposta completa: " f"{data}")

    except ValueError:

        print(f"Resposta: " f"{response.text}")


def main():

    print()
    print("=" * 60)
    print("DIAGNOSTICO JQL")
    print("=" * 60)

    session = create_session()

    test_count(
        session,
        "JQL SIMPLES",
        SIMPLE_JQL,
    )

    test_search(
        session,
        "JQL SIMPLES",
        SIMPLE_JQL,
    )

    test_count(
        session,
        "JQL COMPLETO",
        FULL_JQL,
    )

    test_search(
        session,
        "JQL COMPLETO",
        FULL_JQL,
    )


if __name__ == "__main__":
    main()
