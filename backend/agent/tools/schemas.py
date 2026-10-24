TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Recherche des informations ou actualités récentes sur Internet. "
                "Utilise cet outil lorsque la question exige des données à jour ou des sources."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Requête de recherche"},
                    "max_results": {"type": "integer", "minimum": 1, "maximum": 10},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Météo actuelle et prévisions pour une ville.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "days": {"type": "integer", "minimum": 1, "maximum": 3},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_weather",
            "description": "Compare la météo de plusieurs villes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                    }
                },
                "required": ["locations"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_calendar_events",
            "description": "Liste les événements Google Calendar (primary).",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_min": {"type": "string", "description": "ISO 8601"},
                    "time_max": {"type": "string", "description": "ISO 8601"},
                    "query": {"type": "string"},
                    "max_results": {"type": "integer"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Crée un événement dans Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "start_datetime": {"type": "string", "description": "ISO 8601"},
                    "end_datetime": {"type": "string", "description": "ISO 8601"},
                    "description": {"type": "string"},
                    "timezone": {"type": "string"},
                },
                "required": ["summary", "start_datetime", "end_datetime"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_calendar_event",
            "description": "Modifie un événement existant (uniquement si l'utilisateur l'a demandé).",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "summary": {"type": "string"},
                    "start_datetime": {"type": "string"},
                    "end_datetime": {"type": "string"},
                    "description": {"type": "string"},
                    "timezone": {"type": "string"},
                },
                "required": ["event_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_calendar_event",
            "description": "Supprime un événement (uniquement si l'utilisateur l'a explicitement demandé).",
            "parameters": {
                "type": "object",
                "properties": {"event_id": {"type": "string"}},
                "required": ["event_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_email",
            "description": (
                "Prépare un email et le met en attente. Ne pas envoyer sans confirmation utilisateur."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_pending_email",
            "description": (
                "Envoie le brouillon en attente. user_confirmed doit être true "
                "seulement après confirmation explicite de l'utilisateur."
            ),
            "parameters": {
                "type": "object",
                "properties": {"user_confirmed": {"type": "boolean"}},
                "required": ["user_confirmed"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notion_pages",
            "description": "Recherche des pages ou notes Notion accessibles à l'intégration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_notion_page_content",
            "description": "Lit le contenu textuel d'une page Notion.",
            "parameters": {
                "type": "object",
                "properties": {"page_id": {"type": "string"}},
                "required": ["page_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_notion_page",
            "description": "Crée une page Notion avec un titre et un contenu initial.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "parent_page_id": {"type": "string"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "append_notion_page_content",
            "description": "Ajoute du texte à une page Notion existante.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["page_id", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_drive_files",
            "description": "Recherche des fichiers dans Google Drive.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_drive_file",
            "description": "Lit le contenu d'un Google Doc ou fichier texte Drive.",
            "parameters": {
                "type": "object",
                "properties": {"file_id": {"type": "string"}},
                "required": ["file_id"],
            },
        },
    },
]
