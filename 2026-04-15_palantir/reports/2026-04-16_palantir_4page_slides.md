# Palantir 4-Page Briefing Slides Manuscript

작성일: `2026-04-16`  
대상 템플릿: `sources/ppt_template/Template_4pages_new.pptx`  
목표: `4 content-page`만으로 보안, 경쟁사/시장 신호, 계열사 readiness, 자사 PoC 방향을 토론 가능한 수준으로 정리

## Slide 1. 보안·데이터주권·온톨로지 구축 방식

### Slide objective
- `Palantir = 외부 SaaS 위험`이라는 선입견을 깨되, 보안 우려를 무시하지 않고 설계 문제로 재정의한다.

### Recommended layout
- 좌측 큰 영역: `배포 아키텍처 그림`
- 우측 상단: `보안상 장점`
- 우측 중단: `남는 어려움`
- 우측 하단: `대안 유형 비교`

### Headline
`고위험 제조데이터에서도 핵심은 AI 사용 여부가 아니라 어디에 두고 어떤 권한·행위통제로 운영하느냐다`

### Main content blocks

#### 1) 중앙 그림: 권장 아키텍처
- 상단: `ERP / MES / QMS / EAM / Sensor / Recipe / Defect / Safety data`
- 중간: `Customer-controlled Ontology Layer`
  - lot
  - panel
  - tool
  - defect
  - recipe
  - alarm
  - action / approval
- 하단 분기:
  - `On-prem / Air-gapped zone`
  - `Private cloud zone`
  - `Optional managed LLM zone for low-risk / approved data only`
- 우하단에 작은 note:
  - `원천 데이터, 권한, export policy는 고객이 유지`
  - `Palantir는 ontology / workflow / governance를 공동 설계`

#### 2) 보안상 장점
- `외부 public SaaS로 raw 제조데이터를 넘기지 않는 구조 가능`
- `lineage, checkpoint, audit trail로 access/export/action 추적 가능`
- `object/action 단위 권한으로 AI와 사람 승인 범위 분리 가능`
- `AWS Private Link / Azure Private Link / GCP Private Service Connect 같은 private path 설계 가능`

#### 3) 남는 어려움
- `on-prem = zero risk`는 아님
- vendor support 계정, model logging, patching, export path 관리 필요
- ontology 공수와 data classification 정합성 확보가 핵심

#### 4) 대안 유형 비교
- `Palantir`: ontology + workflow + governance 통합
- `Azure / Vertex / Bedrock`: private AI 가능하지만 governance 조합은 별도 설계 필요
- `In-house GraphRAG`: 통제는 최고, 구축 속도와 유지보수 부담 큼

### Annotation text
- `LGD와 같은 고위험 제조사에서는 "cloud 금지"보다 "어떤 데이터와 action을 밖에 둘 수 없는가"를 먼저 정의해야 함`
- `국가첨단전략산업/국가핵심기술 보호 관점에서 raw 공정·수율·recipe 데이터는 우선 폐쇄영역이 기본`

### Source footer
- Palantir Apollo docs
- Palantir Privacy and Governance Whitepaper
- Azure data/privacy docs
- Vertex AI VPC-SC docs
- law.go.kr strategic technology law link

## Slide 2. 삼성은 "성공사례"보다 "문제공간 신호", LG·현대는 "공개 reference"

### Slide objective
- 삼성을 과장하지 않으면서도, 왜 이 영역을 검토해야 하는지 시장 신호를 설득력 있게 보여준다.

### Recommended layout
- 상단: `2024 -> 2026 timeline`
- 좌측 하단: `Samsung signal vs proof`
- 우측 하단: `LG / HD Hyundai / 기타 peer signals + hiring`

### Headline
`2025-2026 제조 AI 경쟁은 chatbot이 아니라 ontology·workflow·digital twin·operations intelligence로 이동 중`

### Main content blocks

#### 1) Timeline
- `2024-08` 삼성 DX, MS/Google/Palantir 3사 PoC
- `2024-09` customer-facing rollout은 Microsoft 선정
- `2025-09` Samsung AI Forum: 제조데이터 체계화 강조
- `2026-02` DS AI Center KG hiring: `Palantir ontology / Neo4j / GraphRAG / NL2SQL`
- `2026-03` GTC: Agentic AI + digital twin, 공개 축은 NVIDIA / Synopsys
- `2026-03` Hankyung: 2nm yield 개선 신호
- `2026-03` LG CNS-Palantir 공식 partnership
- `2026-01` HD Hyundai group-wide expansion 보도

#### 2) Samsung: Signal vs Proof
- `Signal`
  - ontology / graph hiring
  - manufacturing AI 데이터 전략
  - agentic AI / digital twin 공개 방향
- `Proof`
  - 2024 DX Palantir PoC까지만 공개 확인
  - 반도체 수율 개선의 Palantir attribution은 미확인
- 결론:
  - `삼성은 같은 문제를 풀고 있지만, Palantir 성공사례로 단정하면 안 됨`

#### 3) LG / HD Hyundai / hiring
- `LG CNS`: LG affiliate quality PoC -> full-scale contract signal
- `HD Hyundai`: shipbuilding / refinery / construction equipment / robotics / electrical systems 확장
- `조직 신호`: ontology, graph, FDE 조직은 실제 도입 단계에서 중요해지는 역량

### Annotation text
- `삼성은 strategic signal case`
- `LG·HD Hyundai는 public reference case`
- `핵심 문제는 고객상담 AI가 아니라 운영 workflow 내 AI 실행`

### Source footer
- ETNews `2024-08-05`, `2024-09-02`
- Samsung AI Forum 2025
- Samsung GTC 2026
- Hankyung `2026-03-31`
- LG CNS official release
- Reuters/Yahoo HD Hyundai
- internal Samsung KG JD email (`2026-02-08`)

## Slide 3. 계열사 readiness 및 비용 검토 outline

### Slide objective
- 계열사별 상태를 비교 가능한 working table로 두고, 사용자가 이후 코멘트를 추가할 수 있게 만든다.

### Recommended layout
- 중심: `wide table`
- 우측 또는 하단: `comment box / open questions`

### Headline
`계열사 readiness는 동일하지 않다. 현 단계에서는 stage·문제영역·비용구조를 함께 보는 working outline이 필요하다`

### Main table

| 계열사/주체 | 현재 단계 | 핵심 문제영역 | 공개근거 수준 | 비용 메모 | 추가 코멘트 |
| --- | --- | --- | --- | --- | --- |
| LG CNS / 그룹 공통 | 공식 partnership | enterprise AI / quality / rollout | 높음 | project expansion형 |  |
| LG Energy Solution | PoC 진척 추정 | quality 중심 | 중하 | 내부회의상 5개 POC |  |
| LG Innotek | PoC 후 미도입 추정 | 품질/운영 | 낮음 | 내부회의상 `POC 8억` 언급 |  |
| LG Electronics | 초기 논의 추정 | 미정 | 낮음 | 미확인 |  |
| 자사(LGD) | 검토 전 | quality / process / safety | 해당없음 | PoC-first 필요 |  |

### Supporting bullets
- `Palantir cost는 좌석형 SaaS보다 discovery/bootcamp + ontology modeling + implementation + expansion 구조로 이해하는 편이 정확`
- `Q3 2024 Business Update는 bootcamp -> 7-figure ACV 전환 패턴을 시사`
- `정찰가보다 계약 구조, 범위, 성공지표 기반 상업조건이 더 중요`

### Annotation text
- `이 페이지의 일부 status와 비용 메모는 내부회의 기반 추정이며 추가 검증 필요`
- `사용자 코멘트 추가를 위해 여백 유지`

### Source footer
- Palantir 10-K
- Palantir Q3 2024 Business Update
- GSA pricelist
- LG CNS official release
- three meeting-note emails

## Slide 4. 자사 도입방안: PoC 선정 프레임과 우선 후보

### Slide objective
- `무엇을 먼저 시험할지`를 논의 가능한 수준으로 좁힌다.

### Recommended layout
- 좌측: `평가기준`
- 중앙: `candidate matrix`
- 우측: `recommended shortlist + next questions`

### Headline
`도입 판단의 핵심은 어디에서 가장 빨리, 가장 안전하게, 가장 설명 가능한 운영 성과를 증명할 수 있는가다`

### Main content blocks

#### 1) 평가기준
- 효과성
- 검증 가능성
- 데이터 준비도
- 보안 적합성
- 확장성
- 비용 부담
- ontology 재사용성
- 조직 수용성

#### 2) Candidate matrix
- `품질 / Q-Cost`: 효과 `상`, 검증 `상`, 확대 `상`
- `공정 이상탐지 + 원인분석`: 효과 `상`, 검증 `중상`, 확대 `상`
- `안전 leading indicator`: 효과 `중상`, 검증 `중상`, 보안 `상`
- `설비 예지보전`: 효과 `중상`, 검증 `중`, 확대 `중상`
- `SCM / 병목 대응`: 효과 `중상`, 검증 `중`, 확대 `상`
- `R&D / 실험지식 연결`: 효과 `중`, 검증 `중하`, 확대 `중상`

#### 3) Recommended shortlist
- `1순위: 품질 / Q-Cost`
- `2순위: 공정 이상탐지 + 원인분석`
- `3순위: 안전 leading indicator`

#### 4) Immediate discussion checklist
- 어떤 데이터는 절대 외부 반출 금지인가
- 8~12주 안에 baseline 대비 무엇을 증명할 것인가
- ontology 설계 owner는 누가 될 것인가
- 사람이 승인해야 하는 action은 무엇인가
- Palantir와 비교할 대안 stack은 무엇인가

### Annotation text
- `전사 rollout 논의는 보류, PoC 정의가 우선`
- `성공 기준이 없는 PoC는 비용만 학습하고 끝날 가능성 높음`

### Source footer
- internal meetings
- Palantir factcheck memo
- LG / HD Hyundai public references
- Samsung signal set
