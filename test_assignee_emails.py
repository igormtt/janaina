from jira.client import JiraClient
from jira.service import collect_issues

from config import JIRA_BASE_URL

from services.reminder_service import (
    add_update_information,
    group_issues_by_assignee,
)


def get_user_email(
    client: JiraClient,
    account_id: str,
) -> dict:

    url = f"{JIRA_BASE_URL}" "/rest/api/3/user"

    response = client.session.get(
        url,
        params={
            "accountId": account_id,
        },
        timeout=30,
    )

    if response.status_code != 200:

        return {
            "success": False,
            "status": response.status_code,
            "email": None,
        }

    data = response.json()

    return {
        "success": True,
        "status": response.status_code,
        "email": data.get("emailAddress"),
        "display_name": data.get("displayName"),
        "active": data.get("active"),
    }


def main():

    print()
    print("=" * 70)
    print("DRY-RUN - RESOLUCAO DE E-MAILS DOS RESPONSAVEIS")
    print("=" * 70)
    print()

    # ========================================================
    # COLETA OS CHAMADOS
    # ========================================================

    print("Consultando chamados no Jira...")

    issues = collect_issues()

    if not issues:

        print()
        print("Nenhum chamado retornado pelo Jira.")

        print("Execucao interrompida.")

        return

    print()
    print(f"Total recebido do Jira: " f"{len(issues)}")

    # ========================================================
    # APLICA REGRA DOS 3 DIAS
    # ========================================================

    issues = add_update_information(issues)

    grouped_issues = group_issues_by_assignee(issues)

    print(f"Responsaveis elegiveis: " f"{len(grouped_issues)}")

    print()

    # ========================================================
    # CLIENTE JIRA
    # ========================================================

    client = JiraClient()

    users_with_email = []
    users_without_email = []
    users_with_error = []

    # ========================================================
    # CONSULTA CADA RESPONSAVEL
    # ========================================================

    total_assignees = len(grouped_issues)

    for index, (
        assignee_name,
        assignee_issues,
    ) in enumerate(
        grouped_issues.items(),
        start=1,
    ):

        first_issue = assignee_issues[0]

        account_id = first_issue.get("assignee_account_id")

        print(f"[{index}/{total_assignees}] " f"{assignee_name}")

        if not account_id:

            print("    Account ID: NAO ENCONTRADO")

            print("    E-mail: NAO ENCONTRADO")

            users_without_email.append(
                {
                    "name": assignee_name,
                    "account_id": None,
                    "email": None,
                    "issues": len(assignee_issues),
                }
            )

            print()

            continue

        result = get_user_email(
            client,
            account_id,
        )

        if not result["success"]:

            print(f"    Account ID: {account_id}")

            print(f"    HTTP: {result['status']}")

            print("    E-mail: ERRO NA CONSULTA")

            users_with_error.append(
                {
                    "name": assignee_name,
                    "account_id": account_id,
                    "status": result["status"],
                    "issues": len(assignee_issues),
                }
            )

            print()

            continue

        email = result.get("email")

        print(f"    Account ID: {account_id}")

        print(f"    Ativo: {result.get('active')}")

        if email:

            print(f"    E-mail: {email}")

            users_with_email.append(
                {
                    "name": assignee_name,
                    "account_id": account_id,
                    "email": email,
                    "issues": len(assignee_issues),
                }
            )

        else:

            print("    E-mail: OCULTO/INDISPONIVEL")

            users_without_email.append(
                {
                    "name": assignee_name,
                    "account_id": account_id,
                    "email": None,
                    "issues": len(assignee_issues),
                }
            )

        print()

    # ========================================================
    # RESUMO
    # ========================================================

    print()
    print("=" * 70)
    print("RESUMO")
    print("=" * 70)

    print(f"Responsaveis analisados: " f"{len(grouped_issues)}")

    print(f"E-mails encontrados: " f"{len(users_with_email)}")

    print(f"E-mails indisponiveis: " f"{len(users_without_email)}")

    print(f"Erros de API: " f"{len(users_with_error)}")

    # ========================================================
    # LISTA DOS E-MAILS ENCONTRADOS
    # ========================================================

    print()
    print("=" * 70)
    print("DESTINATARIOS ENCONTRADOS")
    print("=" * 70)

    if users_with_email:

        for user in users_with_email:

            print(
                f"{user['name']} "
                f"-> {user['email']} "
                f"-> {user['issues']} chamado(s)"
            )

    else:

        print("Nenhum e-mail foi encontrado.")

    # ========================================================
    # E-MAILS NAO ENCONTRADOS
    # ========================================================

    if users_without_email:

        print()
        print("=" * 70)
        print("E-MAILS NAO ENCONTRADOS")
        print("=" * 70)

        for user in users_without_email:

            print(f"{user['name']} " f"-> {user['issues']} chamado(s)")

    # ========================================================
    # ERROS
    # ========================================================

    if users_with_error:

        print()
        print("=" * 70)
        print("ERROS DE API")
        print("=" * 70)

        for user in users_with_error:

            print(f"{user['name']} " f"-> HTTP {user['status']}")

    print()
    print("=" * 70)
    print("DRY-RUN FINALIZADO")
    print("=" * 70)

    print()
    print("Nenhuma mensagem foi enviada ao Teams.")


if __name__ == "__main__":
    main()
