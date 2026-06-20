# 설계 스펙

* [01 — 설계 개요](01-design-overview.md) - qooing의 기술스택·방법론·주요 기능 결정 문서
* [02 — Knowledge Base 포맷 스펙](02-knowledge-base-spec.md) - `knowledge_base/` 번들의 디렉토리·frontmatter·index/log 규칙 (OKF 기반)

# 규칙

* **파일명**: 날짜 prefix 없이 `NN-<feature>.md` 순번 prefix (읽는 순서 부여). 예: `03-backend-api.md`.
* **index 갱신**: 새 spec을 추가하면 위 목록에 `* [NN — 제목](NN-<feature>.md) - 한 줄 설명` 한 줄을 추가한다.
* **discoverability**: 이 디렉토리에는 항상 `index.md`를 둔다.
