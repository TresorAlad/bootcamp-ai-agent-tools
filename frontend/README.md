# Study Buddy - frontend (session 5)

Interface React (Vite) : streaming SSE, sélecteur de modèle, notes (`note`), réessai et arrêt du flux.

**Backend** : [TresorAlad/bootcamp-chatbot-backend](https://github.com/TresorAlad/bootcamp-chatbot-backend)

## Lancer en local

1. Backend (port **8001** si le 8000 est occupé) :

```bash
cd bootcamp-chatbot-backend
uv sync && cp .env.example .env
uv run alembic upgrade head
uv run fastapi dev main.py --port 8001
```

2. Frontend :

```bash
npm install
npm run dev
```

3. Ouvrir http://localhost:5173

Le proxy Vite envoie `/api/*` vers `http://localhost:8001` (`vite.config.ts`).

## Endpoints utilisés

| Méthode | Route | Usage |
| ------- | ----- | ----- |
| GET | /models | Liste des modèles autorisés |
| GET | /conversations | Barre latérale |
| POST | /conversations | Nouvelle conversation |
| GET | /conversations/{id}/messages | Messages du fil |
| POST | /conversations/{id}/notes | Note personnelle |
| POST | /chat | Message (flux SSE) |
