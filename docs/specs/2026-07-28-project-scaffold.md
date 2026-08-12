# qooing 실행 가능 스캐폴드 명세

## 1. 목표 / Goal

qooing의 지식 번들, producer, API, LLM agent, 웹 UI, 컨테이너 경계를 실제로 실행 가능한
세로 단면(vertical slice)으로 제공한다. 기본 실행은 외부 자격 증명 없이 결정론적으로 동작하고,
`QOOING_MODEL`이 있으면 같은 agent 경계에서 실제 provider model을 사용한다.

**English recap:** Deliver a credential-free vertical slice whose production model can be swapped
in through configuration without changing API or UI contracts.

## 2. 시스템 경계 / System boundaries

- Python `>=3.14,<3.15`; 루트 uv workspace의 멤버는 `backend/`, `knowledge_producer/`다.
- frontend는 Bun lockfile을 소유하는 React/TypeScript/Vite SPA다.
- `knowledge_base/`는 Markdown/YAML frontmatter contract이며 producer와 backend가 구현을
  공유하지 않고 format만 공유한다.
- 서버는 계정, DB, profile, 대화 기록을 저장하지 않는다.

**English recap:** Producer and consumer stay independently implemented and communicate only through
the knowledge-bundle format.

## 3. Knowledge bundle과 producer

모든 bundle 디렉터리에 `index.md`가 필요하며 `references/`에는 최신순 reliability
`log.md`가 필요하다. concept은 디렉터리에 맞는 `type`, `title`, `description`,
ISO 8601 `timestamp`를 갖는다. Reference는 `resource`와 `reliability`, Source는 구체 문서
`resource`와 발행처를 가리키는 `reference`, Wiki는 Source만 가리키는 `sources`를 갖는다.
bundle 내부 symbolic link는 validation과 index 생성을 모두 거부한다.

- `qooing-kb validate <bundle>`: 모든 위반을 모아 출력하고 위반 시 exit 1.
- `qooing-kb index <bundle>`: concept title 기준 안정적 알파벳순 index 생성 후 검증.

URL fetch와 LLM consolidation은 이 단계의 범위 밖이다.

**English recap:** The producer validates the complete contract and deterministically rebuilds
indexes; acquisition remains an explicit future feature.

## 4. HTTP와 SSE contract

- `GET /api/health` → `{"status":"ok","chat_mode":"offline"|"configured"}`
- `GET /api/wiki` → `{slug,title,description}[]`
- `GET /api/wiki/{slug}` → `{slug,type,title,description,body,sources}`
- `POST /api/chat` body:
  `{"prompt":"non-empty","baby_info":{"name?":string,"birth_date?":"YYYY-MM-DD","notes?":string}}`

Chat response는 `text/event-stream`이며 각 event는 다음 중 하나다.

- `event: delta`, data `{"text":"incremental text"}`
- `event: done`, data `{}`
- `event: error`, data `{"message":"safe public message"}`

잘못된 request는 422, 없는 wiki는 404다. stream 시작 후 provider 오류는 `error` event로
노출하고 내부 예외나 secret은 포함하지 않는다. `name`은 최대 100자, `notes`는 최대
2,000자이며 빈 birth date는 미설정 값으로 정규화한다.

**English recap:** Chat is a stateless POST response streamed as explicit delta, done, and safe error
events.

## 5. Agent 동작

Agent dependencies는 read-only wiki store를 포함하고 `list_wiki`, `read_wiki` tools를
등록한다. 기본 `FunctionModel`은 두 tool을 실제 호출한 뒤 sample 문서의 title/description에
근거한 개발용 응답과 non-medical disclaimer를 출력한다. `QOOING_MODEL`이 설정되면 해당
Pydantic AI model string을 사용하고 `stream_text(delta=True)`로 전송한다.

**English recap:** Offline and provider-backed modes exercise the same agent and tool boundary.

## 6. Frontend 동작

세 panel은 wiki 탐색/Markdown 열람, 메모리 내 chat, baby profile 편집이다. UI가 표시하는
이전 대화는 server에 보내지 않고 현재 prompt와 profile만 보낸다. profile만 localStorage에
저장한다. import/export schema는 `{"version":1,"baby_info":{...}}`이며 잘못된 import는
기존 값을 변경하지 않는다. 세 profile field는 file에서 선택적이며 editor에서는 빈 문자열로
정규화한다. invalid date와 API 길이 제한을 넘는 field는 import 전에 거부한다. SSE client는
반드시 terminal `done` event를 받아야 성공으로 처리한다.

**English recap:** The browser owns profile persistence; the backend receives one prompt and one
profile per stateless request.

## 7. 컨테이너와 품질 기준

backend는 non-root Python 3.14 image, frontend는 Bun build 후 unprivileged nginx image다.
nginx는 `/api`를 backend로 proxy한다. Compose는 frontend `8080`, backend `8000`을 모두
공개하며 backend health 이후 frontend를 시작한다.

필수 local gate는 Ruff format/check, ty, pytest, ESLint, TypeScript, Bun test, Vite build,
`scripts/smoke-local.sh`, `scripts/smoke-compose.sh`다. GitHub Actions, dev container, 인증,
DB, ingestion, 배포 자동화는 제외한다.

**English recap:** Local quality gates and production-like images are included; CI and deployment
automation are not.
