import io
import json

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from agent.tools.google_client import get_google_credentials


def _drive_service():
    return build("drive", "v3", credentials=get_google_credentials(), cache_discovery=False)


def search_drive_files(*, query: str, max_results: int = 10) -> str:
    try:
        service = _drive_service()
        q = f"name contains '{query.replace(chr(39), '')}' or fullText contains '{query.replace(chr(39), '')}'"
        result = (
            service.files()
            .list(
                q=q,
                pageSize=max(1, min(max_results, 25)),
                fields="files(id,name,mimeType,modifiedTime,webViewLink)",
            )
            .execute()
        )
        return json.dumps({"files": result.get("files") or []}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


def read_drive_file(*, file_id: str) -> str:
    try:
        service = _drive_service()
        meta = service.files().get(fileId=file_id, fields="id,name,mimeType").execute()
        mime = meta.get("mimeType") or ""

        if mime == "application/vnd.google-apps.document":
            content = (
                service.files()
                .export(fileId=file_id, mimeType="text/plain")
                .execute()
                .decode("utf-8", errors="replace")
            )
        elif mime.startswith("text/") or mime in {
            "application/json",
            "application/javascript",
        }:
            request = service.files().get_media(fileId=file_id)
            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            content = buffer.getvalue().decode("utf-8", errors="replace")
        else:
            return json.dumps(
                {
                    "error": f"Type de fichier non pris en charge pour la lecture : {mime}",
                    "metadata": meta,
                },
                ensure_ascii=False,
            )

        if len(content) > 12000:
            content = content[:12000] + "\n\n[Contenu tronqué pour limiter la taille.]"

        return json.dumps(
            {"metadata": meta, "content": content},
            ensure_ascii=False,
        )
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
