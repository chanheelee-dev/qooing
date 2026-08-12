# Knowledge Producer — 역할과 스킬 경계

> bundle 형식은 [Knowledge Base 포맷 스펙](02-knowledge-base-spec.md)과
> [Reference 타입](2026-08-12-reference-type.md)이 정의한다. 이 문서는 bundle을 만드는
> producer의 역할 경계만 정의한다.

## Producer 구성

판단이 필요한 절차는 `knowledge_producer/skills/`의 agent skill로, 반복 가능하고 기계적인
검증과 index 생성은 `knowledge_producer/src/`의 Python 코드로 처리한다.

| 스킬 | 쓰기 소유권 | 읽기 입력 |
| --- | --- | --- |
| `register-reference` | `references/<slug>.md`, index, log | 기존 bundle 전체 |
| `fetch-source` | `sources/<slug>.md`, index | `references/` |
| `write-wiki` | `wiki/<slug>.md`, index | `sources/`, `references/` |

각 스킬의 상세 절차는 해당 `SKILL.md`가 단일 출처다. editor나 agent 제품에 노출하기 위한
설정은 canonical skill을 복제하지 않고 이 디렉터리를 가리켜야 한다.

## 불변식

1. `register-reference`만 `reliability`와 reference audit log를 바꾼다.
2. `fetch-source`는 구체 문서 하나를 Source로 보존하고 정확히 한 Reference를 가리킨다.
3. `write-wiki`는 Source를 수정하지 않고 `sources` frontmatter와 본문 링크로 인용한다.
4. 각 변경 뒤 `qooing-kb index`와 `qooing-kb validate`를 실행한다.

## 의존 순서

새로운 provenance chain은 다음 순서로 만든다.

```text
register-reference -> fetch-source -> write-wiki
```

이미 등록된 발행처나 Source가 있으면 해당 앞 단계를 재실행하지 않는다.
