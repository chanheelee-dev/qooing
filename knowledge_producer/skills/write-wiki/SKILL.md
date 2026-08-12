---
name: write-wiki
description: Create or update a qooing Wiki concept by consolidating captured Sources with claim-level citations. Use when producing a knowledge_base/wiki article for a queued topic, revising a wiki after evidence changes, auditing source coverage, or repairing Wiki frontmatter and bundle citations.
---

# Write Wiki

Write one evidence-backed Wiki concept without changing its underlying Sources or publisher trust
records. Follow `docs/specs/02-knowledge-base-spec.md`.

## Workflow

1. Select exactly one topic from `knowledge_producer/topics.yaml` or the user's explicit request.
2. Read relevant `knowledge_base/sources/` documents and their linked References. If concrete
   evidence is missing, use `fetch-source`; do not fetch or register publishers in this workflow.
3. Separate supported facts, reasonable synthesis, uncertainty, and disagreement. For medical or
   safety-sensitive claims, prefer current authoritative Sources and state limits without diagnosing.
4. Create or update `knowledge_base/wiki/<slug>.md` with:

```yaml
---
type: Wiki
title: <display title>
description: <one-sentence summary>
sources:
  - /sources/<evidence>.md
tags: [<tag>]
timestamp: <ISO 8601 meaningful update time>
---
```

5. Cite the supporting Source near each material claim with bundle-root Markdown links. Keep the
   frontmatter `sources` list complete and free of direct `/references/` entries.
6. Preserve useful existing content unless contradicted by stronger evidence. Explain material
   conflicts and avoid presenting a publisher's reliability grade as proof of an individual claim.
7. Run:

```bash
uv run --package qooing-producer qooing-kb index knowledge_base
uv run --package qooing-producer qooing-kb validate knowledge_base
```

Resolve every violation before finishing. Modify only `knowledge_base/wiki/` unless the user
explicitly expands the task.
