# Agent IA personnel (Tool Calling)

Agent de chat déployable : recherche web (Tavily), météo (WeatherAPI), Google Calendar, Google Drive, emails SMTP, Notion. Basé sur le chatbot FastAPI + React du bootcamp, étendu avec une boucle de tool calling via l'API RodiumAI (compatible OpenAI).

## Structure

- `backend/` : FastAPI, agent (`backend/agent/`), outils, persistance SQLite
- `frontend/` : interface React (Vite)

## Installation locale

### Backend

```bash
cd backend
uv sync
cp .env.example .env
# Renseigner les clés dans .env
uv run alembic upgrade head
uv run fastapi dev main.py --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI : http://127.0.0.1:5173 (proxy `/api` vers le backend)

## Variables d'environnement

Voir `backend/.env.example`. Ne jamais committer `.env`.

| Service | Variables |
|---------|-----------|
| LLM | `RODIUMAI_API_KEY`, `RODIUMAI_MODEL` |
| Tavily | `TAVILY_API_KEY` |
| Météo | `WEATHERAPI_KEY` |
| Google | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` |
| Notion | `NOTION_TOKEN`, `NOTION_PARENT_PAGE_ID` (optionnel) |
| Email | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` |

### Obtenir un refresh token Google

```bash
cd backend
uv run python scripts/google_oauth_setup.py
```

Autorisez Calendar et Drive en lecture ; copiez le refresh token dans `.env`.

## Déploiement (soumission)

1. Backend : Render, Railway, Fly.io, etc. (uvicorn, variables d'environnement)
2. Frontend : Vercel ou Netlify avec `VITE_API_URL` ou proxy vers l'URL du backend
3. Soumettre l'URL publique de l'interface de chat

Pour l'évaluation : prévoir des comptes ou dossiers de test, pas vos données personnelles sensibles.

## Outils enregistrés

Définis dans `backend/agent/tools/schemas.py`, exécutés dans `backend/agent/tools/execute.py`. L'agent choisit dynamiquement les outils via `tool_choice: auto`.
