# React, Vite, and Bun

## Mental model

React state는 화면의 현재 snapshot이고 effect는 외부 system과 동기화한다. Vite는 개발 중
module server와 `/api` proxy를 제공하고 production에서는 static bundle을 만든다. Bun은
dependency resolution, lockfile, scripts, native test runner를 소유한다.

**English recap:** React owns UI state, Vite owns development/build behavior, and Bun owns the
frontend toolchain.

## qooing state

- wiki 목록/document: server에서 다시 가져올 수 있는 state.
- chat messages: page lifetime만 유지하는 memory state.
- baby profile: localStorage에만 영속화하는 client-owned state.
- SSE parser: network chunk를 protocol event로 바꾸는 framework-independent library.

Profile import는 optional field를 editor용 빈 문자열로 정규화하고 date/길이를 API와 같은
규칙으로 검증한다. SSE는 완성된 frame만 받았더라도 `done` 없이 연결이 끝나면 실패다.

```bash
cd frontend
bun install --frozen-lockfile
bun run dev
bun run test
bun run typecheck
bun run build
```

## Common mistakes

- render 중 localStorage를 계속 쓰는 문제. 사용자 변경 event에서 저장한다.
- `response.text()`로 전체 SSE response를 기다리는 문제.
- Vite dev proxy가 production에도 존재한다고 생각하는 문제. production proxy는 nginx다.

## Try it

SSE parser test의 JSON 한가운데 chunk를 한 번 더 나누고 결과가 동일한지 확인한다. profile을
export한 뒤 version을 2로 바꿔 import가 기존 profile을 보존하는지 확인한다.

## Further reading

- [React state](https://react.dev/learn/managing-state)
- [Vite guide](https://vite.dev/guide/)
- [Vite proxy options](https://vite.dev/config/server-options.html#server-proxy)
- [Bun package manager](https://bun.com/docs/pm)
- [Bun test runner](https://bun.com/docs/test)
