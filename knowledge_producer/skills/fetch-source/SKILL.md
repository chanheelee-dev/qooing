---
name: fetch-source
description: Capture a concrete web page, document, or user-provided artifact as an immutable qooing Source with publisher provenance. Use when collecting evidence for a wiki topic, refreshing a changed source, processing a supplied URL or document, or repairing knowledge_base/sources metadata and citations.
---

# Fetch Source

Capture one concrete document per Source and connect it to exactly one registered publisher.
Follow `docs/specs/02-knowledge-base-spec.md`.

## Workflow

1. Identify the exact document and canonical URL or artifact URI. Do not use a publisher homepage as
   the Source when a concrete article, guideline, or file exists.
2. Find its publisher in `knowledge_base/references/`. If absent, use `register-reference` before
   continuing; do not create or grade a Reference in this workflow.
3. Fetch or read the document. Preserve permitted source material or write faithful structured notes;
   distinguish quotations, paraphrases, and interpretation, and never invent missing text.
4. Create a new kebab-case `knowledge_base/sources/<slug>.md` with:

```yaml
---
type: Source
title: <document title>
description: <one-sentence scope>
resource: <canonical document URI>
reference: /references/<publisher>.md
timestamp: <ISO 8601 capture time>
---
```

5. Include publication/update dates, retrieval context, scope, and limitations when available. Keep
   Source content stable after capture; create a versioned Source for materially changed evidence.
6. Run:

```bash
uv run --package qooing-producer qooing-kb index knowledge_base
uv run --package qooing-producer qooing-kb validate knowledge_base
```

Resolve every violation before finishing. Modify only `knowledge_base/sources/` unless the user
explicitly expands the task.
