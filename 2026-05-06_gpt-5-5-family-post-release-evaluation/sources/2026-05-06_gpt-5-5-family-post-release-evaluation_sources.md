---
title: GPT-5.5 family post-release evaluation source note
date: 2026-05-06
source_type: user-prompt+shared-chat+web
tags:
  - ai-tech-review
  - openai
  - gpt-5-5
  - model-evaluation
  - hallucination
  - agentic-ai
---

# GPT-5.5 Family Post-release Evaluation Source Note

## 작업 범위

사용자는 2026-05-06에 GPT-5.5 family에 대한 신규 정규 기술리뷰를 요청했습니다.

리뷰 대상은 다음 세 계층으로 분리합니다.

- `GPT-5.5`: OpenAI가 2026-04-23 발표한 frontier reasoning/work model.
- `GPT-5.5 Pro`: 같은 underlying model에 parallel test-time compute 설정을 더한 고성능 variant로 설명됩니다.
- `GPT-5.5 Instant`: 2026-05-05 발표된 ChatGPT 기본 모델 variant. 비교 기준은 GPT-5.3 Instant이며, GPT-5.4 Instant라는 모델명은 공식 system card 기준으로 존재하지 않습니다.

비교 기준은 사용자가 지정한 대로 `GPT-5.4`, `GPT-5.4 Pro`, `GPT-5.3 Instant`, 그리고 like-for-like 조건이 확인되는 frontier peers입니다.

## 사용자 입력

- User-provided prompt: `notes/2026-05-06_gpt-5-5-family-post-release-evaluation_deepresearch_prompt.md`
- Shared ChatGPT conversation: `https://chatgpt.com/share/69fb4e2f-c1f4-83a5-9dcd-3c3ef27303db`
- Playwright로 공유 대화 접근 확인:
  - page title: `GPT-5.5 Advances Overview`
  - snapshot: `.playwright-cli/page-2026-05-06T14-23-36-536Z.yml`
  - 공유 대화는 GPT-5.5 공식 release 확인, Artificial Analysis의 hallucination 우려, deep research prompt code block을 포함합니다.

## Primary sources

| Source | Publisher | Date | URL | Status | Notes |
|---|---|---:|---|---|---|
| Introducing GPT-5.5 | OpenAI | 2026-04-23, updated 2026-04-24 | https://openai.com/index/introducing-gpt-5-5/ | inspected | Official release, benchmark table, latency/token-efficiency claims, API availability update |
| GPT-5.5 System Card | OpenAI Deployment Safety | 2026-04-23, updated 2026-04-24 | https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf | downloaded | Local copy: `sources/web/openai_gpt-5-5_system_card_2026-04-23.pdf` |
| GPT-5.5 Instant: smarter, clearer, and more personalized | OpenAI | 2026-05-05 | https://openai.com/index/gpt-5-5-instant/ | inspected | Instant release, ChatGPT default rollout, internal hallucination claims, personalization/memory-sources claims |
| GPT-5.5 in ChatGPT | OpenAI Help Center | updated 2026-05-06 | https://help.openai.com/en/articles/11909943-gpt-55-in-chatgpt | inspected | ChatGPT availability, usage limits, context windows, tool support |
| ChatGPT Release Notes | OpenAI Help Center | updated 2026-05-04 | https://help.openai.com/en/articles/6825453-chatgpt-can-now-generate-images | inspected | Release timeline for GPT-5.5, GPT-5.5 Instant, GPT-5.4, GPT-5.3 Instant |
| Models | OpenAI API docs | crawled 2026-05 | https://developers.openai.com/api/docs/models | inspected | Current API model list and docs navigation |
| Pricing | OpenAI API docs | crawled 2026-05 | https://developers.openai.com/api/docs/pricing | inspected | API pricing for `gpt-5.5`, `gpt-5.5-pro`, comparison with GPT-5.4 |

## Benchmark / evaluation sources

| Source | Publisher | Date | URL | Status | Notes |
|---|---|---:|---|---|---|
| OpenAI's GPT-5.5 is the new leading AI model | Artificial Analysis | 2026-04-23 | https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model/ | inspected | External benchmark-provider analysis; includes reasoning-effort ladder, token-use/cost analysis, AA-Omniscience hallucination caveat |
| MCP Atlas leaderboard | Scale Labs | updated 2026-04-08 | https://labs.scale.com/leaderboard/mcp_atlas | inspected | Tool-use benchmark with 1,000 tasks, 36 MCP servers, 220 tools; GPT-5.5 xhigh at 75.3% |
| Our evaluation of OpenAI's GPT-5.5 cyber capabilities | UK AISI | 2026-04-30 | https://www.aisi.gov.uk/blog/our-evaluation-of-openais-gpt-5-5-cyber-capabilities | inspected | External cyber capability evaluation; advanced expert tasks, cyber ranges, safeguards caveats |
| BrowseComp | OpenAI | 2025-04 | https://openai.com/index/browsecomp/ | queued | Needed for browsing/search methodology context |
| SWE-Bench Pro | arXiv/OpenReview | 2025 | https://arxiv.org/abs/2509.16941 | queued | Needed for coding-benchmark scope and contamination/memorization discussion |
| SWE-Bench memorization / contamination papers | arXiv | 2025 | https://arxiv.org/abs/2506.12286 | queued | Needed for benchmark contamination section |

## Secondary / commentary queue

These sources are not treated as primary evidence. They are useful for field discussion, public interpretation, and practitioner concerns after primary-source review.

- TechCrunch, `OpenAI releases GPT-5.5 Instant, a new default model for ChatGPT`, 2026-05-05.
- Axios, `OpenAI makes default ChatGPT more personal`, 2026-05-05.
- Reuters / Investing.com mirror, `OpenAI provided GPT-5.5 to US for national security testing`, 2026-05-05.
- The Verge article referenced in shared ChatGPT conversation; queued for direct inspection if accessible.
- Practitioner discussion about hallucination/context regressions and benchmark concerns; use cautiously and label as commentary.

## Initial evidence observations

### Fact

- OpenAI released GPT-5.5 on 2026-04-23 and later updated the release note on 2026-04-24 to say GPT-5.5 and GPT-5.5 Pro were available in the API.
- OpenAI released GPT-5.5 Instant on 2026-05-05 and described it as replacing GPT-5.3 Instant as ChatGPT's default model.
- OpenAI Help Center lists ChatGPT context windows for GPT-5.5 Instant and GPT-5.5 Thinking, including 128K for Pro/Enterprise Instant and up to 400K for Pro-tier Thinking.
- The GPT-5.5 system card says GPT-5.5 Pro is the same underlying model using a setting that makes use of parallel test-time compute.
- OpenAI's GPT-5.5 system card treats GPT-5.5 as High capability for Biological/Chemical and Cybersecurity domains, but below Critical for Cybersecurity.

### Inference

- The main review tension is not whether GPT-5.5 improved. It is where improvement is model-level, where it is inference-compute/tooling/product-layer, and where official metrics do not translate cleanly into production factual reliability.
- GPT-5.5 appears strongest in long-horizon agentic work, terminal/coding workflows, computer-use/tool orchestration, and some long-context settings. Independent tool-use and cyber evaluations support part of this narrative, while hallucination/calibration evidence is mixed.

### Caution

- Official benchmark tables mix internal benchmarks, external benchmarks, different tool conditions, and research-environment runs with `reasoning effort set to xhigh`. Like-for-like comparison must be checked row by row.
- OpenAI's hallucination evaluation on user-flagged factual-error cases is explicitly not a representative production slice.
- Artificial Analysis reports high AA-Omniscience hallucination rate for GPT-5.5 xhigh despite strong knowledge accuracy, suggesting answer-when-uncertain behavior remains a key risk.
- Shared ChatGPT conversation claims about Vellum and SWE-Bench Pro need direct source verification before being used as report conclusions.

## Planned artifacts

- `notes/2026-05-06_gpt-5-5-family-post-release-evaluation_deepresearch_prompt.md`
- `notes/2026-05-06_gpt-5-5-family-post-release-evaluation_research_runlog.md`
- `reports/2026-05-06_gpt-5-5-family-post-release-evaluation_memo.md`
- `reports/2026-05-06_gpt-5-5-family-post-release-evaluation_deepresearch.md`
- `reports/2026-05-06_gpt-5-5-family-post-release-evaluation_final_review.md`
- `reports/2026-05-06_gpt-5-5-family-post-release-evaluation_final_review.html`
- `skywork_inputs/2026-05-06_gpt-5-5-family-post-release-evaluation_skywork_prompt_v1.md`
- `skywork_exports/` final PPTX/PDF after Skywork run
