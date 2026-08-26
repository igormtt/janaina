from export.excel import export_excel
from jira.service import collect_issues


def main():

    print()
    print("=" * 60)
    print("      JIRA SLA AUTOMATION")
    print("=" * 60)
    print()

    print(
        "Consultando chamados no Jira..."
    )

    issues = collect_issues()

    print()
    print(
        f"Chamados encontrados: {len(issues)}"
    )

    print()

    for issue in issues[:10]:

        print(
            f"{issue['key']} | "
            f"{issue['status']} | "
            f"{issue['assignee_name']}"
        )

    print()

    output = export_excel(
        issues
    )

    print(
        f"Excel gerado em: {output}"
    )

    print()


if __name__ == "__main__":
    main()