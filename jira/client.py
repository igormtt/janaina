import requests

from config import (
    JIRA_API_TOKEN,
    JIRA_BASE_URL,
    JIRA_EMAIL,
)


class JiraClient:

    def __init__(self):

        if not JIRA_BASE_URL:
            raise RuntimeError("JIRA_BASE_URL nao foi configurado.")

        if not JIRA_EMAIL:
            raise RuntimeError("JIRA_EMAIL nao foi configurado.")

        if not JIRA_API_TOKEN:
            raise RuntimeError("JIRA_API_TOKEN nao foi configurado.")

        self.session = requests.Session()

        self.session.auth = (
            JIRA_EMAIL,
            JIRA_API_TOKEN,
        )

        self.session.headers.update(
            {
                "Accept": "application/json",
            }
        )

    def search_issues(
        self,
        jql: str,
        fields: list[str],
    ) -> list[dict]:

        url = f"{JIRA_BASE_URL}" "/rest/api/3/search/jql"

        all_issues = []
        next_page_token = None

        while True:

            params = {
                "jql": jql,
                "maxResults": 100,
                "fields": ",".join(fields),
            }

            if next_page_token:
                params["nextPageToken"] = next_page_token

            response = self.session.get(
                url,
                params=params,
                timeout=60,
            )

            print(f"HTTP Jira: " f"{response.status_code}")

            response.raise_for_status()

            data = response.json()

            issues = data.get("issues", [])

            all_issues.extend(issues)

            next_page_token = data.get("nextPageToken")

            is_last = data.get(
                "isLast",
                False,
            )

            print(
                f"Pagina recebida: "
                f"{len(issues)} chamados | "
                f"Total: {len(all_issues)}"
            )

            if not issues and not all_issues:

                print()
                print("=" * 60)
                print("RESPOSTA COMPLETA DO JIRA")
                print("=" * 60)
                print(data)
                print("=" * 60)
                print()

            if is_last:
                break

            if not next_page_token:
                break

        return all_issues

    def get_fields(
        self,
    ) -> list:

        url = f"{JIRA_BASE_URL}" "/rest/api/3/field"

        response = self.session.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_issue(
        self,
        issue_key: str,
        fields: list[str] | None = None,
    ) -> dict:

        url = f"{JIRA_BASE_URL}" f"/rest/api/3/issue/{issue_key}"

        params = {}

        if fields:
            params["fields"] = ",".join(fields)

        response = self.session.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_issue_sla(
        self,
        issue_key: str,
    ) -> dict:

        url = f"{JIRA_BASE_URL}" "/rest/servicedeskapi/request/" f"{issue_key}/sla"

        response = self.session.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()
