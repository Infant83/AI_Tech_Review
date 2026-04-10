---
title: Ralph Loop Log - Industry-Specialized Agentic AI Roundtable
date: 2026-03-22
tags:
  - ralph-loop
  - qa
  - presentation
---

# Ralph Loop Log

## Round 1
- Target:
  - source note
  - memo
  - deep research report
  - NotebookLM source pack
  - presentation webpage
- Quality bar:
  - 한국어 기준으로 빠르게 읽히는 구조
  - 사실과 해석이 구분된 보고서
  - 산업 특화 Agentic AI에 대한 실행 가능한 관점
  - 로컬 웹페이지로 시각화 가능

### Findings
- 영상 핵심은 잘 정리되었지만, 단순 요약에 머물지 않도록 외부 공식 자료와 연결할 필요가 있었다.
- 웹페이지는 생성 직후 브라우저 실검증이 필요했다.

### Actions
- Anthropic, MCP, Google A2A, UiPath, Salesforce, 한국 정책 자료를 추가 검증 소스로 연결했다.
- `index.html`을 생성해 핵심 메시지를 프레젠테이션 형태로 재구성했다.

## Round 2
- Inspection surface:
  - Playwright CLI full-page desktop screenshot
  - Playwright CLI full-page mobile screenshot

### Findings
- 데스크톱은 즉시 사용 가능한 수준이었다.
- 모바일에서 히어로 타이포가 다소 과도하게 크게 보였다.

### Actions
- 모바일 media query에서 `h1` 폰트 크기와 line-height를 조정했다.
- `index.html` 상단 상태를 `Round 2 check complete`로 갱신했다.

## Round 3
- Inspection surface:
  - NotebookLM ad-hoc notebook upload and Q&A
  - NotebookLM automation retry for export feasibility
  - report and webpage synthesis update

### Findings
- NotebookLM은 동일 소스 기준으로도 `workflow operating layer`, `공공 reference workflow`, `trust layer`를 핵심 전략으로 다시 압축했다.
- 금지사항도 명확했다. 거대 플랫폼 선행 투자, UI-only 버티컬, human escalation 없는 자동화는 위험하다.
- NotebookLM 슬라이드/인포그래픽 export 자동화는 활성 Chrome 프로필 충돌 때문에 끝까지 안정화되지 않았다.

### Actions
- NotebookLM Q&A 로그를 별도 노트로 저장했다.
- memo, deep research, `index.html`에 NotebookLM cross-check 블록을 추가했다.
- export 실패 사유를 로그에 남기고, 패키지 안에는 업로드 이후 NotebookLM 스크린샷을 보존하기로 했다.

## Round 4
- Inspection surface:
  - slide + infographic presentation page
  - Playwright desktop screenshot
  - Playwright mobile screenshot

### Findings
- 기존 메인 페이지는 분석 리포트로는 충분했지만, 발표형 시각 요약은 별도 페이지가 더 읽기 쉬웠다.
- 한 화면에서 슬라이드 흐름과 인포그래픽 요약을 같이 보여주는 구성이 경영진 브리프 용도로 더 적합했다.
- 데스크톱과 모바일 모두에서 핵심 메시지는 유지되며, 모바일에서도 카드 단위로 끊어 읽히는 수준이다.

### Actions
- `visual_brief.html`을 추가해 슬라이드형 요약과 인포그래픽형 요약을 한 페이지에 통합했다.
- Playwright로 `visual-brief-desktop.png`, `visual-brief-mobile.png`를 생성해 실제 렌더링을 확인했다.
- 메인 `index.html`에 `Slides + Infographic` 링크를 추가했다.

## Current Status
- High severity issue: 없음
- Medium severity issue: NotebookLM 슬라이드/인포그래픽 export는 아직 미완료
- Low severity issue: 활성 Chrome 세션이 정리되면 NotebookLM native export 자동화를 다시 시도할 수 있음
