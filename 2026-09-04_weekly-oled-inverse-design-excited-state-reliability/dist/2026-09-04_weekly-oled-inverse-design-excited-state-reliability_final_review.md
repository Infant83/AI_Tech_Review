---
title: "다중 여기상태를 매끄럽게 학습하는 법: OLED 분자 역설계의 물리 표현과 검증 경계"
subtitle: "2026년 8월 28일-9월 3일 연구 동향: latent Hamiltonian, QED-GW/BSE, 불확실성 기반 선택, 반응 흐름과 양자 기준선"
type: final review
author: "Hyun-Jung Kim"
date created: 2026-09-04
date modified: 2026-09-04
status: checked
language: ko
canonical url: https://infant83.github.io/AI_Tech_Review/reviews/2026-09-04_weekly-oled-inverse-design-excited-state-reliability/
alternate ko url: https://infant83.github.io/AI_Tech_Review/reviews/2026-09-04_weekly-oled-inverse-design-excited-state-reliability/
alternate en url: https://infant83.github.io/AI_Tech_Review/reviews/2026-09-04_weekly-oled-inverse-design-excited-state-reliability/en/
alternate x-default url: https://infant83.github.io/AI_Tech_Review/reviews/2026-09-04_weekly-oled-inverse-design-excited-state-reliability/
social image url: https://infant83.github.io/AI_Tech_Review/reviews/2026-09-04_weekly-oled-inverse-design-excited-state-reliability/excited_state_reliability_hero-web.webp
tags:
  - OLED
  - molecular-inverse-design
  - excited-state-machine-learning
  - GW-BSE
  - uncertainty-quantification
  - reaction-prediction
  - quantum-annealing
  - VQE
---

# 다중 여기상태를 매끄럽게 학습하는 법: OLED 분자 역설계의 물리 표현과 검증 경계

2026년 8월 28일부터 9월 3일까지 공개되거나 의미 있게 개정된 문헌에서는 TADF 발광체나 PhOLED host를 직접 설계·검증한 새 논문을 찾지 못했다. 그렇다고 이번 주가 빈 주간은 아니다. OLED 역설계에 당장 필요한 것은 후보를 더 많이 만드는 생성기보다, 서로 섞이고 순서가 바뀌는 여러 여기상태를 어떻게 표현하고 어떤 검증으로 신뢰할지에 가깝다.

가장 먼저 읽을 논문은 Juergens 등의 LUSH다. 이 방법은 각 상태의 에너지를 서로 무관한 scalar로 회귀하지 않고, 잠재공간의 대칭 Hamiltonian을 학습한 뒤 대각화한다. 에너지뿐 아니라 oscillator strength와 상태 사이 관계를 하나의 operator 구조 안에 놓으려는 시도다. 이번 주의 불확실성 추정, 반응 경로 생성, cavity GW-BSE 논문도 같은 질문을 다른 층에서 건드린다. 예측값이 좋아 보이는가보다, 물리적 중간 표현과 검증 경계가 설계 의사결정을 견딜 수 있는가가 중요하다.

![다중 여기상태 에너지 곡면, 분자 환경, 반응 가능성, 불확실성 선택과 제한된 양자 구성요소를 표현한 개념 일러스트](excited_state_reliability_hero-web.webp)

*그림 1. 이번 리뷰의 개념 일러스트. 중앙은 결합된 다중 여기상태와 교차영역, 주변은 불확실성 기반 표본 선택·반응 제약·host 환경을 나타낸다. 오른쪽 끝 양자 요소는 이번 주 근거에서 보조 benchmark에 머문다는 경계를 반영한다. 분자, 파동함수와 회로 모티프는 개념 표현이며 특정 화학구조, 계산된 곡면, 측정 morphology 또는 실행 가능한 회로가 아니다.*

::: highlight 이번 리뷰의 판정
LUSH는 OLED 계산에서 S1, T1, Tn, oscillator strength와 향후 SOC 같은 연산자를 서로 연결된 대상으로 학습할 수 있는 설계 원리를 제공한다. 그러나 현재 실증은 singlet 중심 데이터와 random split에 머물며 TADF의 triplet·SOC·RISC와 host 환경을 검증하지 않았다. 가장 유용한 다음 단계는 작은 OLED 이성질체·conformer 세트에서 scalar multitask model과 latent Hamiltonian model을 같은 held-out 조건으로 비교하는 것이다.
:::

레이아웃을 검증한 영문 기술 브리프는 [PDF로 내려받을 수 있다](oled_inverse_design_weekly_brief_2026-09-04.pdf).

## 먼저 읽을 순서

1. **LUSH** - 다중 여기상태를 독립 scalar가 아닌 학습된 Hamiltonian의 고유값과 operator로 다룬다.
2. **QED-GW/BSE** - cavity가 quasiparticle과 exciton에 들어오는 항을 분해하지만, 실용 OLED cavity와는 결합세기가 크게 다르다.
3. **AdaptNTK** - 하나의 neural potential에서 uncertainty를 계산하고 중복이 적은 계산점을 고르는 active-learning 기준을 제시한다.
4. **MAELLE** - 전자 점유 변화의 discrete flow로 반응 결과와 기작 유사 경로를 함께 생성한다.
5. **HiPoly** - 조성·motif·원자 계층을 공유하는 예측·생성 구조를 MD 검증과 연결한다.
6. **LiFT** - 언어 model이 만든 trend prior를 3D flow matching에 조건으로 넣되, 합성성과 물성은 proxy로 평가한다.
7. **D-Wave t-VMC 연구** - annealer 동역학을 고전적으로 재현한 비용과 정확도를 제시해 양자 우위 주장에 필요한 기준선을 강화한다.
8. **torsion-space VQE** - 6 logical qubit와 실제 IBM QPU sampling을 보였지만 on-QPU VQE 최적화나 전자구조 계산은 아니다.

![이번 주 8편을 OLED 근접성과 실행 경계에 따라 배치한 근거 지도](evidence_map.svg)

*그림 2. 리뷰어가 구성한 정성적 근거 지도. 배치는 OLED workflow와의 근접성을 나타내며 성능 순위가 아니다. badge는 원 논문이 실제로 수행한 계산 환경을 표시한다. 이번 주 선정 자료는 모두 프리프린트이고, OLED를 직접 검증한 논문은 없었다.*

## 1. 직접 OLED·TADF·PhOLED 연구: 이번 주 선정 논문 없음

검색 범위 안에서 TADF 발광체, PhOLED host, host-dopant/exciplex, OLED 열화 또는 소자 수명을 직접 다루면서 새로 공개·개정된 신뢰할 만한 primary record는 없었다. 지난 8주 발송분 가운데 확인된 8월 21일과 28일 브리프의 논문도 반복 수록하지 않았다. 따라서 아래 8편은 모두 인접 방법론이다. 이 구분은 해당 연구의 품질이 낮다는 뜻이 아니라, OLED 성능에 대한 직접 증거로 읽으면 안 된다는 뜻이다.

## 2. [프리프린트] LUSH: 상태별 숫자 대신 매끄러운 다중상태 Hamiltonian을 학습한다

David Juergens, Martin Stöhr, Andreas E. Hillers-Bendtsen, O. Jonathan Fajen, Todd J. Martínez의 [*Latent unified smooth Hamiltonians for excited state chemistry*](https://arxiv.org/abs/2609.01871)은 2026년 9월 1일 arXiv에 게시됐다.

### [원 논문 결과]

LUSH는 원자번호와 Cartesian 좌표를 SE(3)-invariant message-passing network에 넣고, cross-attention으로 고정 크기 latent에 압축한다. state pair마다 Pairformer 표현을 만든 뒤 대칭인 잠재 Hamiltonian을 예측하고 대각화한다. 이 구조 덕분에 adiabatic energy를 직접 따로 회귀할 때 생길 수 있는 불연속을 줄이고, conical intersection 부근의 상태 결합을 표현한다. transition dipole과 oscillator strength도 같은 latent operator 틀에서 다룬다. nonadiabatic coupling은 Hellmann-Feynman 관계로 얻을 수 있다는 구성이다.

QM9의 134,000개 분자와 B3LYP/6-31G(2df,p) 라벨에서 약 5.95M parameter model이 Tesla V100 한 장으로 약 48시간 학습 후 대략 1 kcal/mol 수준에 접근했다. 보충자료의 약 7.05M parameter 설정은 energy MAE 0.059 eV, 즉 약 1.36 kcal/mol을 보고한다. QeMFi 실험은 9개 분자에 대해 CAM-B3LYP/def2-TZVP로 만든 135,000개 geometry를 사용했고, azobenzene 실험은 FOMO-hh-TDA-BHLYP/def2-SVP single point 780,745개를 사용했다. 상태공간 경계에서 잘린 spectrum이 target state를 오염시키지 않도록 관심 상태보다 최소 두 개 높은 상태를 buffer로 넣는다.

### [한계]

QeMFi는 90/10 random split, azobenzene은 99/1 random split이다. 새로운 scaffold나 torsion family로의 외삽을 검증한 분할이 아니다. azobenzene에서도 twisted·cis 영역의 표본이 적어 그 구간 오차가 커진다. 현재 실증은 OLED triplet manifold, SOC, RISC, solid-state host perturbation을 포함하지 않는다. 코드도 동료평가 승인 뒤 공개할 계획이라고 적혀 있어 현재 완전한 재현은 어렵다.

### [리뷰 제안]

OLED용으로는 S0/S1/T1/Tn을 함께 두고 상태 에너지, transition dipole, oscillator strength를 통합하며 SOC용 latent operator head를 추가하는 가설을 시험할 수 있다. 이는 LUSH 논문의 실증 결과가 아니다. singlet·triplet 혼합, spin symmetry와 phase convention을 어떻게 보존할지도 새로 정의해야 한다. 성공 여부는 random split MAE가 아니라 scaffold-held-out와 conformer-held-out에서 state-order swap과 이성질체 순위 오류가 줄어드는지로 판단해야 한다.

## 3. [프리프린트] QED-GW/BSE: cavity 효과를 quasiparticle과 exciton 항으로 분해한다

Soohaeng Yoo Willow 등 8명의 [*GW and Bethe-Salpeter Theory for Molecular Polaritons, Quasiparticles, and Excitons*](https://arxiv.org/abs/2609.00594)은 2026년 9월 1일 게시됐다.

### [원 논문 결과]

저자들은 dipole-gauge Pauli-Fierz Hamiltonian과 coherent-state QED-HF reference에서 출발해 QED-GW ionization potential/electron affinity와 static Bethe-Salpeter equation을 구성한다. cavity는 static dipole self-energy shift, screened interaction에 대한 DSE 보정, polariton pole로 들어간다. 네 hydride와 두 aromatic system을 benchmark했고, 비교 가능한 cavity-induced shift에서 QED-CCSD가 near-exact QED-DMRG와 1 meV 안에서 맞았다고 보고했다.

GW는 closed-shell 또는 unbound-anion 계에서 cavity-induced IP redshift를 크게 예측하는 경향을 보였다. EA shift는 거의 정량적으로 맞았지만 absolute EA까지 정확하다는 뜻은 아니다. 가장 낮은 excitation에 대한 cavity 효과는 조사한 분자 가운데 ammonia에서만 뚜렷했다. unbound anion의 exciton binding energy는 basis에 민감했다.

### [한계와 OLED 번역]

주요 계산의 λ=0.05 a.u.는 약 0.74 nm³, 한 변 약 0.9 nm 규모의 mode volume에 해당해 picocavity나 plasmonic nanogap 쪽에 가깝다. 110 nm diffraction-limited planar cavity에서는 single-molecule coupling이 대략 10^-4 수준이며, λ=0.05의 집단 결합을 내려면 약 2×10^5 molecules가 필요하다는 저자 추산이 있다. 따라서 이 결과를 일반 OLED microcavity의 단분자 효과로 옮길 수 없다.

OLED 연구에는 cavity 또는 dielectric environment가 IP, EA, optical gap, exciton binding을 각각 얼마나 움직이는지 기록하는 correction ledger로 유용하다. 다만 분자 한 개의 strong-coupling benchmark에서 amorphous ensemble·disorder·loss를 추론하지 말아야 한다. OmegaQMC 예제와 MOLMPS 구현은 공개돼 있다.

## 4. [프리프린트] AdaptNTK: 한 모델로 불확실성과 표본 중복을 함께 다룬다

Prajwal Ananth와 Shuwen Yue의 [*AdaptNTK: Adaptive Uncertainty Quantification and Active Learning for Neural Network Potentials*](https://arxiv.org/abs/2609.00488)은 2026년 8월 31일 게시됐다.

### [원 논문 결과]

AdaptNTK는 empirical neural tangent kernel feature 공간에서 regularized Mahalanobis distance를 uncertainty score로 사용한다. 새 표본이 들어올 때 Sherman-Morrison 갱신으로 uncertainty를 재계산하므로, sequential batch를 고르는 동안 model을 매번 재학습하지 않아도 된다. 이미 선택한 표본과 비슷한 후보의 점수가 줄어들어 batch redundancy를 억제한다.

rMD17 held-out 실험에서 uncertainty와 error의 Spearman 상관은 0.683±0.018, Pearson은 0.706±0.021이었다. 3-model ensemble의 AURCn 0.310±0.013과 비교해 AdaptNTK는 0.312±0.014였고, ENCE는 0.0125±0.0018이었다. rMD17와 Transition-1X active learning에서 낮은 force error와 transition-state 표본 선택을 보였으며, Transition-1X의 cycle당 시간은 ensemble보다 2.6배 빨랐다. 비교는 같은 MACE architecture, loss, split와 seed 조건에서 이뤄졌다.

### [한계와 OLED 번역]

이 결과는 ground-state force potential에 관한 것이지 excited-state energy·SOC·rate uncertainty가 아니다. OLED에서는 state crossing, oscillator strength, ΔEST와 SOC가 서로 다른 calibration을 가질 수 있다. 하나의 통합 score가 모든 target의 실패를 대신한다고 가정하면 안 된다.

우선 scalar multitask GNN과 latent Hamiltonian model 양쪽에서 NTK score를 계산하고, ensemble disagreement와 함께 비교할 수 있다. 새 TDDFT/TDA 계산점이 torsion·state-crossing·scaffold 공간에서 얼마나 다양하게 선택되는지, uncertainty bin별 실제 error가 맞는지를 봐야 한다.

## 5. [프리프린트 v2] MAELLE: 전자 점유 변화를 따라 반응을 생성한다

Nguyen Xuan-Vu, Octavian Susanu, Daniel Armstrong, Philippe Schwaller의 [*Mechanistic Reaction Prediction via Discrete Flow Matching on Graph-Structured Electron Occupation*](https://arxiv.org/abs/2608.27429)은 8월 27일 처음 올라왔고 28일 v2로 개정돼 이번 범위에 포함했다.

### [원 논문 결과]

MAELLE는 bond, nonbonding electron과 hydrogen site의 정수 점유를 graph state로 나타내고 continuous-time Markov chain 기반 discrete flow matching으로 바꾼다. edit-based mixture path와 optimal transport가 단계별 기작 라벨 없이도 mechanism-like electron move를 만든다.

USPTO-480K에서 top-1 87.2%, top-3 93.0%, top-5 93.9%, top-10 94.6%를 보고했다. Graph2SMILES의 top-1 90.3%, NERF의 90.7%보다 top-1은 낮다. FlowER test의 bond-forming step 37,583개에서 64 trajectories를 합친 coverage는 63.0%였고, persistent edit coverage는 99.6%, transient edit coverage는 29.6%였다. directional agreement는 전체 78.2%, correct prediction 84.6%, top-1 correct 89.0%였다. LLM judge의 plausibility coverage는 약 81.1±0.1%다.

### [한계와 OLED 번역]

elementary step label 없이 만든 경로가 실제 기작임을 증명하지 않는다. LLM plausibility judge는 주관적이며, product prediction 정확도와 실제 실험 route 성공률도 다르다. 저자들은 mass/reaction-type OOD에서 transformation model이 de novo model보다 강하다고 보고했다.

OLED 후보에는 MAELLE형 점수를 hard synthesizability oracle이 아니라 반응 가능성 veto와 reranking 신호로 쓰는 편이 안전하다. Buchwald-Hartwig, SNAr, borylation, ligand formation 등 실제 OLED 합성 family에서 route success와 비교해야 하며, commercial availability와 protecting-group·purification 비용도 별도로 남겨야 한다.

## 6. [프리프린트] HiPoly와 LiFT: 구조 생성보다 조건 표현과 검증이 먼저다

Ge Sun 등 10명의 [*HiPoly: a hierarchical polymer-native AI framework for property prediction and generative design*](https://arxiv.org/abs/2609.02746)은 2026년 9월 2일 게시됐다. G2RINS는 monomer, motif, atom의 세 graph level과 stochastic inter-monomer connectivity, mole fraction, molecular weight를 함께 나타낸다. 약 6,000개 unlabeled polymer와 약 600개 MD-labeled polymer에서 공유 latent space를 학습했고, fivefold CV에서 Tg R² 0.803±0.147, density R² 0.945±0.024를 보고했다. composition aggregation을 제거하면 Tg R²가 0.291로 떨어졌다. 25,000개 PFAS-free 후보를 생성하고 상위 후보를 OPLS 기반 MD로 다시 평가했다.

이 MD는 실험 검증이 아니며 학습 데이터와 같은 force-field·simulation layer에 남는다. NVT 600 K, NPT 600→300 K 50 ns, NVT 300 K 20 ns 조건도 OLED small-molecule glass나 host-dopant film의 검증이 아니다. 그러나 molecule-conformer-dimer-mixture-morphology를 계층으로 표현해야 한다는 아이디어는 host 조성과 packing을 학습하는 데 유용하다.

Tianyu Gao 등 8명의 [*Language-Informed Flow Matching for Trend-Guided Structure-Based 3D Molecular Generation*](https://arxiv.org/abs/2608.31009)은 2026년 8월 31일 게시됐고 Findings of EMNLP 2026 채택을 명시한다. LiFT는 LLM agent가 target-aware SMILES 조건을 만들고, frozen chemical foundation model의 embedding을 3D ODE flow에 주입한다. CrossDocked2020에서 no-reference 설정의 QED가 최대 0.757, SA score 2.659, RDKit/REOS 통과율 71% 이상, PoseBusters 최대 73.56%로 보고됐다.

이 수치는 protein-pocket ligand 생성 지표다. SA score와 rule filter는 합성 성공 증명이 아니며, 언어 prior도 정량 물성 oracle이 아니다. OLED로 옮길 때는 pocket을 host-dopant packing 또는 aggregate context로 바꾸고, LLM 조건화가 단순 property token이나 latent control보다 scaffold-held-out DFT blind set에서 실제로 나은지 비교해야 한다.

## 7. 양자 방법의 실제 경계: annealer 고전 모사와 warm-start QPU sampling

### 7.1 [프리프린트] D-Wave 실험을 고전 t-VMC로 어디까지 재현할 수 있는가

Roeland Wiersema의 [*Numerical simulation of D-Wave's quantum advantage experiment with time-dependent variational Monte Carlo*](https://arxiv.org/abs/2609.01719)은 2026년 9월 1일 게시됐다. correlator state를 쓴 classical time-dependent variational Monte Carlo로 D-Wave Advantage2의 frustrated transverse-field Ising annealing을 2D cylinder, 3D dimer, diamond와 biclique geometry에서 모사한다. anneal time은 7 ns와 20 ns다.

N=72 biclique의 final two-spin correlation은 QPU 결과와 약 7.6% 오차로 가까웠다. N=128 diamond의 TDVP residual은 4.27×10^-3로 안정적이었지만 exact ground truth는 없다. N=72 biclique 한 추정에는 4,194,304 samples가 필요했고, GPU 수백 시간이 든 반면 QPU 실행은 seconds였다. 저자는 더 큰 계에서 sample과 sweep이 늘어난다는 점을 인정하며 강한 scalability 주장을 하지 않는다. parallel tempering, blurred sampling, importance-weighted ODE solver를 사용한 코드는 공개돼 있다.

이 연구는 분자 QUBO를 풀지 않았고 OLED 후보를 고르지 않았다. 그러나 annealer 결과를 평가할 때 “고전적으로 가능하다/불가능하다”가 아니라 correlation error, total samples, GPU-hours, preprocessing과 QPU access time을 같은 장부에 넣어야 한다는 좋은 기준선이다. chemistry-relevant QUBO라면 exact solver, simulated annealing, tensor/network Monte Carlo와 실제 QPU를 동일 instance·budget으로 비교해야 한다.

### 7.2 [프리프린트] logarithmic torsion VQE의 6-qubit 회로와 600건 QPU job

Fabio Cumbo 등 7명의 [*Logarithmic-scale variational quantum eigensolver for off-lattice protein structure prediction in continuous torsional angle space*](https://arxiv.org/abs/2609.02113)은 2026년 9월 2일 게시됐다. torsional degree of freedom을 phase로 encoding해 qubit 수를 O(log2 N)으로 줄이고 EfficientSU2 ansatz와 multi-stage relaxation을 사용한다. statevector에서는 phase를 읽지만 hardware에서는 computational-basis 확률의 empirical CDF로 구조를 복원한다.

classical statevector optimization에서 chignolin은 retained snapshot Cα RMSD 0.623 Å, final 1.199 Å, Trp-cage는 snapshot 2.501 Å, final 3.512 Å를 보고했다. hardware 실험은 IBM Heron R2 156-qubit `ibm_cleveland`와 Nighthawk R1 120-qubit `ibm_miami`에서 각각 300 jobs, job당 8192 shots를 사용했다. 두 장치 모두 같은 6-logical-qubit 회로를 돌렸고, `ibm_miami` 회로는 정확히 60 CZ였지만 분포와 job runtime은 더 나빴다. best RMSD는 Cleveland 1.758 Å, Miami 1.782 Å였으며 2 Å 아래 native-like sample은 각각 88/300과 45/300이었다.

중요한 경계가 있다. QPU에서는 simulation에서 최적화한 parameter로 warm start해 sampling했으며, on-QPU iterative VQE를 수행하지 않았다. 확률 CDF decoder는 state space가 커질수록 많은 shots가 필요하다는 한계를 저자도 인정한다. qubit 절약이 circuit depth·sampling·classical reconstruction 비용을 없애는 것은 아니다. 단백질 conformer energy를 다룬 것이며 electronic-structure VQE도 아니다.

OLED에서는 6-12개의 torsion을 가진 donor-acceptor conformer 탐색을 같은 표현으로 시험할 수 있지만, classical conformer search와 wall time·energy/ranking을 비교해야 한다. 전자 상관과 excited-state energy를 계산했다는 표현은 쓰지 않는다.

## 8. 이번 주 실행안: LUSH-lite와 uncertainty acquisition을 작은 OLED 세트에서 비교한다

![후보 생성, 반응 gate, 다중상태 model, 불확실성 선택과 TDDFT 라벨을 연결한 제안 workflow](proposed_workflow.svg)

*그림 3. 이번 문헌을 토대로 리뷰어가 제안한 검증 workflow. 어느 원 논문도 이 OLED pipeline을 end-to-end로 실행하지 않았다. LUSH-inspired SOC head와 OLED 적용은 후속 연구 가설이다.*

12-24개 분자 또는 이성질체 family로 시작한다. 각 분자에서 여러 torsion geometry를 만들고 동일한 TDA/TDDFT 설정으로 S1, T1, T2/T3, oscillator strength, NTO 기반 CT/LE descriptor를 계산한다. 소수 calibration geometry에는 S1-Tn SOC를 추가한다.

비교 모델은 두 개면 충분하다. Model A는 각 target을 독립적으로 예측하는 scalar multitask GNN이다. Model B는 4-6 state symmetric latent Hamiltonian과 transition-operator head를 가지며 관심 상태 위에 두 개 buffer state를 둔다. SOC head는 별도 proposed ablation으로 취급한다. split은 random이 아니라 leave-one-scaffold-out와 torsion-held-out을 함께 쓴다.

active-learning round마다 AdaptNTK와 3-model ensemble이 각각 고른 20-40개 geometry를 새로 계산한다. energy/gap MAE만 보지 말고 state-order swap, oscillator-strength error, 이성질체 순위, uncertainty calibration, selected-batch diversity, DFT wall time을 기록한다. Model B가 더 복잡하다는 이유로 채택하지 않는다. 고정 기준선보다 catastrophic ranking error를 줄이고, 그 개선이 새로운 scaffold에서도 유지될 때만 다음 규모로 확장한다.

## 9. 이번 주에 새 근거가 없었던 영역

- TADF emitter, PhOLED host, host-dopant/exciplex의 직접 설계·소자 검증
- OLED 안정성·열화와 operational lifetime
- SELFIES-specific 합성 제약, CRBM 또는 Boltzmann-machine molecular sampling
- chemistry-relevant D-Wave/QUBO 또는 QAOA와 경쟁력 있는 고전 기준선
- OLED active space의 electronic-structure VQE와 resource estimate
- OLED 규모에서 입증된 quantum advantage

이 목록은 해당 분야 전체에 연구가 없다는 뜻이 아니다. 이번 7일 범위와 선정 기준 안에서 반복 없이 검토할 새 primary record가 없었다는 뜻이다.

## 결론

이번 주의 신호는 생성 방법의 수가 아니라 상태 표현의 구조에서 나왔다. LUSH는 서로 교차하고 혼합되는 여기상태를 한 latent Hamiltonian의 spectrum으로 다루며, AdaptNTK는 어느 geometry를 추가 계산할지 정량화한다. MAELLE와 계층형 생성 연구는 후보가 합성·조성·환경 제약을 통과해야 한다는 사실을 보완한다.

동시에 증거 경계도 분명하다. cavity QED benchmark의 강한 단분자 결합은 일반 OLED microcavity 조건이 아니고, D-Wave 논문은 고전 GPU simulation이며, torsion VQE의 hardware 결과는 warm-start sampling이다. 어느 것도 TADF·PhOLED 분자의 양자 우위나 생산 workflow를 입증하지 않았다.

가장 값싼 다음 실험은 작은 분자 세트에서 scalar label과 structured operator representation을 같은 분할로 비교하는 것이다. 이 실험이 state ordering과 이성질체 ranking의 실패를 줄일 때, OLED 역설계는 더 많은 후보를 만드는 단계를 넘어 여러 여기상태의 관계를 신뢰할 수 있게 학습하는 단계로 나아갈 수 있다.

## References

1. D. Juergens, M. Stöhr, A. E. Hillers-Bendtsen, O. J. Fajen, T. J. Martínez, [“Latent unified smooth Hamiltonians for excited state chemistry,” arXiv:2609.01871v1 (1 September 2026)](https://arxiv.org/abs/2609.01871). **프리프린트.**
2. S. Y. Willow, G. B. Sim, T. H. Park, T. I. Kim, D. C. Yang, M. Matoušek, J. Brabec, L. Veis, C. W. Myung, [“GW and Bethe-Salpeter Theory for Molecular Polaritons, Quasiparticles, and Excitons,” arXiv:2609.00594v1 (1 September 2026)](https://arxiv.org/abs/2609.00594). **프리프린트.**
3. P. Ananth, S. Yue, [“AdaptNTK: Adaptive Uncertainty Quantification and Active Learning for Neural Network Potentials,” arXiv:2609.00488v1 (31 August 2026)](https://arxiv.org/abs/2609.00488). **프리프린트.**
4. N. Xuan-Vu, O. Susanu, D. Armstrong, P. Schwaller, [“Mechanistic Reaction Prediction via Discrete Flow Matching on Graph-Structured Electron Occupation,” arXiv:2608.27429v2 (28 August 2026)](https://arxiv.org/abs/2608.27429). **프리프린트 v2.**
5. G. Sun, G. Zaldivar, Y. Tian, G. Perez Lemus, J. Park, D. Safarian, M. Han, J. J. de Pablo, [“HiPoly: a hierarchical polymer-native AI framework for property prediction and generative design,” arXiv:2609.02746v1 (2 September 2026)](https://arxiv.org/abs/2609.02746). **프리프린트.**
6. T. Gao, Z. Su, J. Li, W. Gao, Z. Ying, Z. Zhao, F. Zhang, Y. Wei, [“Language-Informed Flow Matching for Trend-Guided Structure-Based 3D Molecular Generation,” arXiv:2608.31009v1 (31 August 2026)](https://arxiv.org/abs/2608.31009). **프리프린트; Findings of EMNLP 2026 채택 표기.**
7. R. Wiersema, [“Numerical simulation of D-Wave's quantum advantage experiment with time-dependent variational Monte Carlo,” arXiv:2609.01719v1 (1 September 2026)](https://arxiv.org/abs/2609.01719). **프리프린트; 고전 GPU simulation.**
8. F. Cumbo, B. Raubenolt, V. Puram, N. Katzenmeyer, J. Joshi, D. Blankenberg, [“Logarithmic-scale variational quantum eigensolver for off-lattice protein structure prediction in continuous torsional angle space,” arXiv:2609.02113v1 (2 September 2026)](https://arxiv.org/abs/2609.02113). **프리프린트; 실제 QPU sampling, on-QPU optimization 아님.**

---

작성정보. 작성자: 김현중. AI 보조: OpenAI Codex Work Mode. 검증 기준일: 2026년 9월 4일. 수치와 방법은 각 원문이 보고한 값이며, OLED workflow 번역, LUSH-inspired SOC head와 이번 주 실행안은 리뷰 제안이다. 선정된 8편은 모두 프리프린트다. 직접 OLED 논문이 없다는 판정과 양자 실행 위치를 원문 범위 안에서 분리해 기록했다.
