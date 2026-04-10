# 2026-04-10 Blue PHOLED IP and Simulation Stack - Sources

## Topic
- `Blue PHOLED IP + simulation stack`
- Seed date: `2026-04-10`
- Intake path: `GPT Pulse -> daily_research_review/2026-04-10_gpt-pulse-daily-review`

## Pulse Seed Items
- `UDC 2026년 4월 특허 — 유기금속 리간드·호스트 혼합 설계`
- `이데미츠 2026년 3월 특허 — 수명 개선형 호스트 설계`
- `블루 PHOLED 수명 예측용 멀티스케일 시뮬레이션`
- `실행 가능한 호스트–도펀트 QUBO 예제 2종`
- `GPU·Autodiff 기반 TMM/RCWA 툴 최신 업데이트`

## Local Seed Artifacts
- `sources/2026-04-10_gpt-pulse-daily-review_pulse_review.md`
- `sources/2026-04-10_gpt-pulse-daily-review_overview_snapshot.yml`
- `sources/2026-04-10_gpt-pulse-daily-review_udc_detail_snapshot.yml`

## Primary / High-Priority External Sources
1. Universal Display press release
   - URL: https://ir.oled.com/newsroom/press-releases/press-release-details/2026/Universal-Display-to-Highlight-OLED-Emissive-Layer-Advances-for-Display-Efficiency-and-Performance-at-ICDT-2026/default.aspx
   - Verified points:
   - `2026-03-25` release.
   - ICDT 2026 invited talk scheduled for `2026-04-02`.
   - UDC explicitly ties PHOLED materials to `single-stack`, `tandem`, `PSF`, and `new pixel designs`.

2. Justia assignee page for Universal Display Corporation
   - URL: https://patents.justia.com/assignee/universal-display-corporation
   - Verified points:
   - `20260096280` published `2026-04-02`.
   - `12598905` and `12598908` granted `2026-04-07`.
   - `20260101630` and `20260101629` published `2026-04-09`.
   - `12593378` granted `2026-03-31` and describes a thermally evaporated `carbazole + triazine` host mixture from one crucible.

3. UDC patent `12593378`
   - URL: https://patents.justia.com/patent/12593378
   - Verified points:
   - Title: `Organic electroluminescent materials and devices`
   - Grant date: `2026-03-31`
   - Abstract-level claim: a mixture of carbazole and triazine derivatives that can be thermally evaporated from one crucible to fabricate thin films for electroluminescent devices.
   - This is the strongest public match to the Pulse phrase about `single-crucible deposition host-mixture design`.

4. Idemitsu patent `12538638`
   - URL: https://patents.justia.com/patent/12538638
   - Verified points:
   - Title: `Organic electroluminescent element and electronic device`
   - Grant date: `2026-01-27`
   - Objective is explicit long lifetime improvement.
   - Public claims connect lifetime to multi-emissive-layer design and host/emitter energy relationships, including `T1(H1) < T1(H2)` and a constrained `LUMO(H2)` to `LUMO(D2)` gap.

5. TMMax
   - URLs:
   - https://github.com/bahremsd/tmmax
   - https://tmmax.readthedocs.io/en/latest/user_guide/code_structure.html
   - Verified points:
   - JAX-based transfer-matrix implementation for multilayer thin films.
   - JOSS citation year `2025`.

6. TMM-Fast
   - URLs:
   - https://github.com/MLResearchAtOSRAM/tmm_fast
   - https://arxiv.org/abs/2111.13667
   - Verified points:
   - GPU/parallelized TMM package.
   - Repo explicitly positions it for thin-film optimization and RL-like optimization environments.

7. grcwa
   - URL: https://github.com/weiliangjinca/grcwa
   - Verified points:
   - Autograd-enabled RCWA implementation for optimization workflows.
   - More relevant to patterned / nanophotonic optical subproblems than to molecular lifetime itself.

8. D-Wave optimization tooling
   - URL: https://github.com/dwavesystems/dwave-optimization
   - Verified point:
   - Public optimization tooling exists for nonlinear / QUBO-like optimization workflows.
   - This validates the optimization path, but not yet the exact Pulse claim that there are blue-PHOLED-specific host-dopant QUBO examples already validated in production.

## Preliminary Validation Notes
- The public record supports a real `March-April 2026` UDC cluster around emissive-layer materials, organometallic ligands, and host/process design.
- The Pulse wording is directionally useful but slightly compressed:
  - `blue PHOLED` is the strategic frame.
  - the directly verifiable public documents are broader `OLED emissive layer / PHOLED platform / host-mixture / organometallic materials` artifacts.
- The Idemitsu signal is real at the patent level, but the exact Pulse phrasing `2026년 3월 특허` did not map one-to-one to a single public page during this pass. The closest validated competitive anchor is patent `12538638`.
- The simulation tools are genuine and useful, but they solve different layers of the stack:
  - `TMMax / TMM-Fast`: planar optical stack simulation
  - `grcwa`: patterned optical structures and differentiable optimization
  - none of them alone are a lifetime predictor for blue PHOLED chemistry

## Research Hypotheses
- The strongest reading is not `UDC has publicly solved blue PHOLED`, but `UDC is aligning molecule design, host/process integration, and stack-level architecture around a PHOLED roadmap`.
- Idemitsu's validated public patent reinforces that `host engineering + multi-emissive-layer structure + energy alignment` remains a core competitive axis for lifetime.
- A realistic `multiscale` stack for this topic should run:
  - molecular descriptors / DFT / TD-DFT
  - host-emitter energy alignment and exciton management
  - kinetic or degradation modeling
  - TMM/RCWA optical extraction simulation
  - accelerated aging and device validation

## Open Questions
- Which of the latest UDC April 2026 applications are explicitly blue-targeted, versus platform-wide ligand patents?
- Is there public experimental evidence tying the one-crucible carbazole/triazine host mixture directly to blue PHOLED lifetime improvements?
- Which parts of the lifetime problem are optical, and which require chemistry/degradation simulation beyond TMM/RCWA?
- Are there public QUBO case studies specifically for OLED host-dopant screening, or is Pulse extrapolating from general materials optimization tooling?
