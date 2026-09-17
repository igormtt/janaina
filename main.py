from export.excel import export_excel

from jira.service import collect_issues

from services.reminder_service import (
    add_update_information,
    group_issues_by_assignee,
)

from teams.service import (
    PRODUCTION_ALLOWLIST,
    PRODUCTION_ALLOW_ALL,
    build_reminder_message,
    get_execution_mode,
    production_dry_run,
    send_production_reminders,
    send_test_reminders,
    validate_execution_mode,
)


def main():

    print()
    print("=" * 60)
    print("      JIRA REMINDER AUTOMATION")
    print("=" * 60)

    # ========================================================
    # VERIFICA O MODO
    # ========================================================

    try:

        validate_execution_mode()

        execution_mode = get_execution_mode()

    except RuntimeError as error:

        print()
        print(f"EXECUCAO BLOQUEADA: {error}")

        return

    print()
    print(f"Modo de execucao: " f"{execution_mode}")

    # ========================================================
    # INFORMACOES DE SEGURANCA
    # ========================================================

    if execution_mode in {
        "DRY_RUN",
        "PRODUCTION",
    }:

        print()

        if PRODUCTION_ALLOW_ALL:

            print("Allowlist: TODOS AUTORIZADOS")

        elif PRODUCTION_ALLOWLIST:

            print("Allowlist de producao:")

            for email in sorted(PRODUCTION_ALLOWLIST):

                print(f"  - {email}")

        else:

            print("Allowlist de producao: VAZIA")

    # ========================================================
    # CONSULTA JIRA
    # ========================================================

    print()
    print("Consultando chamados no Jira...")

    issues = collect_issues()

    if not issues:

        print()
        print("Nenhum chamado foi retornado " "pelo Jira.")

        print("Execucao interrompida por seguranca.")

        print("Nenhuma mensagem foi enviada.")

        return

    print()
    print(f"Total recebido do Jira: " f"{len(issues)}")

    # ========================================================
    # REGRA DOS 3 DIAS
    # ========================================================

    issues = add_update_information(issues)

    reminder_issues = [issue for issue in issues if issue.get("needs_reminder")]

    grouped_issues = group_issues_by_assignee(issues)

    print()
    print("=" * 60)
    print("RESUMO DO PROCESSAMENTO")
    print("=" * 60)

    print(f"Chamados elegiveis: " f"{len(reminder_issues)}")

    print(f"Responsaveis: " f"{len(grouped_issues)}")

    if not grouped_issues:

        print()
        print("Nenhum responsavel possui " "chamados elegiveis.")

        print("Nenhuma mensagem foi enviada.")

        return

    # ========================================================
    # PREVIA
    # ========================================================

    print()
    print("=" * 60)
    print("PREVIA DAS COBRANCAS")
    print("=" * 60)

    for index, (
        assignee,
        assignee_issues,
    ) in enumerate(grouped_issues.items()):

        if index >= 10:

            print()
            print("... demais responsaveis " "ocultados ...")

            break

        print()
        print("-" * 60)
        print(assignee)
        print("-" * 60)

        sorted_issues = sorted(
            assignee_issues,
            key=lambda issue: (
                issue.get(
                    "days_without_update",
                    0,
                )
            ),
            reverse=True,
        )

        for issue in sorted_issues:

            print(
                f"{issue['key']} | "
                f"{issue['status']} | "
                f"{issue['days_without_update']} "
                f"dias"
            )

    # ========================================================
    # PREVIA DAS MENSAGENS
    # ========================================================

    print()
    print("=" * 60)
    print("PREVIA DAS MENSAGENS DO TEAMS")
    print("=" * 60)

    for index, (
        assignee,
        assignee_issues,
    ) in enumerate(grouped_issues.items()):

        if index >= 3:

            print()
            print("... demais mensagens " "ocultadas ...")

            break

        print()
        print("-" * 60)

        print(f"DESTINATARIO ORIGINAL: " f"{assignee}")

        print("-" * 60)

        message = build_reminder_message(
            assignee,
            assignee_issues,
            test_mode=(execution_mode == "TEST"),
        )

        print(message)

    # ========================================================
    # EXPORTA EXCEL
    # ========================================================

    export_excel(reminder_issues)

    # ========================================================
    # EXECUCAO
    # ========================================================

    print()
    print("=" * 60)
    print(f"MODO SELECIONADO: " f"{execution_mode}")
    print("=" * 60)

    if execution_mode == "TEST":

        send_test_reminders(grouped_issues)

    elif execution_mode == "DRY_RUN":

        production_dry_run(grouped_issues)

    elif execution_mode == "PRODUCTION":

        send_production_reminders(grouped_issues)

    print()
    print("=" * 60)
    print("PROCESSAMENTO FINALIZADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
