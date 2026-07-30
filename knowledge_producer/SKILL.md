# qooing Knowledge Producer

1. Select exactly one topic from `topics.yaml`.
2. Capture authoritative material under `knowledge_base/references/` and user-provided material
   under `knowledge_base/sources/`.
3. Record every reference reliability decision in `knowledge_base/references/log.md`.
4. Consolidate claims into `knowledge_base/wiki/<slug>.md`, citing bundle-relative sources.
5. Run `uv run qooing-kb index knowledge_base`.
6. Run `uv run qooing-kb validate knowledge_base` and resolve every violation.

Fetching and LLM consolidation are intentionally manual agent steps in this scaffold.
