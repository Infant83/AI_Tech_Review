# Jev: structured decisions in agent harnesses

Evidence cutoff: 2026-09-21. Korean canonical and English translation.

This review examines the interface and evidence for TypeSafe Jev, with an emphasis on calibration, agent evaluation and research workflows. The review does not call the Jev API or reproduce the benchmark.

## Evidence and attribution

| Material | Used for | Boundary |
|---|---|---|
| [TypeSafe announcement](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | Launch date, names and headline comparison conditions | Vendor claims, not independent measurements |
| [Official concepts](https://docs.typesafe.ai/concepts/system-one) and primitive pages | Input, typed outputs and request example | Interface description, not reconstructed network architecture |
| [Confidence](https://docs.typesafe.ai/confidence) and [AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer) | Probability, concentration and RLCD intent | No invented reward function or confidence formula |
| [Models](https://docs.typesafe.ai/models) | jev-1.13.0, price, two context budgets, language caveat | Snapshot; aliases and service specifications can change |
| [Jev 1.13 limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13) | Arithmetic, long context, adversarial inputs and cross-question consistency | Vendor-disclosed limitations |
| [LangChain experiment](https://www.langchain.com/blog/jev-agent-evals-langsmith) | Five frozen cases, 100 repeats, one reviewer, settings | Early experiment; not 500 independent tasks |
| [Pinned evaluation repository](https://github.com/danielgshea/jev-as-a-judge/tree/adfea74905f721ea2594e22804c8c8edf1693163) | Reported latency, cost and agreement table | Read-only inspection; no benchmark execution |
| [Pinned aggregate JSON](https://github.com/danielgshea/jev-as-a-judge/blob/adfea74905f721ea2594e22804c8c8edf1693163/assets/benchmark-jev-luna-terra-sonnet/6d08df72-c878-458c-b7c5-a7824ee6e721/benchmark.json) | Case count, repetitions, mean within-case variances and ratio arithmetic | Aggregates checked; individual repeated judgments not independently recomputed |
| [Guo et al., ICML 2017](https://proceedings.mlr.press/v70/guo17a.html) | Background on calibration | Not a Jev evaluation |
| [ModernBERT](https://arxiv.org/abs/2412.13663) | Existing encoder-classifier baseline family | No direct Jev comparison reported |

Social discovery: a public [Sergii Shcherbak LinkedIn post](https://www.linkedin.com/posts/sergii-shcherbak-10068866_typesafe-ai-has-introduced-jev-its-first-activity-7505969687915094017-zlGD) links to the announcement. Technical claims were checked against primary material. No private feed, email or conversation content is included in the public package.

## Rebuild

Python with matplotlib is required for the data chart. The rest uses the standard library.

```sh
python 2026-09-21_jev-structured-decisions-agent-harnesses/build.py
python scripts/publish_public_site.py --review 2026-09-21_jev-structured-decisions-agent-harnesses
```

`benchmark_summary.csv` contains the small reported-value table used by `build.py`; these are rounded source means, not new measurements. The latency chart has a zero baseline and no invented error bars. `decision_flow_*.svg` are original conceptual harness diagrams. The 20%-of-runtime, 100-times-stage-speed example is illustrative arithmetic, not a Jev result.

Only final HTML, the generated WebP hero, CSS and SVG figures are published under the review's site directory. Public code and attribution live in this source package. Third-party captured runs and full source text are not redistributed.

## Authorship and review scope

Responsible editor: Hyun-Jung Kim. AI assistance: Codex, one agent, primary-source inspection, bilingual writing, scientific copyediting, figure creation and publication checks. Exact model identifier not retained. AI Tech Review Editorial Harness 2026.08. No separate verification agent or line-by-line human review is claimed.

Copyediting audit: removed generic importance claims and repeated rhetorical contrasts; retained numerical values, sample boundaries, type-versus-correctness and API-versus-proposal distinctions; training internals, broad calibration and workload generalization remain unresolved.
