업로드된 자료와 템플릿을 기반으로 새로운 한국어 PowerPoint deck을 생성하라.

프로젝트명: Encrypted LLM과 AI 데이터 보호
청중: CTO, CISO, 보안 아키텍트, AI 플랫폼 리더, 기술전략 담당자
목적: 동형암호 기반 Encrypted LLM의 기술 현실, 보안 가치, 한계, 도입 전략을 깊이 있게 이해시키는 기술 브리핑
권장 분량: 14장
비율: 16:9

소스 우선순위:
1. 업로드된 `2026-04-10_encrypted-llm-ai-data-protection_deepresearch.md`
2. 업로드된 `2026-04-10_encrypted-llm-ai-data-protection_memo.md`
3. 업로드된 시드 영상 transcript와 metadata
4. 필요한 경우에만 슬라이드 내부 fact anchor를 보강하는 공식 1차 소스

리서치 정책:
- 업로드된 deep research report가 주된 사실 기준이다.
- 외부 검색은 오래되었거나 불확실한 수치, 플레이어 현황, 비교 포인트 보강에만 제한적으로 사용하라.
- 현재 사실, 수치, 벤더 주장에는 출처가 필요하다.

템플릿 원칙:
- 기본 템플릿 리듬은 유지하되 기술 브리핑에 맞게 정보 밀집형으로 구성하라.
- 장표 목적에 따라 thesis slide, evidence matrix, source comparison, annotated workflow, dense memo slide를 섞어라.
- 같은 카드형 2장 이상 반복하지 말고 장표 구조를 바꿔라.

전체 서사:
- 왜 지금 privacy-preserving AI가 중요한가
- HE가 실제로 무엇을 보호하는가
- Encrypted LLM은 어디까지 현실적인가
- FHE와 TEE/MPC는 어떻게 다르며 어떻게 조합해야 하는가
- 어떤 산업에서 먼저 가치가 생기는가
- 경영진은 어떤 기준으로 go / no-go를 판단해야 하는가

섹션 정책:
- CH00: briefing, density=high, evidence=explicit
- CH01: analysis, density=high, evidence=explicit
- CH02: paper_review, density=high, evidence=explicit
- CH03: internal_report, density=high, evidence=explicit
- CH04: analysis, density=high, evidence=explicit
- CH05: briefing, density=high, evidence=explicit

반영해야 할 현재 사실:
- Homomorphic Encryption Standard v1.1은 HE security model과 parameter guidance를 제공한다.
- HomomorphicEncryption.org 2024 benchmarking 자료는 encrypted RAG를 대표 use case로 제시한다.
- Powerformer는 BERT-base 기반 HE inference에서 softmax/LN replacement와 approximation을 통해 기존 대비 계산시간 45% 절감을 보고했다.
- Private LoRA Fine-tuning of Open-Source LLMs with Homomorphic Encryption은 Llama-3.2-1B에 대한 private fine-tuning feasibility를 제시했다.
- AEGIS는 2048-token encrypted Transformer inference의 multi-GPU scaling 효율을 보고했다.
- AWS Nitro Enclaves와 NVIDIA confidential computing 사례는 TEE/confidential AI가 현재 더 넓은 운영 현실성을 가진 대안임을 보여 준다.
- HEaaN은 GPU-accelerated CKKS bootstrapping 수치를 제시하지만 이는 end-to-end LLM latency와 동일하지 않다.

필수 장표 구성:
- 1장: 제목 + 한 줄 결론 + 왜 지금 중요한지
- 2장: executive summary 3x3 구조
- 3장: 위협 모델과 데이터 노출 구간 맵
- 4장: HE vs TEE vs MPC vs conventional encryption 비교표
- 5장: Encrypted LLM에서 실제로 계산되는 것과 어려운 것
- 6장: Transformer pipeline에서 병목이 생기는 지점
- 7장: research-stage / pilot-stage / production-adjacent 분류
- 8장: Powerformer / Private LoRA / AEGIS 비교
- 9장: encrypted retrieval / secure RAG / hybrid architecture 설명
- 10장: 산업별 적용성 매트릭스
- 11장: 벤더 및 생태계 맵
- 12장: 시드 영상 Claim Verification Table 요약
- 13장: 도입 로드맵 0~6개월 / 6~18개월 / 18~36개월
- 14장: go / no-go checklist와 closing insight

시각/레이아웃 정책:
- sparse marketing style보다 정보 밀집형 구성을 우선하라.
- 큰 빈 공간 대신 구조화된 텍스트, 표, 다이어그램, source cue를 사용하라.
- compound slide를 허용하되 하나의 상위 인사이트로 수렴시켜라.
- 기술 용어, caveat, 정의, 맥락 보완은 작은 짙은 녹색 inline annotation text로 본문 옆이나 아래에 붙여라.
- annotation은 별도 카드처럼 분리하지 말고 관련 블록에 종속적으로 배치하라.
- 출처와 reference note는 하단 또는 관련 블록 가까이에 작은 짙은 회색 text로 표기하라.
- 그림이나 아이콘은 장식용이 아니라 설명 기능이 있어야 한다.
- 표와 매트릭스는 실제 판단을 돕는 형태로 구성하라.

좋은 장표가 되기 위한 규칙:
- 각 장표에 하나의 thesis line을 두고, supporting evidence가 그 thesis를 받치게 하라.
- 기술 슬라이드는 수학적 보장, 시스템 현실, 운영 현실을 혼동하지 말라.
- 경영진이 읽을 수 있을 정도로 명료하되, 엔지니어가 봐도 얇지 않게 만들어라.
- 영상의 주장을 그대로 확대 재생산하지 말고 검증 결과를 반영하라.
- “가능하다”와 “실용적이다”를 구분하라.

피해야 할 것:
- 너무 큰 제목과 너무 적은 본문만 있는 빈 슬라이드
- 근거 없는 수치나 출처 없는 비교
- 지나치게 단순한 AI 슬로건 장표
- 암호학적 안전성과 운영적 안전성을 같은 말처럼 취급하는 표현
- 엔드투엔드 encrypted LLM을 이미 일반 상용 기술처럼 묘사하는 과장

이 기준으로 전체 deck을 생성하라.
