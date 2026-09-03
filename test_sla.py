from pprint import pprint

from jira.client import JiraClient


ISSUE_KEY = "CNI-164883"


def main():

    print()
    print("=" * 60)
    print(f"CONSULTANDO SLA: {ISSUE_KEY}")
    print("=" * 60)
    print()

    client = JiraClient()

    data = client.get_issue_sla(
        ISSUE_KEY
    )

    pprint(
        data,
        sort_dicts=False
    )


if __name__ == "__main__":
    main()