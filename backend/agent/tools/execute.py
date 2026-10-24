import json
from collections.abc import Awaitable, Callable
from typing import Any

from agent.tools import calendar, drive, email_tool, notion_tool, weather, web_search

ToolHandler = Callable[..., str | Awaitable[str]]


async def execute_tool(*, name: str, arguments: dict[str, Any], conversation_id: int) -> str:
    handlers: dict[str, ToolHandler] = {
        "web_search": web_search.web_search,
        "get_weather": weather.get_weather,
        "compare_weather": weather.compare_weather,
        "list_calendar_events": calendar.list_calendar_events,
        "create_calendar_event": calendar.create_calendar_event,
        "update_calendar_event": calendar.update_calendar_event,
        "delete_calendar_event": calendar.delete_calendar_event,
        "draft_email": lambda **kwargs: email_tool.draft_email(conversation_id=conversation_id, **kwargs),
        "send_pending_email": lambda **kwargs: email_tool.send_pending_email(
            conversation_id=conversation_id, **kwargs
        ),
        "search_notion_pages": notion_tool.search_notion_pages,
        "get_notion_page_content": notion_tool.get_notion_page_content,
        "create_notion_page": notion_tool.create_notion_page,
        "append_notion_page_content": notion_tool.append_notion_page_content,
        "search_drive_files": drive.search_drive_files,
        "read_drive_file": drive.read_drive_file,
    }

    handler = handlers.get(name)
    if not handler:
        return json.dumps({"error": f"Outil inconnu : {name}"}, ensure_ascii=False)

    try:
        result = handler(**arguments)
        if isinstance(result, Awaitable):
            result = await result
        return result
    except TypeError as exc:
        return json.dumps({"error": f"Arguments invalides pour {name} : {exc}"}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
