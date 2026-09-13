# Source ledger and selection record

Evidence window: 2026-09-06 through 2026-09-12. Inspection: 2026-09-13. Starting main: `115e167398a26a9222dc413f8ce550261de39445` (includes dedicated quantum-vacuum cover correction).

## Selection

Scores are editorial judgments, not measurements of paper quality. Columns follow the requested 25/25/20/15/10/5 weights.

| Candidate | Importance | Novelty/evidence | Research fit | Use/follow-up | Explainability | Timeliness | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Avatar: placement of reasoning in scientific workflow control | 23 | 21 | 20 | 14 | 10 | 5 | 93 | Selected: controlled architecture, negative and positive results, Agent Systems gap |
| ADMET-EvO: evidence-gated scientific iteration | 22 | 21 | 19 | 13 | 9 | 5 | 89 | Strong follow-up candidate, but closer to recent molecular/Materials AI coverage; task-normalized headline needs detailed metric audit |
| AgentIdeaBench: active retrieval versus static ideation | 23 | 21 | 17 | 12 | 9 | 5 | 87 | Valuable evaluation question; critic-based originality and unexecuted hypotheses differ from operational control |
| Anthropic September threat-intelligence report | 24 | 19 | 15 | 13 | 7 | 5 | 83 | Primary industrial source; retrospective cases and provider attribution require a dedicated governance article |

Other discovery queries covered frontier-model evaluations, inference memory and hardware. No equally compelling verified new hardware result was selected. These searches are not an exhaustive claim about all publications. University and national-laboratory evidence drives the selected article; industrial evidence was considered in selection, not made into a second article.

## Duplicate audit

All 26 published manifest records and their Korean public pages were scanned for titles, summaries, section claims and external references. The inventory includes all entries dated in the preceding 12 weeks and older entries, including the May Agent Systems, Frontier Models and Governance articles. Latest relevant DeMARS text was read in detail. Avatar / 2609.10509, ADMET-EvO / 2609.10121 and AgentIdeaBench / 2609.07611 were absent from public review bodies before this addition. A generated inventory preserves headings, summaries and unique citations for comparison.

Category counts before addition: Materials AI 7; AI for Science 3; Quantum Computing 10; AI Hardware 2; AI Governance 1; Quantum AI 1; Frontier Models 1; Agent Systems 1. Date labels alone do not prove coverage: the June 17 hardware article and May agent/harness articles were also inspected. The new review links the September 6 DeMARS article and May 9 harness review in its opening. It does not repeat the quantum or OLED brief; QM9 appears only to characterize a workflow-control test.

### Pre-push main recheck

Main advanced to `c036d5efe539fcf7f0b1b9bc3888589713a297dd` during this run, adding the September 13 multiphoton-reservoir review. Its full Korean review, summary and references were inspected. It concerns optical feature maps and photon-counting evidence, not scientific-workflow control, and does not duplicate Avatar. The inventory was regenerated for all 27 prior reviews. The new review and the upstream OLED page repairs were preserved when integrating main; final hub validation covers 28 cards. All 27 upstream manifest entries are unchanged.

## Sources

| ID | Primary source | Date/version | Inspection and role |
|---|---|---|---|
| A | https://arxiv.org/abs/2609.10509v1 and https://arxiv.org/html/2609.10509v1 | Submitted 2026-09-09; v1; preprint | Full HTML text, §§III–VI. Actual experiment dates not stated. No experiment-specific public code link identified. CC BY-NC-SA 4.0 displayed; no source figure copied. |
| B | https://academy-agents.org/ and https://github.com/academy-agents/academy | Live documentation inspected 2026-09-13; not a new-week release claim | Stateful actors, action interfaces, asynchronous messages; public code is not Avatar experiment code. |
| C | https://colmena.readthedocs.io/en/latest/ | Live documentation inspected 2026-09-13 | Background only, established scientific steering framework. |
| D | https://kylechard.com/ | Live profile inspected 2026-09-13 | University of Chicago Research Associate Professor and Argonne researcher. Suman Raj affiliations come from A, without role inflation. |
| E | https://arxiv.org/abs/2609.10121 | Submitted Sep 9, revised Sep 10 (v2) | Candidate abstract/version metadata; v1 full-text sampling. NOT a full v2 audit; not included as article evidence. |
| F | https://arxiv.org/abs/2609.07611 and https://arxiv.org/html/2609.07611v1 | Submitted Sep 7, 2026 | Candidate evaluation design and main findings inspected. Not selected. |
| G | https://www.anthropic.com/threat-intelligence-report-september-2026 | September report; Sep 10 publication reported by dated news discovery; primary describes Dec 2025–Aug 2026 incidents | Introduction and declared observation scope inspected. Publication and incident dates separated. No incident-specific claims reproduced in review. |

## Protected claims and boundaries

| Claim | Location in A | Qualifier preserved |
|---|---|---|
| M0 rules throughout; M1 LLM provenance diagnosis; M2 LLM provenance and orchestration, executor still rules | §IV | Three actors does not mean three LLM decision-makers |
| Python 3.12; Academy 0.5.0; Parsl 2026.3.9; local exchange; `open-ai/gpt-oss-20b` on Sophia | §IV and §V-A | Single-node compute testbeds, not distributed multi-site deployment |
| E1 p=0.35, permanent-failure fraction parameter x=1/3 | §V-A | Synthetic injected errors, not real electronic-structure failure corpus |
| Up to ~55% wasted-compute reduction | Abstract, contributions, §V-B/Fig.5 context | Maximum conditional claim, not total wall time; no exact point digitized from missing HTML graphics |
| E2 mean backlog ~21 M0/M1 and ~99 M2, N=128 | §V-B | Counts of waiting tasks; not accuracy; 0.2 s is sampling interval, not assumed policy frequency |
| E3 5,000 QM9 candidates, 100 seeds, B=32; GPU MLP on Morgan fingerprints | §V-A | Greedy surrogate selection; fixed data lookup, not new DFT or molecular synthesis |
| E3 baseline/M0/M1 12 rounds, M2 7; same best gap; ~40% less GPU-busy time | §V-B | Not energy, total cost, total wall time, or future-seed guarantee |
| Quadro RTX 6000, CUDA 12.2; one GPU, requested 16 CPU cores | §V-A | Campaign hardware, not identified inference-service hardware |
| E1/E2 CPU configuration | §V-A | Xeon Gold 6248R 3 GHz, 48 CPU cores, 192 GB RAM; added to final text for reproducibility |
| Best gap 0.3997 | §V-B | Omitted from quantitative tables: main-text unit insufficient; do not infer eV/Hartree |
| ~1,200 unchanged core lines | §V-B | Author assertion; no byte-identity check performed |
| 5/12 = 41.666…% | Reviewer arithmetic | Not a recomputation of GPU time |
| Expected-benefit equation and two-timescale figure | Reviewer proposal | Not a result/equation from Avatar; costs in a common unit; no stability guarantee |

## Review scope

One Codex agent, no subagents. Exact runtime model identifier not preserved. Built-in image generation, web research, GitHub tools, shell/Python rendering and validation, browser UI inspection. No independent benchmark reproduction, no external review and no line-by-line human review. Source prose was checked with the scientific copyediting publication workflow; preserved facts are listed above. Do not describe this as independent scientific validation.

These notes and inventories are repository support material and must not be copied into the Pages review directory. Public licensing/attribution and preparation disclosure are in the final text.
