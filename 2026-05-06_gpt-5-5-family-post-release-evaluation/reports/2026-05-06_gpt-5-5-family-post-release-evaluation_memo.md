---
title: GPT-5.5 Family Post-release Evaluation Memo
date: 2026-05-07
author: 김현중 with Codex Agent | AI Governance Team
tags:
  - ai-tech-review
  - openai
  - gpt-5-5
  - model-evaluation
  - hallucination
---

# GPT-5.5 Family Post-release Evaluation Memo

## Summary

- **Fact**: OpenAI는 2026-04-23 `GPT-5.5`를 발표했고, 2026-04-24 업데이트에서 `GPT-5.5`와 `GPT-5.5 Pro`의 API availability를 명시했습니다. 공식 설명은 coding, online research, data analysis, document/spreadsheet creation, software operation, tool use를 하나의 real-work model narrative로 묶고 있습니다. [OpenAI release](https://openai.com/index/introducing-gpt-5-5/)
- **Fact**: `GPT-5.5 Instant`는 2026-05-05 별도 발표됐고, ChatGPT 기본 모델로 `GPT-5.3 Instant`를 대체합니다. OpenAI는 Instant의 factuality 개선, 더 짧고 명확한 답변, personalization/memory source 개선을 강조합니다. [OpenAI Instant release](https://openai.com/index/gpt-5-5-instant/)
- **Fact**: OpenAI Help Center 기준으로 GPT-5.5 Instant와 Thinking은 ChatGPT의 web search, data analysis, image/file analysis, canvas, image generation, memory, custom instructions를 지원합니다. Thinking context window는 paid tier 256K, Pro tier 400K로 안내됩니다. [Help Center](https://help.openai.com/en/articles/11909943-gpt-55-in-chatgpt)
- **Inference**: 이번 리뷰의 중심 질문은 “GPT-5.5가 좋아졌는가”가 아니라, 어떤 개선이 실제 model-level 개선이고 어떤 개선이 inference-time compute, product integration, tool access, prompt/eval design에서 나온 것인지 분리하는 데 있습니다.
- **Caution**: hallucination 개선 주장은 그대로 production factuality 개선으로 읽으면 안 됩니다. OpenAI system card의 user-flagged factuality eval은 hallucination-prone case를 일부러 모은 평가이고, Artificial Analysis는 GPT-5.5 xhigh가 높은 knowledge accuracy를 보이지만 AA-Omniscience hallucination rate에서는 frontier peers보다 불리하다고 보고했습니다.

## 착수 판단

이 주제는 단일 release note 요약으로 처리하면 중요한 차이가 사라집니다. GPT-5.5 Thinking/Pro는 agentic execution과 long-horizon work 쪽의 frontier model 평가이고, GPT-5.5 Instant는 ChatGPT default behavior와 personalization/factuality 개선에 가까운 제품 계층 평가입니다. 두 층을 같은 표에 넣을 수는 있지만, 같은 증거로 결론을 내면 안 됩니다.

따라서 보고서는 세 가지 축으로 나누겠습니다.

1. `모델 계층`: GPT-5.5, GPT-5.5 Pro, reasoning effort, parallel test-time compute, long-context behavior.
2. `제품 계층`: GPT-5.5 Instant, ChatGPT default rollout, memory sources, tool availability, legacy model migration.
3. `평가 계층`: official benchmark, external benchmark-provider results, safety/system-card eval, field commentary.

## 1차 evidence map

| Claim cluster | Primary source | External support | Caveat | Report use |
|---|---|---|---|---|
| Agentic coding and terminal work improved | OpenAI release, system card | Artificial Analysis, Scale MCP Atlas, UK AISI cyber evaluation | Some benchmark rows are internal or research-environment only | Technical Deep Dive, Applications |
| Token efficiency improved | OpenAI release, Artificial Analysis | Artificial Analysis reports roughly 40% fewer output tokens in its Index run | Task mix and harness-specific; not direct enterprise cost guarantee | Cost/latency/quality section |
| GPT-5.5 Pro is not a separate disclosed architecture | GPT-5.5 system card | none needed | It is described as same underlying model with parallel test-time compute setting | Variant matrix |
| Instant hallucination improved vs GPT-5.3 Instant | OpenAI Instant release | secondary press repeats OpenAI claim | Internal eval; high-stakes prompt set; not direct production prevalence | Hallucination methodology table |
| GPT-5.5 still has answer-when-uncertain risk | Artificial Analysis AA-Omniscience | practitioner discussion queued | AA methodology must be inspected before strong conclusion | Hallucination audit appendix |
| Cyber capability increased | OpenAI system card, UK AISI | UK AISI external evaluation | Public deployment has safeguards and access controls; not ordinary-user capability | Safety / deployment implications |

## Immediate source queue

Primary and benchmark-provider sources are already enough to start the structured artifacts. 남은 확인은 아래 순서로 진행합니다.

- BrowseComp methodology and whether GPT-5.5 results are tool/search comparable.
- SWE-Bench Pro paper, leaderboard context, and contamination/memorization papers.
- Vellum or equivalent practitioner analysis that compares GPT-5.5 with Claude Opus 4.7 on SWE-Bench Pro.
- The Verge, TechCrunch, Axios, Reuters coverage as secondary commentary, only after primary-source findings are stable.

## Planned report products

- `deepresearch.md`: 사용자가 준 exact structure에 맞춘 evidence-heavy report.
- `final_review.md`: 같은 근거를 바탕으로 독자가 처음부터 끝까지 읽을 수 있는 완결형 기술 리뷰.
- `final_review.html`: section map, evidence rail, callout, visual explainer, model-selection matrix를 포함하는 rich article.
- `skywork_inputs/`: 추후 Skywork deck 생성용 prompt packet.

## References

- OpenAI, `Introducing GPT-5.5`, 2026-04-23, updated 2026-04-24. https://openai.com/index/introducing-gpt-5-5/
- OpenAI, `GPT-5.5 Instant: smarter, clearer, and more personalized`, 2026-05-05. https://openai.com/index/gpt-5-5-instant/
- OpenAI Deployment Safety, `GPT-5.5 System Card`, 2026-04-23, updated 2026-04-24. https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf
- OpenAI Help Center, `GPT-5.5 in ChatGPT`, updated 2026-05-06. https://help.openai.com/en/articles/11909943-gpt-55-in-chatgpt
- Artificial Analysis, `OpenAI's GPT-5.5 is the new leading AI model`, 2026-04-23. https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model/
- Scale Labs, `MCP Atlas`, updated 2026-04-08. https://labs.scale.com/leaderboard/mcp_atlas
- UK AISI, `Our evaluation of OpenAI's GPT-5.5 cyber capabilities`, 2026-04-30. https://www.aisi.gov.uk/blog/our-evaluation-of-openais-gpt-5-5-cyber-capabilities
