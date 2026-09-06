# Weekly topic selection and source ledger

Evidence cutoff: 2026-09-06

Primary observation window: 2026-08-30 through 2026-09-06

Context extension: up to 30 days where needed

## Duplicate check

`site/manifest.json` and every public review card were inspected. The latest twelve-week period is dominated by Quantum Computing and Materials AI. The closest prior articles are:

- `2026-05-09_ai-updates-weekly`: general agent harness engineering.
- `2026-05-23_ai-scientist-execution-harness`: broad AI-scientist verification.
- `2026-07-03_tabfm-tabular-foundation-model`: foundation models for structured materials/manufacturing data.

The selected review differs by examining a newly proposed unit of scientific software: complete delegation of one bounded computational-materials responsibility, with DeMARS as a current case and code availability as an explicit evidence boundary.

## Candidate scorecard

| Candidate | Importance /25 | Novelty & evidence /25 | Reader fit /20 | Use & follow-up /15 | Explainability /10 | Timeliness /5 | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Agentic programs / DeMARS (arXiv:2609.00795) | 24 | 19 | 20 | 15 | 10 | 5 | **93** |
| Human–AI theorem for 1D collective behavior (arXiv:2609.00322) | 20 | 17 | 19 | 10 | 8 | 5 | 79 |
| Causal foundation models tutorial (arXiv:2609.03003) | 20 | 18 | 14 | 13 | 9 | 5 | 79 |
| Context-window failures in relational foundation models (arXiv:2609.00460) | 21 | 19 | 13 | 12 | 9 | 5 | 79 |

The DeMARS paper won because it was posted within the seven-day window, directly links agentic software to computational materials science, supplies a bounded production case, and supports a high-value discussion of verification. Its evidence score is capped because it is a preprint, source code is unreleased, and the held-out evaluation omits critical denominators.

## Claim ledger

| Claim | Source | Status | Independent check / caveat |
|---|---|---|---|
| Paper posted 2026-09-01 | arXiv:2609.00795v1 metadata | source-reported, independently checked | arXiv abstract and HTML agree |
| Agentic program combines deterministic algorithms, bounded LLM judgment, task gates, episodic maturation, and complete production delegation | main paper, lines 40–58 in arXiv HTML | source-reported | architecture paraphrased, not independently executed |
| DeMARS matured across roughly 800 disordered CIFs | main paper, lines 74–82 | source-reported | no per-case log or public dataset |
| 100 held-out CIFs were processed without execution-time human intervention | main paper, lines 83–86 | source-reported | certification and refusal counts are not disclosed |
| Certified outputs were manually judged reasonable; refusals were evidence-backed | main paper, line 84 | source-reported | internal post-hoc manual inspection, no blinded external rubric |
| Ca/Th/F charge compensation gives 2 + 2 × 0.18 = 2.36 | main paper, lines 62–63 | source-reported and independently recalculated | arithmetic check only; not proof of unique disorder model |
| Current code is not public | main paper, code availability | independently checked against the paper's explicit statement | release promised upon peer-reviewed publication |
| ICSD disorder prevalence and taxonomy | Antypov et al. 2025 DOI 10.1107/S1600576725003000 | cited background | used only at the granularity reported by the DeMARS paper |
| SevenNet-family MLIP supports inexpensive repeated relaxation | Kim et al. 2026 DOI 10.1038/s41467-026-70195-8; DeMARS paper | source-reported context | no DeMARS runtime or DFT cross-check denominator disclosed |

## Primary and authoritative sources

1. https://arxiv.org/abs/2609.00795
2. https://arxiv.org/html/2609.00795v1
3. https://doi.org/10.1107/S1600576725003000
4. https://doi.org/10.1039/D5DD00019J
5. https://arxiv.org/abs/2606.09422
6. https://doi.org/10.1038/s41467-026-70195-8
7. https://doi.org/10.1038/s41586-026-10644-y
8. https://research.google/blog/science-one-framework-a-verifiable-autonomous-research-framework-via-chain-of-evidence/
9. https://doi.org/10.1038/s42256-026-01261-5

## Gap matrix

| Evidence gap | Why it matters | Review treatment |
|---|---|---|
| No DeMARS source or runnable package | Prevents replication and environment inspection | Publication is described as a preprint case study, not production validation |
| No certified/refused denominator for 100 CIFs | “Processed” cannot be interpreted as task success | Explicitly separated in summary, table, limitations, and follow-up tests |
| No repeated-run statistics | LLM decision stability is unknown | Proposed 5–10 repeats per CIF and version regression testing |
| No blind external evaluation or baseline | Internal reasonableness review can miss systematic errors | Proposed external crystallographer/computational-materials rubric |
| No DFT stratified cross-check rate | MLIP energy ordering is a separate model risk | Proposed DFT re-relaxation and ordering-preservation metric |

## Public-page asset provenance

- `agentic_programs_materials_hero.webp`: AI-generated conceptual image; no exact crystal or data represented.
- `agentic_program_architecture_ko.svg`, `agentic_program_architecture_en.svg`: reviewer-constructed deterministic diagrams based on the main paper's Figure 3 and architecture text; no source figure pixels reused.
