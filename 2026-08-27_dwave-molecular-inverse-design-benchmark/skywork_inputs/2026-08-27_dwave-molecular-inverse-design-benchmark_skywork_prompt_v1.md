# Skywork Prompt v1 - D-Wave 분자 역설계 벤치마크

업로드된 LGD 템플릿과 source pack만 사용해 한국어 PowerPoint deck을 생성하라.

## Output Contract

- 프로젝트명: D-Wave 분자 역설계 실험
- 제목: D-Wave 분자 역설계 실험: QPU가 고른 후보를 DFT까지 확인해 보니
- 부제: QM9 5,000개에서 ML·분자 생성·QUBO 선택·QPU 실행·PySCF 검증까지
- 청중: AI Tech Review 독자, quantum optimization·molecular AI·materials informatics 실무자
- 목적: 실제 계산 파이프라인, 정량 결과, claim boundary, 다음 live-loop 검증 설계를 설명
- 언어: 한국어. Chemprop, SELFIES, QUBO, BQM, DFT, QPU, active learning 등 표준 영문 용어는 유지
- 분량: 정확히 12 slides
- 화면비: 16:9
- 템플릿: 업로드된 LGD_Template.pptx를 반드시 기반으로 사용
- 출력: 편집 가능한 PPTX와 같은 deck의 PDF를 모두 export
- 기록: 실제 Skywork project/viewer URL을 남길 수 있는 project로 생성

공식 완료 조건은 실제 Skywork project/viewer URL, PPTX export, PDF export가 모두 있는 상태다. 이미지로만 만든 deck이나 로컬에서 재구성한 PPTX로 대체하지 말라.

## Uploaded Source Priority

1. reports/2026-08-27_dwave-molecular-inverse-design-benchmark_final_review.md
2. artifacts/final_review/data/benchmark_results.csv
3. artifacts/final_review/figure_manifest.md
4. reports/2026-08-27_dwave-molecular-inverse-design-benchmark_deepresearch.md
5. reports/2026-08-27_dwave-molecular-inverse-design-benchmark_memo.md
6. notes/2026-08-27_dwave-molecular-inverse-design-benchmark_sources.md
7. artifacts/final_review/figures의 검토된 이미지

문서 사이에 표현 차이가 있으면 benchmark_results.csv의 aggregate와 final_review의 claim boundary를 우선한다. 업로드 자료에 없는 수치, 분자, solver name, 실행 시각, software version, source hash, 비용, timing unit을 만들어내지 말라.

## Core Editorial Thesis

이 실험은 오픈소스 ML, 세 proposal mechanism, 검증된 acquisition QUBO, 한 번의 D-Wave QPU submission, 여섯 건의 PySCF single-point DFT를 실제 계산 경로로 연결했다.

QPU path는 실행됐다. QPU best sample은 exact optimum을 재현하지 못했다. Exact batch의 mean DFT target error가 낮았고, QPU batch에는 이번 스냅샷의 best single candidate가 포함됐다. Fixed-pool replay는 acquisition implementation을 점검한 proxy다. Persistent generated-space active learning과 quantum advantage는 아직 검증되지 않았다.

## Non-Negotiable Claim Boundaries

- D-Wave QPU는 분자의 전자구조나 orbital gap을 계산하지 않았다.
- D-Wave QPU의 역할은 shortlist 18개에서 다음 PySCF 계산에 보낼 3개 후보 batch를 고르는 acquisition optimization이다.
- BQM energy는 molecular energy가 아닌 selection score다.
- Exact optimum은 -0.480789, QPU best는 -0.434455, gap은 +0.046334다.
- 한 번의 QPU 실행은 exact optimum을 재현하지 못했다.
- QPU 실행을 quantum advantage, speedup, discovery로 표현하지 말라.
- Wall time은 실행 경로가 달라 speedup 비교에 쓰지 말라.
- DFT 결과는 fixed force-field geometry의 B3LYP/6-31G(2df,p) Kohn–Sham HOMO–LUMO orbital gap이다.
- DFT 값을 optical gap, excited-state spectrum, experimental property로 표현하지 말라.
- QPU batch의 best single error 0.119 eV와 batch mean 0.761 eV를 섞지 말라.
- Exact batch mean 0.620 eV와 QPU batch mean 0.761 eV는 배치당 3개의 작은 표본이다.
- Guided generator는 Chemprop-scored SELFIES mutation이며 GNN decoder가 아니다.
- RBM generator는 classical model이다.
- SELFIES validity가 stability나 synthetic accessibility를 보장한다고 쓰지 말라.
- Replay는 fixed QM9 pool과 precomputed labels를 사용했다.
- Replay target은 4.0 eV이며, 앞 절의 6.0 eV molecular snapshot과 별도인 정책 점검 benchmark다.
- Replay의 new DFT, QPU calls, generated-space expansions는 모두 0이다.
- Slide 11의 live loop는 제목과 도식에 PROPOSED / 제안 표시를 반복하고 점선으로 표현하라.

## Exact Metric Anchors

| Layer | Metric |
| --- | --- |
| Dataset | 5,000 molecules; train 4,058; validation 511; test 431 |
| Chemprop | MAE 0.5308 eV; RMSE 0.6882 eV; R² 0.7547 |
| ExtraTrees/Morgan | MAE 0.4743 eV; RMSE 0.6854 eV; R² 0.7567 |
| Generators | governed unique contribution 11 / 8 / 11; union 30 |
| Frozen BQM | 18 variables; 153 interactions; batch size 3 |
| Exact | -0.480789127750 |
| QPU | 100 reads; -0.434455351273; exact gap +0.046333776477 |
| Embedding | 18 logical; 46 physical qubits; mean chain-break fraction 0.01333 |
| Exact DFT batch | 3/3 converged; mean target error 0.620 eV; ML–DFT MAE 0.580 eV |
| QPU DFT batch | 3/3 converged; mean target error 0.761 eV; ML–DFT MAE 0.730 eV |
| QPU best single | PySCF gap 5.8808 eV; target error 0.1192 eV |
| Replay at 52 labels | target 4.0 eV; random 0.2813; greedy 0.1298; exact/QUBO-SA 0.1261 eV |
| Replay exact match | QUBO/classical SA 12/12 acquisitions |
| Live loop | new DFT 0; QPU calls 0; generated-space expansions 0 |

표시 자리 때문에 반올림할 때는 본 프롬프트의 유효 자릿수를 유지하라. -0.480789, -0.434455, +0.046334, 0.620 eV, 0.761 eV, 0.119 eV를 기본 표시값으로 사용한다.

## 12-Slide Storyboard

### Slide 1. Title and Experiment Snapshot

- 제목과 부제
- 큰 숫자 네 개: QM9 5,000 / candidates 30 / QPU 100 reads / PySCF 6 jobs
- 한 문장: “분자를 계산한 QPU가 아니라, 다음 계산에 보낼 세 후보를 고른 QPU”
- 배경 또는 우측 visual: molecular_inverse_design_hero.png
- hero는 editorial illustration이라고 작은 caption으로 표시

### Slide 2. End-to-End Pipeline and Role Split

- 데이터 → surrogate → 세 proposal path → governance → QUBO acquisition → exact/SA/QPU → PySCF → replay의 전체 구조
- QPU와 DFT 역할을 색으로 분리
- QPU: batch selection
- PySCF: orbital-gap calculation
- visual: molecular_inverse_design_infographic.svg 또는 01_evidence_layer_pipeline.png
- live loop 영역이 보이면 PROPOSED와 점선을 유지

### Slide 3. Surrogate Benchmark

- Chemprop D-MPNN ensemble과 ExtraTrees/Morgan의 같은 431-molecule test split 비교
- MAE 0.5308 대 0.4743 eV
- ExtraTrees의 held-out MAE가 낮았다는 관찰
- generated molecules의 OOD 또는 experimental accuracy를 보장하지 않는다는 caveat
- visual: 02_qm9_surrogate_parity.png

### Slide 4. Three Classical Proposal Mechanisms

- Chemprop-guided SELFIES mutation
- SELFIES GRU decoder
- classical SELFIES RBM
- 공통 chemical governance와 unique contribution 11 / 8 / 11, union 30
- raw proposal rejection counter를 작은 rail로 배치: radical 41, size 15, unsupported element 3, non-neutral 1
- training-cost matched benchmark가 아니라는 annotation
- visual: 03_generator_metrics.png

### Slide 5. QUBO as a Batch-Selection Score

- 후보 i 선택 시 x_i = 1
- 목적: target loss - uncertainty reward - novelty reward + similarity penalty + cardinality penalty
- target 6.0 eV, batch size 3
- 18 variables, 153 interactions
- “BQM energy = acquisition score”를 크게 표시
- dense LaTeX 한 줄을 피하고 readable term stack과 coefficient-role table을 사용
- coefficient 값은 source에 없으므로 발명하지 말라

### Slide 6. QPU Run: Path Executed, Exact Missed

- independent exact -0.480789
- classical SA exact match
- D-Wave QPU -0.434455
- exact gap +0.046334
- 100 reads, 18 logical, 46 physical qubits
- 큰 판정 label: “QPU 경로 실행 확인 / exact optimum 미재현”
- quantum advantage 또는 speedup label 금지
- visual: 04_acquisition_comparison.png

### Slide 7. QPU-Selected Molecules under PySCF

- QPU batch 3/3 converged
- 분자별 ML prediction과 PySCF orbital gap
- N#CC=C1CC=NC1O: ML 5.8763 eV, PySCF 5.8808 eV, target error 0.1192 eV
- 나머지 두 후보에는 약 1.1 eV ML–DFT 차이가 있었음을 표시
- visual: 05_dft_molecule_validation.png
- caption: fixed-geometry single-point orbital gap

### Slide 8. Exact Batch vs QPU Batch

- exact mean target error 0.620 eV
- QPU mean target error 0.761 eV
- QPU best single 0.119 eV
- exact best single 0.299 eV
- mean result와 best-hit result를 두 column으로 분리
- 판정: “평균은 exact, 이번 best single은 QPU batch”
- sample size는 batch당 3개라는 caveat
- visual: 07_exact_vs_qpu_dft_batch.png

### Slide 9. Fixed-Pool Replay

- 4.0 eV target이며 앞 절의 6.0 eV molecular snapshot과 별도임을 제목 또는 subtitle에 표시
- 40 labels에서 시작, batch size 3, 4 rounds, final 52 labels, 3 paired seeds
- random 0.2813
- greedy 0.1298
- exact/QUBO-SA 0.1261 eV
- QUBO-SA exact match 12/12
- visual: 06_qm9_replay_convergence.png
- 빨간 또는 amber boundary strip: “0 new DFT · 0 QPU calls · 0 generated-space expansions”

### Slide 10. Evidence Ledger

- reproduced / proxy / not established의 3단 matrix
- reproduced: 두 surrogate, 세 proposal path, QUBO verification, exact/SA, QPU 1회, PySCF 6 jobs
- proxy: fixed-pool hidden-label replay
- not established: optical gap, stability, synthesis, experiment, persistent live loop, speedup, quantum advantage, discovery
- QPU 기록에서 빠진 metadata: exact timestamp, submission-time versions, source hash, timing unit
- 목적: 결과보다 claim boundary가 먼저 보이게 구성

### Slide 11. PROPOSED Live Quantum-Assisted Active Learning

- 제목에 반드시 “PROPOSED / 제안” 포함
- 모든 loop arrow를 점선으로 표시
- persistent ledger → surrogate refit → generate/govern → score → policy select → same DFT oracle → append labels → repeat
- policy lanes: greedy ML / independent exact / classical SA / D-Wave QPU
- matched conditions: same initial labels, candidate opportunity, batch size, DFT budget, round count
- 측정: hit quality, batch mean, diversity, calibration, DFT success, end-to-end time, cost
- 이 슬라이드에 실행 완료를 암시하는 숫자나 실선 loop를 넣지 말라

### Slide 12. Decision Gate

- 현재 판정: “파이프라인 작동, 우위 주장은 보류”
- Go: 같은 예산에서 classical champion 대비 반복 가능한 추가 정보
- Scale: multiple seeds와 larger shortlist에서도 유지
- Stop: quality/diversity 이득이 없거나 queue·sampling overhead가 목적에 맞지 않음
- 마지막 문장: “다음 증거는 더 많은 후보 수가 아니라 matched live-loop bake-off에서 나온다.”
- source pack과 계산 CSV를 확인할 수 있다는 footer

## Visual System

- LGD_Template.pptx의 master, font, footer, brand color를 유지하라.
- 흰 배경, 짙은 회색 본문, LG Red accent를 기본으로 한다.
- 정보 밀집형 기술 브리핑으로 설계하되 최소 20 pt 수준의 본문 가독성을 유지한다.
- 모든 slide가 같은 카드 grid를 반복하지 않도록 pipeline, parity plot, term stack, comparison chart, evidence matrix, loop diagram을 섞는다.
- slide당 하나의 핵심 판정과 하나의 주 visual을 둔다.
- chart의 axis, legend, molecule label이 읽히도록 crop하지 말라.
- 계산 chart는 다시 그리지 말고 업로드된 검토본을 우선 사용한다.
- hero 안의 중앙 장치를 실제 D-Wave 장비 사진처럼 caption하지 말라.
- infographic의 executed solid blocks와 proposed dashed loop 스타일을 보존한다.
- 출처는 각 slide 하단에 9–11 pt 짙은 회색 text로 넣는다.
- 길고 빽빽한 문단을 만들지 말라. 숫자, 판정, caveat, figure caption의 위계를 분명히 한다.

## Source Footer Map

- Dataset: QM9 original collection — https://doi.org/10.6084/m9.figshare.c.978904.v5
- Chemprop — https://chemprop.readthedocs.io/en/main/index.html
- SELFIES — https://github.com/the-matter-lab/selfies
- QUBO — https://docs.dwavequantum.com/en/latest/quantum_research/qubo_ising.html
- EmbeddingComposite — https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/generated/dwave.system.composites.EmbeddingComposite.sample.html
- D-Wave solver properties — https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html
- PySCF DFT — https://pyscf.org/user/dft.html
- PySCF TDDFT — https://pyscf.org/user/tddft.html
- Active learning — https://doi.org/10.1038/s41524-019-0153-8
- 계산 수치 — uploaded benchmark_results.csv and final_review.md

## Final QA Before Export

1. Slide count가 정확히 12인지 확인한다.
2. 숫자를 benchmark_results.csv와 대조한다.
3. QPU exact miss가 명확히 보이는지 확인한다.
4. QPU role과 DFT role이 뒤섞이지 않았는지 확인한다.
5. DFT가 orbital gap이고 optical gap이 아님을 확인한다.
6. Replay에 0 new DFT, 0 QPU, 0 expansion이 표시됐는지 확인한다.
7. Slide 11의 제목과 loop가 PROPOSED·점선으로 표시됐는지 확인한다.
8. Quantum advantage, speedup, discovery 문구가 없는지 확인한다.
9. 모든 figure caption과 source footer가 읽히는지 확인한다.
10. 같은 내용의 PPTX와 PDF를 export하고 실제 Skywork project/viewer URL을 보존한다.
