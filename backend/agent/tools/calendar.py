import json
from datetime import datetime

from googleapiclient.discovery import build

from agent.tools.google_client import get_google_credentials


def _calendar_service():
    return build("calendar", "v3", credentials=get_google_credentials(), cache_discovery=False)


def list_calendar_events(
    *,
    time_min: str | None = None,
    time_max: str | None = None,
    query: str | None = None,
    max_results: int = 20,
) -> str:
    try:
        service = _calendar_service()
        params: dict = {
            "calendarId": "primary",
            "singleEvents": True,
            "orderBy": "startTime",
            "maxResults": max(1, min(max_results, 50)),
        }
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        if query:
            params["q"] = query

        events_result = service.events().list(**params).execute()
        items = events_result.get("items") or []
        simplified = []
        for ev in items:
            start = ev.get("start") or {}
            end = ev.get("end") or {}
            simplified.append(
                {
                    "id": ev.get("id"),
                    "summary": ev.get("summary"),
                    "start": start.get("dateTime") or start.get("date"),
                    "end": end.get("dateTime") or end.get("date"),
                    "location": ev.get("location"),
                    "htmlLink": ev.get("htmlLink"),
                }
            )
        return json.dumps({"events": simplified}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


def create_calendar_event(
    *,
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: str | None = None,
    timezone: str = "UTC",
) -> str:
    try:
        service = _calendar_service()
        body = {
            "summary": summary,
            "start": {"dateTime": start_datetime, "timeZone": timezone},
            "end": {"dateTime": end_datetime, "timeZone": timezone},
        }
        if description:
            body["description"] = description
        created = service.events().insert(calendarId="primary", body=body).execute()
        return json.dumps(
            {
                "id": created.get("id"),
                "summary": created.get("summary"),
                "htmlLink": created.get("htmlLink"),
                "start": (created.get("start") or {}).get("dateTime"),
            },
            ensure_ascii=False,
        )
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


def update_calendar_event(
    *,
    event_id: str,
    summary: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    description: str | None = None,
    timezone: str = "UTC",
) -> str:
    try:
        service = _calendar_service()
        event = service.events().get(calendarId="primary", eventId=event_id).execute()
        if summary:
            event["summary"] = summary
        if description is not None:
            event["description"] = description
        if start_datetime:
            event["start"] = {"dateTime": start_datetime, "timeZone": timezone}
        if end_datetime:
            event["end"] = {"dateTime": end_datetime, "timeZone": timezone}
        updated = (
            service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
        )
        return json.dumps(
            {
                "id": updated.get("id"),
                "summary": updated.get("summary"),
                "start": (updated.get("start") or {}).get("dateTime"),
                "end": (updated.get("end") or {}).get("dateTime"),
            },
            ensure_ascii=False,
        )
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


def delete_calendar_event(*, event_id: str) -> str:
    try:
        service = _calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return json.dumps({"deleted": True, "event_id": event_id}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


def parse_user_datetime_hint(value: str) -> str:
    """Valide un format ISO 8601 minimal pour les outils."""
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value
