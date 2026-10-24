import json
import os

import httpx


async def web_search(*, query: str, max_results: int = 5) -> str:
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        return json.dumps(
            {"error": "TAVILY_API_KEY n'est pas configurée. Impossible de rechercher sur Internet."},
            ensure_ascii=False,
        )

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": True,
        "max_results": max(1, min(max_results, 10)),
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post("https://api.tavily.com/search", json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        return json.dumps({"error": f"Échec de la recherche Tavily : {exc}"}, ensure_ascii=False)

    results = []
    for item in data.get("results") or []:
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
            }
        )

    return json.dumps(
        {
            "answer": data.get("answer"),
            "results": results,
        },
        ensure_ascii=False,
    )
