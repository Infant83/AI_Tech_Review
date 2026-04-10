# Executive Summary
- [Fact] 동형암호 기반 Encrypted LLM은 `암호문 상태에서 연산을 수행하고 결과만 복호화`한다는 점에서 일반적인 암호화-at-rest/in-transit보다 강한 보호 모델을 제공한다.  
  Sources: https://homomorphicencryption.org/wp-content/uploads/2024/08/Homomorphic-Encryption-Standard-v1.1.pdf, https://docs.zama.org/tfhe-rs/get-started/getting-started
- [Fact] 그러나 2026-04-10 기준으로 실용성이 가장 높은 영역은 `범용 장문 생성형 챗봇`이 아니라 `좁은 태스크의 private inference`, `encrypted retrieval`, `secure reranking`, `HE-friendly small model`, `private LoRA fine-tuning`, `TEE/FHE hybrid`다.  
  Sources: https://eprint.iacr.org/2024/1429, https://arxiv.org/abs/2505.07329, https://arxiv.org/abs/2604.03425
- [Fact] 최근 연구는 softmax, layer normalization, GELU 같은 비선형 연산을 직접 계산하기보다 `다항식 근사`나 `구조 대체`로 바꾸고, attention/FFN/bootstrapping을 병목으로 다룬다.  
  Sources: https://eprint.iacr.org/2024/1429, https://research.ibm.com/publications/powersoftmax-towards-secure-llm-inference-over-fhe
- [Fact] 하드웨어와 시스템 연구는 이미 `multi-GPU 병렬화`, `GPU bootstrapping`, `HE-friendly kernels`, `specialized placement`까지 진입했다.  
  Sources: https://heaan.io/, https://arxiv.org/abs/2604.03425
- [Inference] 기술의 전략적 가치는 “모든 AI를 FHE로 돌린다”보다 `가장 민감한 데이터 경로만 평문 노출 없이 처리한다`는 설계 철학에 있다.
- [Fact] TEE/confidential computing은 FHE보다 약한 보장 모델이지만, 현재는 훨씬 넓은 모델 크기와 운영성을 제공한다.  
  Sources: https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html, https://developer.nvidia.com/blog/advancing-security-for-large-language-models-with-nvidia-gpus-and-edgeless-systems/
- [Inference] 향후 2~3년의 경쟁축은 `순수 FHE LLM` 단일 축이 아니라 `FHE vs TEE`가 아니라 `FHE + TEE + sandbox + KMS + policy control`의 조합 설계가 될 가능성이 높다.
- [Fact] 오픈소스 생태계는 OpenFHE, HElib, HEAAN, Microsoft SEAL, Zama TFHE-rs 등으로 이미 형성되어 있으며, 상용 쪽은 CRYPTOLAB, IBM, confidential-computing vendors가 결합하는 구조다.  
  Sources: https://homomorphicencryption.org/availability/, https://openfhe.org/, https://heaan.io/, https://research.ibm.com/projects/ai-on-encrypted-data-via-fhe
- [Inference] 대한민국 맥락에서는 `민감 산업 데이터는 강하지만 공개 학습 데이터와 초대형 모델 생태계는 상대적으로 약하다`는 점 때문에, `데이터 보호형 AI`는 차별화 포인트가 될 수 있다.
- 경영진 한 줄 결론: `Encrypted LLM은 당장 모든 생성형 AI를 대체할 기술이 아니라, 규제·기밀 환경에서 고가치 데이터 경로를 보호하는 선택적 아키텍처로 봐야 한다.`

# Background
민감 데이터가 LLM 파이프라인에 들어가면 공격면은 크게 다섯 개로 나뉜다.
- 학습 데이터 노출
- 프롬프트 및 검색 질의 노출
- 추론 중 메모리 노출
- 모델 추출 및 재현
- 운영 로그, 캐시, 접근패턴, 메타데이터 노출

일반적인 보안 통제는 저장시 암호화, 전송시 암호화, 접근통제, 로그감사, 망분리, 비밀관리 등을 결합한다. 그러나 이 방식은 `실행 중 데이터`를 반드시 신뢰 가능한 실행 환경에 노출시킨다. 반면 FHE는 이 실행 구간까지 암호문 상태를 유지하려 한다.  
Sources: https://homomorphicencryption.org/wp-content/uploads/2024/08/Homomorphic-Encryption-Standard-v1.1.pdf, https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html

시드 영상의 문제의식은 분명하다.
- 우리나라가 가진 민감 데이터는 경쟁력 자산이다.
- 이 데이터는 일반적인 클라우드 AI 파이프라인에 그대로 투입하기 어렵다.
- 따라서 `평문 노출을 극소화하는 AI`가 산업·국가 경쟁력과 연결될 수 있다.

[Inference] 이 문제의식 자체는 타당하다. 다만 기술 검증은 별개다. 영상 속 `시연`, `속도`, `국방 적용`, `마켓플레이스 진입`, `최초 구현` 같은 주장은 외부 1차 자료로 나눠서 검증해야 한다.

Why this matters: 보안 논의에서 가장 흔한 오류는 “암호화 여부”만 보고 판단하는 것이다. 실제 도입은 `어느 구간이 평문인지`, `누가 키를 가지는지`, `누가 실행환경을 통제하는지`, `메타데이터는 남는지`까지 함께 봐야 한다.

# State of the Art
2024년부터 2026년 초까지의 흐름은 세 갈래다.

## 1. 암호학 및 라이브러리 기반 성숙도
- [Fact] HomomorphicEncryption.org는 BGV, BFV, CKKS, TFHE 계열과 보안 파라미터 논의를 계속 표준화하고 있다.  
  Source: https://homomorphicencryption.org/wp-content/uploads/2024/08/Homomorphic-Encryption-Standard-v1.1.pdf
- [Fact] Open-source availability 페이지는 OpenFHE, HElib, HEAAN, Microsoft SEAL, Lattigo, Concrete를 주요 공개 구현으로 정리한다.  
  Source: https://homomorphicencryption.org/availability/
- [Fact] HEaaN은 CKKS 중심으로 GPU 가속 bootstrapping 성능을 전면에 내세우고 있다.  
  Source: https://heaan.io/

## 2. HE-friendly model architecture
- [Fact] Powerformer는 softmax/LN을 power/linear function으로 치환하고 GELU, tanh를 저비용 근사로 바꾸면서 BERT-base 기반에서 기존 대비 계산시간 45% 절감을 보고했다.  
  Source: https://eprint.iacr.org/2024/1429
- [Fact] IBM의 PowerSoftmax는 secure LLM inference용으로 nonlinear bottleneck을 완화하는 구조를 제안한다.  
  Source: https://research.ibm.com/publications/powersoftmax-towards-secure-llm-inference-over-fhe

## 3. 시스템 및 병렬화
- [Fact] AEGIS는 long-sequence encrypted Transformer inference를 multi-GPU로 확장하면서 2048-token 입력에서 inter-GPU communication과 per-device memory를 크게 줄였다고 보고한다.  
  Source: https://arxiv.org/abs/2604.03425
- [Fact] Private LoRA Fine-tuning of Open-Source LLMs with Homomorphic Encryption은 Llama-3.2-1B를 대상으로 private fine-tuning feasibility를 제시한다.  
  Source: https://arxiv.org/abs/2505.07329

## Research-stage / Pilot-stage / Production-adjacent
- Research-stage:
  - long-context encrypted transformer
  - fully encrypted generation with competitive latency
  - large-model training
- Pilot-stage:
  - private LoRA fine-tuning
  - encrypted BERT-like inference
  - encrypted similarity search or retrieval subroutines
- Production-adjacent:
  - HE libraries for selected analytics
  - TEE/confidential computing for LLM serving
  - hybrid FHE + TEE + sandbox design

Why this matters: 현재 기술 성숙도는 “LLM 시대에 FHE가 시작선에 섰다” 정도로 보는 편이 맞다. 과대평가도 경계해야 하지만, 2024년 이후의 연구 가속 자체는 분명하다.

# Technical Deep Dive
## What is actually computed on ciphertexts
[Fact] FHE가 직접 잘하는 것은 덧셈, 곱셈, 회전, 키 스위칭, 그리고 이들을 조합한 회로다.  
Source: https://homomorphicencryption.org/wp-content/uploads/2024/08/Homomorphic-Encryption-Standard-v1.1.pdf

[Fact] CKKS 계열은 근사 실수 연산에 강해 벡터/행렬 연산과 딥러닝 친화적이지만, 모든 연산은 `노이즈 성장`, `모듈러스 체인`, `precision budget`, `bootstrapping`의 제약을 받는다.  
Sources: https://homomorphicencryption.org/wp-content/uploads/2024/08/Homomorphic-Encryption-Standard-v1.1.pdf, https://heaan.io/

## LLM pipeline under FHE
일반 LLM 추론 파이프라인을 FHE 관점에서 나누면 다음과 같다.
- embedding / projection: 상대적으로 구조화된 선형대수
- QKV projection and attention: 대규모 행렬 연산 + normalization + softmax 근사 문제
- MLP blocks: 행렬 연산은 가능하지만 activation 함수 근사가 필요
- token generation: argmax, sampling, iterative decoding이 누적 지연을 유발
- KV cache: 길어질수록 메모리와 ciphertext 비용이 폭증

## What becomes expensive
- bootstrapping
- ciphertext size growth
- context-length scaling
- precision management
- inter-device communication
- function approximation error

## Why softmax and normalization are hard
[Fact] softmax, layer normalization, GELU는 FHE에서 직접 계산 비용이 매우 높다. 그래서 최신 연구는 이들을 다항식 또는 더 단순한 함수로 대체한다.  
Sources: https://eprint.iacr.org/2024/1429, https://research.ibm.com/publications/powersoftmax-towards-secure-llm-inference-over-fhe

## Encrypted RAG
[Fact] HomomorphicEncryption.org의 2024 benchmarking breakout 자료는 encrypted RAG with external knowledge base를 대표 use case로 제시한다.  
Source: https://homomorphicencryption.org/wp-content/uploads/2024/10/Benchmarking.pdf

[Inference] 완전한 encrypted RAG보다 가까운 현실은 다음과 같은 하이브리드다.
- query embedding만 보호
- vector similarity / retrieval만 보호
- retrieved chunk는 최소한만 복호
- generation은 TEE 안에서 수행

## FHE vs TEE vs MPC vs conventional encryption
| 방식 | 보호 구간 | 장점 | 약점 | 2026 현실성 |
| --- | --- | --- | --- | --- |
| Conventional encryption | 저장/전송 | 저렴하고 표준적 | 실행 중 평문 노출 | 매우 높음 |
| TEE / Confidential computing | 실행 중 메모리 격리 | 큰 모델과 기존 스택 수용성 높음 | 하드웨어 신뢰, 측면채널, 운영 신뢰가 남음 | 매우 높음 |
| MPC | 다자 분산 신뢰 | 특정 협업 시나리오에 유리 | 통신비용 큼 | 중간 |
| Pure FHE | 실행 중에도 암호문 유지 | 가장 강한 데이터 기밀성 모델 | 지연, 메모리, 복잡도, 함수 근사 제약 | 제한적 |

[Fact] AWS Nitro Enclaves는 외부 네트워크와 관리자 접근이 차단된 격리 실행 환경을 제공하며, attestation과 KMS 연동을 제공한다.  
Source: https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html

[Fact] NVIDIA + Edgeless Systems 사례는 confidential VM + H100 GPU + sandbox를 결합해 프롬프트와 응답을 보호하는 confidential AI 경로를 제시한다.  
Source: https://developer.nvidia.com/blog/advancing-security-for-large-language-models-with-nvidia-gpus-and-edgeless-systems/

Why this matters: 실제 아키텍처 결정은 `순수 FHE`와 `전통 보안` 중 택일이 아니다. 보호 강도와 운영성의 최적 조합을 찾는 문제다.

# Industry Landscape
## Startups and specialized vendors
- CRYPTOLAB
  - [Fact] HEaaN Private AI를 homomorphic-encryption-based data analysis solution으로 소개하고, Encrypted LLM Experience를 별도 도구로 내세운다.  
    Source: https://www.cryptolab.co.kr/en/mainpages/heaan-ai-en/
- Zama
  - [Fact] TFHE-rs와 Concrete 계열을 중심으로 programmable bootstrapping과 fixed-precision FHE 생태계를 구축 중이다.  
    Source: https://docs.zama.org/tfhe-rs/get-started/getting-started
- IBM
  - [Fact] HElayers와 AI on Encrypted Data via FHE 프로젝트를 통해 상용 AI 애플리케이션 경로를 제공한다.  
    Source: https://research.ibm.com/projects/ai-on-encrypted-data-via-fhe

## Open-source and research ecosystem
- OpenFHE
  - community-driven open-source FHE library
- HElib
  - IBM 계열의 오래된 핵심 라이브러리
- Microsoft SEAL
  - BFV/CKKS 중심의 널리 쓰이는 라이브러리
- HEAAN
  - CKKS 중심 연구·상용화 연결축

## Big tech and infrastructure
- AWS Nitro Enclaves
- Azure Confidential Computing
- NVIDIA confidential AI stack

[Inference] 빅테크는 현재 `FHE-native LLM serving`보다 `confidential computing + secure infrastructure`에 더 무게를 두고 있다. 반면 FHE-native 쪽은 아직 specialized vendors와 academia가 더 빠르다.

## Commercial segments with strongest near-term potential
- regulated analytics
- secure document intelligence
- defense/public sector inference
- private fine-tuning of smaller open models
- cross-organization secure retrieval

Why this matters: 시장은 아직 단일 우승자가 없는 초기 단계다. 기술 구매자는 “가장 화려한 데모”보다 `어떤 보호 모델을 어떤 workload에서 검증했는가`를 물어야 한다.

# Applications
## 금융
- why it matters:
  - 거래, 고객, 리스크 데이터는 민감하고 규제가 강하다.
- feasibility today:
  - private scoring, narrow-document QA, secure retrieval은 가능성이 있다.
- deployment complexity:
  - 높음. 키 관리, audit, latency budget, fallback path 설계 필요
- strategic value:
  - 외부 모델 활용이 막힌 데이터 자산을 더 안전하게 활용 가능

## 의료
- why it matters:
  - 진료 기록과 영상/유전체는 극단적으로 민감하다.
- feasibility today:
  - classification, retrieval, private fine-tuning, selected analytics는 가능성이 있다.
- strategic value:
  - 원자료 노출 없이 분석 협업 가능성 확대

## 국방 / 공공
- why it matters:
  - 외부 API 금지, 망분리, 최고 등급 데이터 처리 요구
- feasibility today:
  - narrow inference, encrypted retrieval, mission-specific models에 유리
- strategic value:
  - 인력 신뢰등급 의존도를 줄이고 외부 처리 가능성을 넓힘

## Enterprise knowledge assistant
- why it matters:
  - 사내 문서, 메일, 설계자료는 유출 비용이 크다.
- feasibility today:
  - encrypted retrieval + TEE generation이 pure FHE full generation보다 현실적
- strategic value:
  - 문서 활용률은 높이고 평문 노출은 줄일 수 있음

## Biometric and privacy-sensitive AI
- why it matters:
  - 얼굴, 음성, 생체인증은 재발급이 불가능한 데이터다.
- feasibility today:
  - secure matching, selected classifiers, low-latency narrow models에 적합

Why this matters: 이 기술은 “모든 AI”가 아니라 `데이터 한 건이 유출되어도 비용이 큰 도메인`에서 먼저 가치가 생긴다.

# Limitations
## Technical limits
- bootstrapping cost remains material
- long-context generation is still expensive
- nonlinear approximations can hurt model quality
- large-model scaling is memory-heavy
- decoding loop latency compounds with each generated token

## Operational limits
- key lifecycle management is hard
- encrypted compute debugging is difficult
- observability can conflict with confidentiality
- software engineering burden is high

## Security limits
- [Fact] FHE는 ciphertext content를 보호하지만, 시스템 전체가 자동으로 안전해지는 것은 아니다.
- metadata leakage
- access-pattern leakage
- traffic analysis
- logging leakage
- model or prompt exfiltration in non-FHE components
- side-channel issues when hybridizing with accelerators or TEEs

## Economic limits
- GPU cost
- engineering specialization
- smaller model constraints
- throughput limits
- uncertain vendor maturity

[Inference] “수학적으로 안전하다”와 “운영상 안전하다”는 다르다. 특히 retrieval, orchestration, logging, key service, human operator 경로는 별도 통제로 봐야 한다.

Why this matters: 과장된 기대는 대개 여기서 무너진다. 실제 도입은 알고리즘보다 배포 설계에서 실패하는 경우가 많다.

# Future Outlook
## 0 to 12 months
- GPU bootstrapping and HE-friendly kernels continue to improve
- small-model encrypted inference demos become more common
- hybrid secure RAG patterns mature faster than pure encrypted generation

## 12 to 24 months
- private fine-tuning and confidential enterprise assistants expand
- vendor differentiation shifts from “can do FHE” to “what workload, what latency, what evidence”
- standardization and benchmarking pressure increases

## 24 to 36 months
- practical adoption depends on:
  - cheaper bootstrapping
  - better attention approximations
  - more efficient key/ciphertext management
  - repeatable benchmark suites
  - clearer procurement standards in regulated sectors

[Inference] adoption curve를 바꿀 핵심은 단순한 알고리즘 진보보다 `benchmark transparency`, `hybrid reference architectures`, `auditable deployment patterns`일 가능성이 크다.

Why this matters: 기술만 빨라져도 시장이 열리는 것이 아니다. 조직이 믿고 살 수 있는 표준화와 운영 모델이 필요하다.

# Actionable Insights
## Do Now
- 민감 워크로드를 `검색`, `랭킹`, `추론`, `튜닝`, `생성`으로 분해하라.
- 각 단계별 평문 노출 구간을 맵핑하라.
- TEE만으로 충분한지, FHE가 필요한지, 하이브리드가 맞는지 workload별로 구분하라.
- 작은 모델 기반의 encrypted PoC를 먼저 설계하라.

## Evaluate Next
- 벤더의 end-to-end latency뿐 아니라 first-token latency, context length, hardware 조건, bootstrapping 포함 여부를 요구하라.
- claim verification table 없이 데모 수치를 믿지 말라.
- key management, audit, observability 설계를 제품 데모와 분리해서 평가하라.

## Monitor
- AEGIS 계열의 long-sequence scaling
- private LoRA fine-tuning 계열
- HE benchmarking standardization
- confidential AI with sandboxed GPUs

## Avoid for Now
- 범용 대형 챗봇을 pure FHE로 바로 대체하려는 계획
- 키 관리와 운영 프로세스 없이 “암호화만 하면 된다”는 접근
- 검증 조건이 없는 vendor benchmark

## 90-day PoC suggestion
1. narrow use case 선정: 민감 문서 검색 또는 private reranking
2. baseline 설계: conventional + TEE + partial FHE 비교
3. 측정 KPI:
   - first-token latency
   - end-to-end latency
   - accuracy delta
   - cost per request
   - plaintext exposure points
4. go / no-go gate:
   - latency budget 충족 여부
   - 운영 복잡도 수용 가능 여부
   - 키 관리 체계 설계 가능 여부
   - 보안팀과 인프라팀의 운영 승인 가능 여부

# References
- Homomorphic Encryption Standard v1.1  
  - type: standard/policy  
  - https://homomorphicencryption.org/wp-content/uploads/2024/08/Homomorphic-Encryption-Standard-v1.1.pdf  
  - relevance: HE security model, scheme taxonomy, parameters, refresh/bootstrapping semantics
- FHE Use-Cases and Benchmarking  
  - type: benchmark disclosure  
  - https://homomorphicencryption.org/wp-content/uploads/2024/10/Benchmarking.pdf  
  - relevance: real-world benchmarking framing, encrypted RAG as representative workload
- Open-Source Availability  
  - type: official documentation  
  - https://homomorphicencryption.org/availability/  
  - relevance: ecosystem map of major HE libraries
- OpenFHE  
  - type: official documentation  
  - https://openfhe.org/  
  - relevance: open-source FHE library ecosystem
- CODE.HEAAN  
  - type: official documentation  
  - https://heaan.io/  
  - relevance: CKKS bootstrapping performance claims and product posture
- HEaaN Private AI  
  - type: official documentation  
  - https://www.cryptolab.co.kr/en/mainpages/heaan-ai-en/  
  - relevance: vendor positioning for HE-based private AI
- TFHE-rs  
  - type: official documentation  
  - https://docs.zama.org/tfhe-rs/get-started/getting-started  
  - relevance: TFHE-based ecosystem and programmable bootstrapping framing
- AI on Encrypted Data via FHE  
  - type: official documentation  
  - https://research.ibm.com/projects/ai-on-encrypted-data-via-fhe  
  - relevance: IBM commercial FHE AI path via HElayers
- Powerformer: Efficient and High-Accuracy Privacy-Preserving Language Model with Homomorphic Encryption  
  - type: preprint / paper  
  - https://eprint.iacr.org/2024/1429  
  - relevance: HE-friendly transformer design and efficiency claims
- Private LoRA Fine-tuning of Open-Source LLMs with Homomorphic Encryption  
  - type: preprint / paper  
  - https://arxiv.org/abs/2505.07329  
  - relevance: encrypted fine-tuning feasibility for smaller LLMs
- AEGIS: Scaling Long-Sequence Homomorphic Encrypted Transformer Inference via Hybrid Parallelism on Multi-GPU Systems  
  - type: preprint / paper  
  - https://arxiv.org/abs/2604.03425  
  - relevance: scaling limits and multi-GPU optimization for encrypted transformer inference
- What is Nitro Enclaves?  
  - type: official documentation  
  - https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html  
  - relevance: TEE comparison point for secure execution
- Advancing Security for Large Language Models with NVIDIA GPUs and Edgeless Systems  
  - type: official documentation  
  - https://developer.nvidia.com/blog/advancing-security-for-large-language-models-with-nvidia-gpus-and-edgeless-systems/  
  - relevance: confidential AI path using H100, sandboxing, and encrypted prompts
- Seed video  
  - type: seed video  
  - https://www.youtube.com/watch?v=j7QmCiowz7k  
  - relevance: source of hypotheses, claims, and strategic framing

# Appendix A: Seed Video Claim Verification Table
| Claim from seed video | Status | Assessment | Evidence |
| --- | --- | --- | --- |
| 천정희 교수는 2017년에 CKKS를 만들었다 | Partially Verified | CKKS는 2017 논문과 표준 문헌에서 확인되지만, 발명자 기여의 세부 표현은 별도 저자 정보 확인이 더 필요하다 | HE Standard v1.1, CKKS literature context |
| 동형암호는 1978년에 개념이 제안되었고 2009년 Gentry가 FHE를 해결했다 | Verified | 업계 표준적 역사 서술과 부합 | HE Standard v1.1 |
| 동형암호는 암호문 상태에서 덧셈과 곱셈을 수행할 수 있다 | Verified | HE 정의 그 자체 | HE Standard v1.1, TFHE-rs docs |
| 23만 건 문서 검색을 수십 ms 수준으로 처리했다 | Unverified | 영상 외 독립 1차 공개 자료를 아직 확보하지 못함 | seed transcript only |
| 국방부 시범사업으로 암호화 상태 객체인식을 적용했다 | Unverified | 외부 공식 보도 또는 보고서 미확인 | seed transcript only |
| 암호화된 상태에서 훈련까지 수행했고 수시간 내 마쳤다 | Partially Verified | HE 기반 fine-tuning feasibility는 2025 논문으로 확인되지만 영상의 특정 실험과 시간 수치는 독립 검증 부족 | Private LoRA paper, seed transcript |
| encrypted RAG로 100만 건 중 필요한 데이터만 최소 노출로 전달할 수 있다 | Partially Verified | encrypted retrieval / RAG use case 자체는 표준화 워크숍 문서에 있으나, 영상의 구체 구조와 효과 수치는 독립 검증 필요 | Benchmarking.pdf, seed transcript |
| Google Cloud와 기술 검증 후 마켓플레이스 등록 예정 | Unverified | 독립 공지 미확인 | seed transcript only |
| 2024년 10월 처음으로 암호화된 LLM을 구현했다 | Unverified | “처음”이라는 표현은 강한 우선권 주장이라 별도 공개 논문/공지가 필요 | seed transcript only |
| 8대의 RTX 4090으로 첫 토큰 150초가 나왔다 | Unverified | 독립 공개 자료 미확인 | seed transcript only |
| NVIDIA가 2025년 12월 134초 수준 논문을 발표했다 | Partially Verified | NVIDIA confidential AI 자료는 확인했지만 영상의 정확한 수치와 논문 대응은 추가 확인 필요 | NVIDIA official blog, seed transcript |
| 최근에는 Llama 3 8B 기준 16초 수준까지 단축했다 | Unverified | 독립 벤치마크/논문/공식 공개 미확인 | seed transcript only |

# Appendix B: Benchmark Comparison Table
| Work | Scope | Model class | Main idea | Main limitation |
| --- | --- | --- | --- | --- |
| Powerformer | HE language model inference | BERT-base style | softmax/LN replacement, HE-friendly nonlinear approximation | not a full frontier generative LLM |
| Private LoRA | private fine-tuning | Llama-3.2-1B | HE-protected LoRA fine-tuning | still small-model and specialized |
| AEGIS | long-sequence encrypted transformer inference | encrypted transformer | multi-GPU hybrid parallelism | still research-stage |
| HEaaN bootstrapping demo | primitive acceleration | CKKS ciphertext refresh | very fast bootstrapping on GPU | not equal to end-to-end LLM latency |

# Appendix C: Glossary
- FHE: Fully Homomorphic Encryption, arbitrary computation on ciphertexts
- CKKS: approximate-number HE scheme suited to real-valued ML workloads
- BFV/BGV: exact arithmetic HE families for modular integer settings
- TFHE: gate / programmable bootstrapping oriented HE family
- Bootstrapping: ciphertext refresh to recover noise budget
- TEE: Trusted Execution Environment, secure enclave / confidential compute model
- MPC: secure multi-party computation using distributed trust
- Encrypted RAG: retrieval or similarity steps performed on protected representations

# Appendix D: Threat Model Matrix
| Threat | Pure FHE helps? | TEE helps? | Additional controls still needed |
| --- | --- | --- | --- |
| cloud operator reads prompt | strong | medium to strong | attestation, logging policy |
| app provider code leaks plaintext | partial | partial if sandboxed | sandbox, code review, outbound filtering |
| storage breach | strong | strong | key management |
| traffic metadata analysis | weak | weak | network-level protections |
| access-pattern leakage | weak to partial | weak | PIR/ORAM-style add-ons |
| model extraction | weak | weak | model serving policy, rate limits |
| insider misuse | partial | partial | IAM, audit, process controls |
