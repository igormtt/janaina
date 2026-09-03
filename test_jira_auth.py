import requests

from config import (
    JIRA_API_TOKEN,
    JIRA_BASE_URL,
    JIRA_EMAIL,
)


def main():

    print()
    print("=" * 60)
    print("TESTE DE AUTENTICACAO JIRA")
    print("=" * 60)
    print()

    if not JIRA_BASE_URL:
        raise RuntimeError("JIRA_BASE_URL nao configurado.")

    if not JIRA_EMAIL:
        raise RuntimeError("JIRA_EMAIL nao configurado.")

    if not JIRA_API_TOKEN:
        raise RuntimeError("JIRA_API_TOKEN nao configurado.")

    session = requests.Session()

    session.auth = (
        JIRA_EMAIL,
        JIRA_API_TOKEN,
    )

    session.headers.update(
        {
            "Accept": "application/json",
        }
    )

    # ==========================================
    # TESTE 1 - USUARIO AUTENTICADO
    # ==========================================

    print("Teste 1 - /rest/api/3/myself")
    print("-" * 60)

    myself_url = f"{JIRA_BASE_URL}" "/rest/api/3/myself"

    response = session.get(
        myself_url,
        timeout=30,
    )

    print(f"HTTP: {response.status_code}")

    try:

        data = response.json()

        if response.status_code == 200:

            print("AUTENTICACAO: OK")

            print(f"Nome: " f"{data.get('displayName')}")

            print(f"Account ID: " f"{data.get('accountId')}")

            print(f"Ativo: " f"{data.get('active')}")

        else:

            print("AUTENTICACAO: FALHOU")

            print(f"Resposta: {data}")

    except ValueError:

        print(f"Resposta: " f"{response.text}")

    print()

    # ==========================================
    # TESTE 2 - ACESSO AO PROJETO CNI
    # ==========================================

    print("Teste 2 - Projeto CNI")
    print("-" * 60)

    project_url = f"{JIRA_BASE_URL}" "/rest/api/3/project/CNI"

    response = session.get(
        project_url,
        timeout=30,
    )

    print(f"HTTP: {response.status_code}")

    try:

        data = response.json()

        if response.status_code == 200:

            print("ACESSO AO PROJETO: OK")

            print(f"Projeto: " f"{data.get('name')}")

            print(f"Chave: " f"{data.get('key')}")

        else:

            print("ACESSO AO PROJETO: FALHOU")

            print(f"Resposta: {data}")

    except ValueError:

        print(f"Resposta: " f"{response.text}")

    print()

    # ==========================================
    # TESTE 3 - BUSCA JQL SIMPLES
    # ==========================================

    print("Teste 3 - JQL simples")
    print("-" * 60)

    search_url = f"{JIRA_BASE_URL}" "/rest/api/3/search/jql"

    payload = {
        "jql": "project = CNI",
        "maxResults": 5,
        "fields": [
            "summary",
            "status",
        ],
    }

    response = session.post(
        search_url,
        json=payload,
        timeout=30,
    )

    print(f"HTTP: {response.status_code}")

    try:

        data = response.json()

        issues = data.get("issues", [])

        print(f"Chamados retornados: " f"{len(issues)}")

        for issue in issues:

            print(f"- {issue.get('key')}")

        if not issues:

            print(f"Resposta completa: " f"{data}")

    except ValueError:

        print(f"Resposta: " f"{response.text}")

    print()
    print("=" * 60)
    print("FIM DO TESTE")
    print("=" * 60)


if __name__ == "__main__":
    main()
