# Knowledge bundle

## Mental model

`knowledge_base/`는 database가 아니라 Git으로 배포되는 self-contained Markdown bundle이다.
YAML frontmatter는 machine-readable routing metadata이고 body는 사람이 읽는 지식이다.
directory hierarchy와 Markdown link가 discovery graph를 만든다.

**English recap:** Markdown is the storage and interoperability contract, not merely presentation
content.

## qooing rules

`references/`는 발행처 신뢰 판단을 audit log와 함께 기록하고, `sources/`는 구체 문서와
그 발행처 연결을 보존하며, `wiki/`는 Source를 인용한 consolidated output이다. 모든 directory에 `index.md`, reference scope에
`log.md`, 모든 concept에 directory와 맞는 `type`이 필요하다.
audit log의 date heading은 `YYYY-MM-DD` 최신순이고 bundle 내부 symbolic link는 허용하지 않는다.

```bash
uv run --package qooing-producer qooing-kb validate knowledge_base
uv run --package qooing-producer qooing-kb index knowledge_base
```

## Common mistakes

- wiki body 주장에는 citation이 있지만 frontmatter `sources`를 갱신하지 않는 문제.
- Wiki에서 구체 Source를 건너뛰고 발행처 Reference를 곧바로 근거로 삼는 문제.
- bundle-root link `/references/x.md`를 filesystem root로 해석하는 문제.
- generator 실행 후 검증하지 않아 깨진 source를 놓치는 문제.

## Try it

sample wiki의 source 이름을 일부러 틀리고 validator가 모든 위반을 함께 보고하는지 확인한 뒤
원복한다.

## Further reading

- [qooing Knowledge Base specification](../specs/02-knowledge-base-spec.md)
- [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [YAML specification](https://yaml.org/spec/)
