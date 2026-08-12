---
type: Reference
title: 예방접종도우미
resource: https://nip.kdca.go.kr
reliability: 확실
description: 한국 국가예방접종(NIP) 표준 일정·기록 공식 포털 (KDCA 직영)
timestamp: 2026-06-21
---

## 등급 근거

예방접종도우미는 [질병관리청(KDCA)](/references/kdca.md)이 직접 운영하는 국가예방접종
전용 포털로, 한국 표준예방접종일정의 공식 발행처다. 공공기관 직영이므로 → **확실**.
운영 주체는 KDCA이나, 한국 NIP 일정의 1차 citation target으로서 독립 항목으로 둔다.

## 커버리지

- 다룸: 표준예방접종일정표, 예방접종 기록·증명, 지정 의료기관·이상반응 안내.
- 안 다룸: 감염병 일반 정보·통계는 본청 [KDCA](/references/kdca.md), 일반 육아는 범위 밖.

## fetch 특성

- 표준예방접종일정표는 **이미지(JPEG)로 제공**되어 WebFetch로 본문 텍스트를 뽑기 어렵다. curl로 바이너리를 받아 멀티모달/OCR로 텍스트를 추출하고 **원본 이미지와 대조 검증**해야 한다.
- 조회·증명 발급 등은 로그인·동적 페이지라 정적 fetch가 어렵다.
- robots/접근 정책은 본청에 준한다.
