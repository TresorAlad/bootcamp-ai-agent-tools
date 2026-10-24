# Frontend build
FROM node:22-bookworm-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Backend + static UI
FROM python:3.14-slim-bookworm AS runtime
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

RUN pip install --no-cache-dir uv

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/ ./
COPY --from=frontend-build /frontend/dist ./static

EXPOSE 8000

CMD sh -c "uv run alembic upgrade head && uv run uvicorn main:app --host 0.0.0.0 --port ${PORT}"
