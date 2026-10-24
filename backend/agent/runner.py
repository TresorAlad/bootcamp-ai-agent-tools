import json
from collections.abc import AsyncIterator, Awaitable, Callable

from agent.llm import chat_completion, extract_assistant_message, parse_tool_arguments
from agent.tools.execute import execute_tool
from agent.tools.schemas import TOOL_DEFINITIONS

MAX_TOOL_ROUNDS = 8


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def stream_agent_reply(
    *,
    model: str,
    llm_messages: list[dict],
    conversation_id: int,
    is_disconnected: Callable[[], Awaitable[bool]] | None = None,
) -> AsyncIterator[str]:
    working = list(llm_messages)
    usage: dict | None = None

    try:
        for _ in range(MAX_TOOL_ROUNDS):
            if is_disconnected and await is_disconnected():
                return

            data = await chat_completion(model=model, messages=working, tools=TOOL_DEFINITIONS)
            if data.get("usage"):
                usage = data["usage"]

            assistant = extract_assistant_message(data)
            tool_calls = assistant.get("tool_calls") or []

            if not tool_calls:
                final_text = (assistant.get("content") or "").strip()
                if not final_text:
                    yield _sse({"type": "error", "detail": "Réponse vide du modèle."})
                    return

                chunk_size = 48
                for index in range(0, len(final_text), chunk_size):
                    if is_disconnected and await is_disconnected():
                        return
                    yield _sse({"type": "delta", "content": final_text[index : index + chunk_size]})

                yield _sse({"type": "agent_complete", "usage": usage})
                return

            working.append(
                {
                    "role": "assistant",
                    "content": assistant.get("content"),
                    "tool_calls": tool_calls,
                }
            )

            for call in tool_calls:
                fn = call.get("function") or {}
                name = fn.get("name") or "unknown"
                args = parse_tool_arguments(fn.get("arguments"))

                yield _sse({"type": "tool", "name": name, "status": "running"})
                result = await execute_tool(name=name, arguments=args, conversation_id=conversation_id)
                yield _sse({"type": "tool", "name": name, "status": "done"})

                working.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id"),
                        "content": result,
                    }
                )

        yield _sse({"type": "error", "detail": "Nombre maximal d'appels d'outils atteint."})
    except RuntimeError as exc:
        yield _sse({"type": "error", "detail": str(exc)})
