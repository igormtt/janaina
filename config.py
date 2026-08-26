import os

from dotenv import load_dotenv


load_dotenv()


# ==========================================
# JIRA
# ==========================================

JIRA_BASE_URL = os.getenv(
    "JIRA_BASE_URL",
    ""
).rstrip("/")

JIRA_EMAIL = os.getenv(
    "JIRA_EMAIL",
    ""
)

JIRA_API_TOKEN = os.getenv(
    "JIRA_API_TOKEN",
    "")


# ==========================================
# MICROSOFT / TEAMS
# ==========================================

MS_TENANT_ID = os.getenv(
    "MS_TENANT_ID",
    ""
)

MS_CLIENT_ID = os.getenv(
    "MS_CLIENT_ID",
    ""
)

MS_CLIENT_SECRET = os.getenv(
    "MS_CLIENT_SECRET",
    "")


# ==========================================
# AUTOMACAO
# ==========================================

DRY_RUN = os.getenv(
    "DRY_RUN",
    "true"
).lower() == "true"

SLA_WARNING_MINUTES = int(
    os.getenv(
        "SLA_WARNING_MINUTES",
        "180"
    )
)

REMINDER_COOLDOWN_HOURS = int(
    os.getenv(
        "REMINDER_COOLDOWN_HOURS",
        "4"
    )
)