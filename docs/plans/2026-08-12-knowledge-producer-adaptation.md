# Knowledge producer 구조 적응 계획

## 목표

`kb-skills` worktree에서 만든 Reference registry와 producer 역할 분리를 현재 실행 가능한
qooing scaffold에 맞게 이식한다. 브랜치를 병합하지 않고 현재 validator, index generator,
sample bundle을 함께 갱신한다.

## 작업

- [x] Reference를 발행처 단위 신뢰 registry로 명확히 하고 `timestamp` 필드로 통일한다.
- [x] `Wiki -> Source -> Reference` provenance를 validator가 검사하게 한다.
- [x] `references/index.md`를 신뢰도 등급별로 결정적으로 생성한다.
- [x] 기존 Reference registry를 이식하고 sample Source를 추가한다.
- [x] producer 절차를 `register-reference`, `fetch-source`, `write-wiki` 스킬로 분리한다.
- [x] 문서 링크, formatter, linter, type checker, test, bundle validation을 통과한다.

## 범위 밖

- 외부 사이트의 최신 내용 및 신뢰도 재심사
- 네트워크 fetch 구현
- LLM 기반 wiki consolidation 자동화
