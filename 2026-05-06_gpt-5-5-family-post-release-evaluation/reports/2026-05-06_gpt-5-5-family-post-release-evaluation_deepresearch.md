---
title: GPT-5.5 Family Post-release Evaluation Deep Research
date: 2026-05-07
author: 김현중 with Codex Agent | AI Governance Team
status: draft-final
language: ko
tags:
  - ai-tech-review
  - openai
  - gpt-5-5
  - model-evaluation
  - hallucination
  - agentic-ai
---

# Executive Summary

## 10 conclusions

1. **Fact**: OpenAI는 2026-04-23 `GPT-5.5`를 발표했고, 2026-04-24 업데이트에서 `GPT-5.5`와 `GPT-5.5 Pro`의 API 제공 계획과 가격을 명시했습니다. 공식 포지셔닝은 coding, online research, data analysis, document/spreadsheet creation, software operation, tool use를 하나의 real-work model narrative로 묶고 있습니다. [OpenAI, 2026-04-23](https://openai.com/index/introducing-gpt-5-5/)
2. **Fact**: `GPT-5.5 Pro`는 공개 자료 기준 별도 architecture로 설명되지 않습니다. System card는 Pro를 같은 underlying model에 parallel test-time compute 설정을 더한 variant로 설명합니다. [OpenAI System Card, 2026-04-23](https://deploymentsafety.openai.com/gpt-5-5)
3. **Fact**: `GPT-5.5 Instant`는 2026-05-05 ChatGPT 기본 모델로 배포되기 시작했고, 공식 기준 baseline은 `GPT-5.3 Instant`입니다. OpenAI는 `GPT-5.4 Instant`라는 모델이 없다고 명시했습니다. [OpenAI Instant System Card, 2026-05-05](https://deploymentsafety.openai.com/gpt-5-5-instant)
4. **Fact**: OpenAI의 발표 표에서 GPT-5.5는 Terminal-Bench 2.0 82.7%, SWE-Bench Pro 58.6%, OSWorld-Verified 78.7%, BrowseComp 84.4%, FrontierMath Tier 4 35.4%를 기록했습니다. 같은 표에서 Claude Opus 4.7은 SWE-Bench Pro 64.3%, OSWorld-Verified 78.0%, BrowseComp 79.3%, FrontierMath Tier 4 22.9%로 제시됩니다. [OpenAI, 2026-04-23](https://openai.com/index/introducing-gpt-5-5/)
5. **Fact**: OpenAI는 GPT-5.5 평가가 `reasoning effort = xhigh`와 research environment에서 수행됐고, production ChatGPT 출력과 약간 다를 수 있다고 명시했습니다. [OpenAI, 2026-04-23](https://openai.com/index/introducing-gpt-5-5/)
6. **Fact**: Artificial Analysis는 2026-04-23 GPT-5.5 xhigh가 Intelligence Index 1위라고 평가하면서도 AA-Omniscience에서 accuracy 57%, hallucination rate 86%를 보고했습니다. 같은 글은 Opus 4.7 max hallucination 36%, Gemini 3.1 Pro Preview 50%를 비교값으로 제시했습니다. [Artificial Analysis, 2026-04-23](https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model/)
7. **Fact**: Scale MCP Atlas는 1,000개 task, 36개 MCP server, 220개 tool을 쓰는 real-world tool-use benchmark입니다. 2026-04 업데이트 기준 GPT-5.5 xhigh는 75.3%, GPT-5.4 xhigh는 70.6%, Claude Opus 4.7 max는 79.1%로 제시됩니다. [Scale Labs MCP Atlas](https://labs.scale.com/leaderboard/mcp_atlas)
8. **Fact**: UK AISI는 2026-04-30 GPT-5.5가 장기 사이버 task에서 강한 성능을 보인다고 평가했고, end-to-end cyber range와 reverse engineering 사례를 공개했습니다. AISI는 이러한 능력이 long-horizon autonomy, reasoning, coding 개선의 부산물일 가능성을 언급했습니다. [UK AISI, 2026-04-30](https://www.aisi.gov.uk/blog/our-evaluation-of-openais-gpt-5-5-cyber-capabilities)
9. **Inference**: GPT-5.5의 가장 믿을 만한 강점은 단일 정답 지식보다 긴 작업을 계속 밀고 가는 능력에 있습니다. Terminal-Bench, OSWorld, MCP Atlas, cyber range, Codex token-efficiency 주장은 모두 planning, tool selection, error recovery, sustained execution 쪽으로 수렴합니다.
10. **Inference**: hallucination 개선은 부분적으로 사실이지만 decision-relevant factuality 개선으로 바로 환산하면 위험합니다. OpenAI Instant 평가는 선택된 high-stakes, user-flagged, factuality-heavy prompt set이고, Artificial Analysis는 모를 때 멈추지 않는 answer-when-uncertain 성향이 여전히 크다고 봅니다.

## Model advances

GPT-5.5 family의 변화는 세 층으로 나누어 읽어야 합니다. `GPT-5.5 Thinking`은 complex real-world work를 위한 reasoning/tool-use model입니다. `GPT-5.5 Pro`는 같은 model family 위에서 parallel test-time compute를 더 쓰는 고정확도 설정입니다. `GPT-5.5 Instant`는 ChatGPT 기본 경험을 더 짧고 개인화되고 factuality가 높은 방향으로 조정한 daily-driver model입니다. OpenAI API 문서는 GPT-5.5의 default reasoning effort가 `medium`이라고 설명하고, `low`, `high`, `xhigh`를 task risk와 latency/cost에 맞추어 조정하라고 안내합니다. [OpenAI API docs](https://developers.openai.com/api/docs/guides/latest-model)

## Performance

성능 향상은 broad하지만 균일하지 않습니다. OpenAI 표에서는 Terminal-Bench 2.0, OSWorld-Verified, BrowseComp, FrontierMath, Graphwalks 1M context에서 GPT-5.4 대비 의미 있는 개선이 보입니다. 그러나 SWE-Bench Pro에서는 GPT-5.5 58.6%가 Claude Opus 4.7 64.3%보다 낮고, MCP Atlas에서도 GPT-5.5 xhigh 75.3%는 Claude Opus 4.7 max 79.1%보다 낮습니다. 이 차이는 GPT-5.5가 약하다는 뜻보다 benchmark별 task surface, harness, tool budget, reasoning effort, possible memorization caveat를 함께 봐야 한다는 뜻에 가깝습니다. [OpenAI](https://openai.com/index/introducing-gpt-5-5/) [Scale Labs](https://labs.scale.com/leaderboard/mcp_atlas)

## Hallucinations

OpenAI는 GPT-5.5 Instant가 GPT-5.3 Instant 대비 high-stakes prompts에서 hallucinated claims를 52.5% 줄였고, user-flagged factual-error conversations에서 inaccurate claims를 37.3% 줄였다고 발표했습니다. 다만 Instant system card는 이 factuality eval들이 production prevalence를 측정하지 않는다고 선을 긋습니다. Artificial Analysis는 별도 private benchmark에서 GPT-5.5 xhigh가 가장 높은 factual accuracy를 보였지만 hallucination rate가 86%라고 보고했습니다. 따라서 지금의 결론은 “factual knowledge와 일부 내부 factuality set은 개선됐지만, uncertainty calibration과 answer-when-uncertain control은 독립적으로 검증해야 한다”입니다. [OpenAI Instant](https://openai.com/index/gpt-5-5-instant/) [OpenAI Instant System Card](https://deploymentsafety.openai.com/gpt-5-5-instant) [Artificial Analysis](https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model/)

# Background

## Scope

이 보고서는 2026-05-06 기준 공개 자료를 바탕으로 GPT-5.5 family를 평가합니다. 분석 단위는 세 개입니다.

| Variant | Public role | Baseline | Primary comparison risk |
|---|---|---|---|
| GPT-5.5 / GPT-5.5 Thinking | complex work, coding, research, tool use, long-context reasoning | GPT-5.4 Thinking | xhigh research eval과 production setting이 다를 수 있음 |
| GPT-5.5 Pro | hardest tasks, higher-accuracy work, long-running workflows | GPT-5.4 Pro | 같은 underlying model의 parallel test-time compute setting이므로 architecture claim 금지 |
| GPT-5.5 Instant | ChatGPT default, everyday Q&A, concise/personalized response | GPT-5.3 Instant | product-layer personalization과 model factuality를 분리해야 함 |

## Release timeline

| Date | Event | Evidence |
|---:|---|---|
| 2026-04-23 | OpenAI publishes `Introducing GPT-5.5`; GPT-5.5 rolls out to Plus, Pro, Business, Enterprise in ChatGPT and Codex; GPT-5.5 Pro rolls out to Pro, Business, Enterprise in ChatGPT. | [OpenAI release](https://openai.com/index/introducing-gpt-5-5/) |
| 2026-04-23 | GPT-5.5 System Card published. It defines GPT-5.5 Pro as same underlying model with parallel test-time compute setting. | [System card](https://deploymentsafety.openai.com/gpt-5-5) |
| 2026-04-24 | OpenAI updates release/system card with API deployment and safeguard details. | [System card](https://deploymentsafety.openai.com/gpt-5-5) |
| 2026-04-30 | UK AISI publishes cyber capability evaluation of OpenAI GPT-5.5. | [UK AISI](https://www.aisi.gov.uk/blog/our-evaluation-of-openais-gpt-5-5-cyber-capabilities) |
| 2026-05-05 | OpenAI releases GPT-5.5 Instant as ChatGPT default, replacing GPT-5.3 Instant. | [OpenAI Instant](https://openai.com/index/gpt-5-5-instant/) |
| 2026-05-05 | GPT-5.5 Instant System Card published. | [Instant system card](https://deploymentsafety.openai.com/gpt-5-5-instant) |
| 2026-05-06 | OpenAI Help Center article states GPT-5.5 Instant is the default for logged-in ChatGPT users and documents context windows/tool support. | [Help Center](https://help.openai.com/en/articles/11909943-gpt-53-and-gpt-55-in-chatgpt) |

## Why it matters now

GPT-5.5가 중요한 이유는 benchmark crown 자체보다 deployment boundary가 바뀌고 있기 때문입니다. 이 family는 ChatGPT 기본 모델, Codex 작업 모델, API agent model, Pro 고정확도 model, cyber trusted-access narrative를 동시에 건드립니다. 한 모델 release가 product default, developer cost curve, enterprise governance, safety capability threshold를 함께 흔드는 상황입니다.

# State of the Art

## Official claims

OpenAI의 공식 주장은 여섯 가지로 정리됩니다.

- **Agentic execution**: GPT-5.5가 messy multi-part task를 plan, tool use, self-check, ambiguity navigation, continuation으로 처리한다고 설명합니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/)
- **Coding and terminal work**: Terminal-Bench 2.0 82.7%, SWE-Bench Pro 58.6%, Expert-SWE internal 73.1%를 제시합니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/)
- **Knowledge work**: GDPval 84.9%, OfficeQA Pro 54.1%, FinanceAgent 60.0%를 제시합니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/)
- **Tool use and browsing**: BrowseComp 84.4%, GPT-5.5 Pro 90.1%, Tau2-bench Telecom 98.0%를 제시합니다. Tau2-bench는 original prompts, no prompt adjustment 조건이라고 명시합니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/)
- **Long context**: Graphwalks 1M과 MRCR 512K-1M에서 GPT-5.4보다 큰 개선을 제시합니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/)
- **Instant factuality**: GPT-5.5 Instant가 GPT-5.3 Instant 대비 high-stakes hallucinated claims 52.5% 감소, flagged conversations inaccurate claims 37.3% 감소를 보였다고 발표합니다. [OpenAI Instant](https://openai.com/index/gpt-5-5-instant/)

## Independent and external validation

독립 검증은 official narrative를 부분적으로 지지하면서도 다르게 읽어야 할 지점을 남깁니다.

- **Artificial Analysis**는 GPT-5.5 xhigh를 Intelligence Index 1위로 평가했습니다. 동시에 AA-Omniscience hallucination rate 86%라는 강한 경고 신호를 제시했습니다. 이는 knowledge recall이 좋아져도 uncertainty calibration이 별도 문제로 남을 수 있다는 뜻입니다. [Artificial Analysis](https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model/)
- **Scale MCP Atlas**는 GPT-5.5 xhigh가 GPT-5.4 xhigh보다 개선됐다고 보고하지만, Claude Opus 4.7 max와 Gemini 3.1 Pro Preview high보다 낮게 배치합니다. 이 benchmark는 real MCP server, noisy tool menu, claim-level LLM judging을 쓰기 때문에 enterprise agent 평가에 직접적인 의미가 있습니다. [Scale Labs](https://labs.scale.com/leaderboard/mcp_atlas)
- **UK AISI**는 GPT-5.5의 cyber capability가 장기 autonomy, reasoning, coding 개선과 함께 상승하고 있다고 봅니다. 이는 safety risk와 defender utility가 동시에 커진다는 신호입니다. [UK AISI](https://www.aisi.gov.uk/blog/our-evaluation-of-openais-gpt-5-5-cyber-capabilities)
- **SWE-Bench Pro paper and Scale public page**는 long-horizon software engineering benchmark의 contamination-resistance, public/private/held-out split, strict resolve-rate definition을 설명합니다. OpenAI release의 58.6% row와 Scale public leaderboard의 current entries는 같은 harness인지 바로 단정할 수 없으므로 report-level 비교에서는 caution으로 남깁니다. [arXiv](https://arxiv.org/abs/2509.16941) [Scale SWE-Bench Pro](https://labs.scale.com/leaderboard/swe_bench_pro_public)

# Technical Deep Dive

## Reasoning behavior

**Fact**: OpenAI API 문서는 GPT-5.5가 `medium` reasoning effort를 default로 사용한다고 설명합니다. `low`는 efficient reasoning, `medium`은 latency/performance 균형, `high`는 complex agentic tasks, `xhigh`는 hardest asynchronous agentic tasks나 intelligence-bound evals에 쓰라고 안내합니다. [OpenAI API docs](https://developers.openai.com/api/docs/guides/latest-model)

**Inference**: GPT-5.5의 benchmark superiority를 읽을 때 effort setting을 반드시 함께 봐야 합니다. OpenAI release의 benchmark table은 xhigh research environment를 기본으로 둡니다. production에서 medium이나 low를 쓰는 팀은 official headline 점수보다 낮은 ceiling을 보게 될 가능성이 있습니다.

**Deployment implication**: migration은 model slug만 바꾸는 방식보다 workload별 effort sweep으로 시작해야 합니다. 특히 tool-heavy workflow에서는 `low -> medium -> high`를 순차로 재평가하고, `xhigh`는 async, high-value, reviewable work에만 제한하는 편이 낫습니다.

## Tool use

GPT-5.5의 tool-use story는 두 방향으로 강합니다. OpenAI는 BrowseComp, MCP Atlas, Toolathlon, Tau2-bench Telecom을 공식 표에 넣었습니다. Scale MCP Atlas는 real MCP servers, 10-25 exposed tools, 3-7 required tools, plausible distractors, 100 max tool calls 조건에서 pass rate를 평가합니다. GPT-5.5 xhigh는 75.3%로 GPT-5.4 xhigh 70.6%보다 높지만 Claude Opus 4.7 max 79.1%보다는 낮습니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/) [Scale Labs](https://labs.scale.com/leaderboard/mcp_atlas)

**Inference**: GPT-5.5의 개선은 “tool을 부를 수 있다”보다 “큰 tool surface에서 적절한 tool을 고르고 중간 실패를 회복한다” 쪽으로 해석하는 편이 맞습니다. Scale의 failure analysis도 wrong tool selection, incorrect parameters, sequencing mistakes가 주요 failure category라고 설명합니다.

## Agentic execution

Terminal-Bench 2.0 82.7%, OSWorld-Verified 78.7%, CyberGym 81.8%, cyber range pass cases는 GPT-5.5가 장기 작업에서 더 강해졌다는 official narrative를 뒷받침합니다. UK AISI는 GPT-5.5가 reverse engineering과 end-to-end cyber range에서 구체적인 chain을 수행하는 사례를 공개했습니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/) [UK AISI](https://www.aisi.gov.uk/blog/our-evaluation-of-openais-gpt-5-5-cyber-capabilities)

**Caution**: agentic execution은 capability와 risk가 함께 증가하는 축입니다. 더 긴 rollout이 가능하면 defensive patching과 codebase migration이 좋아지지만, cyber misuse와 accidental destructive action도 같이 커집니다. OpenAI system card가 accidental data-destructive actions, user confirmations, cyber safeguards를 별도 항목으로 다루는 이유도 여기에 있습니다. [OpenAI System Card](https://deploymentsafety.openai.com/gpt-5-5)

## Long-context handling

OpenAI release는 Graphwalks BFS 1M에서 GPT-5.5 45.4%, GPT-5.4 9.4%, Claude Opus 4.6 41.2%를 제시합니다. Graphwalks parents 1M에서는 GPT-5.5 58.5%, GPT-5.4 44.4%, Claude Opus 4.6 72.0%입니다. MRCR 512K-1M에서는 GPT-5.5 74.0%, GPT-5.4 36.6%, Claude Opus 4.7 32.2%입니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/)

**Inference**: long-context behavior는 명확히 좋아졌지만 uniformly dominant하지 않습니다. Graphwalks parents 1M처럼 peer가 앞서는 row도 있습니다. 따라서 enterprise RAG나 long-document analysis에서는 context size보다 retrieval strategy, chunk provenance, citation verification, answer compaction이 여전히 더 큰 설계 변수입니다.

## Cost, latency, and token efficiency

**Fact**: OpenAI API pricing page는 standard short-context 기준 `gpt-5.5`를 input $5.00, cached input $0.50, output $30.00 per 1M tokens로 제시합니다. `gpt-5.5-pro`는 input $30.00, output $180.00입니다. `gpt-5.4`는 input $2.50, output $15.00입니다. [OpenAI pricing](https://developers.openai.com/api/docs/pricing)

**Fact**: OpenAI release는 GPT-5.5가 GPT-5.4보다 per-token latency를 유지하면서 더 높은 intelligence를 보이고 Codex tasks에서 fewer tokens를 사용한다고 주장합니다. Artificial Analysis도 GPT-5.5 xhigh가 자사 Index run에서 GPT-5.4 xhigh 대비 output tokens를 약 40% 적게 사용해, doubled per-token pricing의 상당 부분을 흡수했다고 평가했습니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/) [Artificial Analysis](https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model/)

**Inference**: unit token price만 보면 GPT-5.5는 GPT-5.4의 2배입니다. 그러나 agentic workflow에서는 retries, failed trajectories, review cycles, output verbosity가 총비용을 좌우합니다. GPT-5.5가 fewer attempts와 fewer tokens로 같은 outcome을 만들면 effective cost는 headline price보다 덜 나빠질 수 있습니다. 이 효과는 내부 eval 없이는 알 수 없습니다.

## Safety and deployment changes

OpenAI system card는 GPT-5.5를 Biological/Chemical과 Cybersecurity에서 High capability로 취급하고, API deployment safeguard update를 2026-04-24에 추가했습니다. Instant system card도 GPT-5.5 Instant를 첫 Instant 모델 중 High capability로 취급한다고 설명합니다. GPT-5.5 Instant는 deployed low reasoning effort이지만, xhigh reasoning effort에서는 preparedness eval performance가 High treatment를 정당화한다고 설명합니다. [GPT-5.5 System Card](https://deploymentsafety.openai.com/gpt-5-5) [GPT-5.5 Instant System Card](https://deploymentsafety.openai.com/gpt-5-5-instant)

**Caution**: capability category는 production user가 같은 capability를 그대로 얻는다는 뜻이 아닙니다. OpenAI는 safeguards, trust-based access, actor-level enforcement, confirmation policy, system-level mitigations를 별도 계층으로 둡니다. 모델 성능과 제품 접근권한을 분리해서 읽어야 합니다.

## Benchmark scorecard

| Benchmark | Task Type | Setup | GPT-5.5 Variant | Baseline | Peer Comparison | Caveat | Takeaway |
|---|---|---|---|---|---|---|---|
| Terminal-Bench 2.0 | Agentic coding / terminal workflows | OpenAI release table, xhigh research environment | GPT-5.5 82.7% | GPT-5.4 75.1% | Claude Opus 4.7 69.4%, Gemini 3.1 Pro 68.5% | Production ChatGPT may differ from research environment | Strong official signal for terminal-based execution |
| SWE-Bench Pro | Real GitHub issue resolution | OpenAI release table | GPT-5.5 58.6% | GPT-5.4 57.7% | Claude Opus 4.7 64.3%, Gemini 3.1 Pro 54.2% | OpenAI footnote references memorization evidence; Scale public page has different current harness context | GPT-5.5 improves slightly over GPT-5.4, but peer lead remains on this row |
| Expert-SWE | Internal long-horizon coding | OpenAI internal eval | GPT-5.5 73.1% | GPT-5.4 68.5% | Not provided | Internal only | Useful as direction, weak for external model selection |
| GDPval | Professional knowledge work | wins/ties metric | GPT-5.5 84.9%; GPT-5.5 Pro 82.3% | GPT-5.4 83.0%; GPT-5.4 Pro 82.0% | Claude Opus 4.7 80.3%, Gemini 3.1 Pro 67.3% | Task mix and judging matter | Broad knowledge-work improvement, but not a factuality guarantee |
| OSWorld-Verified | Computer use | Real computer environment tasks | GPT-5.5 78.7% | GPT-5.4 75.0% | Claude Opus 4.7 78.0% | Tool/UI environment details matter | GPT-5.5 is competitive at computer-use execution |
| BrowseComp | Browsing/search | Hard-to-find short-answer web search benchmark | GPT-5.5 84.4%; GPT-5.5 Pro 90.1% | GPT-5.4 82.7%; GPT-5.4 Pro 89.3% | Claude Opus 4.7 79.3%, Gemini 3.1 Pro 85.9% | BrowseComp authors note short-answer focus may not map to open-ended user distributions | Strong search-agent signal, especially Pro |
| MCP Atlas | Tool-use / MCP orchestration | 1,000 tasks, 36 MCP servers, 220 tools, 100 max tool calls | GPT-5.5 xhigh 75.3% | GPT-5.4 xhigh 70.6% | Claude Opus 4.7 max 79.1%, Gemini 3.1 Pro Preview high 78.2% | LLM-as-judge with claim scoring; public/private split | GPT-5.5 improves over GPT-5.4 but is not top on this external leaderboard |
| Tau2-bench Telecom | Customer-service agent workflow | Original prompts, no prompt adjustment; GPT-4.1 as user model | GPT-5.5 98.0% | GPT-5.4 92.8% | Not provided in OpenAI row | No prompt tuning is useful caveat, but peer comparison absent | Strong official signal for structured customer workflows |
| FrontierMath Tier 4 | Advanced math | OpenAI release table | GPT-5.5 35.4%; GPT-5.5 Pro 39.6% | GPT-5.4 27.1%; GPT-5.4 Pro 38.0% | Claude Opus 4.7 22.9%, Gemini 3.1 Pro 16.7% | Eval contamination/methodology unknown from table alone | Strong official high-difficulty reasoning signal |
| Graphwalks BFS 1M | Long-context graph reasoning | 1M context row | GPT-5.5 45.4% | GPT-5.4 9.4% | Claude Opus 4.6 41.2% | Different peer version row | Large long-context improvement over GPT-5.4 |
| Graphwalks parents 1M | Long-context graph reasoning | 1M context row | GPT-5.5 58.5% | GPT-5.4 44.4% | Claude Opus 4.6 72.0% | Different peer version row | Improved but not dominant across all long-context tasks |
| HealthBench Professional | Health capability and safety | Instant system card, length-adjusted | GPT-5.5 Instant 38.4 | GPT-5.3 Instant 32.9 | No peer row | Answer-length adjustment still benchmark-specific | Health-facing performance improves, but high-stakes deployment still needs controls |
| User-flagged factuality | Hallucination-prone historical conversations | OpenAI Instant internal eval with LLM grader and web access | GPT-5.5 Instant: inaccurate claims down 37.3% vs GPT-5.3 Instant | GPT-5.3 Instant | No peer row | Not representative production traffic | Good signal for known failure modes, not prevalence |
| High-stakes hallucinated claims | Medical/legal/finance prompts | OpenAI Instant internal eval | GPT-5.5 Instant: 52.5% fewer hallucinated claims vs GPT-5.3 Instant | GPT-5.3 Instant | No peer row | Targeted high-stakes prompt set | Directionally important, needs in-house replication |
| AA-Omniscience | Knowledge and hallucination | Artificial Analysis private benchmark | GPT-5.5 xhigh accuracy 57%, hallucination rate 86% | GPT-5.4 xhigh gain +14 pts mostly knowledge-driven | Opus 4.7 max hallucination 36%, Gemini 3.1 Pro Preview 50% | Private benchmark; not same as OpenAI Instant eval | Strong warning on answer-when-uncertain behavior |
| Cyber range / cyber tasks | Offensive/defensive cyber autonomy | OpenAI system card, UK AISI external evaluation | GPT-5.5 | GPT-5.4 Thinking, GPT-5.3 Codex in selected rows | AISI compares to frontier cyber models qualitatively | Safety safeguards and access policy alter real availability | Cyber capability has increased and needs governance |

# Industry Landscape

## Consensus

- GPT-5.5 is stronger than GPT-5.4 on many agentic, coding, tool-use, long-context, and professional-work benchmarks. This is supported by OpenAI tables, Artificial Analysis, Scale MCP Atlas, and AISI cyber work. [OpenAI](https://openai.com/index/introducing-gpt-5-5/) [Artificial Analysis](https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model/) [Scale Labs](https://labs.scale.com/leaderboard/mcp_atlas) [UK AISI](https://www.aisi.gov.uk/blog/our-evaluation-of-openais-gpt-5-5-cyber-capabilities)
- GPT-5.5 Pro should be interpreted as higher test-time compute rather than a separately disclosed architecture. [OpenAI System Card](https://deploymentsafety.openai.com/gpt-5-5)
- GPT-5.5 Instant is a product-default update with factuality and personalization claims, not the same evaluation object as GPT-5.5 Thinking/Pro. [OpenAI Instant](https://openai.com/index/gpt-5-5-instant/) [Help Center](https://help.openai.com/en/articles/11909943-gpt-53-and-gpt-55-in-chatgpt)

## Disagreement

- **Coding leadership**: OpenAI leads on Terminal-Bench 2.0 in its release table, while Claude Opus 4.7 leads on SWE-Bench Pro in the same table. This means “best coding model” depends on whether the team values terminal workflow, repo issue resolution, long-horizon execution, or specific scaffold compatibility.
- **Tool-use leadership**: OpenAI includes MCP Atlas and reports GPT-5.5 above GPT-5.4. Scale's external leaderboard still places Claude Opus 4.7 and Gemini 3.1 Pro Preview above GPT-5.5 xhigh. [Scale Labs](https://labs.scale.com/leaderboard/mcp_atlas)
- **Factuality narrative**: OpenAI Instant claims large reductions in selected hallucination-heavy evals. Artificial Analysis reports very high hallucination rate when the model should avoid unsupported answers. Both can be true because they test different behavior surfaces.

## Recurring critiques

- Benchmark rows often mix internal evals, external evals, public/private splits, tool access, prompt settings, and reasoning effort.
- LLM-as-judge metrics are useful but should not be treated as human adjudication.
- Longer answers can inflate open-ended benchmark scores; both GPT-5.5 and GPT-5.5 Instant system cards discuss answer-length adjustment in HealthBench. [GPT-5.5 System Card](https://deploymentsafety.openai.com/gpt-5-5) [Instant System Card](https://deploymentsafety.openai.com/gpt-5-5-instant)
- Production behavior differs from offline evals because product routing, safeguards, system prompts, tool availability, usage limits, and UI affordances change the model surface.

# Applications

## GPT-5.5

Best fit:

- coding agents that need codebase navigation, terminal use, tests, and validation
- research assistants with browsing, file analysis, citation checking, and long-context synthesis
- enterprise knowledge work where workflow completion matters more than one-shot answer brevity
- data analysis and document/spreadsheet generation with explicit acceptance criteria
- tool-heavy agents where medium/high effort can be evaluated against known task sets

Avoid or constrain:

- cheap high-volume short Q&A where GPT-5.4-mini or Instant-class models may be enough
- high-stakes factual answers without retrieval, uncertainty prompts, and human review
- uncontrolled long-running agents with write/delete permissions

## GPT-5.5 Pro

Best fit:

- hardest research questions, legal/technical review, executive-critical analysis
- asynchronous tasks where latency and cost are acceptable
- final-pass critique, model-comparison arbitration, complex codebase refactors
- search/browse tasks where additional test-time compute has shown a gain, such as BrowseComp Pro row

Avoid or constrain:

- routine customer support
- cost-sensitive batch extraction
- workflows where higher effort causes over-searching or verbose answers
- tasks lacking clear stop rules

## GPT-5.5 Instant

Best fit:

- ChatGPT default consumer and workplace assistance
- concise explanations, translation, technical writing, everyday research triage
- image/photo upload analysis in low-to-medium risk settings
- customer-facing chat where warmer tone and shorter answers matter

Avoid or constrain:

- medical, legal, financial, or compliance decisions without domain guardrails
- workflows where personalization sources could create privacy or provenance questions
- cases requiring deterministic source-grounded answers unless retrieval and citation policy are explicit

# Limitations

- **Undisclosed architecture**: Public sources do not disclose architecture details. Do not infer training mixture, parameter count, MoE routing, or hidden architecture changes.
- **Internal-eval bias**: Expert-SWE, investment banking tasks, some safety and factuality evaluations are internal or not fully reproducible.
- **Answer-length effects**: HealthBench scores require length adjustment because longer answers can score higher without being more useful. [OpenAI System Card](https://deploymentsafety.openai.com/gpt-5-5)
- **Offline-vs-production gaps**: OpenAI states release evals can differ from production ChatGPT. Product routing, safeguards, and system prompts matter.
- **Hallucination metric ambiguity**: Claim-level factual error, response-level factual error, unsupported citation, failure to admit uncertainty, and answer-when-uncertain are different metrics.
- **Benchmark contamination and memorization**: OpenAI footnotes SWE-Bench Pro with memorization evidence; SWE-Bench Pro authors also frame contamination resistance as a design goal. [OpenAI](https://openai.com/index/introducing-gpt-5-5/) [arXiv](https://arxiv.org/abs/2509.16941)
- **Missing independent replication**: GPT-5.5 Instant factuality claims currently rely on OpenAI internal eval descriptions.
- **Vendor framing**: OpenAI's release emphasizes real-work model narrative; external sources show a more mixed picture on tool-use leadership and hallucination behavior.

# Future Outlook

## Model advances

The next frontier is less about raw benchmark score and more about sustained execution under constraints. Expect improvements in memory over long rollouts, tool argument reliability, self-verification, sandboxed computer use, and lower-token reasoning. GPT-5.5's pricing and effort ladder already pushes teams to think in outcome cost rather than token price alone.

## Evaluation methodology

Future benchmark design will likely move toward private task sets, tool-state reproducibility, held-out enterprise codebases, long-horizon traces, provenance-aware judging, and production-like eval harnesses. SWE-Bench Pro and MCP Atlas both point in this direction, even though each has its own limits.

## Hallucination control

The field still has no single hallucination number that matters across workloads. Claim-level factuality, response-level error prevalence, citation support, calibration, refusal behavior, and retrieval-grounding all need separate measurement. GPT-5.5 makes this more visible because high capability and high answer-when-uncertain risk can coexist.

# Actionable Insights

## Recommendations for researchers

- Treat GPT-5.5 as a useful test case for separating reasoning power from calibration.
- Report effort settings, tool access, prompt scaffold, answer length, judge model, and production/offline status in every comparison.
- Do not use single benchmark leadership as a model-level conclusion.

## Recommendations for builders

- Start GPT-5.5 migration with representative workload evals, not global replacement.
- For agentic apps, define allowed side effects, stop rules, confirmation policy, tool provenance, retry budget, and audit logging.
- Use `medium` as the API baseline, evaluate `low` for latency-sensitive workflows, reserve `high/xhigh` for tasks with measurable incremental value.

## Recommendations for evaluators

- Build separate eval sets for claim-level errors, unsupported citations, uncertainty admission, refusal quality, and answer-when-uncertain behavior.
- Evaluate with and without tools. The difference matters.
- Score end-to-end workflow success, not only final answer fluency.

## Recommendations for executives

- Do not buy the model only for headline intelligence. Buy it where failed work is expensive and retry reduction matters.
- Use GPT-5.5 Pro for high-value asynchronous work, not as a blanket default.
- Treat GPT-5.5 Instant as a default user-experience improvement, not as proof that high-stakes factual risk is solved.

## Model-selection matrix

| Use case | Recommended variant | Reasoning effort | Controls | Decision note |
|---|---|---|---|---|
| Codebase refactor with tests | GPT-5.5 | medium -> high | sandbox, tests, diff review, revert-own-work policy | Strong default if acceptance tests exist |
| Complex bug investigation | GPT-5.5 Pro or GPT-5.5 high | high/xhigh for async | trace logs, tool budget, human checkpoint | Use Pro when the cost of missed root cause is high |
| Enterprise document Q&A | GPT-5.5 | medium | retrieval citations, source filters, unsupported-claim checks | Long context helps, but RAG design still matters |
| Daily assistant chat | GPT-5.5 Instant | product default | personalization controls, memory-source visibility | Good default for low-to-medium risk interactions |
| Customer support workflow | GPT-5.5 or Instant after eval | low/medium | policy tool, escalation, transcript audit | Tau2-bench signal is promising but domain eval required |
| Medical/legal/finance advice | GPT-5.5 with retrieval or domain model | medium/high | professional review, calibrated uncertainty, refusal/escalation | Instant factuality gains do not remove high-stakes controls |
| Cyber defense | GPT-5.5 under trusted access/enterprise controls | high/xhigh if authorized | identity, logging, scope, safe tooling, actor-level enforcement | Capability is valuable and risk-bearing |
| High-volume extraction/classification | GPT-5.4-mini/nano or Instant class first | none/low | schema validation, sampling QA | GPT-5.5 may be overkill |

## Hallucination-mitigation checklist

- Define factuality subtype: claim error, response error, unsupported citation, uncertainty failure, answer-when-uncertain.
- Separate closed-book, retrieval-grounded, web-browsing, and tool-use conditions.
- Require source citations for factual claims that affect decisions.
- Add “insufficient evidence” and “cannot determine from sources” as acceptable outputs in evals.
- Penalize unsupported specificity more than cautious incompleteness.
- Use adversarial prompts from prior internal failures, but label them as non-representative.
- Track response length because longer answers create more opportunities for both correct and false claims.
- Run calibration evals where the correct action is to abstain.
- Sample production traffic after deployment and compare to offline evals.
- Keep human review for medical, legal, financial, security, and irreversible operational actions.

# References

## Primary sources

- OpenAI. `Introducing GPT-5.5`. Published 2026-04-23, updated 2026-04-24. https://openai.com/index/introducing-gpt-5-5/
- OpenAI Deployment Safety Hub. `GPT-5.5 System Card`. Published 2026-04-23, updated 2026-04-24. https://deploymentsafety.openai.com/gpt-5-5
- OpenAI. `GPT-5.5 Instant: smarter, clearer, and more personalized`. Published 2026-05-05. https://openai.com/index/gpt-5-5-instant/
- OpenAI Deployment Safety Hub. `GPT-5.5 Instant System Card`. Published 2026-05-05. https://deploymentsafety.openai.com/gpt-5-5-instant
- OpenAI Help Center. `GPT-5.5 in ChatGPT`. Updated 2026-05-06. https://help.openai.com/en/articles/11909943-gpt-53-and-gpt-55-in-chatgpt
- OpenAI API docs. `Using GPT-5.5`. Accessed 2026-05-06. https://developers.openai.com/api/docs/guides/latest-model
- OpenAI API docs. `Pricing`. Accessed 2026-05-06. https://developers.openai.com/api/docs/pricing

## Benchmark sources

- Artificial Analysis. `OpenAI's GPT-5.5 is the new leading AI model`. Published 2026-04-23. https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model/
- Scale Labs. `MCP Atlas`. Updated April 2026. https://labs.scale.com/leaderboard/mcp_atlas
- Scale Labs. `SWE-Bench Pro (Public Dataset)`. Accessed 2026-05-06. https://labs.scale.com/leaderboard/swe_bench_pro_public
- Xiang Deng et al. `SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?` arXiv:2509.16941. Submitted 2025-09-21, revised 2025-11-14. https://arxiv.org/abs/2509.16941
- OpenAI. `BrowseComp: a benchmark for browsing agents`. Published 2025-04-10. https://openai.com/index/browsecomp/
- UK AI Security Institute. `Our evaluation of OpenAI's GPT-5.5 cyber capabilities`. Published 2026-04-30. https://www.aisi.gov.uk/blog/our-evaluation-of-openais-gpt-5-5-cyber-capabilities

## Secondary commentary

- Axios. `OpenAI makes default ChatGPT more personal`. Published 2026-05-05. https://www.axios.com/2026/05/05/openai-chatgpt-update-default-model
- TechCrunch. `OpenAI releases GPT-5.5 Instant, a new default model for ChatGPT`. Published 2026-05-05. https://techcrunch.com/2026/05/05/openai-releases-gpt-5-5-instant-a-new-default-model-for-chatgpt/
- TechCrunch. `OpenAI releases GPT-5.5, bringing company one step closer to an AI super app`. Published 2026-04-23. https://techcrunch.com/2026/04/23/openai-chatgpt-gpt-5-5-ai-model-superapp/
