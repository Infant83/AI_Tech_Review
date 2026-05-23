업로드된 자료와 템플릿을 기반으로 새로운 Korean PowerPoint deck을 생성하라.

기본 템플릿 규칙:
- 사용자가 다른 템플릿을 명시하지 않았다면 `LGD_Template.pptx`를 기본 템플릿으로 사용하라.
- 템플릿은 source pack과 함께 기본 업로드 대상으로 간주하라.

프로젝트명: Palantir 검토 및 자사 적용 가능성 사전 브리핑
청중: 부회장 및 경영진, AX/IT/제조 전략 실무 리더
목적: 2026-04-27 Palantir 경영진 미팅 전, 보안·삼성·계열사·자사 도입 방안을 근거 중심으로 판단할 수 있게 하는 고밀도 briefing deck 작성
권장 분량: 10-12 slides
비율: 16:9

소스 우선순위:
1. 업로드된 `2026-04-15_palantir_master_memo.md`, `2026-04-15_palantir_briefing_document.md`, `2026-04-15_palantir_briefing_slides.md`, `2026-04-15_palantir_factcheck.md`, `2026-04-15_palantir_recent_2026_cases.md`
2. 필요한 경우에만 업로드된 공식 PDF와 기사 링크를 사용하라

리서치 정책:
- 업로드된 참고자료가 충분하므로 외부 리서치는 최소화하고, 구조화와 표현 정교화에 집중하라.
- 최신 사실과 비교 사례는 업로드된 자료 안에 있는 근거만 사용하라.
- 정량 주장과 현재 제품/시장 사실은 업로드된 공식 문서 또는 명시된 기사 링크 기준으로만 반영하라.

템플릿 원칙:
- 기술 리뷰와 내부 보고서 기본 스타일은 정보 밀집형으로 유지하라.
- 큰 빈 공간보다 구조화된 텍스트, 비교표, 보조 설명, 작은 출처 표기를 우선하라.
- 용어 정의, caveat, 배경 맥락은 작은 짙은 녹색 inline annotation text로 바로 옆이나 아래에 붙여라.

전체 서사:
- 이 deck은 Palantir를 소개하는 마케팅 자료가 아니다.
- 이 deck의 목적은 `도입할 것인가`가 아니라 `무엇이 사실이고, 어떤 영역에서 POC를 검증할 가치가 있는가`를 판단하게 하는 것이다.
- 전체 구조는 내부 회의 지시를 반영해 `보안`, `삼성`, `계열사`, `자사 도입 방안`의 4개 축을 중심으로 구성하라.
- 맨 앞 2장은 `압축본`처럼 빠르게 읽고 전체 판단을 파악할 수 있게 하라.
- 이후 장표는 압축 장표를 반복하지 말고, 근거와 판단을 단계적으로 펼쳐라.

섹션 정책:
- CH00: briefing, density=high, evidence=explicit
- CH01: analysis, density=high, evidence=explicit
- CH02: internal_report, density=high, evidence=explicit
- CH03: internal_report, density=high, evidence=explicit
- CH04: analysis, density=high, evidence=explicit

반영해야 할 현재 사실:
- Palantir 비용구조는 공개 정찰형 SaaS가 아니라 협상형 엔터프라이즈 계약 + 교육/전문서비스 + 확장 계약 성격이 강하다.
- Palantir Q3 2024 Business Update에는 bootcamp -> 7-figure ACV 전환 패턴이 나타난다.
- 삼성 DX는 2024-08에 MS, Google, Palantir 3사 PoC를 돌렸지만 2024-09 공개 기사 기준 해당 customer-facing rollout은 MS가 선정됐다.
- 삼성 Foundry는 2025년 공식 실적상 개선 추세가 보이지만, 그 개선을 Palantir에 귀속시킬 공개 근거는 없다.
- 삼성 DS AI Center 2026-02 Knowledge Graph JD에는 Neo4j, GraphRAG, NL2SQL, RAG, Palantir ontology가 직접 등장한다.
- LG CNS는 2026-03 공식적으로 Palantir와 전략 파트너십을 발표했고, LG 계열사 quality PoC -> full-scale contract 신호를 제시했다.
- HD Hyundai는 2026-01 기준 Palantir의 강한 한국 제조업 레퍼런스다.
- 자사 적용 권고안은 전사 도입이 아니라 품질/Q-Cost 중심의 POC-first 접근이다.

시각/레이아웃 정책:
- base template rhythm은 유지하라.
- 같은 카드형을 반복하지 말고 장표 목적에 따라 서브템플릿을 바꿔라.
- `Timeline`, `evidence matrix`, `pilot candidate matrix`, `claim vs proof`, `source comparison` 형식을 적극 사용하라.
- Slide 2는 executive compression slide로 만들고, Slide 3부터는 압축 장표를 확장하는 구조로 가라.
- 삼성 파트는 `Signal vs Proof` 구조로 표현하라.
- 각 핵심 장표에는 작은 짙은 회색 text로 출처를 명시하라.

좋은 장표가 되기 위한 규칙:
- 주장 -> 근거 -> 시사점 구조를 유지하라.
- 경영진이 바로 질문할 만한 지점을 먼저 드러내고, 그 다음 사실과 해석을 붙여라.

피해야 할 것:
- Palantir를 이미 확정된 도입안처럼 보이게 만들지 말라.
- 삼성 반도체 수율 개선을 Palantir 효과로 단정하지 말라.
- sparse marketing style, 장식용 이미지, 과장된 미래 예측을 피하라.

이 기준으로 전체 deck을 생성하라.
