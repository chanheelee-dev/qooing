# Pydantic AI

## Mental model

Pydantic AI의 `Agent`는 model, instructions, tools, typed dependencies를 묶는다. model은
reasoning을 하고 tool은 애플리케이션이 허용한 capability만 제공한다. `AgentDependencies`에
`WikiStore`를 넣어 global state 없이 tool이 같은 request dependency를 사용한다.

**English recap:** The model decides when to call tools, while typed dependencies control what those
tools can access.

## Offline and configured modes

`FunctionModel`은 외부 API 없이 실제 tool-call loop를 재현한다. 첫 요청에서 `list_wiki`,
다음 요청에서 `read_wiki`, 마지막 요청에서 text를 반환한다. `QOOING_MODEL`이 있으면 같은
agent에 provider model string을 주고 `stream_text(delta=True)`를 사용한다.

```bash
QOOING_MODEL=openai:gpt-5-mini \
uv run --package qooing-backend uvicorn app.main:app --app-dir backend
```

## Common mistakes

- `FunctionModel` 결과만 테스트하고 실제 tool 구현을 mock해 경계를 검증하지 않는 문제.
- cumulative text와 delta text를 혼동해 UI에 문장이 반복되는 문제.
- profile을 영구 memory로 오해하는 문제. 매 run의 prompt context일 뿐이다.

## Try it

offline test에서 wiki title을 바꾸고 응답이 실제 tool 결과를 반영하는지 확인한다. 그 다음
`QOOING_MODEL`을 설정했을 때 `/api/health`의 `chat_mode` 변화를 확인한다.

## Further reading

- [Pydantic AI agents](https://ai.pydantic.dev/agent/)
- [Pydantic AI tools](https://ai.pydantic.dev/tools/)
- [Pydantic AI output streaming](https://ai.pydantic.dev/output/)
- [Pydantic AI testing](https://ai.pydantic.dev/testing/)
