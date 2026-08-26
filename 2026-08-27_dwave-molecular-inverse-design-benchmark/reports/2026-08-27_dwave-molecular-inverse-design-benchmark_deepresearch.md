---
title: "D-Wave 분자 역설계 벤치마크 - Deep Research"
date: 2026-08-27
slug: dwave-molecular-inverse-design-benchmark
language: ko
status: checked-deepresearch
---

# D-Wave 분자 역설계 벤치마크 - Deep Research

## 1. Research Question

분자 역설계에서는 원하는 물성을 가진 후보를 만드는 일과 다음 고비용 계산에 보낼 후보를 고르는 일이 분리됩니다. 후보마다 DFT를 수행할 수 있다면 선택 최적화가 필요하지 않습니다. 계산 예산이 제한되면 목표 적합성, 불확실성, novelty, 배치 다양성을 동시에 고려해야 합니다.

이번 실험은 shortlist 18개에서 세 후보를 고르는 acquisition problem을 QUBO로 만들었습니다. 같은 frozen BQM을 independent exact search, Ocean ExactSolver, classical simulated annealing, D-Wave QPU로 풀고, exact와 QPU가 선택한 후보를 PySCF로 계산했습니다. 평가 질문은 다음 네 가지입니다.

1. 오픈소스 molecular ML과 생성 모델이 실제 후보 pool을 만들 수 있는가?
2. readable acquisition objective와 BQM energy가 모든 작은-instance 검증에서 일치하는가?
3. 한 번의 QPU submission이 exact reference와 어떤 차이를 보이는가?
4. 다음 단계의 live active-learning bake-off를 설계할 만큼 provenance와 baseline이 갖춰졌는가?

## 2. Evidence Architecture

이번 결과는 세 종류의 증거로 나눕니다.

| Evidence layer | 계산 | 판정 |
| --- | --- | --- |
| Executed pipeline | surrogate training, proposal, filtering, QUBO build, exact/SA/QPU solve, PySCF 6 jobs | reproduced |
| Policy replay | 고정 QM9 pool에서 hidden precomputed label을 공개 | proxy |
| Proposed extension | generated molecules의 DFT label을 누적하고 재학습·재생성 | not executed |

이 구분은 발표자료에서도 유지해야 합니다. Detailed infographic은 executed block을 실선으로, live loop를 점선과 PROPOSED label로 표시합니다.

## 3. Dataset and Target

QM9 derived dataset 5,000개를 train 4,058개, validation 511개, test 431개로 분리했습니다. Target은 QM9의 precomputed HOMO–LUMO orbital gap을 eV로 변환한 값입니다.

[QM9 original collection](https://doi.org/10.6084/m9.figshare.c.978904.v5)은 약 13만 개의 small organic molecule과 양자화학 property를 제공합니다. 이번 결과는 전체 QM9 benchmark를 재현한 기록이 아닙니다. 화학 규칙을 통과한 결정론적 5,000개 subset과 고정 split의 smoke benchmark입니다.

## 4. Surrogate Models

같은 split에서 두 모델을 비교했습니다.

| Model | MAE | RMSE | R² | 역할 |
| --- | ---: | ---: | ---: | --- |
| Chemprop D-MPNN ensemble | 0.5308 eV | 0.6882 eV | 0.7547 | 구조 기반 external scorer와 ensemble spread proxy |
| ExtraTrees / Morgan | 0.4743 eV | 0.6854 eV | 0.7567 | 강한 classical baseline |

[Chemprop](https://chemprop.readthedocs.io/en/main/index.html)은 message-passing molecular property model을 제공합니다. 이번 held-out 결과에서는 ExtraTrees의 MAE가 0.0565 eV 낮았습니다. GNN 계열이 classical fingerprint model보다 우수하다는 결론은 지원되지 않습니다.

두 Chemprop member의 generated-candidate prediction spread는 약 9e-6–0.00275 eV였습니다. Calibration을 수행하지 않았고 범위도 매우 작습니다. QUBO uncertainty reward는 calibrated epistemic uncertainty가 아니라 탐색용 proxy입니다.

## 5. Candidate Generation

세 proposal mechanism을 실제로 실행했습니다.

1. Chemprop-scored SELFIES mutation
2. autoregressive SELFIES GRU decoder
3. classical SELFIES RBM

[SELFIES reference implementation](https://github.com/the-matter-lab/selfies)은 molecular string generation에 사용할 수 있는 representation을 제공합니다. SELFIES decoding이 성공하더라도 안정성, 합성 가능성, 독성, 원하는 excited-state property는 별도 검증이 필요합니다.

각 경로는 30개 proposal을 반환했습니다. 모든 경로에 RDKit parsing과 canonicalization, CHONF 원소 제한, 최대 9 heavy atoms, neutral closed shell, deduplication을 적용했습니다. Governed union에 기여한 unique candidate는 11개, 8개, 11개로 총 30개였습니다.

Raw proposal stream의 rejection counter는 radical 41개, heavy-atom limit 초과 15개, unsupported element 3개, non-neutral 1개였습니다. 이 수치는 생성 모델의 확률 분포를 완전히 평가한 benchmark가 아닙니다. 공통 governance filter가 proposal stream을 어떻게 정리했는지 보여줍니다.

“GNN-guided” path는 GNN decoder가 아닙니다. Chemprop으로 SELFIES mutation을 점수화한 경로입니다. RBM은 quantum Boltzmann machine이 아닌 classical contrastive-divergence model입니다.

## 6. Acquisition QUBO

### 6.1 Decision Variable

후보 i가 batch에 선택되면 x_i = 1, 선택되지 않으면 x_i = 0입니다. Shortlist에는 18개 후보가 있고, batch size k는 3입니다.

### 6.2 Readable Objective

목표 6.0 eV와의 예측 차이, model-spread proxy, novelty, pair similarity, 정확히 세 개를 고르는 조건을 하나의 minimization score로 구성했습니다.

~~~text
target_loss = sum_i target_weight
                    * ((predicted_gap_i - target_gap) / gap_scale)^2
                    * x_i

uncertainty_reward = sum_i uncertainty_weight
                           * (predicted_std_i / gap_scale)
                           * x_i

novelty_reward = sum_i novelty_weight
                       * novelty_i
                       * x_i

similarity_penalty = sum_(i < j) similarity_weight
                                  * tanimoto_i_j
                                  * x_i * x_j

cardinality_penalty = cardinality_weight
                      * (sum_i x_i - batch_size)^2

acquisition_score = target_loss
                  - uncertainty_reward
                  - novelty_reward
                  + similarity_penalty
                  + cardinality_penalty
~~~

이 식에서 target loss, uncertainty reward, novelty reward는 linear bias에 기여합니다. Similarity와 cardinality expansion은 pairwise quadratic bias에 기여합니다. Cardinality expansion은 linear bias, quadratic bias, constant offset을 함께 만듭니다.

[D-Wave QUBO documentation](https://docs.dwavequantum.com/en/latest/quantum_research/qubo_ising.html)은 0/1 variable의 linear term과 quadratic interaction으로 minimization problem을 표현합니다. Frozen BQM에는 18 variables와 가능한 모든 pair에 해당하는 153 interactions가 있었습니다.

### 6.3 Verification

Readable objective와 BQM energy를 같은 assignment에 넣어 비교했습니다. Independent combination search, Ocean ExactSolver, classical simulated annealing은 같은 batch와 best energy를 찾았습니다.

| Solver | Best energy | Exact gap | Result |
| --- | ---: | ---: | --- |
| independent combination search | -0.480789127750 | 0 | reference |
| Ocean ExactSolver | -0.480789127750 | 0 | reference match |
| classical simulated annealing | -0.480789 수준 | 약 0 | same batch |

이 검증은 QPU submission 전에 sign, coefficient, cardinality, decoding convention을 확인하는 안전장치입니다.

## 7. One D-Wave QPU Submission

같은 BQM을 D-Wave QPU에 100 reads로 한 번 제출했습니다. Recorded embedding은 18 logical variable을 46 physical qubit으로 매핑했습니다. Occurrence-weighted mean chain-break fraction은 0.01333이었습니다.

[EmbeddingComposite.sample documentation](https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/generated/dwave.system.composites.EmbeddingComposite.sample.html)은 logical problem을 QPU topology에 맞게 minor embedding하고 chain-break 정보를 반환하는 경로를 설명합니다.

| Metric | Exact reference | D-Wave QPU |
| --- | ---: | ---: |
| Best acquisition energy | -0.480789 | -0.434455 |
| Gap to exact | 0 | +0.046334 |
| Selected batch | 58d4, b58e, b917 | 1727, 58d4, 7768 |
| Reads | n/a | 100 |

QPU sample은 exact optimum을 재현하지 못했습니다. Recorded client wall time은 2.087초였지만 exact, SA, QPU의 wall time은 서로 다른 실행 경로와 queue·client overhead를 포함합니다. 이 값을 speedup 자료로 사용하지 않습니다.

Archive에는 실행 timestamp, submission-time Python/Ocean version, project source hash, solver timing field unit을 고정한 별도 configuration record가 없습니다. [D-Wave solver properties documentation](https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html)을 기준으로 다음 campaign의 metadata schema를 보강해야 합니다. 현재 환경 값을 과거 실행에 대입하지 않습니다.

## 8. PySCF Validation

QPU-selected batch와 independent exact batch에 각각 세 건의 [PySCF DFT](https://pyscf.org/user/dft.html)를 실행했습니다. 두 배치에 공통으로 들어간 한 분자도 각각 실행했으므로 총 6 jobs, 5 unique molecules입니다. 모든 job이 수렴했습니다.

~~~text
geometry = RDKit ETKDGv3 embedding + MMFF94s optimization
calculation = single point
functional = B3LYP
basis = 6-31G(2df,p)
grid level = 3
SCF convergence tolerance = 1e-8
maximum SCF cycles = 100
~~~

| Batch | Converged | Mean error from 6.0 eV | ML–DFT MAE | Recorded container wall time |
| --- | ---: | ---: | ---: | ---: |
| independent exact | 3/3 | 0.620 eV | 0.580 eV | 92.592 s |
| D-Wave QPU | 3/3 | 0.761 eV | 0.730 eV | 177.258 s |

Exact batch의 mean target error가 0.141 eV 낮았습니다. QPU batch의 N#CC=C1CC=NC1O는 ML 5.8763 eV, PySCF 5.8808 eV였고 target error는 0.1192 eV였습니다. 이번 스냅샷의 best single candidate입니다. Exact batch의 best target error는 0.2994 eV였습니다.

Batch mean과 best single hit는 서로 다른 평가량입니다. 배치당 세 분자라는 작은 표본에서 optimizer의 일반 성능을 결론 내릴 수 없습니다.

PySCF 값은 fixed force-field geometry의 Kohn–Sham HOMO–LUMO orbital gap입니다. Optical excitation은 [PySCF TDDFT](https://pyscf.org/user/tddft.html) 같은 excited-state method가 필요합니다. Geometry optimization, wavefunction stability, vibrational analysis, synthetic accessibility, toxicity, experiment도 이번 계산 범위 밖입니다.

## 9. Fixed-Pool Hidden-Label Replay

[Active learning in materials science](https://doi.org/10.1038/s41524-019-0153-8)는 surrogate, acquisition, 고비용 oracle을 반복하는 구조를 정리합니다. 이번 프로젝트는 live generated-space loop 전에 fixed QM9 pool에서 acquisition implementation을 점검했습니다. 이 replay는 앞선 분자 스냅샷의 6.0 eV가 아니라 별도의 4.0 eV target을 사용했습니다.

세 paired seed에서 40 labels로 시작해 batch size 3으로 네 번 갱신했습니다. Final budget 52 labels의 mean best target error는 다음과 같습니다.

| Policy | Mean best target error |
| --- | ---: |
| random | 0.2813 eV |
| greedy ExtraTrees | 0.1298 eV |
| uncertainty-aware exact | 0.1261 eV |
| uncertainty-aware QUBO / classical SA | 0.1261 eV |

QUBO/classical SA는 recorded 12 acquisitions 모두 exact batch와 일치했습니다. 이 결과는 QUBO mapping과 SA decoding이 fixed-pool setting에서 작동한다는 증거입니다.

Replay에서 실행한 새 DFT는 0건, QPU call은 0회, generated-space expansion은 0회입니다. QPU/exact batch에서 얻은 여섯 DFT label도 training set에 아직 추가되지 않았습니다.

## 10. What the Snapshot Establishes

### Reproduced

- QM9 5,000개 subset의 두 surrogate benchmark
- 세 proposal mechanism과 공통 chemical governance
- 18-variable, 153-interaction acquisition BQM
- readable objective와 BQM energy의 검증
- independent exact, Ocean ExactSolver, classical SA
- 한 번의 100-read D-Wave QPU submission
- exact·QPU batch의 PySCF single-point DFT 6 jobs

### Proxy

- fixed-pool, precomputed-label, 3-seed replay

### Not Established

- generated-molecule surrogate calibration
- stable or synthetically accessible molecule discovery
- optical gap 또는 experimental property
- persistent generated-space active learning
- like-for-like end-to-end speedup
- quantum advantage

## 11. PROPOSED Live Active-Learning Experiment

다음 실험에서는 proposal, acquisition, DFT, retraining을 여러 round 반복합니다. 각 candidate와 계산 결과는 persistent ledger에 보존합니다.

~~~text
initial labeled set
  -> fit surrogate
  -> generate and govern new candidates
  -> score target, uncertainty, novelty, diversity
  -> select batch with policy under test
  -> run the same DFT oracle
  -> append labels and provenance
  -> refit and repeat
~~~

비교 policy는 최소 네 가지입니다.

1. greedy ML
2. independent exact acquisition
3. classical simulated annealing
4. D-Wave QPU

GNN generator, autoregressive decoder, RBM generator는 같은 chemical governance와 DFT budget을 적용해야 합니다. Candidate generation time, model training time, QUBO build time, queue time, sampling time, decoding time, DFT time을 따로 기록합니다.

## 12. Matched Comparison and Stop Gate

| Dimension | Matched rule |
| --- | --- |
| Initial knowledge | 같은 labeled set과 split |
| Candidate opportunity | 같은 candidate pool 또는 사전 정의된 동등 sampling budget |
| Acquisition | 같은 batch size와 round 수 |
| Oracle | 같은 DFT method, geometry policy, convergence rule |
| Compute accounting | fit, generate, build, queue, sample, DFT를 분리 |
| Quality | best target error, batch mean, diversity, validity, DFT success rate |
| Reproducibility | seeds, source hash, software versions, solver metadata |

Go 기준은 QPU policy가 strong classical champion과 같은 label budget에서 반복적으로 추가 정보를 제공하고, 비용·시간을 포함한 운영 목적에 맞을 때입니다. Scale 기준은 여러 seed와 larger shortlist에서도 효과가 유지되는 경우입니다. Stop 기준은 exact/classical SA와 비교해 hit quality나 diversity가 개선되지 않거나 queue·sampling overhead가 목적에 맞지 않는 경우입니다.

## 13. Source Index

- [QM9 original collection, Figshare](https://doi.org/10.6084/m9.figshare.c.978904.v5)
- [PyTorch Geometric QM9 documentation](https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.datasets.QM9.html)
- [Chemprop documentation](https://chemprop.readthedocs.io/en/main/index.html)
- [SELFIES reference implementation](https://github.com/the-matter-lab/selfies)
- [D-Wave: QUBOs and Ising Models](https://docs.dwavequantum.com/en/latest/quantum_research/qubo_ising.html)
- [D-Wave: EmbeddingComposite.sample](https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/generated/dwave.system.composites.EmbeddingComposite.sample.html)
- [D-Wave: General QPU Solver Properties](https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html)
- [PySCF: Density Functional Theory](https://pyscf.org/user/dft.html)
- [PySCF: Time-dependent Hartree-Fock and DFT](https://pyscf.org/user/tddft.html)
- [Lookman et al., Active learning in materials science](https://doi.org/10.1038/s41524-019-0153-8)
