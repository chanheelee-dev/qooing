# qooing — 기술스택·방법론·주요 기능 결정

> 본 문서는 구현 계획이 아니라 **기술스택 / 방법론 / 주요 기능**까지만 확정한 결정 문서.
> 세부 구현(API 엔드포인트, 패널 내부, 위키 구축 자동화)은 의도적으로 비워둠.

## Context

`chanheelee-dev/qooing` 는 public repo (AGPL-3.0, Python `.gitignore`, README 포함).

**제품 정체성:** "미리 구축(pre-built)된 육아 위키를 근거로 답하는 LLM 채팅 어시스턴트."
브레인스토밍으로 확정된 모양:

- 위키는 **오프라인 배치**로 미리 구축: (1) 내가 주제 선정 → (2) 신뢰 출처에서 fetch
  (공신력 있는 공개 가이드 + 내가 모아둔 문서) → (3) LLM이 consolidation → (4) 마크다운으로 저장.
- 웹앱은 **3패널 인터랙티브 앱**:
  - **file-explore** — 미리 만들어진 위키 문서를 **읽기 전용**으로 탐색·열람.
  - **chat** — 위키 + 아기정보를 근거로 답하는 **스트리밍 채팅**.
  - **customization (baby info)** — 아기 프로필. **클라이언트 소유**(서버 저장 없음), import해서 채팅 프롬프트에 주입.
- **검색은 임베딩/벡터DB 없이** "LLM이 알아서". → 에이전트에 위키 조회 툴을 주고 LLM이 스스로 문서를 골라 읽음.
- LLM은 **BYOM** (어떤 모델이든) → **Pydantic AI**로 모델 추상화.

**스택:** Python + `uv` (백엔드/파이프라인), FastAPI + Pydantic AI (백엔드), React + Vite (프론트), SSE (채팅 스트리밍). 라이선스 AGPL-3.0.

## 결정 사항 (확정)

| 항목 | 결정 |
|---|---|
| 위키 구축 | **agent skill 중심** + 보조 코드: 주제선정 → fetch → consolidation을 에이전트가 수행하되, fetch·index 생성 등은 `knowledge_producer/`의 Python 코드로 보조 |
| producer 환경 | `knowledge_producer/`는 backend와 **분리된 uv 워크스페이스 멤버** (자체 pyproject·의존성). build-time 전용, backend 런타임과 의존성 격리 |
| 출처 | 공신력 있는 공개 가이드 + 직접 모은 문서 (`sources/`) — 플러그인 가능하게 |
| 검색 | 임베딩 없음. Pydantic AI 에이전트 + `list_wiki`/`read_wiki` 툴로 LLM이 직접 탐색 |
| LLM | BYOM via Pydantic AI (모델은 env로 지정) |
| 프론트 | React SPA (Vite), 3패널 |
| 채팅 스트리밍 | SSE (서버→클라 단방향) |
| 아기 정보 | 클라이언트(localStorage) 소유 + import/export, 서버 저장 없음 |
| file-explore | 읽기 전용 |
| 계정/DB | 없음 (백엔드는 거의 무상태) |

## 가정 (실행 전 확인 필요할 수 있음)

- 위키/채팅 **콘텐츠 주 언어는 한국어** (영어도 가능하게).
- 출처의 구체 목록은 사용자가 채워넣는 구조로 두고, MVP는 `sources/`에 넣은 로컬 문서 + 설정된 URL로 동작.

## 디렉터리 구조 (모노레포)

```
qooing/
  pyproject.toml            # uv 워크스페이스 (backend + knowledge_producer)
  README.md                 # description/배지/실행법
  LICENSE                   # AGPL-3.0
  knowledge_base/           # 위키 지식베이스 = 번들 (concept 전용)
                            #   포맷 스펙: docs/specs/02-knowledge-base-spec.md
    index.md                # 필수. 번들 루트 디렉토리 목록.
    references/             # type: Reference — 공신력 있는 공개 가이드 등 참조 자료
      index.md              #   필수.
      log.md                #   필수. 신뢰성 결정 audit log.
    sources/                # type: Source — 직접 모은 출처 문서 (스킬의 입력)
      index.md              #   필수.
    wiki/                   # type: Wiki — 생성된 위키 (마크다운, frontmatter 포함) — 커밋됨
      index.md              #   필수.
      <slug>.md
  knowledge_producer/       # 위키 구축(producer) — 번들 밖. 별도 uv 워크스페이스 멤버
    pyproject.toml          #   자체 의존성 (fetch·파서 등, backend와 격리)
    topics.yaml             #   큐레이션한 주제 목록
    SKILL.md                #   주제→fetch(references/·sources/)→consolidation→wiki/*.md 작성 절차
    src/                    #   보조 코드 (fetch, index.md 생성 등) — 구현 TBD
  backend/                  # 별도 uv 워크스페이스 멤버 (런타임)
    app/
      main.py               # FastAPI 앱
      api/                  # 엔드포인트 — TBD (미정)
      agent.py              # Pydantic AI 에이전트 + list_wiki/read_wiki 툴
      wiki_store.py         # knowledge_base/wiki/ 읽기 (목록/본문)
      config.py             # 모델 등 env 설정 (BYOM)
    tests/
  frontend/                 # React + Vite SPA — 3패널 레이아웃만 확정, 구현 TBD
    src/
      App.tsx               # 3패널 레이아웃 (file-explore | chat | baby info)
      panels/               # 각 패널 컴포넌트 — 구현 미정
    package.json
  docs/
    specs/                  # 설계 스펙 (본 문서)
```

> `knowledge_base/`의 포맷(디렉토리·frontmatter·index/log 규칙)은 OKF 기반 스펙
> `docs/specs/02-knowledge-base-spec.md`가 권위를 가진다.
> `references/`(type: Reference, 공신력 있는 공개 가이드) vs `sources/`(type: Source, 직접 모은 자료)는
> 둘 다 producer의 fetch 입력이며, `knowledge_producer/`는 concept이 아니므로 번들(`knowledge_base/`) 밖 repo 루트에 둔다.

## 컴포넌트 설계

### 1. 위키 구축 = **agent skill 중심 + 보조 코드** (`knowledge_producer/`, 번들 밖, 별도 uv 워크스페이스 멤버)
- consolidation 등 판단이 필요한 단계는 **스킬 절차를 따라 에이전트가 수행.** fetch·`index.md` 생성처럼 결정적인 단계는 `src/`의 Python 보조 코드로 처리(구현 TBD).
- backend와 의존성을 격리하기 위해 자체 `pyproject.toml`을 가진 워크스페이스 멤버로 둔다. build-time 전용이라 backend 런타임 이미지에 섞이지 않는다.
- `topics.yaml`: 큐레이션한 주제 목록 (slug, 제목, 키워드, 출처 힌트).
- `SKILL.md`: "주제 1개 → `references/`·`sources/`에서 자료 수집 → consolidation → `knowledge_base/wiki/<slug>.md` 작성" 절차 정의. frontmatter는 KB 스펙(`docs/specs/02-knowledge-base-spec.md`)을 따름: `type: Wiki`(필수), `title`, `description`, `sources`, `timestamp`. `index.md`도 갱신.
- 사용: 위키가 필요하면 그 스킬을 호출해 주제별로 문서를 생성·커밋. (자동화 코드는 추후 필요 시.)

### 2. 백엔드 (`backend/`, FastAPI + Pydantic AI)
- **API 엔드포인트는 미정(TBD)** — 실행 단계에서 확정. 기능 요구만 고정:
  - file-explore용: 위키 목록·본문 제공 (읽기 전용).
  - chat용: **SSE 스트리밍** 채팅. 요청에 `messages[]` + 클라가 주입한 `baby_info` 포함.
- 채팅 동작:
  - 시스템 프롬프트에 아기정보 주입.
  - 에이전트가 `list_wiki()` / `read_wiki(slug)` 툴로 위키를 직접 탐색해 근거 확보 ("LLM이 알아서 검색").
  - Pydantic AI 스트리밍 출력을 SSE 이벤트로 흘려보냄.
- `config.py`: `QOOING_MODEL` 등 env로 모델 지정 → **BYOM** (Pydantic AI 모델 문자열).
- 무상태: 사용자/아기 DB 없음.

### 3. 프론트엔드 (`frontend/`, React + Vite SPA)
- **확정: 3패널 레이아웃** (file-explore | chat | baby info). 그 외 구현은 **TBD**.
- 각 패널의 역할(레이아웃 의도)만 고정:
  - **file-explore**: 위키 문서 읽기 전용 탐색·열람.
  - **chat**: 위키+아기정보 근거 스트리밍 채팅.
  - **baby info**: 아기 프로필 입력, 클라이언트 소유(localStorage) + import/export, 채팅 주입용.
- 컴포넌트 구조·상태관리·API 연동 방식은 실행 단계에서 확정.

### 4. LLM 레이어 (Pydantic AI)
- 단일 에이전트 정의, 모델은 설정 주입 → 어떤 provider든 교체 가능(BYOM).
- 툴: `list_wiki()`, `read_wiki(slug)`. consolidation과 chat 양쪽에서 재사용.
