# End-to-end architecture

## Mental model

qooing은 producer와 consumer를 Markdown contract로 분리한다. producer는 신뢰 자료를 bundle로
만들고, backend agent는 읽기 tool만 사용하며, frontend는 HTTP 이외의 backend 내부를 모른다.

`frontend/src/App.tsx` → `backend/app/main.py` → `backend/app/agent.py` →
`backend/app/wiki_store.py` → `knowledge_base/wiki/` 순서가 질문의 핵심 data flow다.

**English recap:** The browser, agent, and producer are independently replaceable because their
boundaries are HTTP and Markdown rather than shared implementation code.

## Request flow

1. React가 `{prompt,baby_info}`를 `POST /api/chat`으로 보낸다.
2. FastAPI가 Pydantic schema로 입력을 검증한다.
3. agent가 `list_wiki`, `read_wiki`로 근거를 찾는다.
4. Pydantic AI text delta가 SSE frame이 되어 같은 POST response로 돌아온다.
5. stream parser가 chunk 경계와 무관하게 assistant message를 누적한다.

## Commands

```bash
uv run --package qooing-backend uvicorn app.main:app --app-dir backend --reload
cd frontend
bun run dev
```

## Common mistakes

- network chunk 하나를 SSE event 하나라고 가정하지 않는다.
- `knowledge_base/`와 producer code를 같은 배포 단위로 혼동하지 않는다.
- UI history가 backend conversation memory라고 가정하지 않는다. scaffold API는 stateless다.

## Try it

브라우저 개발자 도구에서 `/api/chat` request body와 streamed response를 확인한 뒤,
`backend/app/main.py`의 event 이름과 대응시켜 본다.

## Further reading

- [C4 model](https://c4model.com/)
- [qooing scaffold specification](../specs/2026-07-28-project-scaffold.md)
