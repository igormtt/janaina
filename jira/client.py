import requests

from config import (
    JIRA_API_TOKEN,
    JIRA_BASE_URL,
    JIRA_EMAIL,
)


class JiraClient:
    def __init__(self):
        if not JIRA_BASE_URL:
            raise RuntimeError(
                "JIRA_BASE_URL nao foi configurado."
            )

        if not JIRA_EMAIL:
            raise RuntimeError(
                "JIRA_EMAIL nao foi configurado."
            )

        if not JIRA_API_TOKEN:
            raise RuntimeError(
                "JIRA_API_TOKEN nao foi configurado."
            )

        self.session = requests.Session()

        self.session.auth = (
            JIRA_EMAIL,
            JIRA_API_TOKEN,
        )

        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def search_issues(
        self,
        jql: str,
        fields: list[str],
    ) -> dict:

        url = (
            f"{JIRA_BASE_URL}"
            "/rest/api/3/search/jql"
        )

        payload = {
            "jql": jql,
            "maxResults": 100,
            "fields": fields,
        }

        response = self.session.post(
            url,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_fields(self) -> list:
        """
        Retorna todos os campos disponíveis
        na instância do Jira.
        """

        url = (
            f"{JIRA_BASE_URL}"
            "/rest/api/3/field"
        )

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

        url = (
            f"{JIRA_BASE_URL}"
            f"/rest/api/3/issue/{issue_key}"
        )

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