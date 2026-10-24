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

### Render (gratuit, même Dockerfile)

Si Railway est indisponible (trial expiré), utiliser [Render](https://render.com).

1. **New** → **Blueprint** ou **Web Service** → repo GitHub `bootcamp-ai-agent-tools`
2. **Runtime** : **Docker** (fichier `Dockerfile` à la racine, ou `render.yaml`)
3. **Environment** : ajouter toutes les variables de `backend/.env.example`
4. **Health check path** : `/health`
5. URL Render du type `https://bootcamp-ai-agent-tools.onrender.com` → soumission devoir

Plan free : le service peut s’endormir après inactivité (première requête lente).

### Railway

Nécessite un plan payant si le trial est expiré. Sinon : **New Project** → GitHub → `railway.toml` + variables d’environnement → **Generate Domain**.

### Build local (optionnel)

```bash
docker build -t bootcamp-ai-agent .
docker run --rm -p 8000:8000 --env-file backend/.env bootcamp-ai-agent
```

UI : http://127.0.0.1:8000/

Pour l'évaluation : comptes et dossiers de test, secrets uniquement sur l'hébergeur.

## Outils enregistrés

Définis dans `backend/agent/tools/schemas.py`, exécutés dans `backend/agent/tools/execute.py`. L'agent choisit dynamiquement les outils via `tool_choice: auto`.
