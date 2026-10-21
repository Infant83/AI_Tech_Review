# DQB 후보 원문 대조 — QAOA·Hamiltonian embedding·giant atom

근거 기준일: 2026-10-21. 편집 정책·작성 방법을 적용한 내부 기획 자료. 논문 보고 결과를 대조했으며 코드를 독립 재현하지 않았다. 원문·개인 메일 재배포용이 아니다.

## 1. Higher-order Parity Constraints for Quantum Approximate Optimization

- [원문 v1](https://arxiv.org/html/2610.26381v1), [초록·서지](https://arxiv.org/abs/2610.26381): 2026-10-19 제출, 프리프린트. 저자 Anita Weidinger, Glen Bigan Mbeng, Roeland ter Hoeven, Wolfgang Lechner.
- **실행:** noiseless simulation과 IBM Heron QPU를 구분. §III.2.1–3, Fig. 5: 40은 그래프 정점/논리 변수 수이며 parity 표현은 `K=1.5N`, 따라서 **60 physical parity qubits**. 실제 배치·라우팅의 추가 자원과 동일시하지 않는다.
- **결과:** 한 40정점 그래프의 20개 무작위 Signed Max-Cut 결합 instance에서 최적해를 한 번 이상 측정. direct QAOA는 해당 측정 예산에서 0개. 회로 절삭·spanning-tree decoding을 포함한 비교이며, `M=7`에서 모두 해결. 각 회로 4,096 shots, ibm_fez. 매 shot 성공률 100%라는 뜻이 아니다.
- **고전 비용·경계:** 14정점 12개 학습 instance에서 고전 최적화 후 파라미터 이전. Appendix B: p=1/2/3/4에서 20/160/480/800 최적화 run. §IV·Appendix D: 첫 층은 고전 샘플링 가능한 product-state warm start; decoding 비용도 포함해야 한다. Gurobi가 N=40 최적값을 약 0.02초에 계산했다는 Appendix D 보고 때문에 고전 대비 우위로 쓸 수 없다.
- **기사성:** 조건부 단독 후보. “정점 사이 상호작용을 큐비트로 옮기면 QAOA가 달라지는 이유”라는 메커니즘·노이즈 절충 해설에 적합. 장기 우위 주장보다 표현 변경·고전 warm start·디코더를 분리하는 평가가 핵심.

## 2. Supervised Learning with Quantum Hamiltonian Embeddings

- [원문 v1](https://arxiv.org/html/2610.26833v1), [서지](https://arxiv.org/abs/2610.26833): Molteni 외, 2026-10-19 제출 프리프린트, 59쪽. §II–III의 이론과 §IV의 benchmark를 구분한다.
- **기전:** 학습자료를 매개변수화한 Hamiltonian에 넣고 근사 바닥상태로 분류. 얕은 encoding에서는 학습 후 고전 추론 가능(§III.2, §V). 암호 가정하의 어려운 인공 과제(§III.3)는 Fashion-MNIST 우위의 증명이 아니다.
- **실제 실험:** §IV, Fig. 1, Appendix J.1: **50 data qubits**, ibm_pittsburgh의 156-qubit Heron r2에서 dress/shirt 이진 분류. 800개 표본을 448/112/240 학습/검증/test로 분할하고 PCA 사용. QPU는 SKQD의 bitstring sampling만 담당; Hamiltonian 구성·부분공간 결합·투영·대각화·gradient·Adam은 고전 laptop 계산.
- **선별·성능:** 고전 iterative solver의 validation 결과로 data split·초기값 5개를 선별해 hardware 실행. 100-run 전체 비교에서는 RBF SVC 약 94.6%가 최고; n=50 고전 HE proxy 평균은 88.6%. 선별 hardware run은 경쟁력 있는 정확도를 보였으나 평균·실행시간·비용의 고전 우위를 입증하지 않았다(§IV.2, §V).
- **비용:** Appendix H.3/J.1: 80 epochs, 첫 epoch 13×25,000 shots, 이후 12×8,192 shots. 모두 이 스케줄이면 **run당 8,091,016 shots**라는 리뷰 산술값. 시간진화용 Pauli term 20,000+개를 240개로 절삭하나 투영은 전체 Hamiltonian 사용. pruning·고전 계산·선별 비용을 평가해야 한다.
- **기사성:** 높음. “양자 학습의 일을 바닥상태 탐색에 모으고 추론은 고전으로 돌린다”가 설명축. 독창성·범용성 조건, 바닥상태 근사의 난도와 실제 benchmark를 함께 다루는 비판적 리뷰 권장.

## 3. Enabling Deterministic Passive Quantum State Transfer with Giant Atoms

- [출판사](https://journals.aps.org/prxquantum/abstract/10.1103/6wcb-nj42): **PRX Quantum 7, 043013**, 2026-10-20 발행, DOI **10.1103/6wcb-nj42**. Diekmann과 공저자 9명, **총 10명**이며 Krimer는 저자가 아니다.
- **버전:** 초기 전문 대조는 [v2](https://arxiv.org/html/2605.12018v2)(2026-05-28). 재검수에서 [v3](https://arxiv.org/html/2605.12018v3)(2026-09-15) 초록·§III–IV·Eq.(16)·Fig.3–4를 확인했다. 전체 버전 차이와 출판 PDF의 행별 대조는 미실시.
- **실행:** 이론·수치 최적화 설계이며 새 장치 실험이 아니다. 여러 waveguide 결합점의 위치·강도가 간섭을 만들어, 방출 pulse가 시간반전 대칭에 가까워지도록 한다.
- **수치:** v3 §III, Fig.3, Eq.(16)도 `P₂,max=max |c₂(t)|²`, 수신 atom의 최대 여기확률로 정의한다. 단일 결합점 약 **54%**, 두 점 약 **87%**, 10개 이상에서 **99% 초과**라는 초록 수치는 유지된다. 본문은 약 10개에서 잔여오차 1%. process fidelity 실험으로 바꾸지 않는다.
- **조건:** Fig.3은 chiral coupling 가정의 점 수다. bidirectional waveguide에서 구조로 chirality를 구현하는 제안은 **2N개 physical legs**를 쓴다(§III 끝·§IV.2·Appendix A). 유한 전파지연·pulse 폭에 필적하는 emitter 크기, 무한점 완전전달과 유한점 근사를 구분한다. v3 §IV.2–5는 위치·결합강도·주파수 오차와 분산의 수치 robustness를 다룬다.
- **기사성:** 높음. “시간 제어를 공간 설계로 바꾸는 거대 원자 양자 링크”는 독자 질문과 과학적 장면이 선명하다. 완전전달 해석→유한점 근사→제조 오차라는 조건을 중심으로 기획 가능.

## 세 후보 안의 편집 우선순위

1. **Hamiltonian embedding:** AI Tech Review 독자와의 직접 연결, 이론·QPU·고전 부분을 나누는 설명 가치가 가장 크다. 단독 심층 리뷰 우선 검토.
2. **Giant atom:** 출판 완료, 고유한 물리적 아이디어와 시각화 적합성이 좋다. 독립 물리 리뷰 또는 후속 후보.
3. **Parity QAOA:** 실제 QPU 결과는 흥미롭지만 고전 warm start·디코딩·작은 문제의 고전 최적해 계산을 함께 설명해야 한다. 기법 비교 단신/심층 후보 보류가 적절하다.

우선순위는 이 세 논문 안에서의 리뷰 해석이며 오늘 DQB 전체 후보의 종합 순위가 아니다. 수치·상대 성능은 모두 저자 보고, shots 합계와 40정점→60 parity qubits만 명시한 식의 리뷰 산술이다.
