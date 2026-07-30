# Python 3.14 and uv

## Mental model

uv workspace는 하나의 lockfile과 virtual environment를 공유하지만 각 member가 runtime
dependency를 독립적으로 선언하게 한다. backend에 Pydantic AI가 있어도 producer의 runtime에는
필요하지 않다. 루트 `pyproject.toml`은 quality tools와 workspace membership을 소유한다.

**English recap:** One lockfile gives reproducibility; member manifests preserve dependency
boundaries.

## qooing paths and commands

- `pyproject.toml`: Python 3.14, Ruff, ty, pytest, workspace.
- `backend/pyproject.toml`: API/agent runtime.
- `knowledge_producer/pyproject.toml`: bundle CLI runtime.

```bash
uv sync --all-packages
uv run --package qooing-producer qooing-kb validate knowledge_base
uv run --package qooing-backend pytest backend/tests
uv lock --check
```

`uv run`은 lock과 environment를 확인하고 command를 같은 환경에서 실행한다. 직접 `python`,
`pip`를 호출하지 않는다.

## Common mistakes

- member package test를 실행하면서 `--package`를 빼 dependency가 빠지는 문제.
- `uv.lock`을 수동 편집하거나 commit하지 않는 문제.
- root dev dependency와 member runtime dependency를 섞는 문제.

## Try it

`uv tree --package qooing-producer`와 `uv tree --package qooing-backend`를 비교해 agent
dependency가 어느 쪽에만 존재하는지 확인한다.

## Further reading

- [uv workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)
- [uv projects](https://docs.astral.sh/uv/concepts/projects/)
- [Python 3.14 documentation](https://docs.python.org/3.14/)
