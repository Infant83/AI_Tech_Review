# Skywork Prompt V1

업로드된 자료와 새 템플릿을 기반으로 `정확히 4개의 content slide`만 생성하라.

## 프로젝트 개요
- 프로젝트명: `Palantir 심층 검토 및 자사 도입 논의용 4-Page 브리핑`
- 청중: `부회장 및 경영진`, `AX/IT/제조 전략 실무 리더`
- 목적: `2026-04-27` Palantir 경영진 미팅 전, 보안·삼성·계열사·자사 도입 방안을 근거 중심으로 판단하고 질문할 수 있게 하는 토론형 briefing deck 작성
- 언어: `한국어`
- 비율: `16:9`

## 최우선 템플릿 규칙
- 이번 작업은 기본 LGD 템플릿이 아니라 사용자가 새로 넣어둔 `Template_4pages_new.pptx`를 우선 템플릿으로 사용하라.
- 업로드된 `Template_4pages_new.pptx`의 visual rhythm과 box system을 유지하되, 실제 narrative는 `4 content pages`로만 구성하라.
- 표지 슬라이드, 목차 슬라이드, appendix 슬라이드를 추가하지 말라.
- 결과물은 `Slide 1`부터 `Slide 4`까지 모두 본문 장표여야 한다.

## 업로드 우선순위
1. `sources/ppt_template/Template_4pages_new.pptx`
2. `reports/2026-04-16_palantir_4page_briefing_document.md`
3. `reports/2026-04-16_palantir_4page_slides.md`
4. `notes/2026-04-16_palantir_4page_sources.md`
5. `reports/2026-04-15_palantir_factcheck.md`
6. `reports/2026-04-15_palantir_recent_2026_cases.md`

## 핵심 서사
- 이 deck은 Palantir를 홍보하는 자료가 아니다.
- 이 deck의 목적은 `도입 확정`이 아니라 `무엇이 사실이며, 어디까지 공개 근거가 있고, 자사에서는 어떤 PoC를 먼저 검증해야 하는가`를 판단하게 하는 것이다.
- 전체 구조는 내부 회의 지시를 반영한 `보안`, `삼성/경쟁사 및 시장 신호`, `계열사 readiness와 비용`, `자사 PoC 선정 프레임`의 4개 축으로 고정한다.

## 슬라이드별 목표

### Slide 1. 보안·데이터주권·온톨로지 구축 방식
- headline:
  - `고위험 제조데이터에서도 핵심은 AI 사용 여부가 아니라 어디에 두고 어떤 권한·행위통제로 운영하느냐다`
- 반드시 포함:
  - on-prem / air-gapped
  - private cloud
  - optional managed LLM for low-risk data only
  - customer-controlled ontology layer
  - 장점과 남는 어려움의 균형
- 강조할 것:
  - LGD와 같은 고위험 제조사에서는 보안 위협 없이 사용할 수 있는 구조적 장점
  - raw data 외부반출 없이도 ontology/workflow 설계가 가능하다는 점
- 피할 것:
  - `on-prem이면 끝` 같은 단순화

### Slide 2. 삼성은 signal case, LG/현대는 public reference case
- headline:
  - `2025-2026 제조 AI 경쟁은 chatbot이 아니라 ontology·workflow·digital twin·operations intelligence로 이동 중`
- 반드시 포함:
  - 2024 삼성 DX PoC
  - 2024 Microsoft 선정
  - 2025 Samsung AI Forum
  - 2026 DS AI Center KG hiring signal
  - 2026 GTC agentic AI + digital twin
  - LG CNS partnership
  - HD Hyundai expansion
- 표현 원칙:
  - 삼성은 `Signal vs Proof` 구조로 보여라
  - LG와 HD Hyundai는 공개 레퍼런스 축으로 보여라
- 피할 것:
  - 삼성 2nm 수율 개선을 Palantir 효과로 단정

### Slide 3. 계열사 readiness 및 비용 검토 outline
- headline:
  - `계열사 readiness는 동일하지 않다. 현 단계에서는 stage·문제영역·비용구조를 함께 보는 working outline이 필요하다`
- 반드시 포함:
  - LG CNS / LG Energy Solution / LG Innotek / LG Electronics / 자사(LGD)
  - stage, 문제영역, 공개근거 수준, 비용메모, 추가코멘트
  - commentable blank area
- 표현 원칙:
  - 일부 status와 비용은 내부회의 기반 추정이므로 working outline 톤으로 작성
  - user가 나중에 코멘트를 달기 쉽도록 표를 너무 꽉 채우지 말고 comment cell을 남겨라

### Slide 4. 자사 도입방안과 PoC 선정 프레임
- headline:
  - `도입 판단의 핵심은 어디에서 가장 빨리, 가장 안전하게, 가장 설명 가능한 운영 성과를 증명할 수 있는가다`
- 반드시 포함:
  - 평가기준: 효과성, 검증 가능성, 데이터 준비도, 보안 적합성, 확장성, 비용 부담, ontology 재사용성, 조직 수용성
  - 후보영역: 품질/Q-Cost, 공정 이상탐지+원인분석, 안전 leading indicator, 설비 예지보전, SCM/병목 대응, R&D/실험지식 연결
  - shortlist: 품질/Q-Cost, 공정 이상탐지+원인분석, 안전 leading indicator
- 피할 것:
  - 추상적인 `AI 혁신 필요` 같은 문장
  - 전사 rollout 제안

## 시각 및 편집 규칙
- 정보 밀도는 높게 유지하라.
- 각 슬라이드는 `주장 -> 근거 -> 시사점` 구조로 읽혀야 한다.
- `작은 짙은 녹색 annotation text`를 적극 써서 용어정의, caveat, 보안 메모를 붙여라.
- `작은 짙은 회색 source footer`를 각 슬라이드에 넣어라.
- 표, 타임라인, evidence matrix, candidate matrix를 적극 사용하라.
- 장식용 이미지나 과장된 배경 이미지는 넣지 말라.
- 템플릿의 box system과 corporate rhythm은 유지하되, 빈 공간이 과도하지 않게 채워라.

## 사실성 규칙
- 공개 확인된 사실과 내부 신호를 혼동하지 말라.
- 삼성은 `public proof 부족`을 명시적으로 남겨라.
- LG/현대는 상대적으로 근거가 강함을 보여라.
- 비용은 `seat price`처럼 단순화하지 말고 enterprise contract 구조로 설명하라.

## 최종 산출물 규칙
- 정확히 4개의 본문 슬라이드만 생성
- 별도 appendix 금지
- 별도 cover 금지
- 각 슬라이드는 독립적으로 읽혀야 하지만, 4장을 연속해서 보면 `보안 -> 시장신호 -> readiness/cost -> PoC decision`으로 자연스럽게 흐르도록 구성하라
