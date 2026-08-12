---
name: register-reference
description: Review, register, update, reclassify, or remove a publisher in qooing's knowledge_base/references trust registry. Use when adding a new source domain or portal, changing publisher reliability, correcting publisher metadata, or auditing the Reference registry and log.
---

# Register Reference

Maintain publisher-level provenance without storing individual article content in `references/`.
Follow `docs/specs/2026-08-12-reference-type.md`.

## Workflow

1. Inspect `knowledge_base/references/index.md` and existing Reference `resource` values. Reuse the
   existing record for redirects, URL variants, or paths on the same portal.
2. Identify the publisher and canonical domain. Split a portal only when its audience or content is
   independently published and cited.
3. Assess the operating or reviewing organization. Propose `확실`, `유력`, or `참고`; treat the
   administrator's decision as authoritative.
4. Create or update `knowledge_base/references/<slug>.md` with `type`, `title`, `description`,
   `resource`, `reliability`, and ISO 8601 `timestamp`.
5. Record the rationale, coverage, exclusions, and fetch constraints in the body. Do not place
   article claims or copied article bodies in a Reference.
6. Add a newest-first entry to `knowledge_base/references/log.md` using **Register**,
   **Unregister**, **Reliability**, or **Update**, including the reason for trust decisions.
7. Run:

```bash
uv run --package qooing-producer qooing-kb index knowledge_base
uv run --package qooing-producer qooing-kb validate knowledge_base
```

Resolve every violation before finishing. Modify only `knowledge_base/references/` unless the user
explicitly expands the task.
