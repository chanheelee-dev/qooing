FROM ghcr.io/astral-sh/uv:0.9.21 AS uv
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QOOING_WIKI_ROOT=/app/knowledge_base/wiki

RUN groupadd --system qooing && useradd --system --gid qooing --home /app qooing
WORKDIR /app

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml backend/pyproject.toml
COPY knowledge_producer/pyproject.toml knowledge_producer/pyproject.toml
RUN uv sync --frozen --package qooing-backend --no-dev

COPY backend/app backend/app
COPY knowledge_base knowledge_base
RUN chown -R qooing:qooing /app
USER qooing

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD ["/bin/uv", "run", "--frozen", "--no-sync", "--package", "qooing-backend", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)"]
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
