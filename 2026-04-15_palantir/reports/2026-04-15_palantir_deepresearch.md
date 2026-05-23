# Palantir External Research Note v1

## Executive Takeaways
- `2026-04-15` 기준, 공개 자료로 확인되는 Palantir의 비용 구조는 `정찰제 SaaS`라기보다 `협상형 엔터프라이즈 플랫폼 계약 + 교육/전문서비스 + 일부 사용량 기반 요소`에 가깝다.
- 삼성 관련해서 공개적으로 가장 강한 Palantir 연결고리는 `2024-08-05` 삼성 DX부문의 `루비콘 프로젝트` 3사 PoC 기사다. 하지만 `2024-09-02` 공개 기사에서는 삼성 고객응대 AI 공급사로 `MS`가 낙점됐다고 보도됐다. 즉, 적어도 공개 보도 기준으로는 Palantir가 삼성 DX의 해당 본사업을 따냈다는 증거는 약하다.
- 삼성 반도체/파운드리 쪽은 `2025`년 내내 공식 실적자료에서 `2nm 공정 안정화`, `낮은 가동률`, `대형 고객 확대`, `3Q record-high orders`, `2nm mass production 시작`이 확인되지만, 이를 Palantir 효과로 연결할 수 있는 공개 근거는 아직 찾지 못했다.
- 제조업 비교 사례로는 `HD Hyundai`가 가장 강하다. Palantir의 `2026-02` Q4 2025 investor presentation은 HD Hyundai가 `Foundry`와 `AIP`를 조선, 정유, 건설장비, 로보틱스, 전기시스템으로 그룹 확장 중이라고 적시한다.
- 온톨로지 인력 신호는 생각보다 명확하다. 내부 메일 기준 `2026-02-08` 삼성전자 DS부문 AI센터 `Knowledge Graph` 포지션 JD에는 `Neo4j`, `GraphRAG`, `NL2SQL`, `RAG`, 그리고 `팔란티어 온톨로지` 활용 경험이 직접 요구사항으로 적혀 있다.

## 1. Palantir 비용 구조

### 1-1. 공개 가격표가 아닌 협상형 구조가 기본
- Palantir `2025 FY 10-K`는 자사 `pricing models`가 계속 바뀔 수 있고, 대형 고객은 `different pricing structures`와 `substantial price concessions`를 요구할 수 있다고 설명한다.
- 같은 10-K는 Palantir가 전통적인 `labor contract` 방식보다 `productized basis`로 플랫폼을 제공한다고 적시한다.
- 해석:
  - 기본 단위는 인력투입형 SI가 아니라 플랫폼 계약이다.
  - 하지만 실제 가격은 고객 규모, 복잡도, 계약 길이, 구현 범위에 따라 크게 달라진다.
  - 따라서 `Foundry/AIP는 좌석당 얼마` 같은 단일 숫자로 설명하면 오히려 부정확하다.

### 1-2. 공개 가능한 비용 앵커
- `Forrester Total Economic Impact of Palantir Foundry`는 복합 고객 가정에서 `Foundry + professional services + cloud costs`의 연간 비용을 `USD 30 million`으로 둔다.
- 같은 문서는 비용 변동 요인으로 다음을 든다.
  - customer-specific pricing
  - organization size and complexity
  - pricing model negotiated
  - implementation scope
  - contract length
- 이 수치는 실제 표준 가격표가 아니라 `복합 고객 시뮬레이션`이므로, 대기업 전사 계약의 규모감을 보여주는 참고치로만 써야 한다.

### 1-3. GSA 공개 계약서로 본 하위 가격 구조
- `2024-02-06` 발효 GSA federal pricelist에는 Palantir Platform의 공개 단가가 포함되어 있다.
- 확인 가능한 항목:
  - monthly cloud license, per core: `USD 7,050.77`
  - monthly term license, per core: `USD 7,050.77`
  - perpetual license, per core: `USD 141,015.42`
  - appliance, per core: `USD 151,042.82`
  - annual support per core: `USD 28,203.08` 또는 `USD 37,753.85`
  - Bootcamp training per student: `USD 960.72`
  - Developer & Integrator training per student: `USD 2,505.87`
  - engineering / implementation hourly rates: 약 `USD 201.91`~`USD 353.35`
- 해석:
  - 이 가격표는 `현재 상업용 Foundry/AIP 전체 가격표`로 읽으면 안 된다.
  - 다만 Palantir이 historically 어떤 식으로 `license + support + training + implementation services`를 번들링해왔는지 보여주는 매우 유용한 공개 앵커다.
  - 온톨로지 설계, 개발자/통합자 교육, 현장 엔지니어 투입이 실제 비용 구조의 일부라는 점을 시사한다.

### 1-4. 상업 확장 방식: Bootcamp -> 7-figure ACV
- Palantir `Q3 2024 Business Update`는 상업 고객 전개 방식을 매우 노골적으로 보여준다.
- 사례 슬라이드에는 다음 패턴이 나온다.
  - `Initial Bootcamp`
  - `Use Case Scoping`
  - `50 Days to 7-Figure ACV Deal`
  - `<2 Months to 7-Figure ACV Deal`
  - `Enterprise-Wide expansions in discussion`
- 해석:
  - Palantir은 작은 무료 체험형 SaaS가 아니라, 빠른 현장 몰입 워크숍과 파일럿을 통해 `7-figure ACV` 계약으로 전환하는 영업 모델을 갖고 있다.
  - 따라서 초기 도입비는 `PoC/Bootcamp/서비스 동반형`, 이후 본계약은 `고액 ACV 기반`으로 보는 것이 맞다.

### 1-5. 비용 구조에 대한 실무적 결론
- 보고자료에는 `정확한 정가`를 쓰기보다 아래 프레임이 맞다.
  - `초기비용`: discovery / bootcamp / POC / ontology modeling / integration
  - `본계약비용`: enterprise platform contract, support, cloud or on-prem infrastructure, expansion scope
  - `운영비용`: internal data engineering, ontology maintenance, user enablement, change management
- 즉 Palantir 비용은 소프트웨어 구매비만이 아니라 `운영모델 전환비`를 포함한다.

## 2. 삼성 적용 사례: 무엇이 확인되고 무엇이 안 되는가

### 2-1. 공개적으로 확인되는 직접 기사
- `2024-08-05`, 전자신문:
  - 삼성전자 DX부문이 `루비콘 프로젝트`에서 `MS`, `Google`, `Palantir` 3사를 대상으로 PoC를 진행했다고 보도
  - 목적은 가전/제품 데이터를 학습시켜 고객 맞춤형 응답을 제공하는 생성형 AI 시스템
- `2024-09-02`, 전자신문:
  - 삼성 고객응대 AI 공급사로 `MS`가 낙점됐다고 보도
  - 삼성닷컴과 리테일 매장용 AI 챗봇 시스템 구축이 목표

### 2-2. 이 두 기사로 말할 수 있는 것
- Palantir은 최소한 삼성 DX의 중요한 생성형 AI PoC 경쟁 구도에 들어갔다.
- 하지만 공개 기사 기준으로는 해당 DX customer-facing rollout의 최종 승자는 `MS`다.
- 따라서 `삼성이 Palantir를 도입했다`고 일반화하려면 business unit을 구분해야 한다.
  - `DX customer-facing generative AI`: 공개 기사상 MS 우세
  - `DS/foundry/manufacturing`: 아직 직접 확증 부족

### 2-3. 작년 3월 기사 여부
- 이번 패스에서는 `2025-03`의 Samsung-Palantir 직접 기사 하나를 확정적으로 검증하지 못했다.
- 대신 `2024-08` DX PoC 기사와 `2024-09` MS 선정 기사는 확인됐다.
- 따라서 `2025-03 기사`는 후속 검색에서 한국어 query expansion으로 다시 확인할 필요가 있다.

## 3. 삼성 반도체 / 제조 성과 추이: Palantir 효과로 말할 수 있는가

### 3-1. 공식 실적자료에서 확인되는 2025 흐름

#### 2025 1Q
- 삼성 공식 1Q 2025 earnings presentation:
  - Foundry earnings were weak
  - fab utilization was stagnant
  - company planned to stabilize the 2nm process
  - company aimed to start 2nm mass production and secure major orders in 2H 2025

#### 2025 2Q
- 삼성 공식 2Q 2025 earnings presentation:
  - Foundry revenue grew significantly
  - earnings still remained weak
  - reasons included U.S. export restrictions and prolonged low utilization at mature nodes
  - company planned to ramp mass production of a new mobile SoC on GAA 2nm
  - management explicitly targeted better utilization and profitability through expanded major-customer sales

#### 2025 3Q
- 삼성 공식 3Q 2025 earnings presentation:
  - Foundry achieved `record-high customer orders` mainly on advanced nodes
  - started mass production of `GAA 1st Gen. 2nm`
  - earnings improved substantially as one-off costs subsided and fab utilization improved
  - 2026 outlook points to mass production of `GAA 2nd Gen. 2nm`

### 3-2. 추정 가능한 해석
- `2025`년 동안 삼성 파운드리의 advanced-node business는 분명히 좋아졌다.
- 하지만 공개 공식 자료만으로는 그 개선을 `Palantir 도입 효과`로 연결할 수 없다.
- 이유:
  - 삼성 공식 IR 자료 어디에도 Palantir가 직접 언급되지 않는다.
  - 개선 요인으로는 공정 성숙, 고객 수주, 일회성 비용 축소, utilization 회복 등이 더 직접적으로 보인다.
  - 따라서 `Palantir 덕분에 수율/비용이 개선됐다`는 식의 서술은 현재 단계에서 과장이다.

### 3-3. 삼성 사례를 보고자료에서 다루는 권장 방식
- 가능:
  - `Palantir이 삼성의 주요 AI/데이터 플랫폼 PoC 경쟁 구도에 포함된 적이 있다`
  - `삼성 파운드리는 2025년 하반기로 갈수록 2nm와 주문 측면에서 개선 추세를 보였다`
- 불가:
  - `삼성 파운드리 개선이 Palantir 때문에 발생했다`
  - `2nm 수율 향상에 Palantir가 직접 기여했다`
- 실무 권장:
  - 삼성은 `직접 성공사례`보다 `강한 관심 신호 + 후속 성과 추이의 간접 정황` 정도로 다루는 것이 안전하다.

## 4. 다른 제조업 사례

### 4-1. HD Hyundai
- Palantir `Q4 2025 Investor Presentation`은 `2026-02` 기준으로 HD Hyundai와의 파트너십을 그룹 차원으로 확장했다고 소개한다.
- 적용 영역:
  - shipbuilding
  - refineries
  - construction equipment
  - robotics
  - electric systems
- 해석:
  - 한국 제조업에서 공개적으로 가장 강한 Palantir manufacturing reference는 현재 HD Hyundai다.
  - 이 사례는 `단일 유스케이스`보다 `그룹 확장형 industrial operating platform` 스토리에 가깝다.

### 4-2. Lear
- Palantir `Q4 2025 Investor Presentation`은 Lear를 `AI FDE` 기반의 agentic enterprise 사례로 언급한다.
- 세부 운영성과는 이번 패스에서 추가 공시를 깊게 확인하지 못했지만, 자동차 부품 제조업에서도 Palantir이 단일 분석툴이 아니라 운영체계 레이어로 포지셔닝되고 있음을 보여준다.

### 4-3. SK
- `2026-04-15` 기준 공개 웹 조사에서는 SK 계열 제조업체의 Palantir 직접 도입 사례를 확인하지 못했다.
- 따라서 SK는 현재 `negative evidence` 항목이다.
- 보고자료에는 `공개 확인 사례 없음`으로 적는 것이 안전하다.

## 5. 온톨로지와 채용 신호

### 5-1. 삼성 DS AI Center 채용 JD는 매우 직접적이다
- 내부 메일함의 `2026-02-08` recruiter mail에 첨부된 `JD_Knowledge Graph 분야.docx` 확인 결과:
  - 조직: 삼성전자 `DS부문 > AI센터`
  - 역할:
    - 조직도, 라인 ID, 장비 ID, EA, 용어사전 등 공통/도메인 KG 모델링
    - hierarchical graph, synonym graph, context graph 설계
    - Graph DB 기반 지식 저장과 쿼리 최적화
    - `NL2SQL`, `RAG`, `GraphRAG`, `LangGraph`, agentic multi-turn UX`
  - 필수 또는 핵심 우대:
    - `Neo4j`
    - `팔란티어 온톨로지`
    - KG DB / 검색엔진 / Vector DB / RAG
- 해석:
  - 적어도 삼성 DS AI Center는 `Knowledge Graph`와 `ontology-backed RAG/NL2SQL`을 실무 시스템으로 보고 있다.
  - `팔란티어 온톨로지`가 JD 안에 직접 들어간다는 점은 매우 강한 신호다.

### 5-2. 삼성의 공개 기술 메시지
- Samsung Research의 `Samsung Developer Conference Korea 2023` 뉴스는 keynote에 `data intelligence based on knowledge graph research`가 포함됐다고 설명한다.
- 해석:
  - 삼성 내부에서 knowledge graph는 일회성 용어가 아니라, 공개 개발자 행사에서도 언급되는 연구 축이다.

### 5-3. LG / SK 공개 채용 신호
- LG AI Research 공개 career surface에서는 `Data Intelligence Lab`이 보인다.
- 다만 이번 패스에서는 `ontology` 또는 `knowledge graph`라는 단어가 들어간 LG 공개 공고는 확정적으로 캡처하지 못했다.
- SK 역시 공개 검색에서는 ontology 직접 공고보다 broader AI/data 역할이 더 눈에 띄었고, Palantir 연계 채용은 확인되지 않았다.

### 5-4. 해석
- 한국 대기업 채용시장에서 `ontology`는 아직 대중적인 공고 용어라기보다:
  - `Knowledge Graph`
  - `Graph DB`
  - `GraphRAG`
  - `NL2SQL`
  - `RAG`
  - `agentic workflow`
  - `data intelligence`
  같은 실무 키워드로 분해되어 나타난다.
- 이 점은 보고자료에서 중요하다.
  - 경영진에게는 `온톨로지`를 추상 개념으로 설명하기보다
  - `공장/품질/설비/라인/용어사전/업무 규칙을 기계가 이해하는 operational graph layer`로 번역해서 설명하는 편이 맞다.

## 6. 현재까지의 판단

### 6-1. 무엇을 강하게 말할 수 있는가
- Palantir은 제조업에서 단순 LLM 벤더가 아니라 `ontology + workflow + governed AI + integration`을 파는 운영 플랫폼이다.
- 가격은 정형화된 구독형보다 `고객별 협상`, `고액 ACV`, `서비스 동반`, `확장 계약` 성격이 강하다.
- 제조업 성공사례는 `HD Hyundai`가 가장 강하고, 삼성은 `관심/PoC 정황`은 있으나 `직접 성공사례`로 말하기엔 아직 약하다.
- 삼성 내부 인재 수요는 `Knowledge Graph`와 `ontology-backed RAG/NL2SQL` 쪽으로 실제 움직이고 있다.

### 6-2. 무엇을 아직 말하면 안 되는가
- `삼성 2nm 수율 개선 = Palantir 효과`
- `삼성이 Palantir를 반도체에 본격 도입했다`
- `SK도 Palantir를 도입했다`
- `Palantir 가격은 좌석당 혹은 코어당 얼마로 일반화할 수 있다`

## 7. 다음 조사 우선순위
1. `2025-03` 삼성-Palantir 기사 여부를 한국어 확장 검색으로 재검증
2. LG엔솔 / LG이노텍 / LG전자 내부 도입 단계와 비용 정합성 확인
3. Palantir on-prem / private cloud / hybrid security 아키텍처를 1페이지로 정리
4. 자사 파일럿 후보를 `품질 / Q-Cost / 생산 / SCM / R&D` 기준으로 매트릭스화
5. 경영진용으로는 `삼성 direct success story` 대신 `HD Hyundai strong case + Samsung internal signal + ontology hiring signal` 조합으로 스토리를 짜는 방안 검토

## Sources
- Palantir 2025 FY 10-K  
  https://investors.palantir.com/files/2025%20FY%20PLTR%2010-K.pdf
- Palantir Q3 2024 Business Update  
  https://investors.palantir.com/files/Palantir%20Q3%202024%20Business%20Update.pdf
- Palantir / Forrester Total Economic Impact of Foundry  
  https://www.palantir.com/assets/xrfr7uokpv1b/7h0zi3GZrU3L7AM2HO1Q6O/1ad26eaa42ad949f8e3c80ea22f96b7a/The_Total_Economic_Impact_of_Palantir_Foundry.pdf
- GSA awarded federal pricelist for Palantir  
  https://www.gsaadvantage.gov/ref_text/47QTCA24D004L/103TVU.3VU6QI_47QTCA24D004L_PALANTIR47QTCA24D004L.PDF
- Samsung Electronics 1Q 2025 earnings presentation  
  https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_1Q_conference_eng.pdf
- Samsung Electronics 2Q 2025 earnings presentation  
  https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_2Q_conference_eng.pdf
- Samsung Electronics 3Q 2025 earnings presentation  
  https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_3Q_conference_eng.pdf
- ETNews, Samsung Rubicon PoC article, 2024-08-05  
  https://www.etnews.com/20240805000275
- ETNews, Samsung selected MS for customer-facing AI system, 2024-09-02  
  https://www.etnews.com/20240902000267
- Palantir Q4 2025 Investor Presentation  
  https://investors.palantir.com/files/Palantir%20-%20Q4%202025%20Investor%20Presentation.pdf
- Samsung Research news, SDC Korea 2023  
  https://research.samsung.com/news/Samsung-Electronics-Hosts-the-Samsung-Developer-Conference-Korea-2023-for-Software-Developers
- Internal source: recruiter email dated 2026-02-08, `삼성전자 DS부문 AI센터 Knowledge Graph 포지션 제안 건`
