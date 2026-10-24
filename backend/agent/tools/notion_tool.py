import json
import os

import httpx

NOTION_VERSION = "2022-06-28"


def _headers() -> dict[str, str]:
    token = os.getenv("NOTION_TOKEN", "").strip()
    if not token:
        raise RuntimeError("NOTION_TOKEN n'est pas configuré.")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


async def search_notion_pages(*, query: str, max_results: int = 10) -> str:
    try:
        payload = {"query": query, "page_size": max(1, min(max_results, 25))}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.notion.com/v1/search",
                headers=_headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
    except RuntimeError as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
    except httpx.HTTPError as exc:
        return json.dumps({"error": f"Échec Notion search : {exc}"}, ensure_ascii=False)

    pages = []
    for item in data.get("results") or []:
        title = _extract_title(item)
        pages.append(
            {
                "id": item.get("id"),
                "object": item.get("object"),
                "title": title,
                "url": item.get("url"),
                "last_edited_time": item.get("last_edited_time"),
            }
        )
    return json.dumps({"pages": pages}, ensure_ascii=False)


def _extract_title(item: dict) -> str:
    props = item.get("properties") or {}
    for prop in props.values():
        if prop.get("type") == "title":
            parts = prop.get("title") or []
            return "".join(part.get("plain_text", "") for part in parts)
    return item.get("id", "")


async def get_notion_page_content(*, page_id: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://api.notion.com/v1/blocks/{page_id}/children",
                headers=_headers(),
                params={"page_size": 50},
            )
            response.raise_for_status()
            data = response.json()
    except RuntimeError as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
    except httpx.HTTPError as exc:
        return json.dumps({"error": f"Échec Notion blocks : {exc}"}, ensure_ascii=False)

    lines = []
    for block in data.get("results") or []:
        text = _block_plain_text(block)
        if text:
            lines.append(text)

    return json.dumps({"page_id": page_id, "content": "\n".join(lines)}, ensure_ascii=False)


def _block_plain_text(block: dict) -> str:
    block_type = block.get("type")
    if not block_type:
        return ""
    payload = block.get(block_type) or {}
    rich = payload.get("rich_text") or payload.get("text") or []
    return "".join(part.get("plain_text", "") for part in rich)


async def create_notion_page(*, title: str, content: str, parent_page_id: str | None = None) -> str:
    resolved_parent = parent_page_id or os.getenv("NOTION_PARENT_PAGE_ID", "").strip()
    if not resolved_parent:
        return json.dumps(
            {
                "error": (
                    "Indiquez parent_page_id ou configurez NOTION_PARENT_PAGE_ID "
                    "(page partagée avec l'intégration)."
                )
            },
            ensure_ascii=False,
        )
    parent = {"page_id": resolved_parent}
    body = {
        "parent": parent,
        "properties": {
            "title": {"title": [{"text": {"content": title}}]},
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content[:2000]}}],
                },
            }
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.notion.com/v1/pages",
                headers=_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()
    except RuntimeError as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
    except httpx.HTTPError as exc:
        return json.dumps({"error": f"Échec création page Notion : {exc}"}, ensure_ascii=False)

    return json.dumps(
        {"id": data.get("id"), "url": data.get("url"), "title": title},
        ensure_ascii=False,
    )


async def append_notion_page_content(*, page_id: str, content: str) -> str:
    body = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content[:2000]}}],
                },
            }
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                f"https://api.notion.com/v1/blocks/{page_id}/children",
                headers=_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()
    except RuntimeError as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
    except httpx.HTTPError as exc:
        return json.dumps({"error": f"Échec ajout contenu Notion : {exc}"}, ensure_ascii=False)

    return json.dumps({"page_id": page_id, "blocks_added": len(data.get("results") or [])}, ensure_ascii=False)
