# Palantir 검토 보고서

작성일: 2026-04-15  
용도: `2026-04-27` Palantir 경영진 미팅 전 사전 briefing document

## 문서 사용법
- 앞부분 `3분 압축본`은 빠르게 읽고 현재 판단을 파악하기 위한 요약본이다.
- 뒷부분 `상세 본문`은 근거, 제한사항, 적용 논리를 확인하기 위한 본문이다.
- 본 문서는 `도입 확정 보고서`가 아니라 `도입 검토 판단 보고서`다.

## 3분 압축본

### 한 줄 결론
Palantir는 검토할 가치가 있지만, 지금 단계에서 전사 도입을 논의할 대상은 아니며 `품질/Q-Cost 중심의 좁은 POC`로 타당성을 검증하는 접근이 맞다.

### 지금 당장 말할 수 있는 것
- Palantir는 단순 생성형 AI 모델 회사보다 `데이터-온톨로지-워크플로우-거버넌스`를 묶는 운영 플랫폼으로 보는 것이 적절하다.
- 비용 구조는 공개 정찰형 SaaS가 아니라 `협상형 엔터프라이즈 계약 + 전문서비스 + 확장 계약` 구조다.
- 최근 국내 제조업 기준 강한 공식 레퍼런스는 `LG CNS`, `HD Hyundai`다.
- 삼성은 같은 문제 공간으로 분명히 움직이고 있지만, `2026-04-15` 현재 공개 근거만으로 `Palantir가 삼성 반도체 production platform`이라고 말할 수는 없다.

### 지금 당장 말하면 안 되는 것
- `삼성 반도체 2nm 수율 개선은 Palantir 효과다`
- `삼성이 Palantir를 반도체 생산 플랫폼으로 공식 채택했다`
- `SK도 Palantir를 제조에 도입했다`
- `Palantir 가격은 사용자당 또는 좌석당 얼마다`

### 현재 경영진 판단 포인트
1. Palantir를 `도입할 것인가`가 아니라 `어떤 운영 문제를 어떤 POC로 검증할 것인가`를 먼저 정해야 한다.
2. 삼성은 직접 성공사례보다 `시장 신호 + 내부 역량 구축 + 공개 전략 방향`으로 읽는 것이 안전하다.
3. LG CNS와 HD Hyundai는 국내 제조업 현실성을 보여주는 더 강한 외부 근거다.
4. 보안은 영업 설명을 수용하는 수준이 아니라 `배포 모델 + 권한체계 + 데이터 반출 통제` 수준에서 다시 점검해야 한다.

### 권고안
- 전사 도입 논의는 보류
- `품질 / Q-Cost`를 1순위 POC 후보로 제안
- 미팅에서는 아래 5가지를 집중 확인
  1. on-prem / private cloud / hybrid 실제 배포 방식
  2. ontology 구축 범위와 내부 투입 공수
  3. 제조업 reference에서 무엇이 실제 운영성과였는지
  4. pilot에서 본계약으로 가는 비용 구조와 기간
  5. 우리 데이터 현실에서 가장 짧게 검증 가능한 영역

### 핵심 근거 6개
1. Palantir `2025 FY 10-K`: pricing model이 고정형이 아니고 대형 고객별 구조가 달라질 수 있다고 명시
2. Palantir `Q3 2024 Business Update`: `bootcamp -> 7-figure ACV` 전환 패턴 제시
3. ETNews `2024-08-05`: 삼성 DX가 `MS / Google / Palantir` 3사 PoC 진행
4. ETNews `2024-09-02`: 같은 DX customer-facing rollout은 `MS` 선정
5. LG CNS `2026-03`: Palantir 전략 파트너십 및 LG 계열사 quality PoC -> 본계약 신호
6. 삼성 DS AI Center `2026-02-08` JD: `Neo4j / GraphRAG / NL2SQL / RAG / Palantir ontology` 명시

## 상세 본문

## 1. 검토 배경
- `2026-04-27` 예정된 Palantir 경영진 미팅을 앞두고 사전 판단이 필요하다.
- 내부 회의록 기준 핵심 질문은 이미 정리되어 있다.
  1. 보안과 배포 방식은 설명 가능한가
  2. 삼성과 국내 제조업 사례는 어디까지 사실인가
  3. LG 계열사 적용은 어느 단계까지 왔는가
  4. 자사에 적용한다면 어디서 시작하는 것이 맞는가

## 2. Palantir를 어떤 회사로 봐야 하는가
- Palantir는 foundation model 경쟁사보다:
  - 기업 데이터 연결
  - 온톨로지 기반 의미 구조화
  - 운영 워크플로우 내 AI 실행
  - 권한 및 거버넌스 통제
  를 묶는 운영 플랫폼 성격이 강하다.
- 따라서 검토 프레임도 `모델 성능 비교`보다 `운영 의사결정 플랫폼 비교`로 가져가야 한다.

## 3. 보안과 배포 방식

### 현재까지 확인된 사실
- Palantir는 정부·산업 고객 대상으로 보안, 거버넌스, 배포 유연성을 강하게 내세운다.
- 내부 회의에서는 `on-premise로 보안 우려를 낮출 수 있는가`가 핵심 질문으로 제기되었다.
- 다만 현재 공개 자료만으로 `우리와 같은 환경에서도 완전 동일한 방식으로 구현 가능하다`고 단정할 수는 없다.

### 판단
- 보안 논점은 `클라우드 vs 온프렘` 단순 비교가 아니라 다음 질문으로 다시 써야 한다.
  1. 데이터 반출이 실질적으로 차단되는가
  2. 모델 / 앱 호출 로그와 감사 흔적이 남는가
  3. 권한 구조가 조직도와 업무 분리 원칙에 맞는가
  4. 우리 인프라에서 on-prem, private cloud, hybrid 중 무엇이 현실적인가

### 보고서 표현 권장안
- `보안 우려는 배포 모델과 권한통제 설계 수준에서 검증해야 하며, 영업 설명만으로 충분하다고 보기 어렵다.`

## 4. 비용 구조

### 팩트
- Palantir `2025 FY 10-K`는 가격 모델이 바뀔 수 있고, 대형 고객은 `different pricing structures`와 `substantial price concessions`를 요구할 수 있다고 적는다.
- GSA 공개 가격표에는 코어 단위 라이선스, support, training, engineering rate가 공개되어 있다.
- `Q3 2024 Business Update`는 bootcamp / scoping 이후 `7-figure ACV`로 이어지는 영업 패턴을 보여준다.

### 해석
- 비용은 단순 라이선스 구매비가 아니다.
- 실제 구조는 보통 다음 항목으로 나뉜다.
  - discovery / bootcamp
  - pilot / ontology modeling
  - data integration / implementation
  - 본계약
  - support / enablement / expansion

### 경영진 관점 판단
- ROI 논의는 `얼마냐`보다 `어떤 운영 문제에서 몇 개월 안에 얼마나 측정 가능한 효과를 낼 수 있느냐`로 가야 한다.

## 5. 삼성 흐름

### 확인된 것
- `2024-08-05`: 삼성 DX `루비콘 프로젝트`에서 `MS / Google / Palantir` 3사 PoC
- `2024-09-02`: 해당 DX customer-facing rollout은 공개 기사 기준 `MS` 선정
- `2025 1Q~3Q`: 삼성 공식 실적자료에서 Foundry 회복 흐름 확인
- `2025-09`: Samsung AI Forum 2025에서 반도체 제조 데이터와 AI 중요성 공개 강조
- `2026-02-08`: 삼성 DS AI Center `Knowledge Graph` JD에서 `Palantir ontology` 직접 언급
- `2026-03-18`: 삼성은 설계~제조 전주기 `Agentic AI + digital twin` 전략을 공개
- `2026-03-31`: 업계 보도에서 삼성 2nm 수율 `60% 수준` 언급

### 아직 확인되지 않은 것
- `Palantir가 삼성 반도체 production stack으로 공식 도입되었다`
- `2nm 수율 개선이 Palantir 효과다`
- `2025-03 삼성-Palantir 기사` 원출처 1차 근거

### 실무 해석
- 삼성은 분명히 Palantir이 겨냥하는 문제공간으로 움직이고 있다.
- 그러나 공개 2026 전략에서 이름이 보이는 축은 Palantir보다 `NVIDIA / Synopsys / digital twin / agentic AI` 쪽이 더 선명하다.
- 삼성 파트는 `직접 성공사례`가 아니라 `강한 신호, 약한 귀속` 구조로 다루는 편이 맞다.

## 6. 국내 제조업 레퍼런스

### LG CNS
- `2026-03-11 / 2026-03-12` 공식 전략 파트너십 발표
- LG 계열사 한 곳이 quality PoC를 마치고 본계약으로 전환한 신호 존재
- FDE 조직 신설

### HD Hyundai
- `2026-01-20` Reuters 기반 수억 달러 규모 계약 보도
- 조선, 정유, 건설장비, 로보틱스, 전기시스템으로 그룹 확장

### SK
- `2026-04-15` 현재 강한 공개 확인 사례 없음

### 판단
- 최근 한국 제조업 기준 Palantir는 이미 `실험적 검토` 단계를 넘어 일부 기업에서는 `확장 / 본계약` 단계로 들어갔다.
- 따라서 자사도 기술적 현실성 자체를 부정할 단계는 아니다.

## 7. 온톨로지와 채용 신호
- 삼성 DS AI Center JD는 이 주제에서 매우 강한 내부 신호다.
- 명시된 키워드:
  - KG modeling
  - hierarchical graph
  - synonym graph
  - context graph
  - Neo4j
  - GraphRAG
  - NL2SQL
  - RAG
  - Palantir ontology
- 의미:
  - 삼성은 ontology를 추상 개념이 아니라 `operational graph layer` 수준에서 다루고 있다.
  - 한국 대기업 채용시장에서 ontology는 종종 `KG / GraphRAG / NL2SQL / data intelligence` 형태로 분해되어 나타난다.

## 8. 자사 적용 방안

### 원칙
- 전사 도입 금지
- 좁고 측정 가능한 POC 우선
- 데이터 준비도와 재무 임팩트를 같이 봄

### 후보 영역
1. 품질 / Q-Cost
2. 생산 이상 탐지 및 원인 분석
3. 설비 유지보전
4. SCM 예측 및 병목 대응
5. R&D / 실험 데이터 연결

### 평가 기준
- 재무 임팩트
- 단기 검증 가능성
- 데이터 접근성
- 조직 수용성
- 확대 가능성

### 현재 추천
- 1순위는 `품질 / Q-Cost`
- 이유:
  - 내부 회의 방향과 일치
  - LG 계열사 quality PoC와 연결 가능
  - 비용절감 논리가 가장 명확
  - 지표 설계가 상대적으로 용이

## 9. 미팅에서 바로 물어봐야 할 질문
1. 제조업 reference 중 실제 운영 KPI가 공개 가능한 사례는 무엇인가
2. on-prem / private cloud / hybrid 중 국내 제조 고객이 주로 선택한 방식은 무엇인가
3. ontology 구축 시 고객사 내부 데이터팀이 감당해야 할 공수는 어느 정도인가
4. pilot에서 본계약으로 전환되는 일반적인 기간과 비용 단계는 무엇인가
5. quality / Q-Cost 같은 영역에서 초기 3개월 안에 어떤 성과를 약속할 수 있는가

## 10. 제안
1. Palantir 미팅은 전사 도입 검토가 아니라 `품질/Q-Cost POC 검증 미팅`으로 재정의한다.
2. 삼성은 직접 사례가 아니라 `경쟁사가 같은 문제를 강하게 풀고 있다는 신호`로만 사용한다.
3. 대외 reference는 `LG CNS`, `HD Hyundai`를 중심으로 제시하고, 삼성은 `signal vs proof` 구조로 정리한다.
4. 미팅 후 바로 POC 정의서로 전환할 수 있도록 `대상 업무`, `데이터 소스`, `성공지표`, `3개월 proof window`를 회의 결과물로 남긴다.

## 11. 핵심 링크와 원문 경로

### 공식 자료
- Palantir `2025 FY 10-K` 로컬 PDF: [../sources/external_refs/2026-04-15_palantir_pltr_2025_10k.pdf](../sources/external_refs/2026-04-15_palantir_pltr_2025_10k.pdf)
- Palantir `Q3 2024 Business Update` 로컬 PDF: [../sources/external_refs/2026-04-15_palantir_pltr_q3_2024_business_update.pdf](../sources/external_refs/2026-04-15_palantir_pltr_q3_2024_business_update.pdf)
- Samsung `2025 1Q` earnings PDF: [../sources/external_refs/2026-04-15_palantir_samsung_1q25_earnings.pdf](../sources/external_refs/2026-04-15_palantir_samsung_1q25_earnings.pdf)
- Samsung `2025 2Q` earnings PDF: [../sources/external_refs/2026-04-15_palantir_samsung_2q25_earnings.pdf](../sources/external_refs/2026-04-15_palantir_samsung_2q25_earnings.pdf)
- Samsung `2025 3Q` earnings PDF: [../sources/external_refs/2026-04-15_palantir_samsung_3q25_earnings.pdf](../sources/external_refs/2026-04-15_palantir_samsung_3q25_earnings.pdf)
- LG CNS 공식 보도자료: <https://www.lgcns.com/kr/newsroom/press/detail.enterpriseai-2603-4>
- Palantir / LG CNS 발표 기사: <https://www.nasdaq.com/press-release/lg-cns-and-palantir-announce-strategic-partnership-accelerate-ai-transformation-2026>
- Samsung Semiconductor GTC 2026 공식 블로그: <https://semiconductor.samsung.com/kr/news-events/tech-blog/samsung-showcases-agentic-ai-driven-semiconductor-engineering-innovation-at-nvidia-gtc-2026/>

### 기사 및 보조 확인 링크
- ETNews `2024-08-05` 삼성 DX Rubicon 3파전: <https://www.etnews.com/20240805000275>
- ETNews `2024-09-02` 삼성 DX customer-facing rollout은 MS 선정: <https://www.etnews.com/20240902000267>
- Yahoo Finance / Reuters `2026-01-20` HD Hyundai 계약: <https://finance.yahoo.com/news/exclusive-palantir-signs-hd-hyundai-141518689.html>
- Dailian `2026-04-07` LG-팔란티어 경영진 접촉: <https://www.dailian.co.kr/news/view/1630338/%EA%B5%AC%EA%B4%91%EB%AA%A8-%EC%8B%A4%EB%A6%AC%EC%BD%98%EB%B0%B8%EB%A6%AC%EC%84%9C-AX-%EA%B0%80%EC%86%8DLG-A-2026>
- ETNews `2026-03-18` 삼성·SK의 GTC 2026 제조 AI 흐름: <https://www.etnews.com/20260318000242>
- 연합뉴스 AMP `2026-03-18`: <https://www.yna.co.kr/amp/view/AKR20260318004300091>
- 한국경제 `2026-03-31` 삼성 2nm 수율 60% 보도: <https://www.hankyung.com/article/2026033177201>
- TechPowerUp `2025-03-18` 삼성-Palantir 반도체 기사 2차 인용: <https://www.techpowerup.com/334276/samsung-reportedly-partnered-up-with-palantir-to-improve-chip-production-yields>

### 내부 정리 문서
- 심층 메모: [2026-04-15_palantir_master_memo.md](2026-04-15_palantir_master_memo.md)
- 팩트체크: [2026-04-15_palantir_factcheck.md](2026-04-15_palantir_factcheck.md)
- 2026 사례 정리: [2026-04-15_palantir_recent_2026_cases.md](2026-04-15_palantir_recent_2026_cases.md)
