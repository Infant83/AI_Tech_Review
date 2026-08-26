# Skywork Revision v2 — full-deck factual repair

The first Skywork draft has the correct 12-slide count and LGD visual family, but it is not publishable. Repair all 12 slides in Skywork. Preserve the LGD template and exactly 12 slides. Replace every corrupted phrase, placeholder such as `TITLE`, invented molecule, invented number, and nonsensical footer.

## Absolute rules

- Use only fluent Korean plus standard technical English terms.
- Do not leave mojibake, pseudo-Korean, random Latin strings, or template placeholder text.
- Use the uploaded reviewed figures as images; do not redraw their numerical contents.
- Do not invent molecules, DFT values, solver names, timestamps, versions, source hashes, costs, or timing units.
- D-Wave QPU selected a batch. It did not calculate molecular electronic structure.
- BQM energy is an acquisition score, not molecular energy.
- The one recorded QPU run did not reproduce the exact optimum.
- No quantum advantage, speedup, molecular discovery, optical-gap accuracy, synthesis, or experimental claim.
- Preserve the distinction between the 6.0 eV molecular snapshot and the separate 4.0 eV fixed-pool replay.
- Slide 11 must repeat `PROPOSED / 제안` and use dashed arrows.
- Use short source footers only from the official URLs in the uploaded source note.

## Slide-by-slide replacement contract

### Slide 1 — title and bounded snapshot

- Title: `D-Wave 분자 역설계 실험: QPU가 고른 후보를 DFT까지 확인해 보니`
- Subtitle: `QM9 5,000개에서 ML·분자 생성·QUBO 선택·QPU 실행·PySCF 검증까지`
- KPI: `QM9 5,000`, `후보 30`, `QPU 100 reads`, `PySCF 6 jobs`
- One sentence: `QPU는 분자를 계산하지 않고, 다음 계산에 보낼 세 후보의 배치를 골랐다.`
- Use uploaded `molecular_inverse_design_hero.png` and label it `editorial illustration`.

### Slide 2 — pipeline and role split

- Use uploaded `molecular_inverse_design_infographic.png` or `01_evidence_layer_pipeline.png` as the main visual.
- QPU role: `shortlist 18개에서 PySCF로 보낼 3개 후보 배치 선택`.
- PySCF role: `B3LYP/6-31G(2df,p) single-point Kohn–Sham orbital gap 계산`.
- Proposed loop is not an executed result.

### Slide 3 — surrogate benchmark

- Use uploaded `02_qm9_surrogate_parity.png` without altering chart data.
- Same 431-molecule test split.
- Chemprop MAE `0.5308 eV`; ExtraTrees/Morgan MAE `0.4743 eV`.
- Caveat: held-out QM9 performance does not establish generated-molecule or experimental accuracy.

### Slide 4 — three classical proposal lanes

- Delete all corrupted lane names and pseudo-text.
- Use uploaded `03_generator_metrics.png` as the main visual.
- Lanes: `Chemprop-guided SELFIES mutation`, `SELFIES GRU decoder`, `classical SELFIES RBM`.
- Governed unique contributions: `11 / 8 / 11`; union `30`.
- Filter rejections: radical `41`, oversize `15`, unsupported element `3`, non-neutral `1`.
- State that timing is not a matched training-cost benchmark.

### Slide 5 — readable QUBO

- Remove every `TITLE` placeholder.
- Show:

  `acquisition score`

  `= target loss`

  `- uncertainty reward`

  `- novelty reward`

  `+ similarity penalty`

  `+ cardinality penalty`

- `x_i = 1` means candidate i is selected.
- Target `6.0 eV`; batch size `3`; variables `18`; interactions `153`.
- Large label: `BQM energy = acquisition score ≠ molecular energy`.

### Slide 6 — QPU snapshot

- Delete every corrupted word and every wrong number.
- Use uploaded `04_acquisition_comparison.png` as the main visual.
- Exact and classical SA: `-0.480789`.
- D-Wave QPU best: `-0.434455`.
- Gap to exact: `+0.046334`.
- `100 reads`; `18 logical → 46 physical qubits`; mean chain-break fraction `0.01333`.
- Verdict: `QPU 경로 실행 확인 / exact optimum 미재현`.
- Wall time is not a speedup comparison.

### Slide 7 — QPU batch under PySCF

- Delete the invented molecule and all wrong DFT values currently on this slide.
- Use uploaded `05_dft_molecule_validation.png` as the main visual and do not redraw it.
- QPU batch `3 / 3 converged`.
- `N#CC=C1CC=NC1O`: ML `5.8763 eV`; PySCF `5.8808 eV`; target error `0.1192 eV`.
- QPU batch ML–DFT MAE `0.730 eV`.
- Caption: fixed-force-field-geometry, B3LYP/6-31G(2df,p) single-point Kohn–Sham orbital gap; not optical gap or experiment.

### Slide 8 — exact batch versus QPU batch

- Use uploaded `07_exact_vs_qpu_dft_batch.png` as the main visual.
- Exact batch: mean target error `0.620 eV`; best single `0.299 eV`; ML–DFT MAE `0.580 eV`.
- QPU batch: mean target error `0.761 eV`; best single `0.119 eV`; ML–DFT MAE `0.730 eV`.
- Both batches `3 / 3 converged`; batch overlap `1`.
- Verdict: `평균은 exact batch가 낮았고, 이번 best single은 QPU batch에 있었다.`
- Caveat: three molecules per batch, no optimizer superiority claim.

### Slide 9 — fixed-pool replay at 4.0 eV

- Delete the incorrect chart and all invented benchmark text.
- Use uploaded `06_qm9_replay_convergence.png` as the main visual and do not redraw it.
- Title or subtitle must state `4.0 eV target` and `fixed-pool replay`.
- Initial labels `40`; final labels `52`; batch size `3`; four rounds; three paired seeds.
- Final mean best target error: random `0.2813 eV`; greedy `0.1298 eV`; exact/QUBO-SA `0.1261 eV`.
- QUBO-SA matched exact batch `12 / 12` acquisitions.
- Boundary strip: `0 new DFT · 0 QPU calls · 0 generated-space expansions`.

### Slide 10 — evidence ledger

- Three fluent columns only: `재현됨`, `프록시`, `미확립`.
- Reproduced: two surrogates, three proposal lanes, QUBO mapping, exact/SA, one QPU submission, six PySCF jobs.
- Proxy: 4.0 eV fixed-pool hidden-label replay.
- Not established: optical gap, stability, synthesis, experiment, persistent live loop, speedup, quantum advantage, molecular discovery.
- Missing QPU archive metadata may be a small footer: exact timestamp, submission-time versions, source hash, timing unit.

### Slide 11 — proposed live loop

- Title: `[제안] 실시간 양자 보조 능동 학습 루프`.
- Keep `PROPOSED SYSTEM — ALL FLOWS ARE PLAN ONLY` at top and bottom.
- Use dashed arrows for every loop connection.
- Policy lanes: greedy ML, independent exact, classical SA, D-Wave QPU.
- Same initial labels, candidates, batch size, DFT budget, and round count.
- Metrics: hit quality, batch mean, diversity, calibration, DFT success, end-to-end time, cost.
- Do not imply any live-loop result exists.

### Slide 12 — decision gate

- Current judgment: `파이프라인 작동, 우위 주장은 보류`.
- Go: repeatable additional information versus the classical champion at matched budget.
- Scale: holds across multiple seeds and larger shortlists.
- Stop: no quality/diversity gain or queue/sampling overhead defeats the purpose.
- Closing line: `다음 증거는 matched live-loop bake-off에서 나온다.`

## Final Skywork QA

Before export, visually read every slide. Confirm there are exactly 12 slides, no corrupted text, no placeholders, no invented data, and no cropped figure labels. Export an editable PPTX. The source metrics in uploaded `benchmark_results.csv` and the claim boundaries in the uploaded final review are authoritative.
