import json
import os
import smtplib
from email.message import EmailMessage

from agent.pending_email import PendingEmail, clear_pending, get_pending, set_pending


def draft_email(
    *,
    conversation_id: int,
    to: str,
    subject: str,
    body: str,
) -> str:
    email = PendingEmail(to=to.strip(), subject=subject.strip(), body=body.strip())
    set_pending(conversation_id, email)
    return json.dumps(
        {
            "status": "draft_saved",
            "preview": {
                "to": email.to,
                "subject": email.subject,
                "body": email.body,
            },
            "instruction": (
                "Présentez ce brouillon à l'utilisateur et demandez une confirmation explicite "
                "avant d'appeler send_pending_email avec user_confirmed=true."
            ),
        },
        ensure_ascii=False,
    )


def send_pending_email(*, conversation_id: int, user_confirmed: bool) -> str:
    if not user_confirmed:
        return json.dumps(
            {
                "error": "Envoi refusé : l'utilisateur n'a pas confirmé explicitement.",
            },
            ensure_ascii=False,
        )

    pending = get_pending(conversation_id)
    if not pending:
        return json.dumps(
            {"error": "Aucun brouillon en attente. Utilisez d'abord draft_email."},
            ensure_ascii=False,
        )

    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    from_addr = os.getenv("SMTP_FROM", user).strip()

    missing = [n for n, v in [("SMTP_HOST", host), ("SMTP_USER", user), ("SMTP_PASSWORD", password)] if not v]
    if missing:
        return json.dumps(
            {"error": f"Configuration SMTP incomplète : {', '.join(missing)}"},
            ensure_ascii=False,
        )

    message = EmailMessage()
    message["Subject"] = pending.subject
    message["From"] = from_addr
    message["To"] = pending.to
    message.set_content(pending.body)

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(message)
        clear_pending(conversation_id)
        return json.dumps({"status": "sent", "to": pending.to, "subject": pending.subject}, ensure_ascii=False)
    except smtplib.SMTPException as exc:
        return json.dumps({"error": f"Échec SMTP : {exc}"}, ensure_ascii=False)
