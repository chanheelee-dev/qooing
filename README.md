# qooing

Query a prebuilt baby-care wiki through a read-only explorer and a Pydantic AI chat agent.

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- [Bun](https://bun.com/)
- Docker Compose (optional)

## Local development

```bash
uv sync --all-packages
uv run --package qooing-producer qooing-kb validate knowledge_base
uv run --package qooing-backend uvicorn app.main:app --app-dir backend --reload
```

In another terminal:

```bash
cd frontend
bun install --frozen-lockfile
bun run dev
```

Open <http://localhost:5173>. Without `QOOING_MODEL`, chat uses a deterministic offline
`FunctionModel`. Copy `.env.example` to `.env` and set a Pydantic AI model string plus its provider
credential to use a configured model.

## Quality checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check backend knowledge_producer
uv run pytest

cd frontend
bun run lint
bun run typecheck
bun run test
bun run build
```

Run a local API smoke test with `scripts/smoke-local.sh`.

## Containers

```bash
scripts/smoke-compose.sh
```

- Web app: <http://localhost:8080>
- Direct API and docs: <http://localhost:8000/docs>

See the [technical handbook](docs/references/index.md) for project-guided explanations of every
major technology and data flow.
