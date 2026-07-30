# Testing and debugging

## Mental model

unit test는 작은 contract, integration test는 subsystem boundary, smoke test는 배포된
경로를 검증한다. qooing에서는 producer temp bundle, FastAPI `TestClient`, Bun DOM test,
Compose HTTP smoke가 각각 다른 종류의 실패를 좁혀 준다.

**English recap:** Test at the narrowest boundary that can catch the intended break, then debug from
the first failing boundary outward.

## Quality gates

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

문제가 생기면 bundle validation → backend test → direct `:8000` API → nginx-proxied `:8080`
API → React UI 순서로 확인한다. 이 순서는 dependency 방향과 같아 원인 후보를 빠르게 줄인다.

## Common mistakes

- framework 자체를 test하고 application behavior를 검증하지 않는 문제.
- expected value를 production helper로 계산해 tautological test를 만드는 문제.
- 한 quality gate 성공을 전체 build 성공으로 해석하는 문제.

## Try it

wiki filename을 unsafe name으로 바꿔 producer와 backend 중 어느 test가 어떤 contract를
잡는지 예측한 후 실제 결과와 비교한다.

## Further reading

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Library guiding principles](https://testing-library.com/docs/guiding-principles/)
- [Ruff](https://docs.astral.sh/ruff/)
- [ty](https://docs.astral.sh/ty/)
