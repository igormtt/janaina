from collections import defaultdict
from datetime import datetime


REMINDER_INTERVAL_DAYS = 3


IGNORED_ASSIGNEES = {
    "ScriptRunner for Jira",
    "3layer Gestão Compartilhada",
}


def group_issues_by_assignee(
    issues: list[dict],
) -> dict[str, list[dict]]:

    grouped = defaultdict(list)

    for issue in issues:

        if not issue.get("needs_reminder"):
            continue

        assignee = issue.get("assignee_name")

        if not assignee:
            continue

        if assignee in IGNORED_ASSIGNEES:
            continue

        grouped[assignee].append(issue)

    return dict(grouped)


def parse_jira_datetime(
    value: str,
) -> datetime:

    return datetime.strptime(
        value,
        "%Y-%m-%dT%H:%M:%S.%f%z",
    )


def get_days_without_update(
    updated: str,
) -> float:

    updated_at = parse_jira_datetime(
        updated
    )

    now = datetime.now(
        updated_at.tzinfo
    )

    difference = (
        now - updated_at
    )

    return (
        difference.total_seconds()
        / 86400
    )


def should_remind(
    issue: dict,
) -> bool:

    updated = issue.get(
        "updated"
    )

    assignee_name = issue.get(
        "assignee_name"
    )

    if not updated:
        return False

    if not assignee_name:
        return False

    if assignee_name in IGNORED_ASSIGNEES:
        return False

    days = get_days_without_update(
        updated
    )

    return (
        days >= REMINDER_INTERVAL_DAYS
    )


def add_update_information(
    issues: list[dict],
) -> list[dict]:

    result = []

    for issue in issues:

        updated = issue.get(
            "updated"
        )

        if updated:

            days = get_days_without_update(
                updated
            )

            issue[
                "days_without_update"
            ] = round(
                days,
                1,
            )

        else:

            issue[
                "days_without_update"
            ] = None

        issue[
            "needs_reminder"
        ] = should_remind(
            issue
        )

        result.append(
            issue
        )

    return result