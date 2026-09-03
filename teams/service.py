import os

import requests

from config import JIRA_BASE_URL

POWER_AUTOMATE_URL = os.getenv("POWER_AUTOMATE_URL")

TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"


TEST_RECIPIENTS = {
    "Leandro Cesar De Aguiar Garcia": "t-igor.geraldo@cni.com.br",
    "Jessica Teles Da Costa": "t-janaina.lima@cni.com.br",
    "Greicy Kelly de Araujo Lima Damasceno": "t-danilo.rodrigues@cni.com.br",
}


ALLOWED_TEST_EMAILS = {
    "t-igor.geraldo@cni.com.br",
    "t-janaina.lima@cni.com.br",
    "t-danilo.rodrigues@cni.com.br",
}


def build_reminder_message(
    assignee: str,
    issues: list[dict],
) -> str:

    first_name = assignee.split()[0]

    lines = [
        f"Olá, {first_name}! Tudo bem?",
        "",
        (
            "Identificamos alguns chamados sob sua "
            "responsabilidade que estão há 3 dias ou mais "
            "sem atualização:"
        ),
        "",
    ]

    for issue in issues:

        issue_key = issue["key"]

        days = int(
            issue.get(
                "days_without_update",
                0,
            )
        )

        issue_url = f"{JIRA_BASE_URL}/browse/{issue_key}"

        lines.append(f"• {issue_key} — " f"{days} dias sem atualização")

        lines.append(f"  {issue_url}")

        lines.append("")

    lines.extend(
        [
            (
                "Quando possível, poderia verificar os chamados "
                "e atualizar o andamento, por favor?"
            ),
            "",
            "Obrigado! 😊",
        ]
    )

    return "\n".join(lines)


def send_power_automate_message(
    recipient: str,
    original_assignee: str,
    message: str,
):

    if not POWER_AUTOMATE_URL:
        raise RuntimeError("POWER_AUTOMATE_URL nao configurada no .env")

    if TEST_MODE:

        if recipient not in ALLOWED_TEST_EMAILS:
            raise RuntimeError(
                f"Bloqueio de seguranca: "
                f"{recipient} nao esta autorizado "
                f"no modo de teste."
            )

    payload = {
        "recipient": recipient,
        "original_assignee": original_assignee,
        "message": message,
    }

    response = requests.post(
        POWER_AUTOMATE_URL,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.status_code


def send_test_reminders(
    grouped_issues: dict[str, list[dict]],
):

    print()
    print("=" * 60)
    print("ENVIO DE TESTE PARA O TEAMS")
    print("=" * 60)

    for (
        original_assignee,
        test_email,
    ) in TEST_RECIPIENTS.items():

        issues = grouped_issues.get(original_assignee)

        if not issues:

            print()
            print(
                f"[IGNORADO] " f"Nenhum chamado elegivel para " f"{original_assignee}"
            )

            continue

        message = build_reminder_message(
            original_assignee,
            issues,
        )

        print()
        print(f"Simulando: " f"{original_assignee}")

        print(f"Enviando para: " f"{test_email}")

        try:

            status = send_power_automate_message(
                recipient=test_email,
                original_assignee=original_assignee,
                message=message,
            )

            print(f"Status: {status} - OK")

        except requests.RequestException as error:

            print(f"ERRO ao enviar: " f"{error}")

        except RuntimeError as error:

            print(f"BLOQUEADO: " f"{error}")
