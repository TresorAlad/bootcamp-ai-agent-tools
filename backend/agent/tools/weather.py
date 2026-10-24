import json
import os

import httpx


async def get_weather(*, location: str, days: int = 1) -> str:
    api_key = os.getenv("WEATHERAPI_KEY", "").strip()
    if not api_key:
        return json.dumps(
            {"error": "WEATHERAPI_KEY n'est pas configurée."},
            ensure_ascii=False,
        )

    days = max(1, min(days, 3))
    params = {"key": api_key, "q": location, "days": days, "aqi": "no", "alerts": "no"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("https://api.weatherapi.com/v1/forecast.json", params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        return json.dumps({"error": f"Échec WeatherAPI : {exc}"}, ensure_ascii=False)

    loc = data.get("location") or {}
    current = data.get("current") or {}
    forecast_days = (data.get("forecast") or {}).get("forecastday") or []

    summary = {
        "location": f"{loc.get('name')}, {loc.get('country')}",
        "localtime": loc.get("localtime"),
        "current": {
            "temp_c": current.get("temp_c"),
            "condition": (current.get("condition") or {}).get("text"),
            "humidity": current.get("humidity"),
            "wind_kph": current.get("wind_kph"),
        },
        "forecast": [
            {
                "date": day.get("date"),
                "max_c": (day.get("day") or {}).get("maxtemp_c"),
                "min_c": (day.get("day") or {}).get("mintemp_c"),
                "condition": ((day.get("day") or {}).get("condition") or {}).get("text"),
            }
            for day in forecast_days
        ],
    }
    return json.dumps(summary, ensure_ascii=False)


async def compare_weather(*, locations: list[str]) -> str:
    if len(locations) < 2:
        return json.dumps(
            {"error": "Indiquez au moins deux villes à comparer."},
            ensure_ascii=False,
        )
    parts = []
    for city in locations[:5]:
        parts.append(json.loads(await get_weather(location=city, days=1)))
    return json.dumps({"comparisons": parts}, ensure_ascii=False)
