# Palantir 심층 검토 및 자사 도입 논의용 4-Page 브리핑 문서

작성일: `2026-04-16`  
용도: `2026-04-27` Palantir 경영진 미팅 전 사전 판단, 질문 정리, 내부 PoC 방향 설정

## 문서 사용법
- 앞부분 `압축본`은 3~5분 안에 읽고 현재 판단을 잡는 용도다.
- 뒷부분 `상세 설계 메모`는 실제 4-page 장표를 만들 때 들어갈 메시지, 근거, caveat를 정리한 본문이다.
- 본 문서는 `도입 찬반 보고서`가 아니라 `어디까지 사실이고, 어디서부터 검증해야 하는가`를 정리한 의사결정 보조 문서다.

## 압축본

### 한 줄 결론
Palantir는 `보안·거버넌스가 강한 운영형 데이터/AI 플랫폼`으로 볼 수 있고, 한국 제조업 기준 레퍼런스는 분명해지고 있다. 다만 삼성은 아직 `강한 문제공간 신호`이지 `공개 확인된 성공사례`는 아니므로, 자사에서는 `품질/Q-Cost 중심의 좁은 PoC`로 검증하는 접근이 맞다.

### 지금 확실하게 말할 수 있는 것
- Palantir는 `cloud`, `on-premises`, `disconnected/air-gapped` 배포를 모두 전제로 설명하는 플랫폼이다.  
  출처: Palantir Apollo docs <https://www.palantir.com/docs/apollo/core/introduction>
- Palantir는 단순 LLM SaaS보다 `ontology + workflow + lineage + checkpoint + access control` 성격이 강하다.  
  출처: Palantir Privacy and Governance Whitepaper <https://www.palantir.com/assets/xrfr7uokpv1b/4lXOhv4ycKr5IEMMFybaBj/2d7011ad45d11d189970d13e474f62bd/Palantir_Privacy_and_Governance_Whitepaper__1_.pdf>
- 한국 제조업 2026 공개 레퍼런스의 중심은 `LG CNS`와 `HD Hyundai`다.  
  출처: <https://www.lgcns.com/kr/newsroom/press/detail.enterpriseai-2603-4>, <https://finance.yahoo.com/news/exclusive-palantir-signs-hd-hyundai-141518689.html>
- 삼성은 `2024 DX PoC`, `2025 제조 AI 강화`, `2026 ontology/agentic AI 방향`까지는 읽히지만, `삼성 반도체 성과를 Palantir에 귀속`할 공개 근거는 없다.  
  출처: ETNews `2024-08-05`, ETNews `2024-09-02`, Samsung Semiconductor `2025-09`, `2026-03`, Hankyung `2026-03-31`

### 지금 조심해서 말해야 하는 것
- `삼성이 Palantir를 반도체 production platform으로 채택했다`
- `2nm 수율 개선은 Palantir 효과다`
- `SK도 이미 비슷한 방식으로 도입했다`
- `Palantir 가격은 좌석당 얼마다`

### 경영진이 보고 바로 물어볼 질문
1. 정말 외부로 데이터가 안 나가게 운영할 수 있나
2. 온톨로지는 누가 얼마나 많이 구축해야 하나
3. 삼성이 아니라면 국내 제조업에서 어떤 레퍼런스를 봐야 하나
4. 계열사별 readiness가 다른데 어디서 먼저 붙이는 게 맞나
5. 우리에게 가장 짧게 검증 가능한 PoC는 무엇인가

### 권고안
1. Palantir를 `전사 AI 플랫폼`으로 논의하지 말고 `보안 통제가 강한 운영형 PoC 후보`로 한정해서 본다.
2. Page 1은 `보안 우려를 무시하는 장표`가 아니라 `보안 우려를 설계 문제로 분해하는 장표`가 되어야 한다.
3. Page 2는 삼성을 중심에 두되, `Signal vs Proof` 구조로 정리한다.
4. Page 3은 계열사 진행현황과 비용을 `commentable outline`로 남긴다.
5. Page 4는 `품질/Q-Cost`, `공정 이상·원인분석`, `안전 leading indicator`를 우선 PoC 후보로 제안한다.

## 상세 설계 메모

## 1. Page 1 설계: 보안, 데이터 주권, 온톨로지 구축 방식

### 1-1. 장표에서 전달해야 할 핵심 메시지
`Palantir의 강점은 외부 클라우드에 데이터를 넘겨서 쓰는 SaaS convenience가 아니라, 고객이 데이터·권한·행위통제를 쥔 상태에서 ontology와 AI workflow를 얹을 수 있다는 점이다.`

### 1-2. 왜 이 페이지가 중요한가
- 이번 검토의 가장 큰 내부 우려는 `보안`이다.
- 특히 LGD와 같은 제조사는 국가첨단전략산업 및 국가핵심기술 보호 관점에서 `민감 공정·품질·수율·설비 데이터의 외부 유출 가능성`을 허용하기 어렵다.
- 따라서 이 페이지는 `Palantir도 AI니까 위험하다`와 `on-prem이면 다 된다` 사이를 메워야 한다.

### 1-3. 추천 프레임: 배포 옵션 3분할

| 배포 형태 | 설명 | 보안상 장점 | 남는 어려움 | LGD 적합성 |
| --- | --- | --- | --- | --- |
| `On-prem / Air-gapped` | 고객 IDC 또는 폐쇄망 내부에 Palantir stack과 필요한 model runtime을 둠 | 외부망 반출 최소화, 네트워크 경계 명확, 로그·권한·반출통제 일원화 가능 | 인프라 운영 부담, model/runtime patching 부담, vendor remote support 통제 필요 | `상` |
| `Private cloud / Sovereign-like` | 고객 tenant/VPC/VNet 안에서 private networking으로 운영 | public SaaS보다 통제 용이, 확장성 확보, private endpoint/VPC-SC 활용 가능 | cloud region, logging, managed service boundary를 계약·설계로 확인해야 함 | `중` |
| `SaaS / public managed service` | 운영 편의성과 속도가 가장 높음 | 초기 구축 빠름, 운영 난이도 낮음 | 민감 데이터 외부 노출 우려, 법/감사 대응 복잡, 고위험 데이터에는 부적합 | `하` |

### 1-4. Palantir 쪽에서 공개적으로 확인되는 보안 신호
- Apollo는 `cloud`, `on-premises`, `disconnected (air-gapped)` 환경을 모두 지원한다고 직접 설명한다.  
  출처: <https://www.palantir.com/docs/apollo/core/introduction>
- Apollo는 `regulated and controlled environments`와 `data sovereignty`, `classified clouds without network access`를 직접 언급한다.  
  출처: 같은 문서
- Foundry 문서 인덱스에는 `AWS Private Link`, `Azure Private Link`, `GCP Private Service Connect`가 명시되어 있다.  
  출처: <https://www.palantir.com/docs/foundry/data-lineage/explore-artifacts/index.html>
- Governance whitepaper는 다음 요소를 강조한다.
  - ontology를 조직 공통 의미계층으로 둠
  - lineage로 데이터 흐름과 접근을 추적
  - checkpoint로 export/access/action에 justification과 audit trail 부여
  - purpose limitation과 granular security markings를 지원  
  출처: Palantir Privacy and Governance Whitepaper

### 1-5. 온톨로지 구축을 어떻게 설명할 것인가
이 페이지의 설명 포인트는 `Palantir가 데이터를 가져가는 것`이 아니라 `고객이 가진 데이터를 고객 업무 언어로 재구성하는 운영 계층을 공동 설계하는 것`이다.

권장 설명:
- 고객이 유지해야 하는 것
  - 원천 데이터 저장 위치
  - 데이터 분류체계
  - object/action 권한 원칙
  - 외부 반출 정책
  - 승인체계와 감사 기준
- Palantir와 공동 설계할 것
  - object type 예: lot, panel, tool, defect, recipe, alarm, work order
  - action type 예: release, hold, route change, escalation, investigation
  - workflow 예: 이상탐지 -> 원인후보 -> 승인 -> 조치 -> 추적
- 즉, ontology는 `data schema`가 아니라 `업무를 AI가 이해할 수 있는 운영 모델`이다.

### 1-6. 보안상 이득을 장표에서 강조해야 하는 포인트
- 민감 데이터가 외부 public SaaS로 흘러가지 않는 설계가 가능하다.
- data lineage, action checkpoint, audit log를 통해 `누가 무엇을 왜 봤는지`를 남길 수 있다.
- object/action 권한을 세밀하게 두면 `AI가 할 수 있는 일`과 `사람 승인 없이는 못 하는 일`을 구분할 수 있다.
- private endpoint / VPC boundary / 폐쇄망 구성으로 `model 호출`과 `data 접근`을 분리 제어할 수 있다.
- 특히 고위험 제조 데이터는 `raw data 외부반출 없이 내부 inference + 내부 retrieval` 구조로 설계할 수 있다.

### 1-7. 그래도 남는 어려움
- on-prem이 곧 zero-risk는 아니다.
- 어려움은 다음과 같다.
  - 내부자 권한 남용
  - 데이터 오분류
  - vendor support 계정 통제
  - model runtime patch와 버전관리
  - tool/function/action permission sprawl
  - ontology 설계 공수 과소평가
  - 운영 중 export path가 늘어나는 문제
- 따라서 장표 톤은 `안전하다`가 아니라 `통제 가능한 구조로 설계할 수 있다`가 맞다.

### 1-8. 경쟁 대안과 비교 프레임

| 유형 | 대표 예시 | 강점 | 약점 | 보안 시사점 |
| --- | --- | --- | --- | --- |
| 운영형 ontology 플랫폼 | Palantir | workflow, ontology, lineage, action governance를 통합 | 도입공수와 vendor dependency 큼 | 고위험 업무에 적합할 수 있음 |
| hyperscaler private AI | Azure OpenAI / Microsoft Foundry, Vertex AI, Bedrock | private networking, managed ops, model choice | governance를 별도 설계해야 하는 경우 많음 | tenant/region/logging 조건을 세밀히 봐야 함 |
| in-house private LLM + GraphRAG | 자체 구축, Neo4j, vector DB, orchestrator | 최대 통제, 맞춤성 | 구현 속도 느림, 운영인력 필요 | 민감데이터에는 강함, 확장성이 과제 |
| engineering/digital twin stack | NVIDIA Omniverse, Synopsys 등 | 설계/시뮬레이션 최적화 | enterprise workflow와 ontology는 별도 | 제조 AI의 일부 영역에 강함 |

### 1-9. cloud LLM 보안 관점에서 같이 넣어야 할 사실
- Azure Direct Models 문서는 prompts/completions/customer data가 다른 고객이나 model provider의 학습에 쓰이지 않는다고 명시한다.  
  출처: <https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy>
- 단, abuse monitoring과 geography 처리 조건은 읽어야 하고, preview/global deployment caveat가 있다.
- Azure On Your Data는 private endpoint와 VNet 구성을 전제로 보안 구성을 따로 안내한다.  
  출처: <https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/on-your-data-configuration>
- Google Vertex AI는 VPC-SC perimeter 안에서는 default internet access가 차단된다고 설명한다.  
  출처: <https://docs.cloud.google.com/vertex-ai/docs/general/vpc-service-controls>
- 즉, public cloud를 쓰더라도 `private boundary + managed AI` 구조는 가능하지만, LGD 수준의 민감도라면 `무엇을 밖에 둘 수 있는지`를 먼저 정의해야 한다.

### 1-10. LGD 관점 권고
- 가장 보수적인 권고는 다음과 같다.
  1. 고위험 공정/수율/recipe/raw sensor 데이터는 우선 on-prem 또는 폐쇄 private zone 전용
  2. 외부 managed LLM은 mask/aggregate/approved dataset에 한해 제한 사용
  3. ontology와 workflow는 고객 주도, vendor 공동설계
  4. export path, admin access, model logging, remote support를 계약/설계 문서에 명시

## 2. Page 2 설계: 경쟁사 및 시장 신호, 삼성 2025-2026 흐름

### 2-1. 장표에서 전달해야 할 핵심 메시지
`삼성은 공개적으로 Palantir 성공사례가 확인된 것은 아니지만, 2025-2026 동안 ontology·agentic AI·manufacturing intelligence 방향으로 빠르게 이동했다. 반면 LG와 HD Hyundai는 Palantir과의 공개 연결이 더 분명하다.`

### 2-2. 추천 구조: Signal vs Proof

| 구분 | 삼성 | LG / HD Hyundai | 해석 |
| --- | --- | --- | --- |
| `공개 확인된 Palantir 연결` | 2024 DX PoC | 2026 LG CNS partnership, HD Hyundai expansion | 삼성보다 LG/현대가 공개 근거가 강함 |
| `제조 AI 방향성` | 2025 AI Forum, 2026 GTC agentic AI | LG quality PoC, Hyundai group-wide scaling | 모두 같은 문제공간으로 이동 중 |
| `ontology / graph hiring signal` | 삼성 DS AI Center 강함 | LG CNS FDE 조직 공식화 | 조직 측면에서는 둘 다 진지함 |
| `성과 귀속 가능성` | 약함 | LG/현대는 adoption fact가 더 선명 | 삼성은 signal, LG/현대는 reference |

### 2-3. 삼성 2025-2026 읽는 법

#### 확인된 흐름
- `2024-08-05`: 삼성 DX가 `MS / Google / Palantir` 3사 PoC 진행  
  출처: ETNews <https://www.etnews.com/20240805000275>
- `2024-09-02`: 같은 customer-facing rollout은 Microsoft가 선정  
  출처: ETNews <https://www.etnews.com/20240902000267>
- `2025-09`: Samsung AI Forum에서 제조 데이터를 체계적으로 고품질 데이터화해야 한다는 메시지 강화  
  출처: Samsung Semiconductor blog
- `2026-02-08`: 내부 recruiter email의 DS AI Center KG JD에 `Palantir ontology`, `Neo4j`, `GraphRAG`, `NL2SQL`, `RAG` 명시
- `2026-03-17/18`: GTC 2026에서 삼성은 `Agentic AI + digital twin`을 전면에 제시했고, 공개적으로는 NVIDIA / Synopsys 축이 더 선명  
  출처: Samsung Semiconductor blog, ETNews, Yonhap
- `2026-03-31`: 한국경제가 2nm yield 개선 신호를 보도했지만 Palantir attribution은 없음  
  출처: <https://www.hankyung.com/article/2026033177201>

#### 결론적으로 어떻게 말해야 하나
- 삼성은 `Palantir가 풀려는 문제를 실제로 풀고 있는 기업`이다.
- 그러나 `삼성=Palantir 성공사례`라고 말하면 안 된다.
- 장표에서는 다음 문장 구조가 안전하다.
  - `삼성은 2025-2026 동안 ontology·graph·agentic AI·digital twin 방향으로 이동했다.`
  - `Palantir은 그 문제공간과 구조적으로 맞닿아 있으나, 공개 확인된 production attribution은 부족하다.`

### 2-4. LG / HD Hyundai는 왜 더 강한 레퍼런스인가
- LG CNS는 2026-03에 Palantir 전략 파트너십을 공식 발표했고, LG 계열사 quality PoC -> full-scale contract 신호를 직접 언급했다.  
  출처: <https://www.lgcns.com/kr/newsroom/press/detail.enterpriseai-2603-4>
- Palantir release는 late-2025 deployment가 이미 있었다고 말한다.  
  출처: Nasdaq release
- HD Hyundai는 2026-01 기준 Reuters/Yahoo Finance에서 수억 달러 규모 계약으로 보도되었고, shipbuilding/refinery/construction equipment/robotics/electrical systems로 확장된다고 정리된다.  
  출처: <https://finance.yahoo.com/news/exclusive-palantir-signs-hd-hyundai-141518689.html>

### 2-5. 문제 선정과 인재 영입 신호를 어떻게 묶을 것인가
- 공개 기사에서 드러나는 공통 문제
  - 제조 이상탐지
  - 수율/품질
  - 공정·설비 최적화
  - digital twin
  - end-to-end operations visibility
- 채용/조직 신호에서 드러나는 공통 기술
  - knowledge graph
  - ontology
  - GraphRAG
  - NL2SQL
  - workflow agent
- 해석:
  - 시장은 `LLM을 붙이는 것`보다 `기업 운영언어로 데이터를 구조화하고 workflow로 연결하는 것`으로 이동 중이다.

### 2-6. 이 페이지에서 넣으면 좋은 작은 annotation
- `삼성은 proof case가 아니라 strategic signal case`
- `LG/HD Hyundai는 public reference case`
- `문제 선정의 핵심은 chatbot이 아니라 operations workflow`

## 3. Page 3 설계: 계열사 도입 현황 및 비용 검토 outline

### 3-1. 장표에서 전달해야 할 핵심 메시지
`계열사 readiness는 동일하지 않고, 일부는 실제 PoC/도입 신호가 있으나 상당수 항목은 내부 추정이므로 outline 형태로 두고 토론용 comment space를 남겨야 한다.`

### 3-2. 이 페이지는 확정 장표가 아니라 commentable working page여야 한다
- 사용자가 나중에 코멘트를 추가할 예정이므로 우측 또는 하단에 여백/comment 영역이 있어야 한다.
- 따라서 문장보다 `표 + status tag + 빈 comment line` 형태가 맞다.

### 3-3. 추천 표 구조

| 계열사/주체 | 현재 인지 단계 | 문제영역 | 공개근거 수준 | 비용 메모 | 다음 확인 포인트 |
| --- | --- | --- | --- | --- | --- |
| `LG CNS / 그룹 공통 축` | `공식 partnership` | enterprise AI, quality, rollout | `높음` | partnership + project expansion형 | 어떤 affiliate가 quality full-scale 계약인지 확인 |
| `LG Energy Solution` | `PoC 진척 추정` | quality 중심 | `중간 이하` | 내부회의상 5개 POC 언급 | 현재 단계와 실사용 여부 재확인 |
| `LG Innotek` | `PoC 후 미도입 추정` | 품질/운영 | `낮음` | 내부회의상 `POC 8억` 언급 | 미도입 사유, ROI gap, security issue 여부 |
| `LG Electronics` | `초기 논의` | 미정 | `낮음` | 미확인 | owner 조직과 현 상태 확인 |
| `자사(LGD)` | `검토 전` | quality / process / safety | `해당 없음` | PoC-first 필요 | 후보 문제와 보안 경계 정의 |

### 3-4. 비용은 어떻게 적어야 하는가
- 이 페이지에서는 `숫자 단정`보다 `비용 구조`를 보여주는 편이 안전하다.

#### 공개적으로 쓸 수 있는 cost frame
- Palantir는 협상형 enterprise pricing이 기본이다.  
  출처: Palantir 10-K
- bootcamp / pilot에서 7-figure ACV deal로 가는 패턴이 IR 자료에 명시된다.  
  출처: Q3 2024 Business Update
- GSA pricelist는 software/support/training/engineering이 분해되어 있음을 보여준다.  
  출처: GSA pricelist

#### 이 페이지에서 추천하는 표현
- `초기 비용은 단순 license가 아니라 discovery/bootcamp + ontology modeling + data integration + implementation + support의 조합으로 보는 것이 타당`
- `계열사별 실제 숫자는 계약 구조와 적용범위가 달라 직접 비교가 어렵고, 내부 확인이 더 필요`

### 3-5. 계열사 비교 장표에서 꼭 넣을 caveat
- `LG 계열사 stage는 공개 fact와 내부회의 기반 추정을 혼합한 working outline이며, 일부 항목은 추가 검증 필요`

## 4. Page 4 설계: 자사 도입방안 및 PoC 후보 선정 프레임

### 4-1. 장표에서 전달해야 할 핵심 메시지
`자사 도입 판단은 '어디에 AI를 쓰고 싶은가'가 아니라 '어디에서 보안 통제를 유지한 채 8~12주 안에 성과를 입증할 수 있는가'로 내려야 한다.`

### 4-2. 추천 평가 기준

| 평가기준 | 질문 | 점수 방향 |
| --- | --- | --- |
| `효과성` | 재무·운영 효과가 큰가 | 높을수록 좋음 |
| `검증 가능성` | 8~12주 안에 baseline 대비 개선을 볼 수 있는가 | 높을수록 좋음 |
| `데이터 준비도` | 필요한 데이터가 이미 존재하고 접근 가능한가 | 높을수록 좋음 |
| `보안 적합성` | 고위험 데이터라도 폐쇄구조로 제한 운영 가능한가 | 높을수록 좋음 |
| `확장성` | PoC 후 타 라인/공장/조직으로 복제 가능한가 | 높을수록 좋음 |
| `비용 부담` | 초기 구축과 운영비가 상대적으로 합리적인가 | 낮을수록 좋음 |
| `온톨로지 재사용성` | 한 번 만든 object/action model이 다른 영역에도 쓰이는가 | 높을수록 좋음 |
| `조직 수용성` | 현업이 workflow change를 받아들일 수 있는가 | 높을수록 좋음 |

### 4-3. 후보 영역 평가안

| 후보영역 | 효과성 | 검증 가능성 | 보안 적합성 | 확대성 | 코멘트 |
| --- | --- | --- | --- | --- | --- |
| `품질 / Q-Cost` | `상` | `상` | `상` | `상` | 계량화가 쉽고 LG quality case와 연결 가능 |
| `공정 이상탐지 + 원인분석` | `상` | `중상` | `상` | `상` | sensor, lot, recipe, defect ontology가 핵심 |
| `안전사고 leading indicator` | `중상` | `중상` | `상` | `중` | 현재 내부 분석 과제와 직접 연결됨 |
| `설비 예지보전` | `중상` | `중` | `상` | `중상` | alert fatigue와 false positive 관리가 관건 |
| `SCM / 병목 대응` | `중상` | `중` | `중` | `상` | cross-function data 연결 강점이 있으나 데이터 범위 넓음 |
| `R&D / 실험지식 연결` | `중` | `중하` | `상` | `중상` | 장기적으로 중요하지만 proof window가 김 |
| `에너지 / utility optimization` | `중` | `중상` | `상` | `중` | 빠른 PoC 가능하지만 전략성은 상대적으로 약함 |

### 4-4. 이번 미팅에서 추천할 shortlist
1. `품질 / Q-Cost`
2. `공정 이상탐지 + 원인분석`
3. `안전 leading indicator`

추천 이유:
- 세 영역 모두 제조 운영과 직접 연결되고, object/action ontology를 비교적 자연스럽게 정의할 수 있다.
- 품질/Q-Cost는 재무임팩트가 가장 설명하기 쉽다.
- 공정 이상·원인분석은 Palantir식 ontology/workflow의 진가를 보기 좋다.
- 안전 leading indicator는 현재 내부 분석 과제와 연결되어 `Palantir 없이도 어려운 문제`를 `Palantir을 쓰면 더 잘 정의할 수 있는 문제`로 전환해볼 수 있다.

### 4-5. 경쟁사 비교와 체크포인트

| 체크포인트 | Palantir에 물을 질문 | 비교대상 |
| --- | --- | --- |
| ontology 구축 공수 | 첫 8주에 누가 무엇을 정의하는가 | in-house KG/GraphRAG |
| 보안 통제 | export, admin access, logging, remote support를 어떻게 막는가 | Azure private AI / Vertex / Bedrock |
| 운영 workflow | 사람이 승인해야 하는 action을 어떻게 설계하는가 | 일반 BI/LLM stack |
| manufacturing reference | quality, yield, maintenance에서 어떤 KPI를 공개 가능한가 | LG / HD Hyundai / 삼성 공개 신호 |
| 비용 단계 | bootcamp, PoC, 본사업 전환 시 비용 계단은 어떻게 생기는가 | SI형 구축 vs managed AI |

### 4-6. 미팅 직후 바로 남겨야 할 산출물
- PoC 대상 업무 1~2개
- 대상 데이터 소스 목록
- 금지 데이터 / 외부반출 금지 범위
- success KPI
- 8~12주 proof plan
- stop/go 기준

## 5. 장표 전체 톤 가이드
- `팔란티어가 좋아 보인다`가 아니라 `어디까지 믿고 어디부터 검증할지 안다`는 느낌이 맞다.
- 삼성은 headline case가 아니라 `signal case`다.
- 보안은 marketing reassurance가 아니라 `deployment governance design` 문제로 그려야 한다.
- 마지막 장은 `도입 제안`보다 `PoC 선정 프레임`이 더 중요하다.

## 6. 주요 링크
- Palantir Apollo docs: <https://www.palantir.com/docs/apollo/core/introduction>
- Palantir Foundry doc index: <https://www.palantir.com/docs/foundry/data-lineage/explore-artifacts/index.html>
- Palantir Privacy and Governance Whitepaper: <https://www.palantir.com/assets/xrfr7uokpv1b/4lXOhv4ycKr5IEMMFybaBj/2d7011ad45d11d189970d13e474f62bd/Palantir_Privacy_and_Governance_Whitepaper__1_.pdf>
- Azure data/privacy: <https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy>
- Azure private networking guidance: <https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/on-your-data-configuration>
- Vertex AI VPC-SC: <https://docs.cloud.google.com/vertex-ai/docs/general/vpc-service-controls>
- Korea law reference: <https://www.law.go.kr/LSW/lsPdfPrint.do?ancYnChk=0&bylChaChk=N&efGubun=Y&efYd=20220804&joAllCheck=Y&joEfOutPutYn=on&lsiSeq=240053&mokChaChk=N>
- LG CNS official: <https://www.lgcns.com/kr/newsroom/press/detail.enterpriseai-2603-4>
- Palantir/LG CNS: <https://www.nasdaq.com/press-release/lg-cns-and-palantir-announce-strategic-partnership-accelerate-ai-transformation-2026>
- HD Hyundai Reuters/Yahoo: <https://finance.yahoo.com/news/exclusive-palantir-signs-hd-hyundai-141518689.html>
- ETNews `2024-08-05`: <https://www.etnews.com/20240805000275>
- ETNews `2024-09-02`: <https://www.etnews.com/20240902000267>
- Samsung AI Forum 2025: <https://semiconductor.samsung.com/kr/news-events/tech-blog/future-of-semiconductor-industry-with-ai-samsung-ai-forum-2025/>
- Samsung GTC 2026: <https://semiconductor.samsung.com/kr/news-events/tech-blog/samsung-showcases-agentic-ai-driven-semiconductor-engineering-innovation-at-nvidia-gtc-2026/>
- Hankyung `2026-03-31`: <https://www.hankyung.com/article/2026033177201>

## 관련 내부 문서
- [2026-04-15_palantir_factcheck.md](C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\2026-04-15_palantir\reports\2026-04-15_palantir_factcheck.md)
- [2026-04-15_palantir_recent_2026_cases.md](C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\2026-04-15_palantir\reports\2026-04-15_palantir_recent_2026_cases.md)
- [2026-04-16_palantir_4page_sources.md](C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\2026-04-15_palantir\notes\2026-04-16_palantir_4page_sources.md)
