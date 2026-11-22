# 양자 알고리즘의 실용화 시점과 근거

2026-11-22 · 다음 리뷰의 독립 조사 메모 · quantum_timelines_audit

상용화 전망은 **지금 사용할 수 있는 도구·서비스, 실제 하드웨어에서 수행한 알고리즘, 고전 방법과 비교한 이점, 전체 비용을 감당하는 활용**으로 나누어 읽는다. 각각 필요한 증거가 다르다. 클라우드에서 VQE나 QAOA를 실행할 수 있다는 사실과, 기업의 실제 문제에서 더 나은 비용으로 답을 얻었다는 판단 사이에는 검증해야 할 과정이 남아 있다.

아래 시간 표현은 연구·개발 기획에 사용할 조건부 판단이다. 알고리즘별 보편적인 상용화 연도를 산정한 자료는 아니다. QFT·QPE·QSVT처럼 다른 계산의 구성 요소에 대해서는, 이를 사용하는 전체 응용의 자원과 판독 비용을 함께 평가한다.

## 알고리즘별 현재 수준과 조건부 전망

| 알고리즘 | 지금의 활용과 확인한 수준 | 실용화 전망을 적는 방식 | 남은 과제와 검증할 지표 |
|---|---|---|---|
| Shor | 작은 수의 교육 실행과 별개로, RSA-2048에 대한 상세 컴파일·자원 추정이 계속 발전한다. 2026년에는 cat-qubit·qLDPC·산술 회로를 바꾸는 서로 다른 추정이 나왔다.[1–4] | 암호 크기의 실제 실행 시점은 미정. 2027–30년 개발사 하드웨어 목표를 별도 띠로 표시하고, 해당 회로의 오류·논리 게이트·실행시간 조건을 충족하는지 대조한다. | 물리 큐비트와 논리 큐비트, Toffoli 개수와 깊이, 공장·디코딩·반응 시간, 연결성·잡음 가정을 함께 공개한다. 작은 수를 풀도록 사전 축약한 회로와 일반 알고리즘을 구별한다. |
| Grover | 검색·진폭 증폭의 회로를 작은 규모로 실습할 수 있다. 유리한 오라클 질의 수가 실제 전체 실행의 이점으로 바뀌는지는 별도 자원 문제다.[5] | 범용 데이터베이스 검색의 상용화 연도는 산정하지 않는다. 초기 FTQC에서도 이차 가속을 상쇄하는 비용이 남을 수 있다. | 판정 오라클을 만드는 가역 회로, 상태 준비, 반복 깊이, 병렬 고전 검색과의 비교. ‘100만 후보→약1000회 질의’에는 이 조건을 붙인다. |
| QFT | 이미 구현·교육·실험에서 쓰는 회로 구성 요소다. 주기·위상의 표현을 바꾸며 Shor·일부 QPE의 일부가 된다. | 독립 상품처럼 출시 연도를 매기지 않는다. 해당 QFT를 포함한 응용의 준비 수준을 표시한다. | 작은 각도 회전의 근사, 연결·컴파일 비용, 회전 합성 오차가 최종 성공 확률에 미치는 영향. QFT만 빨라졌다고 고전 FFT의 일반 대체가 되지는 않는다. |
| QPE | 작은 화학 문제의 실제 시연과, 더 큰 문제를 위한 자원 추정이 공존한다. 2026-11-09 v3 연구는 STAR 기반 단일 보조큐비트 QPE의 화학 자원을 추정했다.[6] | 화학 정확도와 산업 규모의 실용 이점은 조건부·시점 미정. 초기 FTQC를 중요한 시험 단계로 삼되, 물리 큐비트·운전시간·초기 상태 중첩 조건을 먼저 적는다. | 긴 시간 진화·제어 연산, 좋은 초기 상태, 원하는 고유상태의 확률, 활성공간과 해밀토니안 근사, 전체 오류 예산. |
| VQE | 양자·고전 하이브리드 계산 소프트웨어와 클라우드 실험 환경이 현재 제공된다. InQuanto의 문서는 VQE와 위상추정·임베딩·오류 저감의 결합을 지원한다.[7] | 개발·공동 연구 서비스는 현재 이용 가능. 특정 분자·재료에서 강한 고전 방법보다 유리한 실용화 시점은 별도로 입증해야 한다. | ansatz의 표현력과 최적화, 측정 샷, 노이즈·오류 저감의 비용, 고전 전처리·대각화 비용. SQD·QSE·HI-VQE의 혼합 계산을 모두 동일한 VQE로 부르지 않는다. |
| QAOA | 2026-11-19 출판 연구에서 Quantinuum H2·Helios의 오류정정된 FT 구성으로 작은 QAOA를 실행했다. 복잡한 논리 회로의 near-breakeven 단계다.[8] | 현재의 물리 실행·클라우드 접근과 대규모 최적화의 경제적 이점을 구별한다. 산업 문제 전반의 실용화 연도는 미정이며, 문제 분포별 비교가 필요하다. | 강한 고전 휴리스틱·정확 해법, 같은 품질의 time-to-solution, 파라미터 학습·샷·실패를 포함한 비용, 깊이 증가에 따른 오류. QAOA+진폭 증폭의 FT 자원 추정도 비교한다.[9] |
| HHL와 양자 선형계 | 위 FT 연구에서 작은 Poisson 문제의 HHL도 실행했다.[8] 이론에서는 상태 준비 질의의 비용을 줄이는 현대 QLSA가 발전하고 있다.[10] | 구현된 작은 선형계와 대규모 수치해석의 이점을 구분한다. 해 상태에서 필요한 관측량을 얻는 응용별로 평가하며 범용 선형해법의 출시 연도는 정하지 않는다. | 행렬 접근·블록 인코딩, 조건수·오차, 우변 준비, 정규화 성공률, 해 전체를 읽는 비용. 같은 입력 접근을 허용한 고전·dequantized 비교도 포함한다.[11] |
| Quantum walks | 그래프 탐색의 알고리즘 계열이자, qubitization을 통한 해밀토니안 시뮬레이션의 기반이다.[12] | 워크 자체의 상용화보다 이를 사용하는 탐색·시뮬레이션 응용의 자원 기준으로 전망한다. | 그래프·이웃 접근 오라클, 스펙트럼 간격, 상태 준비, 검출·판독과 고전 random-walk 기준. |
| QAE | 깊이와 반복 횟수를 절충하는 최근 이론·수치 연구가 있다. 2026년 Erle–Koczor는 보조큐비트·controlled-Grover 없이 깊이를 조절하는 방법을 제안했다.[13] | 금융·불확실성 정량화의 실습과 원형 개발은 현재 가능. 동일 오차의 몬테카를로를 전체 시간·비용에서 앞서는 시점은 상태 준비와 FT 실행의 조건에 달린다. | 확률분포·payoff 인코딩, 진폭 증폭의 반복 깊이, 희귀 사건과 신뢰구간, 고전 분산 감소법. 질의 복잡도와 실제 지연을 별도로 센다. |
| QSVT | 행렬의 특이값에 다항식을 적용하는 설계 틀이며, PennyLane 등의 회로 구성 API가 제공된다.[14] | 이미 쓸 수 있는 알고리즘 설계·소프트웨어 도구다. 응용 전체의 양자 이점은 각 블록 인코딩·정밀도·출력 조건을 기준으로 전망한다. | 효율적인 블록 인코딩, 정규화 계수, 다항식 차수·위상 합성, 상태 준비·후선택, 최종 관측량. ‘행렬을 넣으면 원하는 함수가 공짜로 계산된다’는 설명을 피한다. |

## 2026년의 전선을 보여 주는 근거

### 같은 Shor에서도 다른 자원 장부가 나온다

- Gidney의 2025년 추정은 RSA-2048을 100만 미만 noisy qubit, 1주 미만에 푸는 시나리오다. 최근접 연결, 0.1% 게이트 오류, 1μs surface-code cycle, 10μs 반응 시간을 가정한다.[1]
- Pinnacle의 qLDPC 아키텍처는 같은 크기의 문제에 10만 미만 physical qubit을 추정한다. p=10⁻³, cycle 1μs, reaction 10μs가 전제이며 하드웨어 실행 결과가 아니다.[2]
- 2026-11-19 개정 cat-qubit 연구는 완전 컴파일한 RSA-2048에 약2.3만 cat qubit·3.14일을 보고한다. cycle 1μs, reaction 10μs, pZ=5×10⁻⁴와 bit-flip 부재를 가정한다. 이 조건을 완화하는 추가 부호화에서는 약4.5만으로 달라진다.[3]
- 2026-11-06 산술 연구는 같은 논리 큐비트 예산에서 Toffoli를 줄이는 접근을 제시한다. 1,461 logical qubit에서 5.08×10⁹회, 1,806에서 2.55×10⁹회라는 추정은 물리 시간과 별도다.[4]

이들을 한 그래프의 ‘최소 큐비트 신기록’으로만 나열하면 아키텍처와 시간의 교환을 놓친다. 리뷰에서는 산술 회로 → 논리 게이트 → 부호·팩터리 → 장치 배치·시간으로 이어지는 각 장부를 분리한다. 대표 연구자는 Craig Gidney, André Schrottenloher, cat-qubit 컴파일 연구진, Pinnacle의 Paul Webster·Lawrence Cohen 연구진이다. 이 명단은 확인한 접근의 예이며 성능 순위가 아니다.

### 오류정정된 알고리즘을 실제로 끝까지 실행하는 단계

Perlin과 공동연구진의 2026-11-19 PRX 논문은 JPMorganChase·Quantinuum이 Steane [[7,1,3]] 부호로 QAOA와 작은 Poisson-HHL을 실행한 근거다. 최대 QAOA 사례는 12 logical·97 physical qubit과 2,132 physical two-qubit gate를 사용했으며 무작위 추측보다 나은 성능을 보였다.[8]

이는 오류정정한 논리 알고리즘의 성능을 검증하는 결과다. 해당 12변수 사례는 작은 T-gate 예산에 맞는 인스턴스를 선택하고 고전적으로 파라미터를 최적화했다. 논문도 생성 방식의 비확장성을 밝힌다. ‘near-breakeven’은 논리 부호화 실행과 비부호화 실행의 비교이며, 고전 최적화기 대비 실용 이점으로 옮기지 않는다.

QAOA+진폭 증폭의 다른 자원 연구는 무작위 8-SAT의 특정 조건에서 179변수·약15시간 crossover에 약7,391만 physical qubit을 추정했다.[9] 실험과 자원 추정을 함께 놓으면, 논리 실행의 진전과 실용 규모 사이에서 무엇을 더 줄여야 하는지 설명할 수 있다.

### 화학과 선형대수에서 문제의 구조를 바꾸는 접근

Kanasugi·Toshio·Maruyama·Oshima의 QPE 연구 v3는 unitary weight concentration과 부분 무작위 시간 진화를 STAR 아키텍처에 결합한다. 약20–50 spatial orbital의 활성공간에서 약10⁵ physical qubit과 수일–수주 실행을 추정한다.[6] 이는 실제 QPU에서 그 분자를 계산한 실적과 구별해 표시한다. FCI의 직접 계산 범위를 넘는다는 사실만으로 DMRG·selected CI·coupled-cluster 등 강한 고전 대안 전반보다 유리하다고 판정하지 않는다.

Low–Su의 2026년 QLSA는 우변 상태 준비의 질의 수를 핵심 자원으로 다룬다.[10] Chakrabarti와 공동연구진의 2026-10-30 논문은 QRAM·sampling/query 접근 모형에서 선형대수의 양자–dequantized 차이를 이론적으로 분석한다.[11] 두 접근은 큰 행렬의 차원 하나만으로 가속을 설명하는 관행을 고치는 사례가 된다. 입력 접근 모형, 조건수, 원하는 출력의 형태가 실제 적용을 결정한다.

## 기업 일정은 하드웨어 시나리오로 따로 놓는다

| 공식 근거와 확인 시점 | 개발사가 제시하는 목표 | 알고리즘에 연결할 때 확인할 것 |
|---|---|---|
| IBM, 2026-11-11 갱신 | 2029년 Starling, 200 qubit·1억 quantum operation. 2025년 원 계획은 200 logical qubit으로 명시했다.[15] | 200 logical qubit만으로 RSA-2048이나 임의의 화학 문제를 수행한다고 추론하지 않는다. 논리 오류율·게이트 종류·공장·운전 시간과 대상 회로를 맞춘다. |
| Quantinuum, 2026-11-22 현행 페이지 | Helios에서 2027년 Sol, 2029년 universal fully-FT Apollo로 발전하는 계획.[16] | 현재 Helios의 FT 소규모 실행과 Apollo의 장래 규모·연속 운전 성능을 구별한다. 회사는 일정 변경 가능성을 명시한다. |
| IonQ, 2026-11-22 현행 페이지 | 2027년 800, 2028년 1,600, 2029년 8,000, 2030년 80,000 logical qubit 목표.[17] | 로드맵상 큐비트 수를 해당 날짜의 실증으로 쓰지 않는다. 논리 오류의 정의·보존 시간·보편 게이트·네트워킹·디코딩 속도가 대상 알고리즘을 지탱하는지 확인한다. |

따라서 ‘향후 3–8년’ 같은 한 구간을 모든 알고리즘에 배분하기보다, **현재 접근 가능한 구현 → 확인할 규모와 품질 → 필요한 논리 자원 → 이를 뒷받침할 하드웨어 목표 → 남은 전체 비용**의 순서로 전망을 제시한다. 개발사 계획은 가능한 기획 시나리오이며, 응용의 채택 시점에 대한 독립 예측으로 표현하지 않는다.

## 후속 리뷰의 우선순위와 비교 장치

1. **위상으로 에너지를 읽기:** QFT·QPE를 하나의 분자 예제로 설명하고, VQE와 비교한다. 단순 원리에서 가장 현대적인 화학 자원 추정까지 이어진다.
2. **확률을 증폭하고 추정하기:** Grover·QAE에서 oracle·state preparation·measurement를 같은 장부로 센다. 금융과 몬테카를로에 쓰려면 무엇이 입력되고 무엇을 얻는지 보여준다.
3. **회전하는 행렬과 문제의 구조:** quantum walks·qubitization·QSVT·QLSA를 연결한다. 고유값·특이값·조건수와 관측량을 구체적인 작은 행렬로 소개한다.
4. **최적화와 오류정정의 접점:** 11월 PRX의 실제 QAOA·HHL 실행을 축으로, 오류정정의 breakeven과 고전 대비 이점을 분리한다.
5. **Shor의 실제 비용:** 주기 찾기의 원리와 함께 산술·부호·잡음·배치의 선택이 자원을 얼마나 바꾸는지 읽는다.

종합 리뷰의 성숙도 그림은 알고리즘을 한 줄의 날짜에 놓기보다, **입력·오라클·논리 회로·오류정정·판독·고전 비교** 여섯 칸에서 확인된 근거와 남은 과제를 보여주는 구성이 적합하다. 실제 QPU 결과와 이론적 자원 추정에는 서로 다른 표식을 쓴다. 앞선 에너지 리뷰와의 연결도 질의 수·토큰 같은 중간 지표에서 전체 시간·에너지·품질로 넘어가는 판단에 두면 자연스럽다.

## 참고문헌

[1] C. Gidney, How to factor 2048 bit RSA integers with less than a million noisy qubits, [arXiv:2505.15917v1](https://arxiv.org/abs/2505.15917v1) (2025).

[2] P. Webster, L. Berent, O. Chandra, E. T. Hockings, N. Baspin, F. Thomsen, S. C. Smith, and L. Z. Cohen, The Pinnacle architecture: Reducing the cost of breaking RSA-2048 to 100 000 physical qubits using quantum LDPC codes, [arXiv:2602.11457v2](https://arxiv.org/abs/2602.11457v2) (2026).

[3] A. Pappalardo, D. Goudarzi, V. Hertz, H. Jacinto, L. Kroell, A. Schrottenloher, P. Shanahan, É. Gouzien, R. de la Vieuville, and V. Londe, Shor's algorithm compiled on cat qubits: 22 593 qubits for RSA-2048 in 3.14 days, [arXiv:2610.37839v2](https://arxiv.org/abs/2610.37839v2) (2026).

[4] M. Sharma and H. C. Lau, Shared lookups and lazy residues: Fewer Toffoli gates for factoring RSA-2048, [arXiv:2611.08907v1](https://arxiv.org/abs/2611.08907v1) (2026).

[5] R. Babbush, J. McClean, M. Newman, C. Gidney, S. Boixo, and H. Neven, Focus beyond quadratic speedups for error-corrected quantum advantage, [PRX Quantum **2**, 010103 (2021)](https://doi.org/10.1103/PRXQuantum.2.010103).

[6] S. Kanasugi, R. Toshio, K. Maruyama, and H. Oshima, Enabling chemically accurate quantum phase estimation in the early fault-tolerant regime via unitary weight concentration, [arXiv:2603.22778v3](https://arxiv.org/abs/2603.22778v3) (2026).

[7] Quantinuum, [InQuanto](https://docs.quantinuum.com/inquanto/) (accessed November 22, 2026).

[8] M. A. Perlin, Z. He, A. Alexiades Armenakas, P. Andres-Martinez, T. Hao, D. A. Herman, Y. Jin, K. Mayer, C. N. Self, D. Amaro, C. Ryan-Anderson, and R. Shaydulin, Fault-tolerant execution of error-corrected quantum algorithms, [Phys. Rev. X **16**, 041048 (2026)](https://doi.org/10.1103/gnq3-c2df).

[9] S. Omanakuttan, Z. He, Z. Zhang, T. Hao, A. Babakhani, S. Boulebnane, S. Chakrabarti, D. Herman, J. Sullivan, M. A. Perlin, R. Shaydulin, and M. Pistoia, Threshold for fault-tolerant quantum advantage with the quantum approximate optimization algorithm, [arXiv:2504.01897v1](https://arxiv.org/abs/2504.01897v1) (2025).

[10] G. H. Low and Y. Su, Quantum linear system algorithm with optimal queries to initial state preparation, [Quantum **10**, 2041 (2026)](https://doi.org/10.22331/q-2026-03-23-2041).

[11] S. Chakrabarti, D. Herman, J. L. Kim, and G. Ozgul, The quartic gap between quantum and dequantized algorithms for linear algebra is tight, [arXiv:2610.42069v1](https://arxiv.org/abs/2610.42069v1) (2026).

[12] G. H. Low and I. L. Chuang, Hamiltonian simulation by qubitization, [Quantum **3**, 163 (2019)](https://doi.org/10.22331/q-2019-07-12-163).

[13] J. Erle and B. Koczor, Nearly optimal amplitude estimation at any depth, [arXiv:2608.24434v1](https://arxiv.org/abs/2608.24434v1) (2026).

[14] PennyLane, [qp.qsvt](https://docs.pennylane.ai/en/stable/code/api/pennylane.qsvt.html), version 0.45.1 documentation (accessed November 22, 2026).

[15] M. Steffen and M. Marwick, [Tracking progress on the path to IBM Quantum Starling](https://www.ibm.com/quantum/blog/path-to-ibm-quantum-starling) (November 11, 2026).

[16] Quantinuum, [Roadmaps](https://www.quantinuum.com/company/roadmaps) (accessed November 22, 2026).

[17] IonQ, [Roadmap](https://www.ionq.com/roadmap) (accessed November 22, 2026).

## 조사·확인 범위

현재 공개된 원 논문 초록·판본 정보, PRX의 공개 본문, 공식 제품 문서·기업 로드맵을 직접 확인했다. PRX의 12변수 인스턴스 선택과 breakeven의 뜻을 본문에서 확인했다. 다른 큰 숫자는 원 저자 자원 추정의 조건과 함께 수록했다. 모든 계산·코드·장치 실험을 독립 재현한 것은 아니다. 링크를 제공한 소셜 게시물은 주제 발견의 출발점이며, 위 자원·일정의 근거로 대체하지 않았다.
