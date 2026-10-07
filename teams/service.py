import os
import html

import requests

from config import JIRA_BASE_URL
from jira.client import JiraClient


# ============================================================
# CONFIGURACOES
# ============================================================

POWER_AUTOMATE_URL = os.getenv(
    "POWER_AUTOMATE_URL"
)

TEST_MODE = (
    os.getenv(
        "TEST_MODE",
        "true",
    ).lower()
    == "true"
)

PRODUCTION_ENABLED = (
    os.getenv(
        "PRODUCTION_ENABLED",
        "false",
    ).lower()
    == "true"
)

PRODUCTION_ALLOW_ALL = (
    os.getenv(
        "PRODUCTION_ALLOW_ALL",
        "false",
    ).lower()
    == "true"
)

PRODUCTION_ALLOWLIST = {
    email.strip().lower()
    for email in os.getenv(
        "PRODUCTION_ALLOWLIST",
        "",
    ).split(",")
    if email.strip()
}

MAX_ISSUES_PER_MESSAGE = 15


# ============================================================
# DESTINATARIOS DE TESTE
# ============================================================

TEST_RECIPIENTS = {
    "Leandro Cesar De Aguiar Garcia":
        "t-igor.geraldo@cni.com.br",

    "Jessica Teles Da Costa":
        "t-janaina.lima@cni.com.br",

    "Greicy Kelly de Araujo Lima Damasceno":
        "t-danilo.rodrigues@cni.com.br",
}


ALLOWED_TEST_EMAILS = {
    "t-igor.geraldo@cni.com.br",
    "t-janaina.lima@cni.com.br",
    "t-danilo.rodrigues@cni.com.br",
}


# ============================================================
# VALIDACAO DA CONFIGURACAO
# ============================================================

def validate_execution_mode():

    if (
        TEST_MODE
        and PRODUCTION_ENABLED
    ):

        raise RuntimeError(
            "CONFIGURACAO INVALIDA: "
            "TEST_MODE e PRODUCTION_ENABLED "
            "nao podem estar ativos ao mesmo tempo."
        )

    if (
        PRODUCTION_ENABLED
        and PRODUCTION_ALLOW_ALL
        and PRODUCTION_ALLOWLIST
    ):

        raise RuntimeError(
            "CONFIGURACAO INVALIDA: "
            "PRODUCTION_ALLOW_ALL=true nao deve ser "
            "utilizado junto com PRODUCTION_ALLOWLIST."
        )

    if (
        PRODUCTION_ENABLED
        and not PRODUCTION_ALLOW_ALL
        and not PRODUCTION_ALLOWLIST
    ):

        raise RuntimeError(
            "PRODUCAO BLOQUEADA: "
            "nenhum destinatario foi autorizado "
            "na PRODUCTION_ALLOWLIST."
        )


def get_execution_mode() -> str:

    validate_execution_mode()

    if TEST_MODE:
        return "TEST"

    if PRODUCTION_ENABLED:
        return "PRODUCTION"

    return "DRY_RUN"


# ============================================================
# SEGURANCA DE PRODUCAO
# ============================================================

def is_production_recipient_allowed(
    recipient: str,
) -> bool:

    recipient = recipient.strip().lower()

    if PRODUCTION_ALLOW_ALL:
        return True

    return (
        recipient
        in PRODUCTION_ALLOWLIST
    )


# ============================================================
# DIVISAO DOS CHAMADOS
# ============================================================

def split_issues_into_chunks(
    issues: list[dict],
    chunk_size: int = MAX_ISSUES_PER_MESSAGE,
) -> list[list[dict]]:

    sorted_issues = sorted(
        issues,
        key=lambda issue: (
            issue.get(
                "days_without_update",
                0,
            )
        ),
        reverse=True,
    )

    return [
        sorted_issues[
            index:index + chunk_size
        ]
        for index in range(
            0,
            len(sorted_issues),
            chunk_size,
        )
    ]


# ============================================================
# GERACAO DA MENSAGEM HTML
# ============================================================

def build_reminder_message(
    assignee: str,
    issues: list[dict],
    test_mode: bool = False,
    part_number: int | None = None,
    total_parts: int | None = None,
) -> str:

    first_name = html.escape(
        assignee.split()[0]
    )

    safe_assignee = html.escape(
        assignee
    )

    sorted_issues = sorted(
        issues,
        key=lambda issue: (
            issue.get(
                "days_without_update",
                0,
            )
        ),
        reverse=True,
    )

    lines = []

    if test_mode:

        lines.extend([
            "<strong>🧪 [TESTE DE AUTOMAÇÃO]</strong>",
            "<br><br>",
            (
                "Esta mensagem é apenas um teste. "
                "Nenhuma cobrança está sendo "
                "direcionada a você."
            ),
            "<br><br>",
            (
                "Responsável original no Jira: "
                f"<strong>{safe_assignee}</strong>"
            ),
            "<br><br>",
            "<hr>",
        ])

    if (
        part_number is not None
        and total_parts is not None
        and total_parts > 1
    ):

        lines.extend([
            (
                "<strong>📋 Chamados pendentes "
                f"({part_number}/{total_parts})"
                "</strong>"
            ),
            "<br><br>",
        ])

    lines.extend([
        f"Olá, {first_name}! Tudo bem?",
        "<br><br>",
        (
            "Identificamos alguns chamados sob sua "
            "responsabilidade que estão há 3 dias ou mais "
            "sem atualização:"
        ),
        "<br><br>",
    ])

    for issue in sorted_issues:

        issue_key = html.escape(
            issue["key"]
        )

        days_without_update = issue.get(
            "days_without_update",
            0,
        )

        days = round(
            days_without_update
        )

        issue_url = (
            f"{JIRA_BASE_URL}/browse/"
            f"{issue_key}"
        )

        lines.append(
            "• "
            f'<a href="{issue_url}">'
            f"<strong>{issue_key}</strong>"
            "</a>"
            f" — {days} dias sem atualização"
        )

        lines.append(
            "<br><br>"
        )

    if (
        part_number is None
        or total_parts is None
        or part_number == total_parts
    ):

        lines.extend([
            (
                "Quando possível, poderia verificar "
                "os chamados e atualizar o andamento, "
                "por favor?"
            ),
            "<br><br>",
            "Obrigada! 😊",
        ])

    else:

        lines.append(
            "A lista continua na próxima mensagem."
        )

    return "".join(
        lines
    )


# ============================================================
# RESOLUCAO DO DESTINATARIO
# ============================================================

def resolve_assignee_email(
    client: JiraClient,
    assignee_name: str,
    issues: list[dict],
) -> str | None:

    if not issues:
        return None

    account_id = issues[0].get(
        "assignee_account_id"
    )

    if not account_id:
        return None

    try:

        user = client.get_user(
            account_id
        )

    except requests.RequestException:
        return None

    if not user.get(
        "active",
        False,
    ):
        return None

    email = user.get(
        "emailAddress"
    )

    if not email:
        return None

    return email.strip().lower()


# ============================================================
# ENVIO HTTP
# ============================================================

def post_to_power_automate(
    recipient: str,
    original_assignee: str,
    message: str,
    test_mode: bool,
):

    if not POWER_AUTOMATE_URL:

        raise RuntimeError(
            "POWER_AUTOMATE_URL nao configurada "
            "no .env"
        )

    recipient = (
        recipient.strip().lower()
    )

    if test_mode:

        if recipient not in ALLOWED_TEST_EMAILS:

            raise RuntimeError(
                "BLOQUEIO DE SEGURANCA: "
                f"{recipient} nao esta autorizado "
                "a receber mensagens de teste."
            )

    else:

        if not PRODUCTION_ENABLED:

            raise RuntimeError(
                "ENVIO DE PRODUCAO BLOQUEADO."
            )

        if not is_production_recipient_allowed(
            recipient
        ):

            raise RuntimeError(
                "BLOQUEIO DE PRODUCAO: "
                f"{recipient} nao esta autorizado "
                "pela PRODUCTION_ALLOWLIST."
            )

    payload = {
        "recipient": recipient,
        "original_assignee":
            original_assignee,
        "message": message,
        "test_mode": test_mode,
    }

    response = requests.post(
        POWER_AUTOMATE_URL,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.status_code


# ============================================================
# MODO TESTE
# ============================================================

def send_test_reminders(
    grouped_issues: dict[
        str,
        list[dict]
    ],
):

    validate_execution_mode()

    if get_execution_mode() != "TEST":

        raise RuntimeError(
            "send_test_reminders somente pode "
            "ser executado em TEST_MODE."
        )

    print()
    print("=" * 60)
    print("ENVIO DE TESTE PARA O TEAMS")
    print("=" * 60)

    total_sent = 0
    total_ignored = 0
    total_errors = 0

    for (
        original_assignee,
        test_email,
    ) in TEST_RECIPIENTS.items():

        issues = grouped_issues.get(
            original_assignee
        )

        if not issues:

            print()
            print(
                f"[IGNORADO] "
                f"Nenhum chamado elegivel para "
                f"{original_assignee}"
            )

            total_ignored += 1

            continue

        chunks = split_issues_into_chunks(
            issues
        )

        total_parts = len(
            chunks
        )

        for part_number, chunk in enumerate(
            chunks,
            start=1,
        ):

            message = build_reminder_message(
                original_assignee,
                chunk,
                test_mode=True,
                part_number=part_number,
                total_parts=total_parts,
            )

            print()
            print("-" * 60)

            print(
                f"Responsavel original: "
                f"{original_assignee}"
            )

            print(
                f"Destinatario do teste: "
                f"{test_email}"
            )

            print(
                f"Parte: "
                f"{part_number}/{total_parts}"
            )

            print(
                f"Chamados nesta mensagem: "
                f"{len(chunk)}"
            )

            try:

                status = post_to_power_automate(
                    recipient=test_email,
                    original_assignee=(
                        original_assignee
                    ),
                    message=message,
                    test_mode=True,
                )

                print(
                    f"Status: {status} - OK"
                )

                total_sent += 1

            except (
                requests.RequestException,
                RuntimeError,
            ) as error:

                print(
                    f"ERRO/BLOQUEIO: {error}"
                )

                total_errors += 1

    print()
    print("=" * 60)
    print("RESUMO DO ENVIO DE TESTE")
    print("=" * 60)

    print(
        f"Mensagens enviadas: "
        f"{total_sent}"
    )

    print(
        f"Responsaveis ignorados: "
        f"{total_ignored}"
    )

    print(
        f"Erros/bloqueios: "
        f"{total_errors}"
    )


# ============================================================
# DRY-RUN DE PRODUCAO
# ============================================================

def production_dry_run(
    grouped_issues: dict[
        str,
        list[dict]
    ],
):

    validate_execution_mode()

    if get_execution_mode() != "DRY_RUN":

        raise RuntimeError(
            "production_dry_run somente pode "
            "ser executado em DRY_RUN."
        )

    print()
    print("=" * 70)
    print("DRY-RUN DE PRODUCAO")
    print("=" * 70)

    print()
    print(
        "ATENCAO: nenhuma mensagem sera enviada."
    )

    client = JiraClient()

    resolved = 0
    unresolved = 0
    allowed = 0
    blocked = 0
    total_issues = 0
    total_messages = 0

    for index, (
        assignee,
        issues,
    ) in enumerate(
        grouped_issues.items(),
        start=1,
    ):

        email = resolve_assignee_email(
            client,
            assignee,
            issues,
        )

        chunks = split_issues_into_chunks(
            issues
        )

        print()
        print("-" * 70)

        print(
            f"[{index}/{len(grouped_issues)}] "
            f"{assignee}"
        )

        print(
            f"Chamados: {len(issues)}"
        )

        print(
            f"Mensagens necessarias: "
            f"{len(chunks)}"
        )

        total_issues += len(
            issues
        )

        if not email:

            print(
                "Destinatario: "
                "NAO RESOLVIDO"
            )

            print(
                "Resultado: NAO SERIA ENVIADO"
            )

            unresolved += 1

            continue

        resolved += 1

        print(
            f"Destinatario: {email}"
        )

        if is_production_recipient_allowed(
            email
        ):

            print(
                "Allowlist: AUTORIZADO"
            )

            print(
                "Resultado: PRONTO PARA ENVIO"
            )

            allowed += 1

            total_messages += len(
                chunks
            )

        else:

            print(
                "Allowlist: BLOQUEADO"
            )

            print(
                "Resultado: NAO SERIA ENVIADO"
            )

            blocked += 1

    print()
    print("=" * 70)
    print("RESUMO DO DRY-RUN")
    print("=" * 70)

    print(
        f"Responsaveis: "
        f"{len(grouped_issues)}"
    )

    print(
        f"Chamados envolvidos: "
        f"{total_issues}"
    )

    print(
        f"Destinatarios resolvidos: "
        f"{resolved}"
    )

    print(
        f"Destinatarios nao resolvidos: "
        f"{unresolved}"
    )

    print(
        f"Autorizados pela allowlist: "
        f"{allowed}"
    )

    print(
        f"Bloqueados pela allowlist: "
        f"{blocked}"
    )

    print(
        f"Mensagens que seriam enviadas: "
        f"{total_messages}"
    )

    print()
    print(
        "Mensagens realmente enviadas: 0"
    )

    print(
        "Power Automate acionado: NAO"
    )


# ============================================================
# PRODUCAO
# ============================================================

def send_production_reminders(
    grouped_issues: dict[
        str,
        list[dict]
    ],
):

    validate_execution_mode()

    if get_execution_mode() != "PRODUCTION":

        raise RuntimeError(
            "ENVIO DE PRODUCAO BLOQUEADO."
        )

    client = JiraClient()

    print()
    print("=" * 70)
    print("ENVIO DE PRODUCAO CONTROLADA")
    print("=" * 70)

    if PRODUCTION_ALLOW_ALL:

        print()
        print(
            "ATENCAO: PRODUCTION_ALLOW_ALL "
            "esta ativo."
        )

    else:

        print()
        print(
            "Allowlist de producao:"
        )

        for email in sorted(
            PRODUCTION_ALLOWLIST
        ):

            print(
                f"  - {email}"
            )

    total_sent = 0
    total_people_sent = 0
    total_blocked = 0
    total_skipped = 0
    total_errors = 0

    for assignee, issues in (
        grouped_issues.items()
    ):

        email = resolve_assignee_email(
            client,
            assignee,
            issues,
        )

        if not email:

            print()
            print(
                f"[IGNORADO] {assignee}: "
                f"destinatario nao resolvido."
            )

            total_skipped += 1

            continue

        if not is_production_recipient_allowed(
            email
        ):

            print()
            print(
                f"[BLOQUEADO] "
                f"{assignee} -> {email}"
            )

            total_blocked += 1

            continue

        chunks = split_issues_into_chunks(
            issues
        )

        total_parts = len(
            chunks
        )

        print()
        print("=" * 70)

        print(
            f"[AUTORIZADO] "
            f"{assignee} -> {email}"
        )

        print(
            f"Chamados: {len(issues)}"
        )

        print(
            f"Mensagens: {total_parts}"
        )

        person_sent = False

        for part_number, chunk in enumerate(
            chunks,
            start=1,
        ):

            message = build_reminder_message(
                assignee,
                chunk,
                test_mode=False,
                part_number=part_number,
                total_parts=total_parts,
            )

            print()
            print(
                f"Enviando parte "
                f"{part_number}/{total_parts}..."
            )

            try:

                status = post_to_power_automate(
                    recipient=email,
                    original_assignee=assignee,
                    message=message,
                    test_mode=False,
                )

                print(
                    f"Status: {status} - OK"
                )

                total_sent += 1
                person_sent = True

            except (
                requests.RequestException,
                RuntimeError,
            ) as error:

                print(
                    f"ERRO/BLOQUEIO: {error}"
                )

                total_errors += 1

                break

        if person_sent:
            total_people_sent += 1

    print()
    print("=" * 70)
    print("RESUMO DA PRODUCAO")
    print("=" * 70)

    print(
        f"Responsaveis que receberam: "
        f"{total_people_sent}"
    )

    print(
        f"Mensagens enviadas: "
        f"{total_sent}"
    )

    print(
        f"Responsaveis bloqueados: "
        f"{total_blocked}"
    )

    print(
        f"Destinatarios ignorados: "
        f"{total_skipped}"
    )

    print(
        f"Erros: "
        f"{total_errors}"
    )