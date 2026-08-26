---
title: "D-Wave 분자 역설계 벤치마크 - Memo"
date: 2026-08-27
slug: dwave-molecular-inverse-design-benchmark
language: ko
status: checked-memo
---

# D-Wave 분자 역설계 벤치마크 - Memo

## One-Line Take

QM9 기반 ML, 세 분자 proposal mechanism, 검증된 acquisition QUBO, 한 번의 D-Wave QPU 제출, 여섯 건의 PySCF single-point DFT를 실제 계산 경로로 연결했습니다. QPU 경로는 작동했으나 exact optimum을 재현하지 못했고, quantum advantage와 live active learning은 아직 검증 대상입니다.

## Executive Snapshot

| 질문 | 이번 계산의 답 |
| --- | --- |
| 어떤 데이터를 썼는가? | QM9 derived subset 5,000개, train 4,058 / validation 511 / test 431 |
| 예측 baseline은 어땠는가? | ExtraTrees/Morgan MAE 0.4743 eV, Chemprop D-MPNN ensemble MAE 0.5308 eV |
| 후보는 어떻게 만들었는가? | Chemprop-guided SELFIES mutation, SELFIES GRU, classical SELFIES RBM |
| 공통 필터 뒤 후보 수는? | unique union 30개 |
| QUBO는 무엇을 골랐는가? | shortlist 18개에서 PySCF로 보낼 3개 배치 |
| exact reference는? | acquisition energy -0.480789 |
| QPU 결과는? | 100 reads, energy -0.434455, exact gap +0.046334, exact batch 미재현 |
| DFT는 어떻게 끝났는가? | exact·QPU 배치 모두 3/3 수렴, 총 6 jobs |
| downstream 평균은? | exact batch mean target error 0.620 eV, QPU batch 0.761 eV |
| 가장 가까운 단일 후보는? | QPU batch의 0.119 eV target error |
| replay는 무엇을 보였는가? | 별도 4.0 eV target과 52-label budget에서 random 0.2813, greedy 0.1298, exact/QUBO-SA 0.1261 eV |

## Pipeline in Plain Language

1. QM9 분자 5,000개로 orbital-gap surrogate를 학습했습니다.
2. 세 가지 생성 경로를 실행하고 같은 화학 필터를 적용했습니다.
3. 공통 후보 30개 가운데 frozen shortlist 18개를 만들었습니다.
4. 목표 6.0 eV 적합성, novelty, model-spread proxy, pair similarity, batch size를 QUBO로 묶었습니다.
5. independent exact, Ocean ExactSolver, classical simulated annealing으로 objective와 BQM energy를 확인했습니다.
6. 같은 BQM을 D-Wave QPU에 100 reads로 한 번 제출했습니다.
7. exact batch 세 분자와 QPU batch 세 분자를 PySCF로 계산했습니다.
8. 분자 스냅샷의 6.0 eV와 구분되는 별도 4.0 eV target의 fixed-pool replay에서 acquisition policy를 3 seeds로 비교했습니다.

## D-Wave의 정확한 역할

D-Wave QPU는 분자의 HOMO, LUMO, orbital gap을 계산하지 않았습니다. 다음 계산 예산을 어디에 쓸지 정하는 세 후보의 조합을 골랐습니다. QUBO energy는 batch acquisition score이고, PySCF DFT 결과가 분자별 orbital-gap screen입니다.

Frozen BQM에는 18개 binary variable과 153개 pair interaction이 있었습니다. Independent exact와 classical simulated annealing은 같은 세 후보와 energy -0.480789를 찾았습니다. QPU best sample은 -0.434455였고 exact와의 차이는 +0.046334였습니다.

이 결과가 확인한 내용은 QPU submission, embedding, sampling, decoding 경로가 작동한다는 점입니다. Exact optimum 재현, speedup, quantum advantage는 확인되지 않았습니다.

## DFT에서 본 두 개의 지표

PySCF 계산은 RDKit ETKDGv3와 MMFF94s로 만든 geometry에 B3LYP/6-31G(2df,p) single point를 적용했습니다. Exact batch와 QPU batch의 세 job이 모두 수렴했습니다.

- Batch 평균: exact 0.620 eV, QPU 0.761 eV
- Best single hit: exact 0.299 eV, QPU 0.119 eV

Batch 평균은 exact 선택이 좋았습니다. QPU batch에는 이번 스냅샷에서 목표 6.0 eV에 가장 가까운 단일 후보가 들어 있었습니다. 세 분자씩의 결과이므로 두 optimizer의 일반적 우열을 뜻하지 않습니다.

## Replay를 Live Loop로 부르지 않는 이유

Replay는 분자 스냅샷의 6.0 eV 목표와 다른 4.0 eV target을 사용해 QM9의 precomputed label을 숨겼다가 공개했습니다. 네 번의 acquisition에서 label budget은 40개에서 52개로 늘었습니다. QUBO/classical SA는 12번의 acquisition 모두 exact batch와 일치했습니다.

이 과정에 새 DFT, QPU 제출, generated chemical-space expansion은 없었습니다. 앞서 계산한 여섯 DFT label도 surrogate training set에 아직 추가하지 않았습니다. 따라서 replay는 획득 구현을 확인하는 proxy이며, generated-space active learning의 계산 비용이나 수렴 속도를 말해주지 않습니다.

## Evidence Boundary

| 상태 | 내용 |
| --- | --- |
| reproduced | 두 surrogate, 세 proposal mechanism, 공통 화학 filter, objective–BQM mapping, exact와 classical SA, QPU 1회, PySCF 6 jobs |
| proxy | 고정 QM9 pool의 3-seed hidden-label replay |
| not established | optical gap, 안정성, 합성 가능성, 실험 물성, persistent live loop, scalable speedup, quantum advantage, molecular discovery |

## Next Decision

다음 단계에서는 아래 조건을 고정한 matched live-loop bake-off가 필요합니다.

1. 같은 initial data와 candidate pool
2. 같은 batch size와 DFT label budget
3. greedy ML, independent exact, classical SA, D-Wave QPU의 같은 round schedule
4. surrogate fit, candidate generation, QUBO build, queue, sampling, DFT의 분리된 시간·비용
5. candidate와 계산 이력을 보존하는 persistent ledger
6. 사전에 정한 go / scale / stop 기준

강한 classical champion과 같은 예산으로 비교한 뒤, hit quality, diversity, calibration, DFT success rate, end-to-end wall time과 비용을 함께 봐야 합니다. QPU campaign은 이 비교에서 추가 정보를 제공할 때만 확장합니다.

## References

- [QM9 original collection](https://doi.org/10.6084/m9.figshare.c.978904.v5)
- [Chemprop documentation](https://chemprop.readthedocs.io/en/main/index.html)
- [SELFIES reference implementation](https://github.com/the-matter-lab/selfies)
- [D-Wave: QUBOs and Ising Models](https://docs.dwavequantum.com/en/latest/quantum_research/qubo_ising.html)
- [D-Wave: EmbeddingComposite.sample](https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/generated/dwave.system.composites.EmbeddingComposite.sample.html)
- [PySCF: Density Functional Theory](https://pyscf.org/user/dft.html)
- [PySCF: Time-dependent Hartree-Fock and DFT](https://pyscf.org/user/tddft.html)
- [Lookman et al., Active learning in materials science](https://doi.org/10.1038/s41524-019-0153-8)
