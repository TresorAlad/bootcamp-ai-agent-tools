import json
from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from agent.runner import stream_agent_reply
from config import (
    NOTIFICATION_EVERY,
    NOTIFICATION_ROLE,
    NOTIFICATION_TEXT,
    load_system_prompt,
)
from conversation import build_llm_history, load_messages
from database.db import SessionLocal
from database.models import Message


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def stream_chat_reply(
    *,
    conversation_id: int,
    message: str,
    model: str,
    request: Request,
) -> AsyncIterator[str]:
    db = SessionLocal()
    try:
        rows = load_messages(db, conversation_id)
        history = build_llm_history(rows)
        next_seq = rows[-1].seq + 1 if rows else 1
        user_turn = {"role": "user", "content": message}
        llm_messages = [{"role": "system", "content": load_system_prompt()}, *history, user_turn]

        full_reply = ""
        usage: dict | None = None
        agent_finished = False

        async for chunk in stream_agent_reply(
            model=model,
            llm_messages=llm_messages,
            conversation_id=conversation_id,
            is_disconnected=request.is_disconnected,
        ):
            if await request.is_disconnected():
                return

            if chunk.startswith("data: "):
                try:
                    event = json.loads(chunk[6:].strip())
                except json.JSONDecodeError:
                    event = None

                if event:
                    if event.get("type") == "delta" and event.get("content"):
                        full_reply += event["content"]
                    if event.get("type") == "agent_complete":
                        usage = event.get("usage")
                        agent_finished = True
                        continue
                    if event.get("type") == "error":
                        yield chunk
                        return

            yield chunk

        if not agent_finished:
            return

        if await request.is_disconnected():
            return

        if not full_reply.strip():
            yield _sse({"type": "error", "detail": "Réponse vide du modèle."})
            return

        notification = None
        db.add(
            Message(conversation_id=conversation_id, seq=next_seq, role="user", content=message)
        )
        db.add(
            Message(
                conversation_id=conversation_id,
                seq=next_seq + 1,
                role="assistant",
                content=full_reply,
            )
        )

        if (len(history) + 2) % NOTIFICATION_EVERY == 0:
            notification = NOTIFICATION_TEXT
            db.add(
                Message(
                    conversation_id=conversation_id,
                    seq=next_seq + 2,
                    role=NOTIFICATION_ROLE,
                    content=notification,
                )
            )

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            yield _sse(
                {
                    "type": "error",
                    "detail": "La conversation a été modifiée en parallèle, réessayez.",
                }
            )
            return

        yield _sse({"type": "done", "notification": notification, "usage": usage})
    finally:
        db.close()


def persist_note(db: Session, conversation_id: int, content: str) -> Message:
    rows = load_messages(db, conversation_id)
    next_seq = rows[-1].seq + 1 if rows else 1
    note = Message(
        conversation_id=conversation_id,
        seq=next_seq,
        role="note",
        content=content,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
