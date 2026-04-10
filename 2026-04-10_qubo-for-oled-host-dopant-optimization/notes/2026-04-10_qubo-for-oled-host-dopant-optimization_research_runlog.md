# Research Run Log - QUBO for OLED Host-Dopant Optimization

## Run Metadata

- Topic folder: `2026-04-10_qubo-for-oled-host-dopant-optimization`
- Run date: `2026-04-10`
- Operator: Codex

## Execution Path

- Started from local Pulse daily review package:
  - `daily_research_review/2026-04-10_gpt-pulse-daily-review/`
- Re-read the exact QUBO card title and blurb from the stored YAML snapshot.
- Inspected existing local Blue PHOLED report to avoid duplicating prior conclusions.
- Queried GitHub API directly for:
  - `xyin-anl/MatOpt-bench`
  - `cmc-ucl/QA_solid_solutions`
- Pulled raw README / model / example code files from GitHub.
- Pulled the PMC article page for the `Science Advances` paper and extracted key sections around:
  - QUBO
  - D-Wave
  - chemical potential
  - graphene / AlGaN / Ta-W
- Pulled D-Wave Ocean documentation page for `dwave-optimization`.
- Used previously validated OLED-domain sources plus one additional current host/dopant paper to evaluate domain fit.

## Key Evidence Captured

- Pulse card wording:
  - `MatOpt‑bench와 D‑Wave 예제를 활용해 화학 퍼널티 항이 포함된 고체용 QUBO를 직접 실행해볼 수 있어.`
- MatOpt-bench repo description and example list
- `09_solid_solution_qubo` code path and formulation
- Science Advances workflow:
  - DFT-trained QUBO
  - chemical potential composition tuning
  - D-Wave QA sampling
  - symmetry filtering and DFT revalidation
- D-Wave docs note that `dwave-optimization` supports nonlinear models for hybrid solver workflows
- OLED host design references showing that real host-dopant design depends on triplet alignment, charge balance, transfer pathways, and local packing/stability

## Interpretation Notes

- The Pulse card appears to compress two distinct public artifacts:
  - a materials-optimization benchmark repo
  - a separate D-Wave-based solid-solution thermodynamics workflow
- Public evidence supports `executable solid-state QUBO examples`.
- Public evidence does **not** yet support `OLED host-dopant QUBO` as a mainstream validated workflow.

## Limitations

- No public OLED-specific host-dopant QUBO benchmark was found in this pass.
- The MatOpt-bench QUBO example is benchmark/formulation-oriented and not by itself a D-Wave hardware tutorial.
- Science.org direct HTML access was blocked by anti-bot checks, so the PMC mirror was used instead.
