# GPT Deep Research Raw Capture

- Capture date: 2026-04-10
- Capture method: authenticated ChatGPT Deep Research session via Playwright iframe text extraction
- Session URL: https://chatgpt.com/c/69d8893c-0e44-83a4-9b32-d68f7bb6471b
- Note: This file preserves the raw completion text with ChatGPT's internal citation number markers such as `2`, `3`, `19`. Those markers are not resolved URLs in this export. The consolidated workspace report in `reports/2026-04-10_encrypted-llm-ai-data-protection_deepresearch.md` is the citation-normalized working document.

# Raw Output

동형암호 기반 Encrypted LLM과 AI 데이터 보호 심층 리서치

Executive Summary

본 보고서는 동형암호(HE, Homomorphic Encryption) 를 기반으로 한 Encrypted LLM(암호문 상태에서의 LLM 추론) 과, 더 넓은 맥락의 AI 데이터 보호(특히 RAG·임베딩·검색·학습 파이프라인 보호) 를 2026-04-10 기준 최신 1차 출처 중심으로 재검증·정리한 심층 리서치다. 시드 영상은 가설 생성용으로만 사용하고, 핵심 주장·수치·현실성은 외부 1차 출처(논문/표준/공식 문서)로 재검증했다. 
1

표기 규칙(요구사항 반영)

[Fact]: 인용된 1차 출처로 직접 뒷받침되는 서술
[Inference]: 인용 출처의 사실을 조합해 도출한 분석/귀결(조건부)
[Speculation]: 2~3년 전망·가정 기반 시나리오(불확실성 명시)

핵심 결론은 다음과 같다.

[Fact] FHE(완전 동형암호)는 “데이터를 복호화하지 않고 연산”하게 해 Data-in-use 보안을 제공하지만, 연산 모델이 제한적(덧셈·곱셈·회전 중심)이며 비선형(Softmax 등)은 다항 근사 등으로 우회해야 한다. 이는 정확도·지연·메모리 병목을 유발한다. 
2
[Fact] 최신 연구는 GPU 다중화·컴파일러/런타임 최적화로 전진하고 있으며, 예컨대 Cerium은 CKKS 기반으로 부트스트래핑 7.5ms(8×B200), BERT-Base 8.8s, Llama3-8B 첫 토큰 134s(128-token prompt) 를 보고한다. 
2
[Inference] “LLM 전체를 완전 암호문 상태로 실시간 서비스(대화형 스트리밍)하는 Encrypted LLM”은 현 시점(2026)엔 제한적 파일럿/데모 영역에 머물 가능성이 높다. 이유는 첫 토큰 지연(TTFT)·토큰당 지연·초거대 메모리 풋프린트·부트스트래핑 빈도·근사오차 관리가 동시에 충족되기 어렵기 때문이다. 
2
[Fact] 반면 “검색/조회” 계열(예: PIR, (근사)최근접 탐색 기반 검색)은 암호문 질의 보호를 목표로 하는 프로덕션 배치가 이미 존재한다. 대표적으로 애플은 BFV 기반 HE를 PIR/PNNS와 결합해 Photos ‘Enhanced Visual Search’ 등 서버 조회를 프라이버시 친화적으로 운영한다고 공개했다. 
3
[Fact] 다만 접근패턴(access pattern)·메타데이터(샤드/클러스터 선택)·네트워크 식별자(IP) 는 HE만으로 자동 제거되지 않으며, 애플 사례는 이를 차등프라이버시(DP) + OHTTP 릴레이(익명화 네트워크) 로 보완한다(ε=0.8, δ=1e-6 언급). 
3
[Fact] TEE는 “거의 네이티브 성능” 장점이 있으나, SGX 개발자 가이드가 명시하듯 사이드채널에 대한 명시적 보호를 제공하지 않는다(개발자 책임)라는 구조적 리스크가 있다. 
4
[Fact] MPC는 강한 보안 모델(분산 신뢰) 가능성이 있으나, 대규모 모델에선 통신량/라운드가 병목이 되기 쉬워 HE+MPC 하이브리드가 연구되며, 최근 연구는 네트워크 비용이 지배적임을 지적한다(예: 128-token BERT-Base가 LAN에서도 91s 필요하다는 비교 서술). 
2

요약하면, 2026년 기준 “엔드투엔드 Encrypted LLM”은 Go/No-Go 판단이 필요한 고비용 영역인 반면, “Encrypted RAG(특히 검색/조회와 임베딩 보호) + (필요 시) TEE/온디바이스 LLM” 같은 하이브리드 아키텍처는 현실적 도입 경로로 보인다. 
3

Background
왜 ‘AI 데이터 보호’가 새로 어려워졌는가

[Fact] 전통적 암호화(전송 중 TLS, 저장 중 암호화)는 데이터의 in transit / at rest 를 보호하지만, 클라우드 LLM/RAG가 수행되는 “in use” 시점(메모리·연산) 에서는 복호화가 필요해 노출면이 생긴다. 이 “Data-in-use” 문제를 해결하려는 대표 축이 FHE(암호문 연산) 와 TEE(신뢰 실행 환경), 그리고 MPC다. 
5

동형암호의 역사적 맥락과 현대 FHE 계열

[Fact] “프라이버시 호모모피즘(privacy homomorphism)” 맥락에서의 문제제기는 1978년 Rivest·Adleman·Dertouzos의 고전적 문제제기로 거슬러 올라가며, 이후 2009년 Gentry가 “이상격자(ideal lattices)” 기반의 최초 FHE 구성을 제안했다. 
6

[Fact] 현대 실무 FHE는 크게 두 계열을 많이 쓴다.

(R)NS 기반 BGV/BFV/CKKS 계열: 다항 링에서 SIMD(배칭)·회전·키스위칭·(일부)부트스트래핑을 사용해 벡터/행렬 연산을 구현한다. CKKS는 “근사 실수 연산”을 제공한다. 
7
TFHE/CGGI 계열: 부울/정수 연산과 “프로그램 가능 부트스트래핑(PBS)”로 비선형을 LUT처럼 평가하는 데 강하다(다만 대규모 선형대수는 또 다른 비용 구조). 
8
표준화와 신뢰 기반의 성숙도

[Fact] 국제 표준화는 “부분 동형(예: Paillier/Exponential ElGamal)”을 다루는 ISO/IEC 18033-6:2019가 이미 발행되어 있으며, FHE에 대해서는 ISO/IEC 28033(다부) 초안(Draft/ DIS)들이 2025~2026년 시점에도 ‘Under development’ 로 관측된다. 
9

[Fact] NIST CSRC는 ISO/IEC JTC1/SC27 하에서의 FHE 표준화 진행을 “Efforts on Standardizing Fully Homomorphic Encryption at ISO/IEC” 등 공개 행사 문맥에서 다뤘다. 
10

State of the Art
암호문 연산 성능: 부트스트래핑이 ‘긴 회로’의 가격표

[Fact] 부트스트래핑은 누적 노이즈/레벨 제한을 리셋해 “무한 연산”을 가능하게 하지만, 전통적으로 매우 비쌌다. 예컨대 TFHE 맥락에선 2016년 “<0.1초 부트스트래핑” 같은 전환점이 보고됐다. 
8

[Fact] CKKS 부트스트래핑의 GPU 최적화는 2021년 연구에서 “amortized bootstrapping time 0.423μs per bit(257× speedup vs single-thread CPU)” 같은 수치가 공개됐다(논문/저널 버전). 
11

[Fact] 더 최신의 대규모 프레임워크 연구(Cerium)는 “실제 부트스트래핑 10ms 장벽 돌파”를 주장하며, 표에 따르면 B200에서 부트스트래핑 7.5ms(8 GPU) 를 보고한다. 
2

[Fact] 산업 오픈소스/문서 측면에서 Zama는 TFHE-rs에 대해 H100 기준 GPU 벤치(멀티스레드 PBS 등 조건 포함)를 공개하고, 별도 글에서 “GPU에서 마이크로초 수준 부트스트랩”을 조건(보안수준, 메시지 비트폭, 인스턴스)과 함께 서술한다. 
12

자동화(컴파일러/IR)와 하드웨어 가속 생태계

[Fact] FHE는 연산 모델이 제한적이며(덧셈·곱셈·회전), 텐서 연산은 패킹·회전·누산으로 “회로”를 구성해야 한다. 이 때문에 최적화가 강하게 필요하며 Cerium은 “컴파일러+런타임”으로 이를 자동화하려는 흐름을 보여준다. 
2

[Fact] 구글은 MLIR 기반의 HE 컴파일러 체인으로 HEIR 프로젝트를 공개적으로 운영한다. 
13

[Fact] 오픈소스 라이브러리 측면에서 OpenFHE는 BGV/BFV/CKKS/TFHE류를 폭넓게 지원하고, threshold FHE·proxy re-encryption 등 멀티파티 확장도 포함한다. 
14

Technical Deep Dive
Threat model

아래는 “Encrypted LLM/Encrypted RAG”를 논할 때 반드시 선명히 해야 하는 위협 모델이다.

시스템 구성(추상화)
클라이언트(사용자/기관): 프롬프트·문서·임베딩·PII/PHI의 “실소유자”.
AI 서비스 제공자(클라우드 추론/검색 인프라): 모델/벡터DB/캐시/로그/관측성을 운영.
키 관리(KMS/HSM/오프라인 관리): 비밀키·평가키·정책·로테이션을 담당.
(선택) 제3자 프라이버시 인프라: 익명화 릴레이(OHTTP 등), DP 메커니즘, 오딧/컴플라이언스 등.
공격자 가정(현실적)
A1: 클라우드 운영자/하이퍼바이저/OS 권한자(insider 혹은 침해된 운영계정)
A2: 동일 호스트/동일 클러스터 상 공존 테넌트(co-tenant)
A3: 네트워크 관찰자(메타데이터/트래픽 분석 포함)
A4: 공급망/하드웨어 결함 악용자(TEE 사이드채널/결함주입 등)
A5: 로그·모니터링·데이터 파이프라인(ETL/LLMOps) 침해자
자산(보호 목표)
X1: 사용자 프롬프트/질의
X2: RAG 컨텍스트(검색된 원문/요약/스니펫)
X3: 임베딩(문서 임베딩/쿼리 임베딩) 및 인덱스 구조
X4: 모델 가중치/시스템 프롬프트/정책(모델 IP)
X5: 키(material)와 파생키, 평가키(relin/galois/eval keys)
X6: 메타데이터(누가, 언제, 어떤 샤드/클러스터, top-k 결과 id 등)
보안 목표(기본)
C(기밀성): X1~X3의 평문 노출 방지
I(무결성): 결과 조작/응답 위·변조 방지(일부 기술은 I 목표가 약함)
M(메타데이터 최소화): 접근패턴/샤드 선택/쿼리 빈도 등 누출 최소화
A(가용성): 대규모 지연/리소스 폭주/DoS 완화

[Fact] HE는 “서버가 복호키를 갖지 않고도 연산”하게 하여 (X1~X3의) 기밀성에 매우 강하나, 크기·타이밍·접근패턴 등 메타데이터 누출면은 별도 설계가 필요하다(예: 애플이 DP+OHTTP로 샤드/연결성 누출을 보완). 
3

[Fact] TEE는 “데이터 in-use” 보호를 목표로 하지만, SGX 개발자 가이드가 명시하듯 사이드채널에 대한 명시적 보호는 제공되지 않으며(개발자 책임) OS/BIOS 권한 공격자 모델에서 다양한 공격이 연구되어 왔다. 
4

Threat Model Matrix
공격/누출면	Conventional encryption (전송/저장)	HE/FHE (암호문 연산)	TEE (Enclave/CVM)	MPC
클라우드 운영자/OS 권한자가 “메모리 평문”을 보는 위협	보호 불가(대체로 평문 in-use 발생)	강함(서버에 평문 없음) 
15
	중간(격리/메모리암호화)이나 사이드채널·구현 리스크 
4
	분산 신뢰로 강하게 설계 가능(대신 통신/라운드 비용) 
16

네트워크 트래픽 분석(빈도/시간/목적지)	부분적(암호화되어도 메타데이터 잔존)	잔존(HE만으로는 메타데이터 제거 아님) 
17
	잔존	잔존
접근패턴 누출(어떤 문서/샤드를 조회했나)	일반적으로 누출	핵심 리스크(PIR/ORAM/DP 필요) 
17
	TEE 내부는 숨길 수 있으나 외부 I/O 패턴은 누출 가능	프로토콜 설계에 따라 완화 가능하나 비용 상승
사이드채널(캐시/전력/결함주입)	해당 없음(암호와 별개)	HE 자체는 키가 서버에 없으므로 상대적으로 완화되나, 구현/시간 기반 관측은 남을 수 있음	높은 관심사(문서가 ‘보호 없음’ 명시) 
4
	구현·네트워크 측면의 사이드채널 가능
키 관리 실패(유출/오남용)	치명적	치명적(복호키 유출 시 의미 상실)	키가 TEE 밖에 있으면 동일	프로토콜 키/시드 관리가 복잡
암호문 상태에서 실제 수행 가능한 연산 범위
(R)NS 기반(BFV/BGV/CKKS)에서 “현실적으로 가능한 것”

[Fact] CKKS는 (i) 덧셈, (ii) 곱셈, (iii) 순환 회전(cyclic rotation)이라는 제한된 프리미티브를 제공하며, 고수준 텐서 연산은 이들의 조합(회로)로 구성된다. 
2

[Fact] 제한의 직접적 함의는 두 가지다.

비선형 함수(division, ReLU, max, softmax, SiLU 등)를 “그대로” 표현할 수 없어 다항 근사가 필요하다. 
2
텐서 인덱싱이 직접 지원되지 않아, 패킹/회전/누산으로 구현해야 하며 회로는 레이어 차원·시퀀스 길이·헤드 수 등에 강하게 결합된다. 
2

[Fact] BFV는 “정수 모듈러 정확 연산”에 강점이 있고, CKKS는 “근사 실수/복소 연산”을 제공하며 근사 오차가 본질적으로 존재한다(정확도 요구 수준에 따라 스케일·다항 차수·부트스트래핑 삽입이 달라짐). 
7

TFHE/CGGI 계열에서 “현실적으로 가능한 것”

[Fact] TFHE-rs는 PBS(Programmable Bootstrapping)를 포함해 불리언/단정밀 정수 연산을 제공하며, GPU 벤치마크 문서는 PBS 측정 조건(예: H100, multithreaded PBS 등)을 함께 공개한다. 
12

[Inference] TFHE 계열은 “비선형/비교”를 LUT 평가로 처리하는 장점이 있으나, LLM의 주 계산량인 대규모 matmul/attention을 전부 TFHE 스타일로 처리하는 것은 다른 형태의 병목(거대한 부울 회로 규모)로 전환될 수 있어, 실제 시스템은 대개 역할 분담(예: 비교·정렬은 TFHE, 선형대수는 CKKS) 같은 하이브리드를 지향한다. 
18

파이프라인 단계별 현실성 평가

아래 평가는 “HE 단독”이 목표인지, “HE + (온디바이스/TEE/MPC)” 하이브리드가 목표인지에 따라 달라진다.

Inference (LLM 추론)
[Fact] Cerium은 Llama3-8B 디코더 블록의 ‘첫 토큰 생성’ 을 “128-token prompt” 조건에서 암호문 상태로 수행하며, 8×B200에서 134초를 보고한다. 
2
[Inference] 134초 TTFT는 “대화형 서비스(수초 내 응답, 스트리밍)” 기준으로는 매우 크며, 토큰을 반복 생성하는 오토리그레시브 구조상 “토큰당 지연”까지 고려하면 실시간 LLM 서비스로의 직접 전환(프로덕션) 은 어렵다. 다만 규제가 강하고 응답 지연 허용치가 큰 워크플로(예: 배치 분석/오프라인 리포팅)나 “서버가 절대 평문을 보지 못해야 하는” 초고규제 상황에선 제한적 파일럿/데모 여지가 남는다. 
2
Embedding (임베딩 생성)
[Fact] 임베딩은 “원문을 안전하게 대체하는 익명 표현”이 아니다. 텍스트 임베딩에서 원문을 재구성(embedding inversion)하는 공격이 활발히 연구되었고, “Text Embeddings Reveal (Almost) As Much As Text”는 임베딩이 원문 정보를 상당히 보존함을 실험적으로 보인다. 
19
[Inference] 따라서 “임베딩만 저장하면 안전”은 성립하기 어렵고, 임베딩 자체도 민감 데이터로 취급하는 것이 현실적이다. 임베딩 생성은 (a) 온디바이스 수행, (b) TEE내 수행, (c) HE로 수행(연산량 큰 경우 비현실적) 중 선택이 되며, 2026년 기준 일반적 엔터프라이즈에선 (a)/(b)가 우세하다. 
3
Reranking (재정렬)
[Fact] 애플 사례는 서버 측 HE 조회 후 온디바이스의 ‘lightweight reranking model’ 로 최종 결정을 하며, 이는 “재정렬은 클라이언트에서”라는 매우 실용적인 분할을 보여준다. 
3
[Inference] Cross-encoder reranker(LLM/Transformer 기반)는 비선형·attention이 많아 HE 단독으로는 비용이 커질 가능성이 높고, 2026년 기준 HE로 reranking까지 포함한 e2e RAG 는 데모 가능성이 있더라도 “프로덕션급”으로 일반화하기 어렵다. 
2
RAG (Retrieval-Augmented Generation)
[Fact] RAG의 핵심 리스크는 “원문 컨텍스트”뿐 아니라 “검색 질의/임베딩/접근패턴”이다. 애플은 서버 조회를 HE로 처리하면서도, 샤드 선택·IP 링크 가능성 등 메타데이터가 민감해질 수 있음을 인정하고 DP + OHTTP 릴레이 를 결합한다. 
3
[Inference] 따라서 Encrypted RAG의 현실적 목표는 보통 “(1) 검색/조회/인덱싱 단계의 프라이버시 강화 + (2) 생성 단계는 온디바이스 또는 TEE로 처리(혹은 최소한 민감 컨텍스트만 클라이언트에서 조합)”로 수렴한다.
Vector search (벡터 검색 / ANN)
[Fact] Wally는 “private search”에서 전체 DB 스캔의 비용을 피하기 위해 클러스터링·익명화·가짜 질의·SHE를 결합하고, 다수 클라이언트가 존재할 때 오버헤드가 상쇄되는 설계를 제시한다(3,000 QPS 서술 포함). 
17
[Fact] 애플은 PNNS를 “서버가 클라이언트 임베딩을 알지 못한 채” 근사 검색을 수행하는 흐름으로 설명하고, 샤딩 및 온디바이스 사전 코드북을 사용한다. 
3
[Inference] 벡터 검색은 HE로 “거리 계산(dotp/cosine)” 자체는 가능하나, top-k 선택·인덱스 트리 탐색·ORAM/PIR 결합에서 병목이 생긴다. 접근패턴을 숨기려면 ORAM 같은 기법이 필요하며, 이는 추가 오버헤드를 낳는다. 
20
Fine-tuning / Training
[Fact] HE로 “모델 학습” 자체가 불가능한 것은 아니며, 예컨대 GPU 부트스트래핑 최적화 연구는 로지스틱 회귀 학습에서 CPU 대비 가속을 보고한다. 
11
[Inference] 그러나 LLM 파운데이션 모델 수준의 대규모 파인튜닝/학습을 HE로 수행하는 것은 연산·메모리·통신·보정(근사오차) 관점에서 2026년 기준 매우 비현실적이다. 현실적 경로는 (a) 연합학습+안전한 집계, (b) 특정 통계/회귀/리스크스코어 등 제한된 모델 학습, (c) 파인튜닝은 TEE/온프레미스에서 수행하고 “inference/query privacy”를 HE로 맡기는 분리다. 
21
병목 분석
Latency / First-token latency / Throughput
[Fact] Cerium의 Llama3-8B 결과는 “첫 토큰 생성”에서 134초를 보고하며, 이는 TTFT 병목을 명확히 보여준다. 
2
[Fact] Cerium은 동일 문맥에서 BERT-Base를 8.8초(128-token input)로 보고하며, “LLM이라도 구조/목표가 다르면 지연 스케일이 크게 달라짐”을 보여준다. 
2
[Inference] 오토리그레시브 생성형 LLM은 “토큰이 스트리밍”되어야 사용자 경험이 성립하는데, HE는 회로가 큰 경우 토큰마다 큰 비용이 반복되기 쉬워, “고TTFT + 저throughput”의 이중 병목을 낳는다.
Memory overhead / Context length / Model size scalability
[Fact] Cerium은 FHE가 메모리 요구량을 “극단적으로 부풀린다”는 점을 정량적으로 보여주며, BERT-Base가 1.5TB, Llama3-8B가 112TB 메모리 풋프린트를 예시로 든다. 
2
[Fact] 또한 평가키(eval keys) 총량이 ML 워크로드에서 “10~100GB” 수준일 수 있음을 설명한다. 
2
[Inference] LLM의 컨텍스트 길이는 attention 및 KV 캐시와 결합해 비용을 키우는데, HE 환경에선 “패킹/회로 구조가 시퀀스 길이에 결합”되어 컨텍스트 길이 유연성이 떨어지고, 길이 증가가 성능을 비선형적으로 악화시킬 가능성이 높다. 
2
Bootstrapping / Approximation error
[Fact] CKKS는 근사 실수 연산을 제공하므로, 정확도 확보를 위해 비선형을 다항으로 근사해야 하며, 다항 차수·정밀도·부트스트랩 위치가 정확도/지연을 좌우한다. 
2
[Inference] “정확도 저하 없는 Encrypted LLM”은 곧 “근사오차·정밀도 관리와 부트스트래핑 비용을 동시에 감당”해야 함을 의미하며, 이 trade-off가 2026년 기준 상용화를 가르는 핵심이다.
HE vs TEE vs MPC vs Conventional encryption 비교
비교 요약(정성)

HE/FHE

강점: 서버가 복호키를 가지지 않아 “서버 침해/내부자”에 매우 강함(in-use 보호). 
15
약점: 지연·메모리·근사/부트스트래핑·접근패턴 설계가 난제. 
2

TEE(Confidential computing)

강점: 성능이 훨씬 유리(대개 근접 네이티브), 기존 코드 이식성이 상대적으로 좋음. 
5
약점: 사이드채널/결함주입/마이크로아키텍처 리스크. SGX 문서가 “명시적 보호 없음”을 선언. 
4

MPC

강점: 신뢰를 분산(비협력 가정)해 강한 보안 모델 가능
약점: 대규모 모델에서 통신량/라운드가 병목. HE+MPC 하이브리드에서도 네트워크 비용이 지배적일 수 있음(연구 비교 서술). 
2

Conventional encryption

강점: 성능/도입 용이
약점: data-in-use 문제 미해결
Benchmark Comparison Table (조건 포함)
항목	수치(보고치)	조건/해석	용도 구분
초기 FHE 구현의 극단적 지연	“단일 논리게이트에 약 30분” 서술	역사적 맥락(초기 구현)	기반 맥락 
22

CKKS GPU 부트스트래핑(학술)	amortized 0.423 μs per bit	“per bit”·“amortized” 지표(직접 비교 주의)	가속 추세 
11

Cerium 부트스트래핑	7.5 ms	B200, 8 GPU, 표 내 보고	LLM급 회로의 핵심 부품 
2

Cerium BERT-Base	8.8 s	128-token input, 표 내 “FHE inference”	제한적 파일럿 후보 
2

Cerium Llama3-8B	134 s	128-token prompt, “first token” 생성	데모/연구 
2

Wally private search	3,000 QPS(서술)	다수 클라이언트·가짜질의·익명화 전제	대규모 검색(조건부) 
17

애플 PNNS/HE 운영	BFV + PIR/PNNS + DP/OHTTP	프로덕션 아키텍처(온디바이스+서버)	프로덕션 가능 영역 
3
Industry Landscape
주요 생태계 지도(벤더/빅테크/오픈소스)

아래는 2026-04-10 기준 “Encrypted AI” 관련 생태계의 대표 축이다(각 항목은 벤더 주장과 독립 검증 사실을 분리해 읽어야 한다).

오픈소스 FHE 라이브러리/툴체인

Microsoft SEAL: BFV/BGV/CKKS 제공(정수/근사 실수). 
7
OpenFHE: 주요 스킴과 멀티파티 확장(Threshold FHE, PRE 등) 지원. 
14
Google HEIR: MLIR 기반 HE 컴파일러/IR. 
13

상용/산업용 PET 플랫폼(기업 데이터 협업·규제 산업 타깃)

Duality Technologies: HE/DP/MPC/TEE 등을 조합한 데이터 협업 플랫폼을 표방(플랫폼 문서/클라우드 배치 가이드 존재). 
21

FHE 중심 스타트업/오픈소스 스택(특히 TFHE 계열)

Zama: TFHE-rs/Concrete 계열을 오픈소스로 제공하며 GPU 벤치를 공개. 
12

빅테크의 프로덕션 배치 사례(‘검색/조회’ 중심)

Apple: BFV 기반 HE를 PIR/PNNS/DP/OHTTP와 결합해 Photos의 Enhanced Visual Search 등 “프라이빗 서버 룩업”을 설명하고 관련 라이브러리도 오픈소스로 공개. 
3
벤더 주장 vs 독립 검증: 해석 가이드
[Fact] “프로덕션 배치”를 뒷받침하는 가장 강한 신호는 (a) 공식 기술 블로그/연구 포스트에서 아키텍처·위협모델·프라이버시 보완책(DP/익명화)까지 공개, (b) 합리적 측정 조건과 trade-off(정확도·지연·비용)를 함께 공개하는 경우다(애플 사례가 이에 해당). 
3
[Inference] 반대로 “암호화 LLM의 초단기 TTFT(예: 수초 수준)” 같은 수치는, 동료심사 논문·재현 가능한 코드·측정 조건(TTFT 정의, context length, GPU 수, 보안 파라미터)이 없으면 “마케팅 수치”로 남을 위험이 높다. Cerium류 논문은 측정 조건(128-token prompt, first token)을 명시한다는 점에서 비교적 견고하다. 
2

Applications
금융(Finance)
[Fact] 금융은 기관 간 데이터 결합(부정거래 탐지, 신용·리스크 분석)에서 규제/기밀성 문제로 데이터 공유가 막히는 경우가 많고, HE 기반 “암호화 상태의 통계·쿼리”가 그 간극을 메우는 PET로 제안되어 왔다(Duality의 금융권 협업 배치 가이드 등). 
23
[Inference] 금융에서 Encrypted LLM의 우선 적용은 “LLM 추론 자체를 FHE로”보다, RAG의 검색/조회 층을 암호화해 내부 데이터(거래규정, 고객정책, 사고 리포트)의 노출면을 줄이고, 생성은 TEE/온프레미스로 제한하는 방향이 현실적이다. 
17
의료(Healthcare)
[Fact] 의료 데이터는 PHI/유전체/영상 등 고민감 정보가 많아 “데이터 이동 없이 분석” 요구가 강하며, HE는 “암호문 상태 연산”을 통해 제3자 연산 환경에서의 노출을 줄이는 도구로 연구되어 왔다. 
15
[Inference] 의료 현장에서는 “실시간 대화형 LLM(초저지연)”보다, (a) 프라이빗 검색/조회(용어·가이드라인 매칭), (b) 특정 스코어/통계 계산, (c) 프라이버시 민감 임베딩의 보호 같은 부분에서 HE의 비용-효익이 먼저 맞을 가능성이 높다. 
3
국방/공공(Defense/Public Sector)
[Fact] DARPA는 “암호화된 데이터 위의 컴퓨팅”을 목표로 하는 프로그램을 오래 전부터 추진해 왔고(PROCEED 등), 2011년 무렵 “약 2천만 달러” 규모 투자 보도가 있었다. 
24
[Inference] 국방/공공은 “서버 운영자(혹은 위탁사업자)도 평문을 보면 안 되는” 요구가 크고, 지연 허용치가 상대적으로 큰 배치/분석 업무가 존재하므로, Encrypted LLM이 가장 먼저 ‘실증’될 정책 수요가 있다. 다만 대화형 실시간 지휘통제에 FHE LLM을 바로 넣는 것은 TTFT/가용성/운영 복잡도로 인해 위험하다. 
2
Enterprise Knowledge Assistant (사내 지식비서)
[Fact] 임베딩은 재구성 공격에 취약해 “임베딩 저장만으로 안전”하지 않다. 즉 사내 문서 임베딩은 사실상 “민감 자산”이다. 
19
[Inference] 사내 지식비서의 실전 설계는 (1) 임베딩/벡터DB 접근패턴 보호(Encrypted retrieval), (2) 컨텍스트 최소화(최소 문장만), (3) 생성 단계의 신뢰 경계(온프레미스/TEE/로컬)라는 3층 방어가 필요하다. 애플의 “검색은 HE, 리랭킹은 온디바이스” 패턴은 기업용에서도 유효한 설계 힌트다. 
3
Biometric / Privacy-sensitive AI (생체·민감 AI)
[Fact] 생체(음성/얼굴/특징벡터)는 유출 시 회수가 불가능하므로 “암호문 상태 매칭”이 특히 설득력 있는 유스케이스다. 예컨대 HE 기반 1:N 생체 매칭을 다루는 연구(Blind-Match)가 공개되어 있다. 
25
[Inference] 생체는 보통 “유사도 계산 + top-k” 구조이므로, HE는 핵심 계산(내적/코사인)에는 적합할 수 있으나, 대규모 DB에서 접근패턴을 숨기는 설계(ORAM/PIR/클러스터링+DP)가 동반되지 않으면 메타데이터 누출이 남는다. 
20

Limitations
Side-channel
[Fact] Intel SGX 문서는 “사이드채널에 대한 명시적 보호를 제공하지 않는다”고 명시하며, 대표 공격으로 결함주입(Plundervolt) 등이 학술적으로 검증되었다. 
4
[Fact] AMD 계열에서도 SEV-SNP의 위협모델 범위와 취약점 공지가 존재하며, 2026년에도 아키텍처 공격(StackWarp)이 “무결성 붕괴”를 주장하는 등 리스크가 지속적으로 보고된다. 
26
[Inference] 따라서 “TEE만으로 충분”은 위험하며, 고위협 환경에서는 TEE를 쓰더라도 (a) side-channel 완화 코딩, (b) 배포/패치/마이크로코드 업데이트, (c) 원격 검증(attestation) 파이프라인, (d) 로그 최소화를 포함한 운영 설계가 필수다.
Metadata leakage / Access-pattern leakage
[Fact] HE는 “평문을 숨긴 채 연산”하지만, 서버는 여전히 (i) 요청 빈도/시간, (ii) 요청 크기, (iii) 어떤 샤드/클러스터가 접근되었는지 같은 메타데이터를 관찰할 수 있다. 애플은 이를 DP+OHTTP 릴레이로 보완한다. 
3
[Fact] ORAM은 “접근패턴을 숨기는” 대표 기법이며, 실무적으로는 오버헤드/종료채널 등 구현-정의 간 간극이 논의된다. 
27
[Inference] Encrypted RAG에서 “top-k 문서 id” 자체는 민감 정보가 될 수 있다. (예: 어떤 법률/질병/프로젝트 문서를 조회했는가) 따라서 secure retrieval은 ‘암호 연산’만이 아니라 ‘관측 가능성(Observability) 설계’ 문제다.
Key management
[Fact] HE는 “서버가 비밀키를 가지지 않는다”는 점이 강점이지만, 역으로 “비밀키를 가진 곳”이 단일 실패점이 된다. 평가키(evaluation keys)도 대용량일 수 있다(10–100GB 서술). 
2
[Inference] 실전 권고는 (a) KMS/HSM 분리, (b) 키 로테이션/폐기 정책, (c) 필요 시 threshold FHE(키 분산) 도입(OpenFHE가 threshold 확장을 지원한다고 명시). 
28
Logging leakage / Integration risk
[Fact] 개인/기업용 LLM 시스템은 LLMOps 관측성(프롬프트·컨텍스트·리트리벌 결과·에러 로그)을 남기는 경향이 강하며, 이것이 “암호화로 보호하려던 데이터”를 역류시킬 수 있다(기술 자체보다 통합 리스크).
[Inference] HE/TEE/MPC는 “암호/격리 계층”일 뿐, 파이프라인 통합에서 (1) 캐시, (2) 디버그 덤프, (3) A/B 테스트 샘플링, (4) 프롬프트 수집, (5) 티켓/슬랙 붙여넣기 등으로 데이터가 새는 경우가 잦다. 따라서 “통합 위험”은 별도 통제(데이터 최소화·민감정보 탐지·로깅 정책·접근통제)로 다뤄야 한다.

Future Outlook
2~3년 전망(2026→2028/2029)
[Fact] 성능·자동화는 “GPU + 컴파일러/런타임”을 중심으로 빠르게 전진 중이며, 2025 말~2026 초 Cerium은 TTFT/부트스트래핑/다중 GPU 확장과 “LLM급 규모”를 정면으로 다룬다. 
2
[Inference] 2028~2029년까지 가장 빠르게 상용화가 확산될 영역은 “Encrypted retrieval(PIR/PNNS/벡터검색 변형) + DP/익명화” 같은 검색/조회 계층일 가능성이 높다. 이미 빅테크가 프로덕션 사례를 공개했고, 이 영역은 LLM 전체 FHE보다 회로가 작고 요구 정확도도 관리 가능하기 때문이다. 
3
[Inference] Encrypted LLM(전체 생성형 추론)은 23년 내에도 ‘특정 조건에서만’ 제한적 도입 가능성이 높다. 조건은 (a) 짧은 컨텍스트, (b) 배치/오프라인, (c) 좁은 도메인 모델, (d) 고비용을 감당할 강한 규제·위협 환경이다. Cerium이 보여준 메모리 풋프린트(수 TB수십 TB)는 여전히 대중적 상용화를 막는 큰 벽이다. 
2
[Speculation] “표준화(ISO/IEC 28033 계열)의 Final 발행”이 진행되면(일정 불확실), 공공 조달/규제 수용성이 올라가며, 특히 “성능이 검증된 조회/검색 계층”의 도입이 빨라질 수 있다. 다만 2026-04-10 기준으로는 DIS 단계들이 언급되므로, 단기간에 ‘표준=즉시 상용 확산’으로 연결된다고 단정하기 어렵다. 
29
Go / No-Go 기준(실무 체크리스트)

아래는 “Encrypted AI(특히 RAG/LLM) 도입”의 실무적 의사결정 기준이다.

Go(프로덕션) 가능 조건 — 주로 Encrypted Retrieval 중심

[Fact] 위협모델이 “서버/운영자도 데이터 평문을 볼 수 없음”으로 명확하고, 메타데이터 누출까지 설계로 다룬다(DP/익명화/클러스터링/가짜질의 등). 
3
[Fact] SLA가 “초저지연 대화형”이 아니라, 수백 ms수 초(조회) 또는 수 초수십 초(제한적 분석)도 허용된다. 
17

No-Go(또는 TEE/온프레미스로 전환) 조건 — Encrypted LLM 전체 추론

[Fact] TTFT가 사용자경험 요구(예: <2초)를 충족해야 한다. 현재 공개 연구의 134초 TTFT(LLM급)는 이에 미달. 
2
[Fact] 모델/컨텍스트 확장 시 메모리 풋프린트가 운영가능 범위를 초과한다(예: 수 TB~수십 TB). 
2
[Inference] 근사오차로 인한 품질 저하를 허용할 수 없고, 재학습(LoRA 등)이 금지되어 회로 최적화 여지가 작다. 
2

Actionable Insights
하이브리드 “Encrypted RAG” 권고 아키텍처

권고안 A: 검색/조회(Encrypted), 생성(온디바이스/온프레미스)

[Fact] 애플이 보여준 패턴(온디바이스 임베딩/리랭킹 + 서버 HE 조회 + DP/OHTTP)을 엔터프라이즈 RAG로 일반화한다. 
3
[Inference] 서버는 “문서 원문”을 직접 반환하지 말고, (a) 암호화 점수/메타데이터 최소치, (b) PIR로 필요한 조각만 가져오는 방식으로 접근패턴 누출을 줄인다.

권고안 B: 생성(TEE), 검색(Encrypted or 최소화), 로깅 최소화

[Fact] confidential computing은 data-in-use 보호를 목표로 한다. 
5
[Inference] 다만 TEE의 사이드채널 리스크를 인정하고, “가장 민감한 데이터는 여전히 클라이언트에서 암호화/레드랙션” 후 주입하는 식의 다층 방어가 필요하다. 
4
PoC 설계 시 반드시 포함할 측정 항목
[Fact] 측정 조건을 명시해야 한다(토큰 길이, TTFT 정의, GPU 수, 보안 파라미터, DP ε/δ 등). Cerium은 128-token 및 first token 조건을 명시한다. 
2
[Inference] 특히 비용 산정은 “암호 연산 비용”뿐 아니라 키/평가키 배포(10–100GB급 가능), 메모리 오케스트레이션, 모니터링/로그, 장애 처리까지 포함해야 한다. 
2
최소 리스크 운영 가이드(요약)
[Fact] 임베딩은 민감 정보일 수 있으므로(재구성 공격), 임베딩 보관·전송 정책은 PII/PHI 수준으로 다룬다. 
19
[Inference] “Encrypted”를 표방하는 시스템에서 가장 흔한 실패는 로그/캐시/분석 파이프라인에서의 평문 유출이므로, LLMOps 가시성 정책을 보안 요구와 정합시킨다.
References
Rivest, Adleman, Dertouzos. On Data Banks and Privacy Homomorphisms (1978). 
6
Gentry. Fully Homomorphic Encryption Using Ideal Lattices (2009) 및 박사학위논문. 
30
Cheon et al. Homomorphic Encryption for Arithmetic of Approximate Numbers (CKKS) (preprint/2016; ASIACRYPT 2017 맥락). 
31
ISO/IEC 18033-6:2019(부분 동형 메커니즘), ISO/IEC DIS 28033-1 및 ISO/IEC DIS 28033-3(초안). 
9
NIST CSRC STPPA: ISO/IEC FHE 표준화 소개(행사/발표 맥락). 
10
Chillotti et al. Faster Fully Homomorphic Encryption: Bootstrapping in Less Than 0.1 Seconds (2016). 
8
Jung et al. Over 100x Faster Bootstrapping in Fully Homomorphic Encryption through Memory-centric Optimization with GPUs (2021) – 공개 초록/본문 일부. 
11
Jayashankar et al. A Scalable Multi-GPU Framework for Encrypted Large-Model Inference (Cerium) (2025, arXiv). 
2
Apple Machine Learning Research. Combining Machine Learning and Homomorphic Encryption in the Apple Ecosystem (2024). 
3
Apple 연구: Scalable Private Search with Wally (2024). 
17
Morris et al. Text Embeddings Reveal (Almost) As Much As Text (EMNLP 2023). 
19
Li et al. Generative Embedding Inversion Attack to Recover the Whole Sentence (ACL Findings 2023). 
32
TEIA(ACL 2024) 코드/맥락(임베딩 역공학). 
33
Intel SGX Developer Guide(사이드채널 비보호 명시), Plundervolt(결함주입), AMD SEV-SNP 공지/최근 공격 보고, Confidential Computing 개요. 
4
ORAM/접근패턴 은닉(정의·실무 오버헤드 논의). 
20
HEIR(구글), OpenFHE, Duality 플랫폼 문서, Zama TFHE-rs 문서/벤치. 
13

Appendix A: Seed video claim verification table

아래 표는 시드 영상(동일 링크)을 기준으로 “핵심 주장”을 최소 10개 추출해 Verified / Partially Verified / Unverified / Misleading or Overstated 로 분류하고, 핵심 수치·주장은 외부 1차 출처로 재검증한 결과다. (시드 영상의 ‘발언 내용’ 자체는 영상 원문을 근거로 하며, 표의 “검증 근거”는 외부 출처다.) 
1

#	시드 영상 핵심 주장(요약)	판정	검증 근거(요약)	외부 1차 출처
1	1978년 MIT 교수진이 동형암호(프라이버시 호모모피즘) 개념을 제안	Verified	1978년 Rivest·Adleman·Dertouzos가 해당 문제를 제기	
6

2	2009년 Gentry가 완전 동형암호를 제안/해결	Verified	2009년 논문 및 박사논문에서 FHE 구성 제시	
30

3	CKKS(근사 실수 연산 동형암호)가 2017년(전후) 제안되어 ML/AI 연산에 유리	Verified	CKKS는 근사 산술을 위한 HE 스킴을 제안(리스케일링 포함)	
31

4	2021년부터 FHE 국제표준화가 진행 중이며 2026년쯤 마무리 기대	Partially Verified	ISO/IEC 28033-1, 28033-3 등이 2025~2026에도 DIS 단계로 관측(완료 시점은 불확실)	
29

5	DARPA가 약 23M 달러를 들여 동형암호 구현을 추진	Partially Verified	2011년 무렵 DARPA가 FHE 성능 개선을 목표로 약 20M 달러 투자 보도가 존재(23M는 확인 곤란)	
34

6	초기 FHE는 1비트/게이트 처리에 약 30분이 걸릴 정도로 느렸다	Verified(정성)	“약 30분에 단일 로직게이트”는 역사적 설명으로 문헌에 등장	
22

7	지난 10여 년간 성능이 “10억 배” 이상 개선되었다	Partially Verified	30분(≈1800s) 대비 μs~ms급(예: 0.423μs/bit, 7.5ms bootstrap 등)로 ‘규모상’ 10^9급 개선이 성립할 수 있으나, 비교 대상/지표가 일치하지 않으면 과장될 수 있음	
11

8	애플은 HE를 활용해 iPhone Photos의 랜드마크/시각 검색을 프라이빗하게 운영한다	Verified	애플이 BFV+PIR/PNNS+DP/OHTTP를 결합해 Enhanced Visual Search를 운영한다고 상세 설명	
3

9	“암호화 검색/조회”는 DP·익명화 없이는 접근패턴/메타데이터가 샐 수 있다	Verified	애플은 샤드 식별이 민감할 수 있음을 지적하고 DP/OHTTP를 결합; Wally도 접근패턴 누출을 주요 이슈로 제기	
3

10	BERT-Base의 암호문 추론이 약 8초 수준까지 가능하다는 연구가 있다	Verified	Cerium이 BERT-Base FHE inference를 8초대(표에선 8.8s)로 보고(128-token input 조건)	
2

11	Llama3-8B에 대해 “첫 토큰” 암호문 추론이 134초 수준으로 보고됐다	Verified	Cerium이 128-token prompt에서 first token 생성 134s(8×B200) 보고	
2

12	(예: 2GB/s 암호화 검색, 200MB/s 복호 처리 등) 특정 처리량 수치가 가능	Unverified	공개 1차 출처(논문/공식 벤치)로 동일 수치를 동일 조건에서 확인하기 어려움. 유사 주장은 시스템/파라미터/데이터셋에 크게 의존	(재현 가능한 1차 출처 확인 불충분)
