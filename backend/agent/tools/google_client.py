import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
ALL_SCOPES = CALENDAR_SCOPES + DRIVE_SCOPES


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Variable d'environnement manquante : {name}")
    return value


def get_google_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=_require("GOOGLE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=_require("GOOGLE_CLIENT_ID"),
        client_secret=_require("GOOGLE_CLIENT_SECRET"),
        scopes=ALL_SCOPES,
    )
    creds.refresh(Request())
    return creds
