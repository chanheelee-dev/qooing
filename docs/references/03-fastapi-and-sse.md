# FastAPI and Server-Sent Events

## Mental model

FastAPI는 HTTP boundary의 schema와 status code를 담당하고, domain logic은 `WikiStore`와
`ChatService`에 둔다. SSE는 특별한 socket이 아니라 `text/event-stream` 형식의 오래 열린
HTTP response다. 이 프로젝트는 request body가 필요하므로 `EventSource` 대신 `fetch` POST를 쓴다.

**English recap:** FastAPI validates before streaming; SSE is framed text over a normal streaming
HTTP response.

## qooing flow

`ChatRequest`가 빈 prompt와 잘못된 날짜를 422로 거절한다. `StreamingResponse`의 async
generator는 `delta`, `done`, `error` frame을 만든다. response header가 전송된 뒤 생긴 오류는
HTTP status를 바꿀 수 없으므로 safe `error` event로 표현한다.

```text
event: delta
data: {"text":"new text"}

event: done
data: {}
```

## Commands

```bash
uv run --package qooing-backend uvicorn app.main:app --app-dir backend
curl http://localhost:8000/api/health
curl -N -X POST http://localhost:8000/api/chat \
  -H 'content-type: application/json' \
  -d '{"prompt":"수면 질문","baby_info":{}}'
```

## Common mistakes

- newline 두 개로 event를 종료하지 않는 문제.
- 내부 exception이나 provider secret을 error event에 노출하는 문제.
- generator가 시작된 뒤 503 status를 반환할 수 있다고 생각하는 문제.

## Try it

`curl -N`을 빼고 실행한 결과와 비교해 client-side buffering이 streaming 체감에 미치는
영향을 확인한다.

## Further reading

- [FastAPI response streaming](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [FastAPI request body validation](https://fastapi.tiangolo.com/tutorial/body/)
- [HTML SSE specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
