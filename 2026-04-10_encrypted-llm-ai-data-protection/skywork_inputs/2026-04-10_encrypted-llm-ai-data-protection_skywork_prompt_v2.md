업로드된 자료와 템플릿을 기반으로 새로운 한국어 PowerPoint deck을 생성하라.

프로젝트명: Encrypted LLM과 AI 데이터 보호
청중: CTO, CISO, 보안 아키텍트, AI 플랫폼 리더, 기술전략 담당자
목적: 동형암호 기반 Encrypted LLM의 기술 현실, 보안 가치, 한계, 도입 전략을 깊이 있게 이해시키는 기술 브리핑
권장 분량: 14장
비율: 16:9

사용할 업로드 자료:
1. `2026-04-10_encrypted-llm-ai-data-protection_deepresearch.md`
2. `2026-04-10_encrypted-llm-ai-data-protection_memo.md`
3. `2026-04-10_encrypted-llm-ai-data-protection_gpt_deepresearch_raw.md`

소스 우선순위:
1. 업로드된 통합 deep research report
2. 업로드된 GPT deep research raw report
3. 업로드된 memo
4. 시드 영상 transcript와 metadata
5. 필요한 경우에만 공식 1차 소스

핵심 편집 원칙:
- deck의 thesis는 `Encrypted LLM은 전략적으로 중요하지만, 현재의 실전 중심은 end-to-end encrypted chat이 아니라 encrypted retrieval + hybrid privacy architecture` 여야 한다.
- 시드 영상의 문제의식은 살리되, 속도 수치나 상용화 수준은 반드시 검증 결과에 맞춰 낮추거나 caveat를 붙여라.
- 정보 밀도가 높아야 하며, 빈 슬라이드나 큰 카피 중심 장표를 피하라.
- 기술 보장, 시스템 현실, 운영 현실을 분리해서 설명하라.

반드시 반영할 verified / high-confidence facts:
- Homomorphic Encryption Standard v1.1은 HE security model과 parameter guidance를 제공한다.
- 2024 benchmarking breakout은 encrypted RAG를 대표 use case로 제시한다.
- Apple은 BFV + PIR/PNNS + DP/OHTTP를 결합해 privacy-preserving search architecture를 공개했다.
- Cerium은 CKKS 기반 multi-GPU encrypted large-model inference 연구로 bootstrapping 7.5ms, BERT-Base 8.8s, Llama3-8B first token 134s를 제시한다.
- Wally는 private search throughput을 논의하지만 조건 의존적이므로 benchmark caveat를 명시해야 한다.
- Powerformer는 softmax/LN replacement와 approximation으로 BERT-base 계열 FHE inference 최적화를 제시한다.
- Private LoRA Fine-tuning of Open-Source LLMs with Homomorphic Encryption은 Llama-3.2-1B private fine-tuning feasibility를 제시한다.
- AEGIS는 2048-token encrypted Transformer inference의 multi-GPU scaling 효율을 보고한다.
- OpenFHE, HEIR, TFHE-rs/Zama, HEaaN, IBM, CRYPTOLAB은 현재 생태계를 설명하는 핵심 축이다.
- 임베딩은 안전한 익명 표현이 아니며 embedding inversion risk를 분명히 설명해야 한다.
- TEE는 운영 현실성이 더 높지만 side-channel / hardware trust / attestation 문제를 남긴다.

반드시 피할 것:
- 엔드투엔드 encrypted LLM을 이미 상용 대화형 서비스 수준이라고 묘사하는 과장
- HE benchmark와 end-to-end LLM latency를 같은 수치처럼 섞는 표현
- 벤더 주장과 논문 검증 결과를 구분하지 않는 서술
- 너무 큰 타이틀과 빈 여백만 있는 마케팅 스타일

필수 장표 구성:
- 1장: 제목 + 한 줄 결론 + 왜 지금 중요한지
- 2장: executive summary 3x3
- 3장: 위협 모델과 데이터 노출 구간 맵
- 4장: HE vs TEE vs MPC vs conventional encryption 비교표
- 5장: 암호문 상태에서 실제 가능한 연산과 불리한 연산
- 6장: Transformer pipeline 병목과 bootstrapping / approximation / memory overhead
- 7장: research-stage / pilot-stage / production-adjacent maturity map
- 8장: Powerformer / Private LoRA / AEGIS / Cerium 비교
- 9장: Apple-style encrypted retrieval / secure RAG / hybrid architecture
- 10장: 산업별 적용성 매트릭스
- 11장: 오픈소스 / 스타트업 / 빅테크 / confidential computing ecosystem map
- 12장: 시드 영상 claim verification table 요약
- 13장: 0~6개월 / 6~18개월 / 18~36개월 도입 로드맵
- 14장: go / no-go checklist + closing insight

시각 정책:
- sparse marketing style보다 dense technical briefing style을 우선하라.
- 표, evidence matrix, layered diagram, annotated workflow를 적극 사용하라.
- annotation은 작은 짙은 녹색 텍스트로 관련 블록 근처에 붙여라.
- source cue와 reference는 작은 짙은 회색 텍스트로 하단 또는 관련 블록 근처에 붙여라.
- 장식용 이미지 대신 설명 기능이 있는 구조 도식과 비교표를 사용하라.

좋은 슬라이드의 조건:
- 각 슬라이드마다 thesis line 하나와 evidence block 여러 개가 있어야 한다.
- 경영진이 읽어도 명료하고, 엔지니어가 봐도 얇지 않아야 한다.
- `가능하다`와 `실용적이다`를 구분하라.
- `privacy-preserving search`와 `fully encrypted generation`을 같은 성숙도로 보이지 않게 구성하라.

이 기준으로 전체 deck을 생성하라.
