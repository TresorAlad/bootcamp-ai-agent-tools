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

## Déploiement (Railway + Docker, une URL)

Le `Dockerfile` à la racine build le frontend React et sert l'UI depuis FastAPI (`backend/static`).

### Railway

1. [railway.app](https://railway.app) → **New Project** → **GitHub Repo** → `bootcamp-ai-agent-tools`
2. Railway détecte `railway.toml` et le `Dockerfile`.
3. **Variables** : copier toutes les clés de `backend/.env.example` (valeurs réelles dans le dashboard Railway, jamais dans Git).
4. **Networking** → **Generate Domain** → URL publique du chat (soumission devoir).
5. Vérifier : `https://TON-DOMAINE/health` → `{"status":"ok"}` puis ouvrir `/` pour le chat.

### Build local (optionnel)

```bash
docker build -t bootcamp-ai-agent .
docker run --rm -p 8000:8000 --env-file backend/.env bootcamp-ai-agent
```

UI : http://127.0.0.1:8000/

Pour l'évaluation : comptes et dossiers de test, secrets uniquement sur l'hébergeur.

## Outils enregistrés

Définis dans `backend/agent/tools/schemas.py`, exécutés dans `backend/agent/tools/execute.py`. L'agent choisit dynamiquement les outils via `tool_choice: auto`.
