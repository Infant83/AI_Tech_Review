# QUBO for OLED Host-Dopant Optimization - Sources

## Scope

- Topic: `QUBO 관련 Pulse 카드가 실제로 무엇을 가리키는지 확인하고, 그것이 OLED host-dopant optimization과 얼마나 직접 연결되는지 평가`
- Review date: `2026-04-10`

## Seed Claim From Pulse

- Pulse card title:
  - `실행 가능한 호스트–도펀트 QUBO 예제 2종`
- Pulse blurb captured from local snapshot:
  - `MatOpt‑bench와 D‑Wave 예제를 활용해 화학 퍼널티 항이 포함된 고체용 QUBO를 직접 실행해볼 수 있어.`

Local evidence:
- `daily_research_review/2026-04-10_gpt-pulse-daily-review/sources/2026-04-10_gpt-pulse-daily-review_udc_detail_snapshot.yml`
- `daily_research_review/2026-04-10_gpt-pulse-daily-review/notes/2026-04-10_gpt-pulse-daily-review_pulse_review.md`

## Primary Sources Reviewed

### 1. MatOpt-bench repository

- Repository:
  - https://github.com/xyin-anl/MatOpt-bench
- GitHub metadata checked on `2026-04-10`:
  - created: `2025-07-07T15:59:20Z`
  - updated: `2025-11-15T21:03:39Z`
  - description: `Benchmark problems demonstrating the application of mathematical optimization to inorganic materials design problems`
- README:
  - https://raw.githubusercontent.com/xyin-anl/MatOpt-bench/main/README.md
- Mathematical formulations:
  - https://raw.githubusercontent.com/xyin-anl/MatOpt-bench/main/models.md
- QUBO example code:
  - https://raw.githubusercontent.com/xyin-anl/MatOpt-bench/main/examples/09_solid_solution_qubo.py

What it shows:
- MatOpt-bench is a benchmark suite for `inorganic materials design`, not an OLED-specific project.
- The relevant example is `09_solid_solution_qubo`.
- The README explicitly lists the example systems as `N-doped graphene`, `AlGaN`, and `Ta-W`.
- The QUBO example script builds a QUBO objective and supports constrained or unconstrained optimization, but the default benchmark path uses `MatOptModel` with `cplex`, so it is closer to a formulation/benchmark asset than a turnkey D-Wave hardware demo.

### 2. Science Advances paper on quantum annealing for disordered materials

- Article:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC12143349/
- DOI:
  - https://doi.org/10.1126/sciadv.adt7156
- Title:
  - `Exploring the thermodynamics of disordered materials with quantum computing`
- Associated code repository:
  - https://github.com/cmc-ucl/QA_solid_solutions
- Repository metadata checked on `2026-04-10`:
  - created: `2024-07-23T16:35:37Z`
  - updated: `2025-08-22T04:04:01Z`

What it shows:
- The paper uses D-Wave quantum annealers for `disordered solid solutions`.
- The workflow is:
  - build a supercell
  - train QUBO parameters on a subset of DFT data
  - add a `chemical potential` term to tune composition
  - use repeated annealing to obtain Boltzmann-like distributions
  - symmetry-filter returned structures
  - recheck selected structures with higher-level theory
- The three application systems explicitly named are:
  - `nitrogen-doped graphene`
  - `Al1-xGaxN`
  - `Ta1-xWx`
- The paper explicitly argues that a chemical-potential formulation is preferable to a hard composition constraint because hard constraints create a fully connected QUBO that maps poorly to current hardware.

### 3. D-Wave documentation

- Ocean optimization documentation:
  - https://docs.dwavequantum.com/en/latest/ocean/api_ref_optimization/index.html

What it shows:
- D-Wave's current public software stack is not limited to raw QUBO/BQM.
- `dwave-optimization` is described as enabling `nonlinear models for industrial optimization problems` for the hybrid nonlinear-program solver.
- This matters because some future materials-design formulations may fit nonlinear hybrid optimization better than a pure QUBO reduction.

### 4. OLED host-dopant design references

- Host-material review:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC2635741/
- Deep-blue phosphorescent OLED host example:
  - https://www.nature.com/articles/s41467-025-59583-8

What they show:
- Suitable phosphorescent OLED host design depends on more than a binary substitution map.
- Key variables include:
  - host triplet level relative to guest triplet
  - HOMO/LUMO offsets and charge balance
  - Förster/Dexter transfer conditions
  - chemical and morphological stability
  - quenching, rigidity, and local packing around the dopant
- The `2025` Nature Communications paper is especially useful because it shows host compactness and local environment around the dopant being analyzed with MD, which is much richer than a simple site-occupation QUBO.

## Preliminary Interpretation

- Pulse was directionally right that executable QUBO materials examples exist.
- The strongest public evidence points to `solid-solution / substitutional disorder` problems on fixed lattices, not to a mature OLED host-dopant benchmark.
- The most realistic OLED use of QUBO today is not full molecular discovery, but `candidate prioritization under pairwise penalties and composition/style constraints`.

## Open Questions

- Is there any public OLED-specific host-dopant QUBO benchmark beyond the general solid-solution examples?
- Which part of the OLED design stack would most naturally map to QUBO:
  - host/dopant pair selection
  - layer-stack combinatorics
  - ratio/recipe search
  - experiment scheduling
- At what point does a richer nonlinear or hybrid model become more appropriate than raw QUBO?
