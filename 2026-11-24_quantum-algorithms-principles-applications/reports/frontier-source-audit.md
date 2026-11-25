# 양자 알고리즘 최근 연구와 실용화 근거 대조

2026-11-24 · 편집부(AEDAUT) 조사·과학 감수 · quantum_frontier_update

11월 22일 승인 기획의 대표 연구를 공개 원 논문과 공식 자료로 다시 확인했다. 아래는 집필에서 사용할 대상·지표·비교 조건을 정리한 기록이다. 확인한 열 가지 알고리즘의 대표 문헌에 판본 변경은 발견하지 못했다. ‘최전선’은 병목을 다르게 줄이는 대표 사례의 의미로 사용한다.

## 열 가지 알고리즘의 대표 연구

| 알고리즘 | 대표 연구자·기관과 접근 | 11월 24일 확인한 판본·실행 수준 | 본문에서 연결할 구체적인 진전 |
|---|---|---|---|
| QFT | Philipp Aumann·Michael Fellner·Wolfgang Lechner 등, ParityQC. SWAP 이동을 줄이는 Parity Twine. | 2604.12465v3, 2026-11-04. IBM Heron r3·Rigetti Ankaa-3 실제 QPU.[1] | 필요한 쌍별 상호작용을 장치 연결에 배치하는 방법이 같은 QFT의 충실도를 바꾼다. |
| QPE | Kaur Kristjuhan·Dominic W. Berry, Molecular Quantum Solutions·Macquarie. DPSS 제어 상태·MPS 준비·중간 측정. | Quantum 10, 2193, 2026-08-19. arXiv v3는 2026-08-07. 회로 구성·수치적 상태 근사 연구.[2] | 제어 상태의 가중치를 바꾸어 위상 추정의 오차 분포를 모으고, 세 제어 큐비트를 재사용한다. |
| Shor | Axel Pappalardo와 공동연구진, Alice & Bob·Inria 등. cat-qubit 산술·LDPC-cat 배치와 스케줄. | 2610.37839v2, 2026-11-19. 물리 배치까지 포함한 자원 추정.[3] | 알고리즘·산술·오류정정 부호·공장·피드백 속도가 합쳐져 총 자원을 결정한다. |
| Grover | Evan M. Reeves·Elias Sopkin·Thomas A. Searles. Minecraft seed 복원용 상수 산술과 가역 판정기. | 2610.33139v1, 2026-10-23. 큰 회로 자원 분석과 축소 회로의 IBM·Quantinuum H2-1 실행.[4] | 질의 한 번을 구성하는 산술과 역계산을 줄이는 문제가 검색 반복 횟수만큼 중요하다. |
| QAE | Farrokh Labib. 2배 간격 이외의 깊이 사다리와 최대우도 추정. | 2609.02715v1, 2026-09-02. 이론·수치 비교·공개 코드 소개.[5] | 깊이 스케줄·병렬 실행·오차 구간을 함께 설계한다. |
| VQE | Hugo D. Nogueira·Jean-Philip Piquemal 등, Sorbonne·Qubit Pharmaceuticals. VULCAN의 회로 성장·압축·고전 섭동 보정. | 2610.40561v3, 2026-11-02. 주 결과는 잡음 없는 에뮬레이션, 별도 H₂ 분자의 실제 H2 장치 초기 실험.[6] | 측정 대리지표·회로 깊이·큐비트·GPU 후처리 사이의 자원 분업을 설명한다. |
| QAOA | Michael A. Perlin·Ruslan Shaydulin 등, JPMorganChase·Quantinuum. Steane 부호의 FT 회전·동적 회로. | Phys. Rev. X 16, 041048, 2026-11-19. H2·Helios 실제 오류정정 알고리즘 실행.[7] | 회전 합성의 정확도와 T 게이트 오류의 경쟁을 실제 응용 회로로 읽는다. |
| HHL·현대 QLSA | [7]의 작은 Poisson 문제와 Guang Hao Low·Yuan Su의 초기 상태 준비 질의 최적화. | [7]은 실제 FT 회로. Quantum 10, 2041, 2026-03-23은 이론적 질의 개선.[8] | 행렬 접근과 우변 준비를 별도 자원으로 센다. 해 상태에서 어떤 관측량을 읽을지 정한다. |
| Quantum walks | Massimiliano Incudini·Guglielmo Mazzola의 fully-quantum Metropolis, Tao Rong 등 연구진의 완전 이분 그래프 검색. | 2607.22818v1, 2026-07-24는 FT 컴파일·고전 비교; 2611.20053v1, 2026-11-15는 실제 gate-based 검색.[9,10] | 입력 그래프와 축소 불변부분공간 인코딩, 탐색·표본화의 서로 다른 목표를 구별한다. |
| QSVT | Joel Bierman·Pawan Poudel·Yuan Liu의 double randomization, Xi Lu·Yuan Liu·Hongwei Lin의 U(N) 확장. | 2611.18881v1, 2026-11-13은 오차 정리·수치적 상한 평가. Quantum 10, 2048, 2026-03-27은 이론적 변환 체계.[11,12] | 블록 인코딩·다항식·회로 깊이·표본 비용을 함께 바꾸는 방법으로 설명한다. |

## 본문에 사용할 다섯 연구의 근거 위치

### QFT에서는 연결성이 계산의 품질이 된다

[1]의 본문 §III와 Appendix B를 확인했다. IBM Heron r3의 50큐비트 QFT에서 보고한 약10⁻²는 **과정 충실도**다. 기본 실험은 입력 상태 20개와 회로당 2,000 shots를 사용한다. 논문이 SWAP 기반 방법과 비교한 초지수적 개선은 과정 충실도 비의 스케일링이다. 이 결과를 연산시간의 고전 대비 가속으로 옮기지 않는다.

Plurality voting을 사용한 52큐비트의 거의1인 평균 결과 성공확률은 별도 지표다. 여러 동등 회로의 결과를 비선형으로 모은 후처리이므로 과정 충실도와 같은 축으로 놓지 않는다. 본문에서는 ‘같은 연산도 어디에 어떤 게이트로 놓느냐에 따라 결과가 달라진다’는 설명에 연결한다.

### Shor의 숫자는 산술에서 장치 배치까지 이어진다

[3]의 Table 1과 그 직전·직후 자원 가정을 확인했다. RSA-2048의 균형 구성은 **22,593 cat qubits·총3.14일** 추정이다. 표의 한 shot 시간은7.84시간, 예상 shots는9.60이다. 오류정정 주기1μs, 반응시간10μs, phase-flip 확률5×10⁻⁴, bit-flip 무시 조건을 함께 둔다. 원문은 이에 약100년의 bit-flip 시간 조건이 필요하다고 설명한다.

Bit-flip 시간이 약1시간일 때 추가 보호층을 넣은 별도 구성은 약45,000 cat qubits로 추정된다. 큐비트 수를 단독 지표로 읽기보다, 잡음의 비대칭을 활용하는 부호·공장과 시간의 교환을 보여주는 사례다.

### QAOA에서는 회전각의 근사와 오류가 경쟁한다

[7]의 PDF §III.C, §IV.B, Figs.12–15, Table IV를 확인했다. 5·6변수 LABS에서는 회전을 더 많은 T 게이트로 근사한 회로가 개선됐다. 선택한 12변수 portfolio 사례에서는 깊이2 회로의 2,132 physical two-qubit gates가 깊이1의1,132개보다 더 큰 오류 비용을 만들었고, 깊이2의 결과가 나빴다. 둘 모두 무작위 추측보다 나은 결과를 냈다.

12변수는97 physical qubits를 사용했다. 사례와 각도는 작은 T 게이트 예산에 맞춰 고전적으로 선택했으며, 저자는 그 생성 방식의 비확장성을 설명한다. 논문의 near-breakeven은 **부호화된 양자 회로와 비부호화된 양자 회로**의 비교다. 실제 회전과 최적화의 관계를 설명한 뒤, 같은 각도를 오류정정 게이트로 바꿀 때 생기는 비용으로 이어 가면 자연스럽다.

같은 논문의 HHL은 주기 경계를 가진 1차원4격자점 Poisson 문제다. b=(1,−1,i,−i)를 사용한 작은 least-squares 문제이며, 일반적인 대규모 수치해석과의 전체 비용 비교는 다른 질문이다. 본문이 수치해법으로 확장될 때 입력·출력 조건을 구체화하는 데 사용할 수 있다.

### VQE에서는 무엇을 줄였는지 구체적인 자원으로 읽는다

[6]의 §II.2–II.6과 §III를 확인했다. 수소 사슬·BeH₂·H₂O에서 기준 batched ADAPT-VQE 대비 **5–20%**는 잡음 없는 상태벡터 에뮬레이션의 **누적 Pauli-term evaluation count**다. 실제 shots나 벽시계 시간의 계측값으로 바꾸지 않는다. 압축 전 회로는 측정 대리지표를 줄이면서 더 깊어질 수 있고, 별도 압축·부분공간 투영·GPU 섭동 보정은 각각 다른 자원을 다룬다.

실제 Quantinuum H2의 H₂ 분자 초기 결과는 −1.12666Ha, 에뮬레이션은 −1.12836Ha다. 저자가 제시한 차이는1.7mHa로, 이 논문의 화학정확도 기준1.6mHa에 가깝다. 큰32큐비트 에뮬레이션의 결과와 이 장치 실험을 나누면, 양자·고전 분업이 어디에서 작동했는지 설명할 수 있다.

### QPE의 전체 실행시간과 가장 긴 회로는 다른 시계다

추가 집필 근거 [13]의 §V.3.2, Table 4, Fig.7을 확인했다. Fujitsu·Osaka의 Kanasugi 등은 Hamiltonian 표현의 계수를 집중시키고 부분 무작위 시간 진화와 STAR 기반 부분 내결함성 실행을 결합한다. **31공간궤도의 P450-Cpd I(E)**에 대해 QPU당1.41×10⁵ physical qubits, 단일 QPU 총37.4일을 추정한다. 이때 최장 개별 회로는33.9초다.

조건은 초기 바닥상태 겹침p₀>0.99(ξ=.01), 목표정밀도1.6mHa, physical error rate10⁻³다. 물리 큐비트 총예산5×10⁵에서 세 QPU를 병렬 사용한 추정은12.5일이다. 이 표는 물리 장치 실험이 아니라 자원 모형이다. 총실행시간·한 번의 연속 회로·반복과 병렬성의 차이를 독자가 직접 읽게 한다.

## QSVT와 제어 상태 준비의 추가 확인

[11]의 §V.2–V.3, Figs.1–4를 확인했다. 8×8 장거리 Heisenberg 모형과 철–황 복합체 Hamiltonian에 대한 diamond-norm 오차 **상한**을 수치적으로 평가했다. 10⁻³ 목표에서 블록 인코딩에 필요한 Pauli 항 수가 일부 경우10배 이상 줄어드는 결과는 함수·상호작용 범위·궤도 기저에 따라 달라진다. 원문의 줄인 양은 Pauli 항 예산이고, 이를 깊이 절감으로 연결할 때 선택한 블록 인코딩 구현을 함께 제시한다.

[2]는 공식 출판사 소개와 arXiv v3의 도입·§2.1을 읽었다. arXiv HTML은 이후 변환이 끊겨 전체 방법을 제공하지 않았고, 출판 PDF는 검색 도구의 후속 요청에서 timeout이 있었다. 제어 레지스터 세 큐비트의 재사용·DPSS/MPS 접근과 최대2²⁴차원 시험은 출판사 초록·설명에서 확인한 범위다. 시스템 레지스터·시간 진화용 작업 큐비트까지 총세 개라고 표현하지 않는다.

## 실용화 전망에 사용할 공식 시간표

| 공식 자료·확인일 | 현재 제시한 목표 | 본문에 연결할 조건 |
|---|---|---|
| IBM, 2026-11-11 글을11월24일 재확인.[14] | Starling 2029년, 200 qubits·1억 operations. | 이 글의 장치 목표와, 논문이 요구하는 논리 게이트 종류·오류 예산·시간·공장을 대조한다. |
| Quantinuum 현행 Roadmaps, 2026-11-24.[15] | Sol 2027년·Apollo 2029년 계획. | 현재 Helios의 작은 FT 알고리즘 실행과 차세대 장치 계획을 별도 표식으로 둔다. |
| IonQ 현행 Roadmap, 2026-11-24.[16] | 2027년800, 2028년1,600, 2029년8,000, 2030년80,000 logical qubits 목표. | 논리 오류의 정의·보편 게이트·반복·네트워크와 실제 회로의 요구를 연결한다. |

‘현재 도구·연구 서비스 → 응용 규모의 검증 → 경쟁 가능한 전체 비용’의 세 단계는 승인 기획대로 유지할 수 있다. 2027–2029년은 위 기업 계획이 실현되는 경우 더 큰 초기 오류정정 응용을 관찰할 시간 창이다. 알고리즘별 경제적 채택 연도는 원하는 출력과 정확도, 자원표·장치 조건을 맞춰 판단한다.

기존 보조 자원 문헌도 판본을 재확인했다. Gidney의100만 미만 noisy qubits·1주 미만 추정[17], Pinnacle의10만 미만 physical qubits 추정[18], Sharma–Lau의 산술 Toffoli 절감[19], QAOA+진폭 증폭의8-SAT crossover 자원 모형[20]은 모두 기존 판본을 유지한다. 이 네 자료는 이번에 서지·초록·가정까지만 재확인했으며 수치의 본문 재검산은 수행하지 않았다.

## 집필 감수에 반영할 판단

- ‘최신·최전선’은 확인한 최근 대표 연구의 범위로 쓴다. 이 조사로 연구자·기업의 단일 선두 순위를 만들지 않는다.
- QFT의 충실도·후처리 성공확률, VULCAN의 평가 횟수·shots, 총실행시간·최장 회로, 부호화 회로의 breakeven·고전 대비 비용 우위를 각각 해당 결과의 지표로 설명한다.
- 약속된 하드웨어 연도와 실제 연구 결과를 같은 데이터 점으로 그리지 않는다. 달력의 기업 목표에는 기관과 확인일을, 실험·자원 추정에는 실행 수준과 조건을 표시한다.
- 이번 조사는 원문 대조다. 원 논문의 장치 실험·에뮬레이션·자원 계산을 독립 재실행하지 않았다. 리뷰의 작은 교육 예제 계산은 별도 코드·검산 기록에 연결한다.

## 참고문헌

[1] P. Aumann, M. Fellner, D. Alber, M. Cykiert, C. Fleckenstein, R. ter Hoeven, L. Stenzel, R. J. Valencia-Tortora, and W. Lechner, Demonstrating record fidelity for the quantum Fourier transform, [arXiv:2604.12465v3](https://arxiv.org/abs/2604.12465v3) (2026).

[2] K. Kristjuhan and D. W. Berry, Quantum phase estimation with optimal confidence interval using three control qubits, [Quantum **10**, 2193 (2026)](https://doi.org/10.22331/q-2026-08-19-2193).

[3] A. Pappalardo, D. Goudarzi, V. Hertz, H. Jacinto, L. Kroell, A. Schrottenloher, P. Shanahan, É. Gouzien, R. de la Vieuville, and V. Londe, Shor’s algorithm compiled on cat qubits: 22 593 qubits for RSA-2048 in 3.14 days, [arXiv:2610.37839v2](https://arxiv.org/abs/2610.37839v2) (2026).

[4] E. M. Reeves, E. Sopkin, and T. A. Searles, The cost of a real Grover oracle: Minecraft seed search from software to quantum hardware, [arXiv:2610.33139v1](https://arxiv.org/abs/2610.33139v1) (2026).

[5] F. Labib, Quantum amplitude estimation beyond power-of-two schedules, [arXiv:2609.02715v1](https://arxiv.org/abs/2609.02715v1) (2026).

[6] H. D. Nogueira, S. Badreddine, O. Adjoua, D. Traore, G. Michel, and J.-P. Piquemal, Grow, compress, and perturb: A hybrid quantum-classical pathway to scalable quantum chemistry on quantum computers, [arXiv:2610.40561v3](https://arxiv.org/abs/2610.40561v3) (2026).

[7] M. A. Perlin, Z. He, A. Alexiades Armenakas, P. Andres-Martinez, T. Hao, D. A. Herman, Y. Jin, K. Mayer, C. N. Self, D. Amaro, C. Ryan-Anderson, and R. Shaydulin, Fault-tolerant execution of error-corrected quantum algorithms, [Phys. Rev. X **16**, 041048 (2026)](https://doi.org/10.1103/gnq3-c2df).

[8] G. H. Low and Y. Su, Quantum linear system algorithm with optimal queries to initial state preparation, [Quantum **10**, 2041 (2026)](https://doi.org/10.22331/q-2026-03-23-2041).

[9] M. Incudini and G. Mazzola, Practical advantage beyond the quadratic speedup limit with fully-quantum walks, [arXiv:2607.22818v1](https://arxiv.org/abs/2607.22818v1) (2026).

[10] T. Rong, M. Li, X. Tong, J. Cai, Y. Li, N. Zhou, S. Li, S. Cao, Y. Li, Y. Xu, F. Chen, M. Gong, X. Sun, and C. Zha, Hardware-aware realization of deterministic quantum-walk search on complete bipartite graphs, [arXiv:2611.20053v1](https://arxiv.org/abs/2611.20053v1) (2026).

[11] J. Bierman, P. Poudel, and Y. Liu, Double-randomized quantum singular value transformations for early fault-tolerant quantum computers, [arXiv:2611.18881v1](https://arxiv.org/abs/2611.18881v1) (2026).

[12] X. Lu, Y. Liu, and H. Lin, Quantum signal processing and quantum singular value transformation on U(N), [Quantum **10**, 2048 (2026)](https://doi.org/10.22331/q-2026-03-27-2048).

[13] S. Kanasugi, R. Toshio, K. Maruyama, and H. Oshima, Enabling chemically accurate quantum phase estimation in the early fault-tolerant regime via unitary weight concentration, [arXiv:2603.22778v3](https://arxiv.org/abs/2603.22778v3) (2026).

[14] M. Steffen and M. Marwick, [Tracking progress on the path to IBM Quantum Starling](https://www.ibm.com/quantum/blog/path-to-ibm-quantum-starling) (November 11, 2026).

[15] Quantinuum, [Roadmaps](https://www.quantinuum.com/company/roadmaps) (accessed November 24, 2026).

[16] IonQ, [Roadmap](https://www.ionq.com/roadmap) (accessed November 24, 2026).

[17] C. Gidney, How to factor 2048 bit RSA integers with less than a million noisy qubits, [arXiv:2505.15917v1](https://arxiv.org/abs/2505.15917v1) (2025).

[18] P. Webster, L. Berent, O. Chandra, E. T. Hockings, N. Baspin, F. Thomsen, S. C. Smith, and L. Z. Cohen, The Pinnacle architecture: Reducing the cost of breaking RSA-2048 to 100 000 physical qubits using quantum LDPC codes, [arXiv:2602.11457v2](https://arxiv.org/abs/2602.11457v2) (2026).

[19] M. Sharma and H. C. Lau, Shared lookups and lazy residues: Fewer Toffoli gates for factoring RSA-2048, [arXiv:2611.08907v1](https://arxiv.org/abs/2611.08907v1) (2026).

[20] S. Omanakuttan, Z. He, Z. Zhang, T. Hao, A. Babakhani, S. Boulebnane, S. Chakrabarti, D. Herman, J. Sullivan, M. A. Perlin, R. Shaydulin, and M. Pistoia, Threshold for fault-tolerant quantum advantage with the quantum approximate optimization algorithm, [arXiv:2504.01897v1](https://arxiv.org/abs/2504.01897v1) (2025).
