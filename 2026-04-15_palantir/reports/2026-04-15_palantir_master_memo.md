# Palantir 심층리서치 통합 메모

작성일: 2026-04-15  
주제: Palantir 경영진 미팅 대비 검토 메모  
목적: 현재까지 수집한 회의록, 외부 기사, 공식 문서, 내부 채용 신호를 하나의 실무 메모로 통합하고, 이후 보고자료 작성의 기준본으로 사용

## 1. 이 메모의 결론
- Palantir는 단순한 생성형 AI 벤더가 아니라 `ontology + workflow + governed AI + integration` 중심의 운영 플랫폼으로 보는 것이 맞다.
- 비용 구조는 `정찰형 SaaS`가 아니라 `협상형 엔터프라이즈 계약 + 교육/전문서비스 + 확장 계약` 구조다.
- 한국 제조업 기준 최근 공개 레퍼런스는 `LG CNS + Palantir`, `HD Hyundai + Palantir`가 가장 강하다.
- 삼성은 `2024 DX PoC`, `2025 반도체 적용설`, `2026 ontology hiring + agentic AI 전략 공개`까지는 보이지만, `2026-04-15` 현재 공개 근거만으로 `Palantir가 삼성 반도체 생산 플랫폼으로 확정 도입됐다`고 말할 수는 없다.
- 따라서 현 단계의 보고는 `도입 확정 보고`보다 `도입 검토용 판단 보고`로 설계해야 한다.

## 2. 이 메모에서 연결되는 핵심 파일

### 내부 정리 문서
- [소스 노트](../notes/2026-04-15_palantir_sources.md)
- [초기 메모](2026-04-15_palantir_memo.md)
- [외부 조사 노트 v1](2026-04-15_palantir_deepresearch.md)
- [팩트체크](2026-04-15_palantir_factcheck.md)
- [최근 2026 사례 / 삼성 흐름](2026-04-15_palantir_recent_2026_cases.md)
- [리서치 실행 로그](../notes/2026-04-15_palantir_research_runlog.md)

### 로컬 보관 PDF
- [Palantir 2025 10-K](../sources/external_refs/2026-04-15_palantir_pltr_2025_10k.pdf)
- [Palantir Q3 2024 Business Update](../sources/external_refs/2026-04-15_palantir_pltr_q3_2024_business_update.pdf)
- [Palantir GSA pricelist](../sources/external_refs/2026-04-15_palantir_gsa_pricelist.pdf)
- [Samsung 1Q25 earnings](../sources/external_refs/2026-04-15_palantir_samsung_1q25_earnings.pdf)
- [Samsung 2Q25 earnings](../sources/external_refs/2026-04-15_palantir_samsung_2q25_earnings.pdf)
- [Samsung 3Q25 earnings](../sources/external_refs/2026-04-15_palantir_samsung_3q25_earnings.pdf)

### 외부 링크
- LG CNS 공식 보도자료: <https://www.lgcns.com/kr/newsroom/press/detail.enterpriseai-2603-4>
- Palantir/LG CNS 보도자료: <https://www.nasdaq.com/press-release/lg-cns-and-palantir-announce-strategic-partnership-accelerate-ai-transformation-2026>
- ETNews `루비콘 프로젝트` 기사: <https://www.etnews.com/20240805000275>
- ETNews `MS 낙점` 기사: <https://www.etnews.com/20240902000267>
- ETNews `삼성·SK 반도체 전주기 AI 적용` 기사: <https://www.etnews.com/20260318000242>
- 한국경제 `2nm 수율 60%` 기사: <https://www.hankyung.com/article/2026033177201>
- Samsung Semiconductor GTC 2026 blog: <https://semiconductor.samsung.com/kr/news-events/tech-blog/samsung-showcases-agentic-ai-driven-semiconductor-engineering-innovation-at-nvidia-gtc-2026/>
- Samsung Semiconductor AI Forum 2025 blog: <https://semiconductor.samsung.com/kr/news-events/tech-blog/future-of-semiconductor-industry-with-ai-samsung-ai-forum-2025/>
- Reuters/Yahoo Finance `HD Hyundai` 기사: <https://finance.yahoo.com/news/exclusive-palantir-signs-hd-hyundai-141518689.html>

## 3. 왜 지금 Palantir를 검토하는가
- `2026-04-27` 예정된 Palantir 경영진 미팅을 앞두고, 사전 판단 보고가 필요하다.
- 내부 회의록 기준 보고서의 중심 질문은 이미 정리되어 있다.
  1. 보안과 배포 방식은 설명 가능한가
  2. 삼성과 국내 제조업 사례는 어느 수준까지 사실로 쓸 수 있는가
  3. LG 계열사 적용은 어디까지 진척됐는가
  4. 자사에 적용한다면 어떤 영역에서 POC를 시작하는 것이 타당한가

## 4. Palantir를 어떻게 정의해야 하는가
- Palantir는 자체 foundation model을 앞세우는 회사라기보다,
  - 기업 데이터 연결
  - 온톨로지 기반 의미 구조화
  - 운영 워크플로우 내 AI 실행
  - 권한/거버넌스 통제
  를 묶어 파는 플랫폼이다.
- 따라서 우리 보고서에서도 `LLM 비교`보다 `운영 의사결정 플랫폼 비교` 프레임으로 다뤄야 한다.

## 5. 비용 구조

### 현재까지 확인된 사실
- Palantir `2025 FY 10-K`는 가격 모델이 계속 바뀔 수 있고, 대형 고객은 `different pricing structures`와 `substantial price concessions`를 요구할 수 있다고 적시한다.
- Palantir `Q3 2024 Business Update`는 `Initial Bootcamp -> 7-figure ACV` 전환 패턴을 제시한다.
- GSA 공개 가격표에는 라이선스, 지원, 교육, 엔지니어링 단가가 보인다.

### 실무 해석
- 초기비용:
  - discovery / bootcamp / pilot
  - ontology modeling
  - data integration
  - implementation service
- 본계약비용:
  - platform contract
  - support
  - infrastructure
  - enterprise expansion
- 운영비용:
  - internal data engineering
  - ontology maintenance
  - enablement
  - change management

### 보고서에 써도 되는 문장
- `Palantir 비용은 단순 사용자 수 기반 SaaS보다는 고액 엔터프라이즈 계약과 서비스 동반형 구조에 가깝다.`
- `초기 PoC와 Bootcamp 이후 본계약으로 전환되는 영업 패턴이 공식 IR 자료에서 확인된다.`

### 쓰면 안 되는 문장
- `Palantir는 좌석당 얼마다`
- `Foundry/AIP 도입비는 코어당 공개 가격만 보면 된다`

## 6. 삼성 흐름: 2024 -> 2026

### 확인된 흐름
- `2024-08-05`: 삼성 DX `루비콘 프로젝트`에서 `MS`, `Google`, `Palantir` 3사 PoC
- `2024-09-02`: 해당 DX 고객응대 AI 시스템은 공개 기사 기준 `MS`가 선정
- `2025-03-18`: 삼성 반도체가 Palantir로 수율/품질/생산성을 개선한다는 2차 보도 체인 발생
- `2025 1Q~3Q`: 삼성 공식 실적자료에서 Foundry 회복 흐름 확인
- `2025-09`: Samsung AI Forum 2025에서 DS AI Center가 제조 데이터와 AI를 공개적으로 강조
- `2026-02-08`: 삼성 DS AI Center `Knowledge Graph` JD에서 `팔란티어 온톨로지` 직접 등장
- `2026-03-18`: GTC 2026에서 삼성은 반도체 전주기 `Agentic AI + digital twin` 전략 공개
- `2026-03-31`: 한국경제가 삼성 2nm 수율 `60% 수준` 보도

### 현재 시점의 해석
- 삼성은 분명히 `Palantir이 겨냥하는 문제 공간`으로 들어왔다.
- 그러나 공개적으로 보이는 2026년 스택은 `NVIDIA Omniverse`, `digital twin`, `Synopsys`, `agentic AI` 쪽이 더 선명하다.
- 삼성 반도체에 Palantir가 실제 production stack으로 들어갔는지는 아직 공개 팩트가 약하다.

### 보고서에 써도 되는 문장
- `삼성은 2024년 DX 영역에서 Palantir를 포함한 외부 AI 플랫폼 PoC를 진행한 바 있다.`
- `삼성 DS AI Center는 2026년 ontology/graph 기반 AI 역량을 실제 채용 중이며, 제조 전주기 AI 전략을 공개적으로 강화하고 있다.`

### 쓰면 안 되는 문장
- `삼성 반도체 2nm 수율 개선은 Palantir 효과다`
- `삼성이 Palantir를 반도체 생산 플랫폼으로 공식 채택했다`

## 7. 국내 제조업 최근 사례

### LG CNS + Palantir
- `2026-03-11 / 2026-03-12` 공식 파트너십 발표
- LG 계열사 1곳이 품질관리 PoC를 성공적으로 마치고 본계약으로 전환
- LG CNS가 FDE 조직을 만들고 그룹 확장을 추진

### HD Hyundai + Palantir
- `2026-01-20` Reuters 기준 `hundreds of millions` 규모 계약
- Palantir Q4 2025 investor presentation 기준 조선, 정유, 건설장비, 로보틱스, 전기시스템으로 확장

### SK
- `2026-04-15` 현재 강한 공개 확인 사례 없음

## 8. 온톨로지 / 채용 신호
- 내부 메일함의 `2026-02-08` 삼성 DS AI Center `Knowledge Graph` JD는 이 주제에서 매우 강한 증거다.
- JD에 직접 들어간 키워드:
  - `KG modeling`
  - `hierarchical graph`
  - `synonym graph`
  - `context graph`
  - `Neo4j`
  - `GraphRAG`
  - `NL2SQL`
  - `RAG`
  - `팔란티어 온톨로지`
- 이건 삼성이 ontology를 개념 수준이 아니라 실무 시스템 수준으로 보고 있다는 뜻이다.

## 9. 자사 적용 논점

### 지금 당장 전사 도입을 권할 수 없는 이유
- 삼성 direct success story가 아직 약하다.
- 비용은 높고, 운영 전환 부담이 크다.
- ontology/data modeling 없이는 효과가 제한될 가능성이 높다.

### 그래도 검토할 가치는 있는 이유
- 국내 제조업 공식 사례는 늘고 있다.
- LG 계열사에서 이미 품질관리 PoC -> 본계약 전환 신호가 나왔다.
- 자사도 품질/Q-Cost/생산/설비/SCM 같은 영역에서 같은 문제 구조를 갖고 있다.

### 가장 타당한 접근
- `전사 도입`이 아니라 `POC-first`
- 후보 영역:
  - 품질 / Q-Cost
  - 생산 이상 탐지 / 원인 분석
  - 설비 유지보전
  - 수요-생산-재고 연결
- 평가 기준:
  - 효과 측정 가능성
  - 단기간 검증 가능성
  - 데이터 접근성
  - 확대 가능성
  - 변화관리 부담

## 10. 현재 시점에서 경영진에게 권할 문장
- `Palantir는 단순 생성형 AI 모델보다, 제조·품질·운영 의사결정을 연결하는 엔터프라이즈 운영 플랫폼으로 이해하는 것이 적절합니다.`
- `최근 공개 사례 기준으로는 LG CNS와 HD Hyundai가 가장 강한 국내 제조업 레퍼런스입니다.`
- `삼성은 같은 문제 공간으로 움직이고 있으나, 공개 근거만으로는 Palantir production adoption을 단정할 수 없습니다.`
- `따라서 검토 방향은 전사 도입이 아니라, 데이터 준비도가 있는 고효과 영역의 POC 우선 접근이 타당합니다.`

## 11. 남아 있는 빈칸
- `2025-03` 삼성-Palantir 원출처 기사 복구
- LG 계열사별 실제 비용과 단계 확인
- Palantir on-prem / private cloud / hybrid security 정리
- 자사 파일럿 후보에 대한 정량 점수화
