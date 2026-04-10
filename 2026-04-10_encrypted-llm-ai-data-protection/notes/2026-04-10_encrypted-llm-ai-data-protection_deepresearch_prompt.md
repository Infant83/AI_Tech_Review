# 🔷 Deep Research Prompt

## 1. 역할 정의
당신은 privacy-preserving AI, homomorphic encryption, encrypted inference, secure RAG, confidential computing, enterprise AI security architecture를 전문으로 하는 시니어 리서치 에이전트다.

반드시 다음 역할을 동시에 수행하라.
- Researcher: 1차 출처를 수집하고 구조화하라.
- Critic: 과장, 누락된 전제, 검증되지 않은 벤치마크를 반박하라.
- Strategist: 기술 결과를 도입 전략, 운영 모델, 투자/우선순위로 번역하라.

반드시 입력으로 제공된 시드 영상/발표를 출발점으로 사용하라.
반드시 시드 영상의 핵심 주장, 용어, 암묵적 전제를 먼저 추출하라.
단, 시드 영상을 최종 근거로 사용하지 마라. 핵심 주장과 수치는 반드시 외부 1차 출처로 재검증하라.

Do:
- Use the seed video as a hypothesis generator.
- Validate claims with primary sources.
- Separate mathematics, systems engineering, and business implications.

Avoid:
- 단일 출처 의존
- 마케팅 문구 재진술
- 검증되지 않은 속도/정확도 수치 반복
- 출처 없는 비교
- fabricated citations

---

## 2. 목표 정의
주제: 동형암호 기반 Encrypted LLM과 AI 데이터 보호

목표:
- Encrypted LLM의 기술 원리, 보안 보장, 실제 구현 방식, 성능 한계, 산업 적용성, 상용화 가능성을 심층 분석하라.
- “암호화된 상태에서 무엇이 실제로 계산되는가”를 명확히 설명하라.
- “이 기술이 지금 가능한 것”과 “아직 연구 단계인 것”을 분리하라.
- “보안적으로 강한 주장”과 “운영적으로 실용적인 주장”을 분리하라.
- 향후 2~3년 내 현실적인 도입 시나리오와 과장된 기대를 구분하라.

환경 가정:
- 민감 데이터 처리
- 온프렘 또는 프라이빗 클라우드 우선
- 외부 API 제한 가능성
- 규제 및 감사 대응 필요
- 조직 내 보안팀, 인프라팀, AI팀의 공동 의사결정 필요

반드시 아래 질문에 답하라.
1. Encrypted LLM의 정확한 위협 모델(threat model)은 무엇인가?
2. 어떤 연산이 실제로 암호문 상태에서 수행되는가?
3. 적용 범위는 inference, embedding, reranking, RAG, vector search, fine-tuning, training 중 어디까지인가?
4. 핵심 성능 병목은 무엇인가?  
   - latency  
   - first-token latency  
   - throughput  
   - memory overhead  
   - bootstrapping cost  
   - approximation error  
   - context length  
   - model size scalability
5. 동형암호 기반 접근은 TEE, MPC, 일반 암호화-at-rest/in-transit, 데이터 마스킹, differential privacy와 어떻게 다른가?
6. 어떤 산업(금융, 의료, 국방, 공공, B2B 지식검색, 얼굴/생체, 온디바이스 보안 AI 등)에서 즉시 의미가 있는가?
7. 어떤 조건에서는 아직 비실용적인가?
8. 상용 벤더/스타트업/빅테크/오픈소스 생태계는 어떻게 구성되는가?
9. 향후 2~3년 동안 무엇을 주시해야 하는가?
10. 기술 도입 시 경영진이 반드시 확인해야 할 go / no-go 기준은 무엇인가?

반드시 시드 영상 기반 Claim Verification Table을 작성하라.
- 시드 영상에서 최소 10개, 가능하면 15~20개의 핵심 주장을 추출하라.
- 각 주장마다 상태를 분류하라:
  - Verified
  - Partially Verified
  - Unverified
  - Misleading / Overstated
- 각 주장마다 근거 출처를 붙여라.
- 검증 불가한 경우 그 이유를 명시하라.

---

## 3. 리서치 프로세스

### STEP 1: 문제 정의
Must:
- 시드 영상의 핵심 주장, 핵심 용어, 암묵적 전제를 추출하라.
- 문제를 다음 축으로 재정의하라:
  1. 암호학적 보장
  2. 시스템 구현 가능성
  3. 모델 품질 영향
  4. 운영 비용
  5. 산업 적용성
- 용어집(glossary)을 먼저 작성하라.
- Encrypted LLM, FHE/HE, CKKS, BFV/BGV, TFHE, bootstrapping, secure inference, secure RAG, confidential computing, MPC 등 혼동 가능한 용어를 구분하라.

### STEP 2: 정보 수집 (학술 / 산업 / 엔지니어링)
Must:
- 최근 2~3년 자료를 우선하라.
- 단, foundational paper와 표준/원천 개념은 예외적으로 포함하라.
- 다음 범주에서 균형 있게 수집하라:
  - Academic: 논문, preprint, 학회/저널
  - Industry: 공식 기술 블로그, 벤치마크 공개자료, 제품 문서
  - Engineering: 구현 아키텍처, 하드웨어 가속, 시스템 최적화 자료
  - Standards / Policy: 표준화 논의, 규제, 보안 가이드
- 벤치마크 수집 시 다음 조건을 함께 기록하라:
  - model size
  - task type
  - dataset
  - hardware
  - precision / quantization
  - batch size
  - prompt length / context
  - latency metric definition
  - throughput metric definition
  - whether precomputation is included
- 기업 발표 자료는 반드시 독립 출처로 교차검증하라.

### STEP 3: 출처 검증
Must:
- 모든 출처를 신뢰도 등급으로 분류하라:
  - Tier 1: 원 논문, 공식 문서, 표준, 공식 벤치마크
  - Tier 2: 전문 매체, 산업 분석
  - Tier 3: 인터뷰, 세미나, 발표 영상, 마케팅 자료
- Tier 3 출처는 단독 근거로 사용하지 마라.
- peer-reviewed와 preprint를 구분하라.
- 수치가 충돌하면 더 높은 신뢰도 출처를 우선하라.
- 충돌이 해소되지 않으면 둘 다 제시하고 불확실성을 명시하라.
- Fact / Inference / Speculation을 명시적으로 구분하라.

Format:
- [Fact]
- [Inference]
- [Speculation]

### STEP 4: 구조화
Must:
- 다음 비교표를 작성하라:
  1. HE scheme comparison
  2. Encrypted LLM architecture patterns
  3. HE vs TEE vs MPC vs conventional encryption 비교
  4. 산업별 적용성 비교
  5. 벤더/생태계 맵
  6. 도입 난이도 vs 보안 이점 매트릭스
- 기술 설명은 “수학적 원리 → 시스템 아키텍처 → 성능 현실 → 운영 현실” 순서로 구조화하라.
- 이론적으로 가능한 것과 운영적으로 배포 가능한 것을 분리하라.

### STEP 5: 인사이트 도출
Must:
- 다음 질문에 대한 통찰을 도출하라:
  - 보안 강도가 실제 운영 가치를 만드는 지점은 어디인가?
  - 어떤 워크로드가 Encrypted LLM에 가장 적합한가?
  - 어떤 요구사항에서는 TEE나 하이브리드 방식이 더 합리적인가?
  - 현재 시장에서 과대평가된 주장과 저평가된 기회는 무엇인가?
- “핵심 trade-off”를 요약하라:
  - security vs latency
  - privacy vs utility
  - accuracy vs encrypted approximation
  - on-prem control vs engineering complexity
  - cryptographic rigor vs deployability

### STEP 6: 전략 해석
Must:
- 다음 이해관계자별 권고안을 제시하라:
  - CTO / Head of AI
  - CISO / Security Architect
  - Infra / Platform leader
  - Product leader
  - Investor / Strategy team
  - Public sector / regulated enterprise
- 0~6개월, 6~18개월, 18~36개월 로드맵을 제시하라.
- PoC, Pilot, Production 기준을 구분하라.
- 기술 도입을 위한 go / no-go checklist를 작성하라.
- “지금 당장 실험할 것”, “조건부로 관찰할 것”, “아직 기다릴 것”을 구분하라.

---

## 4. 출력 포맷
반드시 markdown으로 작성하라.
반드시 아래 top-level heading을 정확히 사용하라.

# Executive Summary
- 8~12개의 핵심 결론을 제시하라.
- 가장 중요한 기술적 결론 3개, 산업적 결론 3개, 전략적 결론 3개를 포함하라.
- 경영진용 한 줄 결론을 포함하라.

# Background
- 왜 AI 데이터 보호가 중요한지 설명하라.
- 기존 AI 보안 접근과 Encrypted LLM 접근의 차이를 설명하라.
- 시드 영상의 문제의식을 요약하되 검증 전제 여부를 명시하라.

# State of the Art
- 최근 2~3년 기준 학술·산업 동향을 정리하라.
- 대표 연구 방향, 구현 패턴, 가속 전략, 오픈 문제를 정리하라.
- “research-stage / pilot-stage / production-adjacent”로 분류하라.

# Technical Deep Dive
- 사용되는 암호학적 기법과 연산 모델을 설명하라.
- LLM inference pipeline에서 암호문 연산이 들어가는 위치를 설명하라.
- token generation, KV cache, attention, MLP, approximation, bootstrapping 문제를 다뤄라.
- encrypted RAG, encrypted embeddings, secure retrieval, hybrid architecture 가능성을 다뤄라.
- 성능 병목과 하드웨어 요구를 설명하라.
- 수학적 보장과 시스템 구현 보장을 분리하라.

# Industry Landscape
- 주요 플레이어 유형을 분류하라:
  - startups
  - big tech
  - infrastructure vendors
  - accelerator / hardware ecosystem
  - open-source / research ecosystem
- 각 플레이어의 포지셔닝과 차별점을 분석하라.
- 상용화 가능성이 높은 세그먼트와 아직 이른 세그먼트를 구분하라.

# Applications
- 산업별 use case를 제시하라.
- 각 use case마다 아래를 제시하라:
  - why encrypted AI matters
  - security requirement
  - feasibility today
  - deployment complexity
  - expected ROI or strategic value
- 최소한 금융, 의료, 국방/공공, enterprise knowledge assistant, biometric/privacy-sensitive AI를 포함하라.

# Limitations
- 기술적 한계, 운영적 한계, 비용 한계, 성능 한계, 인력/도입 한계를 분리하라.
- “수학적으로 안전하지만 운영상 취약한 지점”을 따로 적어라.
- side-channel, metadata leakage, access-pattern leakage, key management, logging leakage, integration risk를 다뤄라.

# Future Outlook
- 향후 2~3년의 발전 가능성을 예측하라.
- 무엇이 개선되면 adoption curve가 바뀌는지 설명하라.
- 하드웨어, 알고리즘, 하이브리드 아키텍처, 규제 수요, 표준화의 영향을 분석하라.

# Actionable Insights
- 조직이 지금 내릴 수 있는 5~10개의 실행 권고를 제시하라.
- PoC 설계안, 벤더 평가 질문, 보안 검토 질문, KPI 제안, 파일럿 우선순위를 포함하라.
- 다음 형식으로 정리하라:
  - Do Now
  - Evaluate Next
  - Monitor
  - Avoid for Now

# References
- 1차 출처를 우선 배치하라.
- 각 출처의 성격을 표시하라:
  - paper
  - preprint
  - official documentation
  - benchmark disclosure
  - standard/policy
  - industry analysis
  - seed video
- 링크, 제목, 저자/기관, 연도, 한 줄 relevance note를 포함하라.

필요 시 아래 부록을 추가하라.
- Appendix A: Seed Video Claim Verification Table
- Appendix B: Benchmark Comparison Table
- Appendix C: Glossary
- Appendix D: Threat Model Matrix

---

## 5. 품질 제약
Must:
- 모든 핵심 주장에 출처를 달아라.
- Fact / Inference / Speculation을 구분하라.
- 출처를 조작하지 마라.
- 불확실성을 숨기지 마라.
- 최신 정보 우선 원칙을 적용하라.
- 시점이 중요한 정보에는 날짜를 명시하라.
- 숫자 비교에는 측정 조건을 함께 적어라.
- 벤더 주장과 독립 검증 결과를 분리하라.
- “가능하다”와 “실용적이다”를 같은 의미로 쓰지 마라.
- “데모 가능”, “제한적 파일럿 가능”, “프로덕션 가능”을 구분하라.

Do:
- 상충하는 자료가 있으면 둘 다 제시하라.
- 연구 공백과 미해결 문제를 명확히 적어라.
- 수학적 안전성, 구현 안전성, 운영 안전성을 분리하라.

Avoid:
- 근거 없는 낙관론
- 근거 없는 비관론
- 최신성 검증 없는 주장
- 홍보성 문구
- 추정치를 사실처럼 표현하는 서술

---

## 6. 스타일
- 한국어로 작성하라.
- 문장은 간결하게 유지하라.
- 불필요한 수사 없이 분석적으로 작성하라.
- 기술 용어는 최초 1회 정의하라.
- 표와 매트릭스를 적극 활용하라.
- 각 주요 섹션 끝에 “Why this matters”를 2~4문장으로 추가하라.
- 경영진이 읽을 수 있을 정도로 명료하게 쓰되, 연구자/엔지니어가 검증 가능한 수준의 정밀도를 유지하라.
- 긴 인용 대신 요약과 비교를 사용하라.
- 보고서 전체에서 반복을 줄이고, 핵심 trade-off를 지속적으로 강조하라.

---

## 7. 확장 옵션

### Option A: 멀티에이전트 모드
다음 순서로 내부 검토를 수행하라.
1. Researcher Draft
2. Critic Review
3. Strategist Synthesis

각 단계에서 반드시 이전 단계의 약점을 보완하라.

### Option B: 온프렘 / 프라이빗 클라우드 모드
다음 항목을 추가 분석하라.
- 외부 API 차단 환경
- 데이터 상주성(data residency)
- KMS / HSM / 키 수명주기
- 네트워크 분리
- 감사 로그 및 포렌식
- 모델 업데이트 절차
- GPU 스케줄링과 격리
- 오프라인 배포 운영성

### Option C: 보안 심화 모드
다음 보안 항목을 별도 섹션으로 분석하라.
- threat model taxonomy
- key management failure modes
- metadata leakage
- access-pattern leakage
- prompt / retrieval leakage
- model extraction risk
- insider threat
- supply chain risk
- benchmark fraud risk

### Option D: 실행 중심 모드
다음을 반드시 산출하라.
- 90일 PoC 계획
- 벤더 평가 질문 20개
- 보안 검토 질문 20개
- 파일럿 성공 KPI
- go / no-go gate criteria

### Option E: 지역/정책 모드
입력 맥락이 특정 국가 또는 규제 환경과 연결되어 있으면 다음을 추가하라.
- 해당 지역의 정책/규제 요구
- 공공조달 또는 산업별 규제 이슈
- 현지 기업/연구기관 생태계
- 데이터 주권 관점의 시사점

최종 산출물은 “영상 요약”이 아니라 “검증된 심층 리서치 보고서”여야 한다.
시드 영상은 연구 질문을 여는 출발점일 뿐, 최종 결론의 근거가 되어서는 안 된다.
