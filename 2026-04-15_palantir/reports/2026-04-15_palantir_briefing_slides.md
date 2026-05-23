# Palantir 보고자료 슬라이드 원고

목적: `2026-04-27` Palantir 경영진 미팅 전 사전 briefing  
권장 분량: 11~12 slides  
장표 원칙: `보안`, `삼성`, `계열사`, `자사 도입 방안` 4개 축을 중심으로 하되, 맨 앞에 압축 장표를 따로 둔다.

## Deck Narrative
- CH00: 2장 안에 전체 판단을 압축
- CH01: Palantir를 어떤 플랫폼으로 봐야 하는지 정의
- CH02: 보안과 비용을 판단 프레임으로 정리
- CH03: 삼성과 국내 제조업 레퍼런스를 분리해 비교
- CH04: 자사 POC 제안으로 수렴

## Slide 1. Cover
### Title
`Palantir 검토 및 자사 적용 가능성 사전 브리핑`

### Subtitle
- `2026-04-27 경영진 미팅 대비`
- `보안 / 삼성 흐름 / 국내 제조업 사례 / 자사 POC 제안`

### Layout hint
- 좌측 상단 제목
- 우측 하단에는 작은 짙은 회색 글씨로 작성일과 작성부서

## Slide 2. Executive Compression
### Main message
`지금 단계의 권고안은 전사 도입 검토가 아니라, 품질/Q-Cost 중심의 좁은 POC 검증이다.`

### Body
- Palantir는 LLM 공급사보다 `ontology + workflow + governed AI` 중심 운영 플랫폼으로 보는 것이 맞다.
- 국내 제조업 공식 레퍼런스는 `LG CNS`, `HD Hyundai`가 가장 강하다.
- 삼성은 강한 신호는 있으나 `direct public proof`는 아직 약하다.
- 비용은 정찰형 SaaS보다 `협상형 엔터프라이즈 계약 + 서비스 동반형` 구조다.

### Annotation
- `삼성 production adoption은 공개 근거상 아직 미확정`

### Sources
- Palantir 10-K
- LG CNS release
- Reuters/HD Hyundai
- ETNews Samsung

## Slide 3. Decision Frame
### Main message
`이번 미팅의 질문은 도입 여부가 아니라, 어떤 운영 문제를 어떤 POC로 검증할지다.`

### Body
- 판단 질문 1: 보안과 배포 방식이 실제로 설명 가능한가
- 판단 질문 2: 국내 제조업에서 reference quality가 충분한가
- 판단 질문 3: 자사에서 가장 먼저 검증할 가치가 있는 영역은 어디인가
- 판단 질문 4: pilot -> 본계약 비용 구조와 기간은 어떤가

### Visual hint
- 4-quadrant question board

## Slide 4. What Palantir Actually Is
### Main message
`Palantir의 핵심은 모델이 아니라 운영 의사결정 구조를 데이터와 워크플로우에 연결하는 데 있다.`

### Body
- 핵심 구성:
  - enterprise data integration
  - ontology / semantic operational layer
  - workflow orchestration
  - governed AI execution
  - audit / permission / traceability
- 제조 현장과 맞는 이유:
  - 품질, 수율, 설비, SCM은 단순 검색보다 `운영 연결`이 중요

### Annotation
- `챗봇형 AI보다 운영 시스템 레이어에 가까움`

## Slide 5. Security and Deployment
### Main message
`보안은 영업 설명의 문제가 아니라 배포 모델과 권한 구조의 문제다.`

### Body
- 확인해야 할 4개:
  - 데이터 반출 통제
  - 로그 및 감사성
  - 권한 체계 적합성
  - on-prem / private cloud / hybrid 현실성
- 현재 단계 판단:
  - on-prem 가능성 자체는 검토 포인트
  - 그러나 우리 환경에서 동일 구현 가능 여부는 별도 검증 필요

### Visual hint
- `Can say now / Need proof` two-column board

## Slide 6. Cost Structure
### Main message
`Palantir 비용은 소프트웨어 구매비보다 운영 전환비에 가깝다.`

### Body
- 공개 가격 구조 앵커:
  - GSA license / support / training / engineering rate
- 공식 영업 패턴:
  - bootcamp
  - pilot / scoping
  - 7-figure ACV
  - enterprise expansion
- 내부적으로 봐야 할 항목:
  - ontology build
  - data integration
  - enablement
  - change management

### Annotation
- `좌석당 단가 질문으로는 실제 비용 구조를 설명하기 어려움`

## Slide 7. Samsung Timeline: Signal vs Proof
### Main message
`삼성은 같은 문제공간으로 빠르게 이동하고 있지만, Palantir production adoption 공개 근거는 아직 약하다.`

### Body
- `2024-08`: DX Rubicon PoC with MS / Google / Palantir
- `2024-09`: DX customer-facing rollout publicly reported to MS
- `2025-03`: semiconductor Palantir rumor in secondary press
- `2025`: Foundry recovery visible in official earnings materials
- `2026-02`: DS AI Center hiring mentions `Palantir ontology`
- `2026-03`: Samsung publicly presents `agentic AI + digital twin` manufacturing strategy
- `2026-03-31`: Korean press reports 2nm yield around 60%

### Conclusion line
- `Problem-space alignment: strong`
- `Direct public production proof: weak`

## Slide 8. Korean Manufacturing References
### Main message
`최근 국내 제조업에서 가장 신뢰도 높은 Palantir reference는 LG CNS와 HD Hyundai다.`

### Body
- LG CNS
  - 2026-03 strategic partnership
  - LG affiliate quality PoC -> full-scale contract signal
  - FDE organization established
- HD Hyundai
  - Reuters-scale large contract
  - shipbuilding / refinery / construction equipment / robotics / electrical systems expansion
- SK
  - no strong public confirmation found

### Visual hint
- `Reference strength matrix`
  - rows: LG CNS / HD Hyundai / Samsung / SK
  - columns: official source, manufacturing relevance, deployment certainty, recency

## Slide 9. Ontology / Hiring Signal
### Main message
`온톨로지는 개념 논의가 아니라, 삼성이 실제 채용으로 집행 중인 역량 축이다.`

### Body
- Samsung DS AI Center Knowledge Graph JD
- explicit keywords:
  - Neo4j
  - GraphRAG
  - NL2SQL
  - RAG
  - Palantir ontology
- implication:
  - Samsung is building graph / ontology-backed operational AI capability

### Annotation
- `채용시장에서는 ontology보다 KG / GraphRAG / NL2SQL 형태로 나타남`

## Slide 10. Where It Could Matter for Us
### Main message
`자사에서 가치가 날 가능성이 가장 높은 영역은 품질/Q-Cost 축이다.`

### Body
- 후보 영역:
  - 품질 / Q-Cost
  - 생산 이상 탐지 및 원인 분석
  - 설비 유지보전
  - SCM 병목 대응
  - R&D 데이터 연결
- 좋은 후보의 조건:
  - 높은 비용 또는 손실 노출
  - 데이터 접근 가능
  - 짧은 proof window
  - 전사 확장 가능성

## Slide 11. Pilot Candidate Matrix and Recommendation
### Main message
`1순위 POC 후보는 품질/Q-Cost다.`

### Matrix
- rows:
  - 품질 / Q-Cost
  - 생산
  - 설비
  - SCM
  - R&D
- columns:
  - 재무 임팩트
  - 단기 검증 가능성
  - 데이터 접근성
  - 확대 가능성
  - 변화관리 부담

### Recommendation
- 품질 / Q-Cost를 우선 제안
- 이유:
  - 내부 회의 방향과 일치
  - LG quality PoC 사례와 연결 가능
  - 재무 논리가 가장 직접적
  - KPI 설계가 용이

## Slide 12. Recommendation and Meeting Ask
### Main message
`이번 미팅은 구매 미팅이 아니라 검증 미팅으로 운영해야 한다.`

### Ask to Palantir
- 제조업 reference 중 공개 가능한 운영 KPI
- deployment model options
- ontology build scope and required client effort
- pilot -> contract timeline and cost ladder
- quality/Q-Cost use case expected proof window

### Final recommendation
- `Do not recommend enterprise-wide rollout now`
- `Recommend POC-first`
- `Use LG CNS + HD Hyundai as core evidence`
- `Use Samsung as signal, not proof`

## Source Links for Deck Build
- LG CNS 공식 보도자료: <https://www.lgcns.com/kr/newsroom/press/detail.enterpriseai-2603-4>
- Palantir / LG CNS 발표 기사: <https://www.nasdaq.com/press-release/lg-cns-and-palantir-announce-strategic-partnership-accelerate-ai-transformation-2026>
- Yahoo Finance / Reuters `HD Hyundai`: <https://finance.yahoo.com/news/exclusive-palantir-signs-hd-hyundai-141518689.html>
- ETNews `2024-08-05` 삼성 DX Rubicon: <https://www.etnews.com/20240805000275>
- ETNews `2024-09-02` 삼성 DX rollout / MS 선정: <https://www.etnews.com/20240902000267>
- Samsung Semiconductor GTC 2026 공식 블로그: <https://semiconductor.samsung.com/kr/news-events/tech-blog/samsung-showcases-agentic-ai-driven-semiconductor-engineering-innovation-at-nvidia-gtc-2026/>
- 한국경제 `2026-03-31` 삼성 2nm 수율 보도: <https://www.hankyung.com/article/2026033177201>
- Palantir `2025 FY 10-K` 로컬 PDF: [../sources/external_refs/2026-04-15_palantir_pltr_2025_10k.pdf](../sources/external_refs/2026-04-15_palantir_pltr_2025_10k.pdf)
- Palantir `Q3 2024 Business Update` 로컬 PDF: [../sources/external_refs/2026-04-15_palantir_pltr_q3_2024_business_update.pdf](../sources/external_refs/2026-04-15_palantir_pltr_q3_2024_business_update.pdf)
- Samsung earnings PDF 묶음: [../sources/external_refs/2026-04-15_palantir_samsung_1q25_earnings.pdf](../sources/external_refs/2026-04-15_palantir_samsung_1q25_earnings.pdf), [../sources/external_refs/2026-04-15_palantir_samsung_2q25_earnings.pdf](../sources/external_refs/2026-04-15_palantir_samsung_2q25_earnings.pdf), [../sources/external_refs/2026-04-15_palantir_samsung_3q25_earnings.pdf](../sources/external_refs/2026-04-15_palantir_samsung_3q25_earnings.pdf)
