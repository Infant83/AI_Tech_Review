---
title: AI Updates Weekly Final Review Rewrite Audit
date: 2026-05-09
type: audit-note
topic: ai-updates-weekly
status: completed
tags:
  - audit
  - rewrite
  - writing-harness
  - final-review
---

# AI Updates Weekly Final Review Rewrite Audit

## 기준

이번 감사는 다음 작업공간 정책을 기준으로 한다.

- `AGENTS.md`의 Korean Human Writing Style Rules
- `.automation/writing-style-audit-harness.md`
- final-review article rule
- emphasis hierarchy: links, bold, italic, underline, roman/upright, code
- Quanta-style article pattern: message-led title/dek, early hero figure, captioned visuals, narrow readable body, mid-article diagrams or pull quotes
- English-term audit: generic English work words는 한국어로 풀고, 남겨야 하는 기술어는 첫 등장 설명을 붙인다.

## 현재 리뷰의 강점

- 첫 문단에서 하네스 전환이라는 메시지가 보인다.
- Lev Selector 영상 자체가 아니라, 영상에서 잡은 주제의식을 출발점으로 논문과 공식 자료를 다시 엮고 있다.
- 도입부에 독자 장면이 있다. 코드 수정, 테스트, 되돌리기, 병합 충돌 같은 업무 장면이 하네스 개념으로 자연스럽게 이어진다.
- `보류할 신호` 같은 작성 과정 중심 섹션은 final review에서 제거되어 있다.
- 공식 발표, arXiv 논문, 저장소 문서, 제품 문서가 References에 분리되어 있다.
- imagegen hero artwork가 들어가며 article-like visual entry가 생겼다.

## 부족한 지점

### 1. 본문 중반 이후가 아직 actor-by-actor survey에 가깝다

현재 구조는 `논문 -> Anthropic -> Connector -> 오픈소스 -> 개발자 도구 -> 의료` 순서다. 흐름은 자연스럽지만, 중반 이후에는 주장이 전진한다기보다 근거 묶음을 차례로 설명하는 느낌이 강하다.

재작성에서는 actor 중심이 아니라 논점 중심으로 다시 묶는 편이 좋다.

- 하네스가 연구 대상이 된 이유
- 기업용 AI가 connector, permission, approval로 이동하는 이유
- 장기 실행 에이전트에는 memory hygiene과 evaluation loop가 필요한 이유
- 개발자 도구에서 병목이 생성에서 병합과 되돌리기로 이동하는 이유
- 더 많은 에이전트가 항상 좋은 답이 아닌 이유

### 2. visual program이 hero 한 장에서 멈춘다

현재 hero image는 주제 진입에는 좋다. 다만 정책이 요구하는 Quanta-style figure 흐름으로 보면 중간 도식이 부족하다.

추가 후보:

- `Harness Stack` 도식: Model core / context / tools / memory / permission / evaluation / approval / merge
- `Evidence Map` 도식: papers / companies / open-source / developer tools / domain safety
- `Orchestration Decision` matrix: 한 모델로 처리할 작업 vs 여러 에이전트로 나눌 작업
- `Developer Bottleneck` flow: generate -> test -> review -> merge -> rollback

정확한 구조와 비교를 담는 자료이므로 imagegen보다 SVG/HTML deterministic diagram이 맞다.

### 3. English-term audit가 아직 덜 끝났다

남겨도 되는 용어와 바꿔야 하는 용어가 섞여 있다.

남길 수 있는 용어:

- 제품명, 논문명, 저장소명, MCP, OAuth, LangGraph, Claude Code, Zed, Jujutsu, Mergiraf, Weave

다시 볼 용어:

- `controller code`: 구현 제어 코드 또는 컨트롤러 코드로 풀어쓰기
- `pitchbook`, `KYC screening`, `agent template`: 업무 맥락 설명 필요
- `memory store`, `grader`, `compute capacity`, `rate limit`, `peak-hour reduction`: 첫 등장 설명 또는 자연스러운 한국어 문장 필요
- `shell`, `git`, `RLM`, `LSP diagnostics`, `session resume`: 목록에만 두면 기술어 나열로 보임
- `multi-agent system`, `AI gateway`, `native GPU-accelerated Rust app`, `entity-level semantic merge driver`: 남길 경우 짧은 설명 필요

### 4. 강조 계층은 도입부에만 선명하다

현재 bold는 첫 핵심 문장에 잘 쓰였다. 다만 본문 각 섹션의 전환점에는 독자가 붙잡을 문장이 부족하다. 정책상 bold를 남발하면 안 되지만, 각 큰 논점마다 한 문장 정도는 메시지를 잡아주는 편이 낫다.

예:

- `하네스는 모델 밖의 보조 장치가 아니라, 에이전트 성능을 바꾸는 설계 대상입니다.`
- `기업용 에이전트의 핵심은 답변 능력보다 업무 도구 안에서 남길 수 있는 권한과 승인 표면입니다.`
- `AI 코딩의 병목은 생성 속도보다 변경을 합치고 되돌리는 구조로 옮겨갑니다.`

### 5. 근거 지도와 신뢰도 표기가 약하다

현재 `한눈에 보는 흐름` 표는 유용하지만, source strength를 보여주지는 않는다. final review policy는 근거 지도와 검증 경로를 더 명시적으로 요구한다.

다음 형태가 더 좋다.

| 근거 축 | 대표 소스 | 소스 성격 | 리뷰에서의 역할 |
|---|---|---|---|
| 하네스 연구 | arXiv 논문 2편 | 연구 논문 | 하네스를 성능 결정 구조로 해석 |
| 기업용 작업면 | Anthropic 공식 발표 | 공식 제품 발표 | connector, approval, managed agents 흐름 확인 |
| 업무 데이터 연결 | xAI 문서 | 공식 문서 | connector가 사용자 표면이 되는 흐름 확인 |
| 개발자 병목 | Zed/Jujutsu/Mergiraf/Weave 문서 | 저장소/제품 문서 | merge, rollback, coordination 병목 확인 |

### 6. 마무리가 조금 길고 다시 요약하는 느낌이 있다

결론의 방향은 맞다. 다만 `지금까지 ... 살펴보았습니다` 이후 사례를 다시 나열하는 부분이 길어져 본문 요약처럼 읽힌다. 재작성에서는 마무리를 세 가지 질문으로 닫는 편이 더 좋다.

- 이 AI 도구는 어떤 데이터를 안전하게 연결하는가?
- 실패했을 때 누가 확인하고 어떻게 되돌리는가?
- 여러 에이전트가 만든 변경을 어떻게 합치는가?

마지막 문장 `이 모델을 어떤 하네스 안에서 일하게 할 것인가?`는 유지할 가치가 있다.

### 7. hero caption이 아직 작업 로그처럼 보인다

현재 caption은 `Image generated with ChatGPT imagegen`을 직접 말한다. 작성 정보에는 맞지만, figure caption에서는 약간 작업 과정이 튀어나온다.

권장:

`그림 1. 하네스는 모델을 둘러싼 실행 구조입니다. connector, memory, permission, verification, merge 같은 장치가 함께 있어야 모델은 실제 업무 흐름 안에서 일을 끝낼 수 있습니다.`

작성 정보에서만 imagegen 사용을 언급한다.

## 재작성 방향

기조는 유지한다.

- 친근하게 들어간다.
- 쉬운 업무 예시로 기술어를 연다.
- 결론은 초반에 보여준다.
- Lev Selector보다 하네스 전환이라는 주제를 앞에 둔다.
- 근거는 논문과 공식 자료 중심으로 둔다.

구조는 다음처럼 바꾼다.

1. Hero + title + 하네스 전환 메시지
2. 모델 순위표 다음에 보이는 병목
3. 하네스는 무엇인가: AI의 작업 환경
4. 논문들이 하네스를 성능 결정 구조로 다루기 시작했다
5. 기업은 connector, permission, approval을 제품 표면으로 올린다
6. 장기 실행 에이전트에는 memory hygiene과 평가 루프가 필요하다
7. 오픈소스 하네스는 파일, 명령, 재개, 스킬 관리로 실험된다
8. 개발자 도구의 병목은 생성보다 병합과 되돌리기다
9. 더 많은 에이전트가 항상 답은 아니다
10. 이 흐름을 어떻게 읽을 것인가

## 재작성 완료 기준

- 첫 화면에서 title, subtitle, hero image, thesis가 함께 보인다.
- 첫 5문단 안에 하네스의 쉬운 설명과 독자 장면이 있다.
- actor list가 아니라 argument flow로 읽힌다.
- source labels는 본문 첫 언급에서 링크로 보인다.
- generic English work words는 줄고, 남긴 English term은 설명이 있다.
- 중간에 최소 1개 deterministic diagram 또는 evidence map이 추가된다.
- 결론은 사례 나열보다 독자 질문과 판단 프레임으로 닫힌다.

## 재작성 반영 결과

- `reports/2026-05-09_ai-updates-weekly_final_review.md`를 논점 중심 구조로 재작성했다.
- `artifacts/final_review/figures/harness-stack.svg`를 추가해 하네스 구성 요소를 deterministic diagram으로 보강했다.
- hero caption에서 생성 로그처럼 보이던 문장을 제거하고, 작성 정보에서만 imagegen 사용을 언급하도록 정리했다.
- `이번 리뷰는`, `결론적으로`, `요컨대`, `핵심은`, `보류할 신호`, 반복적 `아니라/아닙니다` 패턴 검색을 통과했다.
- HTML companion을 다시 렌더링했고, Obsidian mirror에도 markdown/html/figure assets를 동기화했다.
