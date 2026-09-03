from export.excel import export_excel

from jira.service import collect_issues

from services.reminder_service import (
    add_update_information,
    group_issues_by_assignee,
)

from teams.service import (
    build_reminder_message,
    send_test_reminders,
)


def main():

    print()
    print("=" * 60)
    print("      JIRA REMINDER AUTOMATION")
    print("=" * 60)
    print()

    # ==========================================
    # 1. CONSULTA DOS CHAMADOS NO JIRA
    # ==========================================

    print("Consultando chamados no Jira...")

    issues = collect_issues()

    # ==========================================
    # PROTECAO CONTRA RETORNO INESPERADO
    # ==========================================

    if not issues:

        print()
        print("=" * 60)
        print("EXECUCAO INTERROMPIDA")
        print("=" * 60)

        print()
        print("O Jira retornou 0 chamados.")

        print("Nenhuma mensagem sera enviada " "ao Teams.")

        print("Verifique a consulta do Jira " "antes de tentar novamente.")

        print()

        return

    print()
    print(f"Total recebido do Jira: " f"{len(issues)}")

    # ==========================================
    # 2. CALCULA TEMPO SEM ATUALIZACAO
    # ==========================================

    issues = add_update_information(issues)

    # ==========================================
    # 3. FILTRA CHAMADOS ELEGIVEIS
    # ==========================================

    issues_to_remind = [issue for issue in issues if issue["needs_reminder"]]

    # ==========================================
    # 4. AGRUPA POR RESPONSAVEL
    # ==========================================

    grouped_issues = group_issues_by_assignee(issues_to_remind)

    # ==========================================
    # 5. PREVIA DAS COBRANCAS
    # ==========================================

    print()
    print("=" * 60)
    print("PREVIA DAS COBRANCAS")
    print("=" * 60)

    print(f"\nChamados elegiveis: " f"{len(issues_to_remind)}")

    print(f"Responsaveis que receberiam mensagem: " f"{len(grouped_issues)}")

    for index, (
        assignee,
        assignee_issues,
    ) in enumerate(
        grouped_issues.items(),
        start=1,
    ):

        if index > 10:

            print()
            print("... demais responsaveis ocultados ...")

            break

        print()
        print("-" * 60)
        print(assignee)
        print("-" * 60)

        for issue in assignee_issues:

            print(
                f"{issue['key']} | "
                f"{issue['status']} | "
                f"{issue['days_without_update']} dias"
            )

    # ==========================================
    # 6. PREVIA DAS MENSAGENS
    # ==========================================

    print()
    print("=" * 60)
    print("PREVIA DAS MENSAGENS DO TEAMS")
    print("=" * 60)

    for index, (
        assignee,
        assignee_issues,
    ) in enumerate(
        grouped_issues.items(),
        start=1,
    ):

        if index > 3:

            print()
            print("... demais mensagens ocultadas ...")

            break

        message = build_reminder_message(
            assignee,
            assignee_issues,
        )

        print()
        print("-" * 60)

        print(f"DESTINATARIO ORIGINAL: " f"{assignee}")

        print("-" * 60)

        print(message)

    # ==========================================
    # 7. EXPORTACAO
    # ==========================================

    excel_path = export_excel(issues)

    print()
    print(f"Excel gerado em: " f"{excel_path}")

    # ==========================================
    # 8. ENVIO CONTROLADO
    # ==========================================

    print()
    print("=" * 60)
    print("INICIANDO TESTE CONTROLADO")
    print("=" * 60)

    send_test_reminders(grouped_issues)

    print()
    print("=" * 60)
    print("PROCESSAMENTO FINALIZADO")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
