"""Génère un refresh token Google pour Calendar + Drive (usage local, une fois)."""

import os
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.tools.google_client import ALL_SCOPES

CLIENT_SECRETS = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "client_secret.json")


def main() -> None:
    if not os.path.isfile(CLIENT_SECRETS):
        raise SystemExit(
            f"Téléchargez les identifiants OAuth (type application de bureau) "
            f"depuis Google Cloud Console et enregistrez-les sous {CLIENT_SECRETS}."
        )

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, scopes=ALL_SCOPES)
    creds = flow.run_local_server(port=0)
    print("\nCollez dans .env :\n")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()
