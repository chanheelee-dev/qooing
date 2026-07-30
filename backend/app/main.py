from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agent import ChatService
from .schemas import ChatRequest, HealthResponse, WikiDocument, WikiSummary
from .wiki_store import InvalidSlugError, WikiNotFoundError, WikiStore


def sse(event: str, data: dict[str, str]) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event}\ndata: {payload}\n\n"


def default_wiki_root() -> Path:
    configured = os.getenv("QOOING_WIKI_ROOT")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / "knowledge_base/wiki"


def create_app(wiki_root: Path | None = None, model_name: str | None = None) -> FastAPI:
    store = WikiStore(wiki_root or default_wiki_root())
    configured_model = model_name if model_name is not None else os.getenv("QOOING_MODEL") or None
    chat = ChatService(store, configured_model)
    app = FastAPI(title="qooing API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:8080"],
        allow_methods=["GET", "POST"],
        allow_headers=["content-type"],
    )

    @app.get("/api/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(chat_mode="configured" if chat.configured else "offline")

    @app.get("/api/wiki", response_model=list[WikiSummary])
    async def list_wiki() -> list[WikiSummary]:
        return store.list()

    @app.get("/api/wiki/{slug}", response_model=WikiDocument)
    async def read_wiki(slug: str) -> WikiDocument:
        try:
            return store.read(slug)
        except WikiNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Wiki document not found") from exc
        except InvalidSlugError as exc:
            raise HTTPException(status_code=400, detail="Invalid wiki slug") from exc

    async def event_stream(request: ChatRequest) -> AsyncIterator[str]:
        try:
            async for delta in chat.stream(request.prompt, request.baby_info):
                yield sse("delta", {"text": delta})
            yield sse("done", {})
        except Exception:
            yield sse("error", {"message": "Chat service is unavailable"})

    @app.post("/api/chat")
    async def post_chat(request: ChatRequest) -> StreamingResponse:
        return StreamingResponse(event_stream(request), media_type="text/event-stream")

    return app


app = create_app()
