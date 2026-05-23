---
title: AI Updates Weekly Editorial Graphics Audit
date: 2026-05-09
status: active
auditor: graphics-placement-agent
scope:
  - reports/2026-05-09_ai-updates-weekly_final_review.md
  - artifacts/final_review/figures/
  - skywork_inputs/
---

# Editorial Graphics Audit

## 결론

현재 `final_review`는 그림 수 자체는 충분합니다. Hero 1개, 구조 SVG 3개, 본문 bitmap illustration 2개가 들어가 있으며, `hero + 핵심 개념도 + 참고자료 맵 + 복잡 구간 판단/프로세스 figure` 기준을 대체로 충족합니다.

다만 아래 세 구간은 본문에 비해 시각적 받침이 약합니다.

1. `오래 실행되는 에이전트에는 기억 관리와 평가 루프가 필요합니다`
2. `Connector는 업무 데이터와 AI를 연결하는 첫 관문입니다`
3. `의료처럼 위험한 영역에서는 하네스가 안전장치가 됩니다`

이 구간은 모두 추상도가 높습니다. 따라서 독자의 이해를 돕는 작은 loop/process figure가 있으면 글이 더 편하게 읽힙니다.

## 현재 충분한 지점

| 구간 | 현재 그림 | 판단 |
|---|---|---|
| 도입부 | `agent-harness-hero-v2-web.png` | 주제형 hero로 적절합니다. 권한, 체크리스트, connector, 작업 엔진이 보입니다. |
| 하네스 설명 | `harness-stack.svg` | 하네스 구성요소를 정확히 보여줍니다. |
| 참고자료 연결 | `reference-map.svg` | 논문, 기업 발표, 오픈소스, 개발자 도구 흐름을 묶어줍니다. |
| 기업용 AI | `enterprise-harness-illustration-v2-web.png` | 권한/검토/감사 기록의 분위기와 메시지가 맞습니다. |
| AI 코딩 병목 | `coding-merge-illustration-web.png` | 테스트, 리뷰, 병합, 되돌리기 메시지를 잘 받칩니다. |
| 오케스트레이션 | `orchestration-matrix.svg` | 에이전트 수보다 작업 구조가 먼저라는 판단 기준을 제공합니다. |

## 부족한 구간과 권장 figure

| 우선순위 | Figure | 위치 | 권장 도구 | 이유 |
|---:|---|---|---|---|
| 1 | Memory / Evaluation Loop | `memory-evaluation` 섹션 | deterministic SVG 또는 Skywork `인포그래픽` | Dreaming, Outcomes, 기억 정리, 평가, 재시도는 순환 구조라 loop figure가 적합합니다. |
| 2 | Connector Permission Surface | `connectors` 섹션 | Skywork `인포그래픽` 또는 SVG cutaway | connector가 사용자에게는 편의 기능, 관리자에게는 권한/감사/민감 데이터 제어점이라는 이중성을 보여줄 수 있습니다. |
| 3 | High-risk Domain Safety Harness | `domain-safety` 섹션 | deterministic process map 또는 Skywork `인포그래픽` | Planner/Talker, 근거 확인, 안전 경계, 사람 검토를 순서로 보여주면 하네스가 안전장치라는 결론이 더 선명해집니다. |
| 4 | Open-source Harness Capability Matrix | `open-source-harness` 섹션 | compact HTML table 또는 SVG matrix | DeepSeek-TUI, Hermes, OpenSwarm, InsForge가 어떤 실행층을 건드리는지 비교할 수 있습니다. |
| 5 | Closing Checklist Figure | 결론 직전 | small recap panel | 새 정보를 넣기보다 세 가지 질문을 회수하는 역할입니다. |

## 도구 역할

| 도구 | 이번 리뷰에서의 역할 |
|---|---|
| imagegen | hero와 본문 중간의 주제형 illustration. 독자가 쉬어갈 수 있는 기사형 장면. |
| Skywork Image | 정보형 editorial infographic. memory loop, connector permission surface, domain safety flow 같은 개념 설명 후보. |
| deterministic SVG/HTML | 정확한 라벨, 비교, 참고자료 맵, 판단 매트릭스. |
| NotebookLM | 참고자료 기반 요약 후보. watermark와 텍스트 오류가 있으면 본문 미채택. |

## 적용 판단

현재 리뷰에는 이미 6개 figure가 있으므로, 바로 5개를 모두 추가하면 과해질 수 있습니다. 우선순위는 아래가 적절합니다.

1. Skywork `인포그래픽`으로 `Memory / Evaluation Loop` 후보를 만듭니다.
2. Skywork `인포그래픽` 또는 deterministic SVG로 `Connector Permission Surface` 후보를 만듭니다.
3. `High-risk Domain Safety Harness`는 짧은 deterministic process map으로 처리합니다.

이렇게 하면 SVG만 반복되는 느낌을 줄이고, `imagegen`과 다른 역할의 Skywork 이미지가 본문 중간에서 설명력을 보탤 수 있습니다.

## 채택 기준

- 인접 문단의 핵심 메시지가 그림만 봐도 추정됩니다.
- 이미지 내부에 가짜 텍스트, 잘못된 한국어, 가짜 로고가 없습니다.
- prompt, project/artifact URL, 원본 export, 후보 복사본, 선택 이유가 남아 있습니다.
- caption은 “무엇을 보여주는가”보다 “독자가 이 그림으로 무엇을 이해하면 되는가”를 말합니다.
- 모바일/데스크톱 HTML에서 crop, overlap, 너무 작은 글자 문제가 없습니다.
