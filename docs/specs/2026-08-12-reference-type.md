# Reference 타입 — 발행처 신뢰 registry

> `knowledge_base/references/`의 qooing 전용 규칙이다. 공통 bundle 규칙은
> [Knowledge Base 포맷 스펙](02-knowledge-base-spec.md)을 따른다.

## 역할과 단위

`Reference`는 본문 지식이 아니라 발행처의 provenance와 신뢰 판단을 기록하는 registry
concept이다. 구체적인 문서 본문은 `Source`가 보존하고, `Wiki`는 그 Source를 인용한다.

```text
Reference (발행처 신뢰) <- Source (구체 문서) <- Wiki (통합된 주장)
```

- 도메인 또는 독립 포털 하나를 파일 하나로 등록한다.
- 같은 운영 주체라도 콘텐츠와 canonical domain이 분리된 포털은 별도 Reference다.
- 같은 콘텐츠의 redirect나 URL 경로 차이는 새 Reference가 아니다.

## Frontmatter

qooing validator는 registry 운영에 필요한 다음 필드를 요구한다.

```yaml
---
type: Reference
title: 질병관리청 (KDCA)
description: 예방접종·감염병 정보 공식 출처
resource: https://www.kdca.go.kr
reliability: 확실
timestamp: 2026-08-12T00:00:00+09:00
---
```

`reliability`는 다음 값 중 하나다.

| 등급 | 기준 |
| --- | --- |
| `확실` | 공공기관, 전문학회, 공식 의료기관 등 해당 분야의 직접 권위 |
| `유력` | 전문가가 검수·운영하지만 직접 공식 권위보다 한 단계 낮은 발행처 |
| `참고` | 단독 근거로 사용하지 않고 보조로만 사용하는 발행처 |

등급은 개별 글의 정확성이 아니라 발행처의 운영·보증 주체에 대한 판단이다. 자동 제안은
가능하지만 등록과 등급 변경은 관리자가 승인한다.

## Body convention

본문에는 다음 내용을 기록하는 것을 권장한다.

- 등급 근거
- 잘 다루는 주제와 다루지 않는 주제
- robots, paywall, JavaScript rendering, 언어 같은 fetch 특성

## Index와 log

`references/index.md`는 `확실`, `유력`, `참고` 순서로 묶고 각 그룹 안에서는 title
알파벳순으로 생성한다. `references/log.md`는 최신 날짜부터 다음 사건을 기록한다.

- **Register**: 신규 등록
- **Unregister**: 신뢰 철회 및 제거
- **Reliability**: 등급 변경
- **Update**: URL, coverage, fetch 특성 등 갱신
