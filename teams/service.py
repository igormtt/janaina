def build_reminder_message(
    issues: list[dict],
) -> str:

    lines = [
        "Olá! Tudo bem?",
        "",
        "Passando para lembrar dos chamados "
        "abaixo que estão sob sua responsabilidade:",
        "",
    ]

    for issue in issues:

        sla = issue.get(
            "sla",
            "não identificado",
        )

        lines.append(
            f"• {issue['key']} "
            f"— SLA: {sla}"
        )

    lines.extend([
        "",
        "Quando possível, poderia verificar "
        "o andamento deles, por favor?",
        "",
        "Obrigado! 😊",
    ])

    return "\n".join(lines)