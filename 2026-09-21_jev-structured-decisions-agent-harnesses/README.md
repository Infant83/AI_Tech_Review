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

## Follow-up: shared LinkedIn post (2026-09-21)

The user supplied https://lnkd.in/p/guwDmcaA, resolving to the public post by 차예솔 (Peter Cha), activity 7507419610468503552. The post was read as public HTML. Its external-link pages identify browser-use/jev-ultrafast, standardagents/jevpilot and the TypeSafe launch. Only a short attributed summary is republished, not the post or captured third-party files.

| Evidence | Finding | Boundary |
|---|---|---|
| Jev Ultrafast, commit `1231850a0bf1a0c0341fe408ef1668dbbfdfac46`, README and `jev_ultrafast/agent.py` | Indexed observed controls; operation and targets; text-helper handoff; stale-state handling | Code inspection, no execution or API calls |
| Same commit, `docs/flights-measurement.json` and `docs/performance.md` | 7.073 seconds; 17 Jev requests; 2 Mercury 2.5 calls; 90,558 input tokens | Initial navigation/setup and independent final verification outside timer; search only, not booking |
| Token arithmetic at $0.042 / million plus reported helper charge | $0.003803436 + $0.00006272 = $0.003866156 | Jev dollar amount estimated, browser/hosting/development excluded |
| `docs/full-speed-measurement.json` | 3 runs per implementation, both 3/3; medians 9.450 → 7.092 seconds and 1,092 → 101 protocol calls | Runtime-code comparison holding models fixed; one task; no general reliability inference |
| JevPilot, commit `e1beeb13b9a928fb76f167f86af584f4ce9cf180`, README, `src/jev-request.js`, `server/jev.js` | Local candidate construction, single-option resolution, validated selection and imminent-collision rejection | Simulation only; no camera perception or road-safety validation |
| https://jev-trader.vercel.app/ | MON/USDC bid/ask interface; dry-run label, connecting/waiting state | No transactions, profitability claims, wallet connection or execution |
| https://docs.typesafe.ai/patterns/fan-out | Concurrent speculative questions with code selecting the relevant branch | Interface pattern, not statistical-independence claim |

New `action_loop_ko.svg` and `action_loop_en.svg` are original explanatory figures, not screenshots or measured data. Existing benchmarks and the initial scope remain unchanged. The update adds a visible dated note, source links, bilingual sections and expanded authoring/verification disclosures.

Publication copyediting audit:
- Replaced broad novelty/speed rhetoric with the concrete model/executor division.
- Preserved source sample sizes, models, timing exclusions, price units and simulation boundaries.
- Remaining uncertainty: out-of-task reliability, deployment cost, broad calibration and trading outcomes; no independent rerun or separate verification agent.
