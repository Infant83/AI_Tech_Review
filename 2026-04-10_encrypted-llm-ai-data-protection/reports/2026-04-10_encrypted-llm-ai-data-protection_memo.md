# 2026-04-10 Encrypted LLM AI Data Protection Memo

## One-Line Take
- 동형암호 기반 Encrypted LLM은 `민감 데이터가 절대 평문으로 노출되면 안 되는 워크로드`에는 전략적 가치가 크지만, 2026-04-10 기준으로는 `범용 고성능 생성형 AI의 기본 실행 방식`이라기보다 `좁은 범위의 고보안 추론, 검색, 분석, 그리고 하이브리드 아키텍처`에 더 현실적이다.

## What Matters Most
- [Fact] 동형암호는 암호문 위에서 덧셈·곱셈과 그 조합 연산을 수행할 수 있으며, 표준화 논의와 오픈소스 생태계가 이미 형성되어 있다.
  - Sources: Homomorphic Encryption Standard v1.1, OpenFHE, HEAAN, TFHE-rs
- [Fact] 최근 연구는 `작은 모델`, `BERT 계열`, `특수 구조 변형 Transformer`, `HE-friendly self-attention`, `GPU 병렬화`, `가속기`에 집중되어 있다.
  - Sources: Powerformer, PowerSoftmax, Private LoRA Fine-tuning, AEGIS
- [Inference] 지금 가장 실용적인 방향은 `완전한 end-to-end encrypted generative chat`보다 `encrypted retrieval`, `secure reranking`, `private fine-tuning`, `민감 워크로드용 소형 모델`, `TEE+FHE 하이브리드`다.
- [Fact] TEE나 confidential computing은 이미 클라우드와 GPU 레벨에서 상용화 경로가 훨씬 분명하다.
  - Sources: AWS Nitro Enclaves, Azure Confidential Computing, NVIDIA confidential computing blog
- [Inference] 따라서 조직 관점의 기본 질문은 `FHE가 가능한가`가 아니라 `어느 연산을 FHE로 보호하고, 어느 구간은 TEE 또는 일반 보안 통제로 처리할 것인가`다.

## Strategic Reading
- 영상은 기술 가능성과 국가 경쟁력 측면을 강하게 제시한다.
- 실제 도입 판단은 `암호학적 보장`, `첫 토큰 지연`, `문맥 길이`, `모델 크기`, `연산 비용`, `키 관리`, `메타데이터/접근패턴 누출`, `배포 복잡도`를 함께 봐야 한다.
- 보안적으로는 FHE가 매우 강력하지만, 운영적으로는 `데이터 전 구간을 암호문으로 유지하는 설계`가 병목과 개발 난이도를 급격히 올린다.

## Where It Is Most Plausible Now
- 금융, 의료, 공공/국방처럼 `데이터가 매우 민감`하고 `지연보다 기밀성이 더 중요`한 환경
- 외부 API 사용이 어렵고, 온프렘 또는 프라이빗 클라우드에서 `좁은 태스크`를 반복하는 환경
- 문서 검색, 유사도 계산, 민감한 분석 파이프라인, small-model inference, private LoRA fine-tuning

## Where It Is Still Weak
- 장문 컨텍스트를 가진 범용 챗봇
- 높은 TPS가 필요한 실시간 서비스
- 대형 모델의 일반적인 end-to-end token generation
- 키 관리와 운영 체계 없이 “암호만 넣으면 안전하다”는 식의 단일기술 접근

## Recommended Framing For Slides
- `Why privacy-preserving AI now`
- `HE vs TEE vs MPC: what each actually protects`
- `What encrypted LLM really computes`
- `What is practical in 2026 and what is not`
- `Vendor and ecosystem map`
- `Decision framework for regulated enterprises`
