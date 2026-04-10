# Deep Research Prompt - QUBO for OLED Host-Dopant Optimization

## Topic

Assess the `2026-04-10` GPT Pulse item about executable `host-dopant QUBO` examples, identify the real source base behind that claim, and evaluate how directly those examples apply to OLED host-dopant optimization.

## Target Audience

- engineers working on materials informatics, display materials, and simulation workflows
- technical managers deciding whether QUBO/quantum-annealing tooling is worth near-term attention

## Research Questions

1. What exactly does the Pulse QUBO card appear to compress into a single summary?
2. What does `MatOpt-bench` actually provide, and what problem classes are included in its QUBO example?
3. What does the `Science Advances` / `QA_solid_solutions` workflow actually do with D-Wave quantum annealers?
4. Which claims are directly supported by public evidence:
   - executable QUBO examples
   - chemical-potential tuning
   - hardware-aware formulation choices
   - application to optoelectronic materials
5. What parts of OLED host-dopant optimization map poorly to this solid-solution QUBO framing?
6. What parts of the OLED workflow could still plausibly benefit from a QUBO layer in the near term?
7. As of `2026-04-10`, is there any public evidence that OLED host-dopant QUBO is a validated mainstream workflow rather than an exploratory candidate-ranking approach?

## Required Source Priorities

1. Pulse local snapshot and local workspace notes
2. official or primary repositories
   - MatOpt-bench
   - QA_solid_solutions
3. primary paper / publisher or PMC version
   - `Exploring the thermodynamics of disordered materials with quantum computing`
4. official D-Wave documentation
5. primary OLED host/dopant design literature for comparison

## Deliverables

- a short memo for Obsidian capture
- a deeper report with:
  - fact vs interpretation separation
  - source-backed decomposition of the Pulse claim
  - applicability analysis for OLED host-dopant optimization
  - explicit uncertainty statement
  - concrete next actions for an engineering team

## Version / Date Sensitivity

- Use exact dates for repository metadata, paper publication timing, and Pulse snapshot timing.
- Treat current findings as `as of 2026-04-10`.

## Comparison Points

- `solid-solution QUBO on fixed lattice` vs `OLED host-dopant design`
- `hard composition constraints` vs `chemical potential approach`
- `QUBO/BQM` vs `richer nonlinear/hybrid optimization`
- `candidate prioritization layer` vs `full predictive design loop`

## Risks And Uncertainties To Validate

- Over-reading a materials benchmark as an OLED-specific workflow
- Assuming D-Wave example code and MatOpt-bench are the same asset
- Assuming a QUBO reduction is expressive enough for the real OLED design problem
- Confusing optoelectronic material examples like `AlGaN` with organic emitter-host engineering
