---
title: Deep research prompt - GPT-5.5 family post-release evaluation
date: 2026-05-06
source: user prompt + ChatGPT shared conversation
tags:
  - ai-tech-review
  - openai
  - gpt-5-5
  - deepresearch-prompt
---

# Deep Research Prompt

## 1. 역할 정의

You are a frontier-model research analyst specializing in post-release evaluation of large language models.

Investigate the OpenAI GPT-5.5 family, including GPT-5.5, GPT-5.5 Pro, and GPT-5.5 Instant.

Use current web research.
Prioritize primary sources first: official OpenAI release notes, system cards, deployment safety documents, API documentation, benchmark-provider pages, and academic papers.
Use reputable journalism and practitioner analysis only after primary-source review.
Do not invent undisclosed architecture details.
Distinguish model-level changes from product-layer changes, inference-time compute settings, prompting changes, and safety-policy changes.

## 2. 목표 정의

Assume the purpose is technical + strategic analysis.
Assume the audience is AI researchers, ML engineers, product leaders, and executives.
Assume the environment is web-enabled and cloud-based.
Assume the output is a markdown report.

Your goals are to determine:

- what is genuinely new in the GPT-5.5 family
- how strong the reported performance gains are
- whether hallucination and factuality have improved in a robust, decision-relevant way

Compare official claims against independent evaluations and field discussion.
Compare against GPT-5.4, GPT-5.4 Pro, GPT-5.3 Instant, and relevant frontier peers only when a like-for-like comparison exists.

Answer these questions:

1. What changed across GPT-5.5, GPT-5.5 Pro, and GPT-5.5 Instant?
2. Which gains look broad and durable, and which look benchmark-specific or product-specific?
3. How do results differ across coding, agentic computer use, browsing/search, knowledge work, and scientific or technical workflows?
4. How is hallucination being measured, and what do the numbers actually mean?
5. Where do independent evaluators support or challenge the official narrative?
6. What are the practical implications for model selection, deployment, prompting, and risk controls?

Mandatory themes:

- agentic execution
- tool use
- reasoning-effort settings
- token efficiency
- long-context behavior
- latency / cost / quality tradeoffs
- hallucination and factuality
- uncertainty calibration
- answer-when-uncertain behavior
- benchmark contamination / memorization debate
- internal-eval vs external-eval vs production-gap discussion

## 3. 리서치 프로세스

### STEP 1: 문제 정의

Define the scope clearly.
Separate GPT-5.5, GPT-5.5 Pro, and GPT-5.5 Instant.
Define comparison baselines and peer set.
Define evaluation axes: model advances, performance, hallucinations/factuality, and current field discussion.
Define hallucination subtypes separately:

- claim-level factual error
- response-level factual error
- unsupported citation
- failure to admit uncertainty
- answer-when-uncertain behavior

### STEP 2: 정보 수집

Collect current material from official OpenAI sources first.
Then collect benchmark-provider sources and academic papers.
Then collect reputable journalism, analyst coverage, and practitioner writeups that discuss results, caveats, or real-world experience.

At minimum, inspect benchmark families active in the current discussion, including:

- coding
- agentic work
- browsing/tool-use
- knowledge/hallucination
- health/safety
- professional-work benchmarks

Capture exact source dates, model variant names, reasoning-effort settings, tool access, and whether each evaluation is internal or external.

### STEP 3: 출처 검증

Label every source as:

- Primary
- Secondary
- Commentary

Check whether each comparison is like-for-like.
Verify:

- tool access
- prompt tuning
- answer-length sensitivity
- LLM-as-judge limitations
- contamination or memorization concerns
- offline-vs-production differences
- non-representative prompt sets

Reject claims that cannot be traced to an accessible source.
When official and independent results diverge, explain plausible reasons for divergence instead of forcing false consensus.

### STEP 4: 구조화

Build these artifacts before writing the final narrative:

- release timeline
- model-variant matrix
- benchmark scorecard
- hallucination-methodology table
- discussion map showing consensus, disagreement, and unresolved questions

Separate:

- official claims
- third-party validation
- critical commentary

### STEP 5: 인사이트 도출

Identify which advances look like genuine model improvements versus effects of:

- better prompting guidance
- more inference-time compute
- product integrations
- evaluation design

Separate raw accuracy from calibration.
Explicitly analyze the tension between "higher performance" and "still hallucinates when uncertain."
Identify:

- where GPT-5.5 appears strongest
- where peers still lead
- where the evidence is incomplete or not comparable

### STEP 6: 전략 해석

Translate the research into decisions.
State which GPT-5.5 variant seems best for which use cases.
State when GPT-5.5 should be preferred over earlier OpenAI models and when caution is warranted.
Recommend how teams should evaluate hallucination risk in-house rather than relying only on vendor metrics.
Explain what the current discussion implies for:

- enterprise deployment
- research workflows
- benchmark design

## 4. 출력 포맷

Produce the final report in the exact structure below.

# Executive Summary

Open with the 10 most important conclusions.
Use exact dates.
Mark each conclusion as Fact, Inference, or Speculation.
Include one short paragraph each on:

- model advances
- performance
- hallucinations

# Background

Summarize the GPT-5.5 family, the release timeline, the relevant model variants, and why the topic matters now.

# State of the Art

Describe the current competitive and technical position of GPT-5.5 relative to prior OpenAI models and frontier peers.
Separate official claims from independent validation.

# Technical Deep Dive

Analyze model advances in detail:

- reasoning behavior
- tool use
- agentic execution
- long-context handling
- cost/latency/quality tradeoffs
- documented safety or deployment changes

Include a benchmark table with these columns:

| Benchmark | Task Type | Setup | GPT-5.5 Variant | Baseline | Peer Comparison | Caveat | Takeaway |
|---|---|---|---|---|---|---|---|

# Industry Landscape

Summarize what benchmark providers, researchers, major tech press, and practitioners are saying.
Highlight:

- consensus
- disagreement
- recurring critiques

# Applications

Map the most credible use cases for:

- GPT-5.5
- GPT-5.5 Pro
- GPT-5.5 Instant

Cover:

- coding
- research
- enterprise knowledge work
- customer workflows
- high-stakes factual domains

# Limitations

List all important caveats, including:

- undisclosed architecture details
- internal-eval bias
- answer-length effects
- offline-vs-production gaps
- hallucination metric ambiguity
- contamination or memorization concerns
- missing independent replications
- vendor-specific framing

# Future Outlook

Project the next likely areas of improvement and the questions the field is still debating.
Focus on:

- model advances
- evaluation methodology
- hallucination control

# Actionable Insights

Give concrete recommendations for:

- researchers
- builders
- evaluators
- executives

Include:

- a model-selection matrix
- a hallucination-mitigation checklist

# References

List all sources with:

- full titles
- publishers
- publication dates
- URLs

Sort in this order:

1. primary sources
2. benchmark sources
3. secondary commentary

## 5. 품질 제약

Separate Fact, Inference, and Speculation explicitly.
Prioritize the newest sources and use absolute dates.
Cite every nontrivial factual claim.
Treat official vendor claims as important but not conclusive.
Compare like-for-like settings only.
Distinguish model changes from product or policy changes.
Distinguish factual accuracy from calibration and refusal behavior.
State uncertainty, missing data, and unresolved conflicts.
Avoid fabricated sources, fabricated numbers, and undocumented architecture claims.
Do not smooth over disagreement.
Do not rely on a single benchmark or a single vendor narrative.
Do not interpret targeted hallucination evaluations as direct production prevalence unless a source explicitly supports that inference.

## 6. 스타일

Write in a precise, analytical, non-marketing tone.
Use command-driven research language.
Be concise but evidence-dense.
Prefer structured comparison over hype.
Explain why disagreements exist.
Use tables only when they improve decision quality.
Avoid empty adjectives such as:

- impressive
- amazing
- revolutionary

unless directly quoting a source.

## 7. 확장 옵션

Enable these modes when useful:

### Multi-agent mode

- Researcher gathers evidence
- Critic attacks weak comparisons and benchmark claims
- Strategist turns validated findings into decisions

### Freshness mode

Prioritize the last 90 days, then use the previous 2-3 years for context.

### Deployment mode

Add enterprise implications for:

- cost
- latency
- privacy
- tool use
- evaluation policy

### Hallucination audit mode

Add a dedicated appendix comparing:

- factuality metrics
- calibration behavior
- answer-when-uncertain tendencies

across sources.

### Executive mode

Add a one-page board-level summary after the full report.
