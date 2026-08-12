# qooing Knowledge Base 포맷 스펙

> `knowledge_base/`에 무엇을 어떤 형식으로 넣을지 정의하는 **포맷 가이드**다.
> [OKF (Open Knowledge Format)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)를
> 거의 그대로 차용하되, qooing에 맞춘 몇 가지 강화 규칙을 둔다.
>
> **우선순위:** 이 스펙(= OKF + 아래 강화 규칙)이 1순위다. 다른 문서와 충돌하면 이 문서를 따른다.

## 1. Philosophy

### 1.1 Minimally Opinionated (최소 규정)

기본 OKF interoperability 요구사항은 모든 concept의 `type` 필드 하나다. qooing의 실행 가능한
profile은 육아 지식의 provenance를 검증하기 위해 §4.2와 타입별 필드를 추가로 요구한다.

- 어떤 type이 존재하는지 (taxonomy 강제 없음)
- 어떤 추가 frontmatter 필드를 둘지
- body에 어떤 섹션을 쓸지

스펙은 **content model이 아니라 interoperability surface**를 정의한다. schema registry도, 중앙 권위도,
필수 tooling도 없다. 이 최소주의가 진입 장벽을 없앤다 — SDK 없이 누구나 produce, integration 없이 누구나 consume.

### 1.2 Producer / Consumer Independence (생산·소비 분리)

지식을 **쓰는 쪽**과 **읽는 쪽**을 깔끔하게 분리한다. format이 contract이므로 양 끝 tooling은 서로 모른 채 독립적으로 swap 가능하다.

| 생산 (producer) | ↔ format ↔ | 소비 (consumer) |
| --- | --- | --- |
| 손으로 쓴 bundle | | AI agent가 소비 |
| metadata export 파이프라인 | | visualizer가 브라우징 |
| 한 LLM이 synthesize | | 다른 LLM이 query |

qooing에서는 `knowledge_producer/`(또는 손)가 produce하고, 백엔드의 Pydantic AI 에이전트가 `list_wiki`/`read_wiki`로 consume한다.
양쪽은 이 포맷만 알면 되고, 서로의 구현은 몰라도 된다.

### 1.3 Format, Not Platform (플랫폼이 아닌 포맷)

특정 cloud·database·model provider·agent framework에 묶이지 않는다. markdown + YAML frontmatter가 전부다.

## 2. Terminology

- **Knowledge Bundle** — 자기완결적·계층적 지식 문서 모음. 배포 단위. qooing에서는 `knowledge_base/`가 번들이다.
- **Concept** — bundle 내 지식의 단일 단위. markdown 문서 하나. tangible asset(가이드 문서, API)이든 추상 개념(metric, process)이든 무엇이든 될 수 있다.
- **Concept ID** — bundle 내 파일 경로에서 `.md`를 뺀 것. 예: `wiki/newborn-sleep.md` → `wiki/newborn-sleep`.
- **Frontmatter** — 파일 최상단 `---`로 구분되는 YAML 메타데이터 블록.
- **Body** — frontmatter 이후 전체.
- **Link** — concept 간 표준 markdown 링크. 암묵적 parent/child 계층을 넘어선 관계 표현.
- **Citation** — concept에서 외부 source로의 링크. body의 주장을 뒷받침한다.

## 3. Bundle Structure

번들은 markdown 파일들의 디렉토리 트리다. qooing의 번들은 `knowledge_base/`이며, 다음 세 개의 concept 디렉토리로 구성된다.

```
knowledge_base/                  # ← 번들 (concept 전용)
├── index.md                     # 필수. 번들 루트 디렉토리 목록.
├── references/                  # type: Reference — 발행처 단위 신뢰 registry
│   ├── index.md                 # 필수.
│   ├── log.md                   # 필수. 신뢰성 결정 audit log.
│   └── <concept>.md
├── sources/                     # type: Source — 직접 모은 출처 문서 (producer 입력)
│   ├── index.md                 # 필수.
│   └── <concept>.md
└── wiki/                        # type: Wiki — 생성된 위키 (최종 산출물)
    ├── index.md                 # 필수.
    └── <slug>.md
```

- 디렉토리 구조는 도메인 독립적이다 — producer가 지식에 맞게 자유롭게 조직한다. 위 세 디렉토리는 qooing의 기본 분류일 뿐, 하위 디렉토리를 더 두어도 된다 (각 디렉토리에 `index.md` 필수).
- **`knowledge_producer/`는 번들 밖이다.** index 생성·위키 저작 등 producer 도구는 concept이 아니므로 `knowledge_base/`에 두지 않고 repo 루트 `knowledge_producer/`에 둔다.
- 번들은 git repository로 배포된다 (history·attribution·diff 제공). 이 repo의 일부 subdirectory 형태다.

## 4. Frontmatter

```yaml
---
type: <Type name>                  # REQUIRED
title: <표시 이름>                  # qooing 필수
description: <한 줄 요약>           # qooing 필수
resource: <원본 asset의 canonical URI>   # 타입에 따라 필수
tags: [<tag>, <tag>, …]            # 선택
timestamp: <ISO 8601 datetime>     # qooing 필수 (마지막 의미있는 변경 시각)
# … 그 외 producer 정의 key/value
---
```

### 4.1 Required: `type`

concept 종류를 식별하는 짧은 문자열. consumer가 routing·filtering·presentation에 사용한다.

- type 값은 중앙 등록되지 않는다. producer는 descriptive·self-explanatory한 값을 골라야 한다 (SHOULD).
- consumer는 모르는 type을 graceful하게 처리해야 한다 (MUST) — 보통 generic concept으로 취급.

**qooing 타입 분류:**

| 디렉토리 | `type` 값 | 의미 |
| --- | --- | --- |
| `references/` | `Reference` | 발행처 단위 신뢰 registry |
| `sources/` | `Source` | 구체 문서 본문과 provenance를 보존한 producer 입력 |
| `wiki/` | `Wiki` | LLM이 consolidation한 최종 위키 문서 |

Reference의 단위, reliability, index와 audit event는
[Reference 타입 스펙](2026-08-12-reference-type.md)이 정의한다.

### 4.2 qooing 공통 필수 metadata

- **`title`** — 사람이 읽는 표시 이름.
- **`description`** — 한 문장 요약. `index.md` 생성기·검색 스니펫·프리뷰가 사용한다.
- **`timestamp`** — 마지막 의미있는 변경의 ISO 8601 datetime.

`Reference`와 `Source`는 추가로 `resource`가 필수다. Reference의 `reliability`, Source의
`reference`, Wiki의 `sources`처럼 타입별 필수 필드는 각 타입 규칙과 validator가 정의한다.

### 4.3 선택 metadata

- **`tags`** — cross-cutting 분류용 짧은 문자열 YAML 리스트.
- 그 외 producer-defined key/value.

### 4.4 타입별 provenance

`wiki/newborn-sleep.md`:

```yaml
---
type: Wiki
title: 신생아 수면 패턴
description: 0~3개월 아기의 수면 주기와 밤중 수유 가이드
sources:                           # producer 필드 (citation 보조)
  - /sources/aap-sleep.md
tags: [수면, 신생아]
timestamp: 2026-06-20T09:00:00Z
---
```

`sources/aap-sleep.md`:

```yaml
---
type: Source
title: AAP Safe Sleep Recommendations
description: AAP의 구체적인 안전 수면 권고 문서 보존본
resource: https://publications.aap.org/pediatrics/article/...
reference: /references/aap.md
timestamp: 2026-06-20T09:00:00Z
---
```

## 5. Cross-linking

concept은 표준 markdown 링크로 다른 concept을 연결할 수 있다 (MAY). 두 형식을 지원한다.

### 5.1 Absolute (bundle-relative) — 권장

`/`로 시작하며 bundle 루트(`knowledge_base/`) 기준으로 해석한다.

```markdown
조인 키는 [customers 출처](/sources/aap-sleep.md)를 참고하라.
```

문서를 디렉토리 내에서 옮겨도 안정적이므로 이 형식을 권장한다.

### 5.2 Relative

표준 markdown 상대 경로.

```markdown
[옆 concept](./other.md) 참고.
```

### 5.3 Link Semantics

A→B 링크는 관계를 assert한다. 관계의 **종류**(parent/child, references, depends-on 등)는 링크 자체가 아니라
**주변 prose**가 전달한다. graph view를 만드는 consumer는 보통 모든 링크를 untyped 관계의 directed edge로 취급한다.

consumer는 **broken link를 tolerate해야 한다 (MUST)** — 대상이 번들에 없는 링크는 malformed가 아니라, 아직 쓰지 않은 지식일 수 있다.

### 5.4 Citation

`wiki/` concept은 body의 주장을 뒷받침하는 구체 문서인 `sources/` concept을 인용한다.
각 Source는 `reference` frontmatter로 발행처 registry를 가리킨다. 따라서 기본 provenance는
`Wiki -> Source -> Reference`다. Wiki의 `sources` 필드는 citation을 기계가 읽게 한다.

## 6. Index Files (필수)

> **qooing 강화 규칙:** OKF에서 `index.md`는 optional이지만, **이 번들에서는 모든 디렉토리(번들 루트 포함)에
> `index.md`가 필수다 (MUST).** discoverability — 사람이나 에이전트가 개별 문서를 열기 전에 무엇이 있는지 파악하기 위함.

- `index.md`는 **frontmatter가 없다.**
- body는 heading으로 묶인 1개 이상의 섹션으로 구성한다.
- 각 entry는 링크된 concept frontmatter의 `description`을 포함해야 한다 (SHOULD).
- producer는 `index.md`를 자동 생성할 수 있다 (`knowledge_producer/`). consumer는 없을 때 즉석에서 합성할 수 있다.

예시 (`knowledge_base/wiki/index.md`):

```markdown
# 수면

* [신생아 수면 패턴](newborn-sleep.md) - 0~3개월 아기의 수면 주기와 밤중 수유 가이드

# 수유

* [모유수유 기초](breastfeeding-basics.md) - 초기 수유 자세와 빈도
```

## 7. Log Files

`log.md`는 해당 scope의 변경 history를 기록한다. date-grouped 평면 리스트, **최신순(newest first)**.

> **qooing 강화 규칙:** OKF에서 `log.md`는 어디서나 optional이지만, **`references/`에는 필수다 (MUST)** —
> 참조 자료의 신뢰성(reliability) 관련 결정을 audit log로 남기기 위함. 그 외 디렉토리에서는 optional.

- date heading은 ISO 8601 `YYYY-MM-DD` 형식이어야 한다 (MUST).
- entry는 prose다. Reference event 어휘는
  [Reference 타입 스펙](2026-08-12-reference-type.md)을 따른다.

예시 (`knowledge_base/references/log.md`):

```markdown
# References Log

## 2026-06-20
* **Register**: [WHO](/references/who.md) 등록. 국제 공공보건기관으로 **확실**.

## 2026-06-15
* **Unregister**: 출처 불명으로 [블로그](/references/blog.md) 제거.
```

## 8. Producer / Consumer (참고)

- **Producer**: repo 루트 `knowledge_producer/`의 역할별 agent skill과 결정적 Python 도구. 자세한 경계는
  [Knowledge Producer 스펙](2026-08-12-knowledge-producer.md)을 따른다.
- **Consumer**: 백엔드 Pydantic AI 에이전트가 `list_wiki()`/`read_wiki(slug)` 툴로 `wiki/`를 탐색·소비한다.

두 쪽은 이 포맷만 contract로 공유하며 독립적이다.
