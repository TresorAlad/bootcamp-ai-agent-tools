from dataclasses import dataclass


@dataclass
class PendingEmail:
    to: str
    subject: str
    body: str


_pending: dict[int, PendingEmail] = {}


def set_pending(conversation_id: int, email: PendingEmail) -> None:
    _pending[conversation_id] = email


def get_pending(conversation_id: int) -> PendingEmail | None:
    return _pending.get(conversation_id)


def clear_pending(conversation_id: int) -> None:
    _pending.pop(conversation_id, None)
