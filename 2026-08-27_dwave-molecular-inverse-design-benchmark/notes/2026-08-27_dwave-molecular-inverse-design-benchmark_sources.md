---
title: "D-Wave 분자 역설계 벤치마크 - Source Note"
date: 2026-08-27
slug: dwave-molecular-inverse-design-benchmark
language: ko
status: checked-source-note
---

# D-Wave 분자 역설계 벤치마크 - Source Note

## Scope

이 패키지는 QM9 기반 분자 물성 예측, 세 가지 후보 생성 경로, QUBO 배치 선택, 한 번의 D-Wave QPU 제출, PySCF single-point DFT, 고정 라벨 replay를 하나의 계산 스냅샷으로 정리합니다.

검토 질문은 다음과 같습니다.

- 실제로 실행된 계산 단계는 어디까지인가?
- D-Wave QPU는 분자 계산과 후보 선택 가운데 어느 일을 수행했는가?
- exact search, classical simulated annealing, QPU가 같은 BQM에서 어떤 결과를 냈는가?
- QPU와 exact가 선택한 후보를 PySCF로 계산했을 때 어떤 차이가 관찰됐는가?
- 고정 QM9 replay와 앞으로 실행할 live active-learning loop를 어떻게 구분해야 하는가?

## Public Evidence Package

| 자료 | 상태 | 용도 |
| --- | --- | --- |
| [최종 리뷰](../reports/2026-08-27_dwave-molecular-inverse-design-benchmark_final_review.md) | checked | 독자용 계산 설명과 claim boundary |
| [계산 결과표](../artifacts/final_review/data/benchmark_results.csv) | checked aggregate | 슬라이드와 인포그래픽에 쓰는 공개 정량 앵커 |
| [Figure manifest](../artifacts/final_review/figure_manifest.md) | checked | 각 그림의 제작 경로, 근거, 공개 사용 범위 |
| [상세 인포그래픽](../artifacts/final_review/figures/molecular_inverse_design_infographic.svg) | checked deterministic SVG | 실행된 계산과 제안된 live loop를 구분한 전체 구조 |
| [생성형 hero](../artifacts/final_review/figures/molecular_inverse_design_hero.png) | checked illustration | 주제형 표지 이미지. 실제 장비나 계산 결과 화면이 아님 |
| [예측 모델 비교](../artifacts/final_review/figures/02_qm9_surrogate_parity.png) | checked chart | 동일 test split의 Chemprop·ExtraTrees 예측 비교 |
| [생성 경로 비교](../artifacts/final_review/figures/03_generator_metrics.png) | checked chart | 세 proposal mechanism과 공통 필터 결과 |
| [획득 최적화 비교](../artifacts/final_review/figures/04_acquisition_comparison.png) | checked chart | exact·classical SA·QPU의 energy gap과 기록 wall time |
| [QPU 배치 DFT](../artifacts/final_review/figures/05_dft_molecule_validation.png) | checked chart | QPU-selected 세 후보의 ML 예측과 PySCF 결과 |
| [고정 라벨 replay](../artifacts/final_review/figures/06_qm9_replay_convergence.png) | checked chart | random·greedy·exact·QUBO/SA의 고정 pool 비교 |
| [Exact 대 QPU DFT 배치](../artifacts/final_review/figures/07_exact_vs_qpu_dft_batch.png) | checked chart | 배치 평균과 단일 best hit의 차이 |

공개 패키지는 계산 결과의 aggregate와 검토된 figure를 포함합니다. upstream 실험의 raw QM9 mirror와 credential, account 정보, private solver metadata는 포함하지 않습니다.

## Executed Result Ledger

| 계산 층 | 확인된 수치 | Evidence state | 해석 범위 |
| --- | --- | --- | --- |
| QM9 derived dataset | 5,000 molecules; train 4,058, validation 511, test 431 | reproduced | 고정 split의 orbital-gap benchmark |
| Chemprop D-MPNN ensemble | MAE 0.5308 eV; RMSE 0.6882 eV; R² 0.7547 | reproduced | held-out QM9 성능 |
| ExtraTrees / Morgan | MAE 0.4743 eV; RMSE 0.6854 eV; R² 0.7567 | reproduced | 같은 split의 classical baseline |
| Candidate generation | guided SELFIES 11, SELFIES GRU 8, classical SELFIES RBM 11; union 30 | reproduced | 공통 화학 규칙을 통과한 unique contribution |
| Frozen acquisition problem | 18 binary variables, 153 interactions, batch size 3 | reproduced | 같은 BQM을 optimizer별로 비교 |
| Independent exact / Ocean ExactSolver | best energy -0.480789127750 | reproduced | frozen BQM의 reference optimum |
| Classical simulated annealing | exact batch와 같은 energy와 batch | reproduced | 2,000-read offline stochastic baseline |
| D-Wave QPU | 100 reads; best energy -0.434455351273; exact gap +0.046333776477 | reproduced | QPU submission path는 실행됨. exact optimum은 미재현 |
| QPU embedding | 18 logical, 46 physical qubits; mean chain-break fraction 0.01333 | reproduced | 한 번의 recorded embedding 결과 |
| PySCF exact batch | 3/3 converged; mean target error 0.620 eV | reproduced | B3LYP/6-31G(2df,p) single-point screening |
| PySCF QPU batch | 3/3 converged; mean target error 0.761 eV; best single error 0.119 eV | reproduced | 세 후보 배치의 소수 표본 결과 |
| Fixed-pool replay | 별도 4.0 eV target에서 random 0.2813, greedy 0.1298, exact/QUBO-SA 0.1261 eV | proxy | 52-label budget에서 3-seed mean best target error |
| Replay exact match | QUBO/SA 12/12 acquisitions | proxy | 고정 QM9 pool에서 classical SA가 exact batch와 일치 |
| Live generated-space loop | new DFT 0, QPU calls 0, space expansions 0 | not executed | 다음 단계로 제안된 실험 |

## Method Boundary

### D-Wave가 계산한 값

D-Wave QPU는 세 후보를 고르는 binary quadratic acquisition score를 최소화했습니다. BQM energy는 목표 적합성, model-spread proxy, novelty, pairwise similarity, batch cardinality를 합친 선택 점수입니다. 분자의 전자구조 에너지가 아닙니다.

### PySCF가 계산한 값

PySCF 결과는 RDKit ETKDGv3와 MMFF94s로 만든 고정 geometry에서 수행한 B3LYP/6-31G(2df,p) single-point 계산의 Kohn–Sham HOMO–LUMO orbital gap입니다. optical gap, excited-state spectrum, geometry-optimized minimum, 합성 가능성, 실험 측정값을 뜻하지 않습니다.

### Replay가 계산한 값

Replay는 분자 스냅샷의 6.0 eV와 구분되는 별도 4.0 eV target에서, 고정된 QM9 pool의 precomputed label을 숨긴 뒤 획득 정책에 따라 공개했습니다. 새 분자를 생성하거나 DFT를 호출하거나 QPU에 제출하지 않았습니다. 획득 구현을 점검하는 고전 proxy입니다.

## Primary and Official External Sources

| Source | 확인한 범위 | 사용 경계 |
| --- | --- | --- |
| [QM9 original collection, Figshare](https://doi.org/10.6084/m9.figshare.c.978904.v5) | QM9 collection의 구조·물성 데이터 출처 | 이번 5,000개 subset 수치는 로컬 계산 기록에서 가져옴 |
| [PyTorch Geometric QM9 documentation](https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.datasets.QM9.html) | QM9 target과 dataset interface 참고 | 계산 결과의 독립 증거로 사용하지 않음 |
| [Chemprop documentation](https://chemprop.readthedocs.io/en/main/index.html) | D-MPNN 기반 molecular property prediction 도구 | 이번 MAE는 로컬 실행 결과 |
| [SELFIES reference implementation](https://github.com/the-matter-lab/selfies) | SELFIES 표현과 구현 | 유효 문자열이 안정성·합성 가능성을 보장한다는 주장은 하지 않음 |
| [D-Wave: QUBOs and Ising Models](https://docs.dwavequantum.com/en/latest/quantum_research/qubo_ising.html) | binary quadratic objective의 기본 표현 | 분자 에너지와 BQM score를 구분 |
| [D-Wave: EmbeddingComposite.sample](https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/generated/dwave.system.composites.EmbeddingComposite.sample.html) | logical BQM의 topology embedding과 chain-break 정보 | 한 번의 embedding으로 일반화하지 않음 |
| [D-Wave: General QPU Solver Properties](https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html) | QPU solver property와 timing field의 맥락 | 현재 기록에 빠진 과거 metadata를 추정하지 않음 |
| [PySCF: Density Functional Theory](https://pyscf.org/user/dft.html) | PySCF DFT method와 설정 | single-point 계산의 방법 설명 |
| [PySCF: Time-dependent Hartree-Fock and DFT](https://pyscf.org/user/tddft.html) | excited-state calculation 경로 | orbital gap과 optical excitation을 구분 |
| [Lookman et al., Active learning in materials science](https://doi.org/10.1038/s41524-019-0153-8) | surrogate·acquisition·고비용 oracle을 반복하는 active-learning 구조 | 이번 replay를 live loop로 표현하지 않음 |

## Claim Status Matrix

| Claim | Status | Notes |
| --- | --- | --- |
| 오픈소스 ML, 세 proposal path, QUBO, QPU, PySCF를 하나의 실행 경로로 연결했다. | reproduced | 각 단계의 결과와 aggregate가 남아 있음 |
| ExtraTrees의 held-out MAE가 Chemprop보다 낮았다. | reproduced | 0.4743 eV 대 0.5308 eV, 같은 test split |
| 한 번의 QPU 실행이 exact optimum을 재현했다. | refuted | energy gap +0.046334, batch 불일치 |
| QPU path가 실제로 실행됐다. | reproduced | 100 reads, recorded embedding과 sample |
| QPU가 분자 orbital gap을 계산했다. | refuted | QPU는 acquisition BQM을 풀었고 PySCF가 orbital gap을 계산 |
| QPU batch가 평균 target error에서 exact batch보다 좋았다. | refuted | 0.761 eV 대 0.620 eV |
| QPU batch에 이번 스냅샷의 best single candidate가 포함됐다. | reproduced | target error 0.119 eV |
| 이 결과가 optimizer 우열이나 quantum advantage를 입증한다. | not established | QPU 1회, 배치당 3개, matched budget·반복 campaign 부재 |
| fixed-pool replay가 live molecular active learning을 입증한다. | refuted | 새 DFT·QPU·generated-space expansion이 모두 0 |
| PySCF 값이 optical gap 또는 실험 물성이다. | refuted | fixed-geometry Kohn–Sham orbital gap |

## Presentation Guardrails

- 모든 정량 수치는 공개 CSV와 최종 리뷰에 있는 값만 사용합니다.
- QPU 결과는 “경로 실행 확인”과 “exact optimum 미재현”을 함께 표시합니다.
- wall time은 실행 경로가 달라 speedup 비교에 사용하지 않습니다.
- 배치 평균과 best single hit를 같은 지표처럼 합치지 않습니다.
- 세 생성 경로의 반환 수와 union contribution을 구분합니다.
- guided path는 Chemprop-scored SELFIES mutation이며 GNN decoder가 아닙니다.
- RBM은 classical generator입니다.
- detailed infographic의 실선 영역은 실행됨, 점선 live loop는 PROPOSED입니다.
- 공식 deck은 Skywork project/viewer URL과 PPTX·PDF export가 모두 남아야 완료로 기록합니다.
