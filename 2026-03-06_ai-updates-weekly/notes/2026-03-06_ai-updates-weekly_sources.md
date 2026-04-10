---
title: 2026-03-06 AI Updates Weekly Sources
date: 2026-03-09
tags:
  - ai-review
  - sources
  - agents
  - weekly-digest
source_type: youtube-plus-web
---

# Source Note

## Seed Input
- Video: [Have you heard these exciting AI news? - March 06, 2026 AI Updates Weekly](https://www.youtube.com/watch?v=waMSY9hc8eU)
- Presenter: Lev Selector
- Published: March 06, 2026
- Runtime: 36m 51s
- Companion slide deck: [2026-03-06-AI-Updates.pptx](https://raw.githubusercontent.com/lselector/seminar/master/2026/2026-03-06-AI-Updates.pptx)
- Slide repo: [lselector/seminar](https://github.com/lselector/seminar)

## Local Artifacts Created
- Raw video description
- Raw auto-caption VTT
- Cleaned transcript text
- Slide text extract
- Slide link list

## Chapter Map From The Video Description
- 00:00 Introduction
- 00:07 AI is a "wrecking ball" destroying SaaS
- 00:28 "Skills instead of SaaS"
- 00:45 "Your Job is to Onboard AI Agents" - Peter Yang
- 01:07 Crowd-sourced LM Arena leaderboard
- 02:51 Mercury 2 by Inception Labs
- 03:55 OpenAI GPT-5.4 and GPT-5.3 Instant
- 04:58 Google Gemini 3.1 Flash-Lite and Pro
- 05:24 Gemini Nano Banana 2
- 05:52 Qwen3-Coder-Next
- 06:13 Claude Co-Work scheduling
- 06:41 Anthropic Skill Creator
- 07:42 Claude Code MEMORY.md
- 08:19 Claude Code voice mode
- 09:01 Alibaba CoPaw and ModelScope
- 10:20 Claude Code vs OpenClaw
- 10:42 Claude Code remote control
- 11:08 Claude remembers work habits
- 12:17 From apps and SaaS to generic agent
- 14:46 ClawX
- 15:13 OpenClaw + Simflow
- 15:20 Accomplish desktop agent
- 15:42 NullClaw
- 15:58 Harness engineering
- 17:42 MaxClaw
- 18:16 Qwen3.5-9B
- 19:47 OpenClaw tips
- 21:14 Tools that make OpenClaw useful
- 21:43 Toggle browser agent skill
- 22:00 SHARE + Sidecar
- 22:32 Kane AI
- 22:40 Claude Code + Telegram bot
- 22:58 Apple updates
- 24:02 AI agents making money and doing marketing
- 24:42 2028 Global Intelligence Crisis report
- 25:38 AT&T multi-agent architecture
- 26:10 Perplexity Computer
- 26:50 Ilya / SSI
- 28:05 Liquid AI LFM2-24B-A2B
- 28:33 CodeBuff
- 28:52 Humanize Text
- 30:18 Anthropic vs U.S. Department of Defense
- 33:42 Moonshots
- 34:00 Interview with Andrew Ng
- 34:37 SaaS collapse into personal AI agents
- 36:40 Jobs, layoffs, AI engineer demand

## High-Value Supporting Sources

### Product and model releases
- [OpenAI GPT-5.3 Instant](https://openai.com/index/gpt-5-3-instant/)
- [OpenAI GPT-5.4 Thinking System Card](https://openai.com/index/gpt-5-4-thinking-system-card/)
- [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)
- [Gemini 3.1 Flash-Lite model card](https://deepmind.google/models/model-cards/gemini-3-1-flash-lite/)
- [Gemini 3.1 Pro announcement](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/)
- [Mercury 2 search and pricing page](https://www.inceptionlabs.ai/introducing-mercury)
- [Liquid AI LFM2-24B-A2B model card](https://huggingface.co/LiquidAI/LFM2-24B-A2B)

### Agent operating system and workflow layer
- [Anthropic Skill Creator repository](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- [Claude Code memory docs](https://code.claude.com/docs/en/memory)
- [Claude Code remote control docs](https://code.claude.com/docs/en/remote-control)
- [Claude memory import](https://claude.com/import-memory)
- [CoPaw GitHub repository](https://github.com/agentscope-ai/CoPaw)
- [AgentScope GitHub repository](https://github.com/agentscope-ai/agentscope)
- [CodeBuff GitHub repository](https://github.com/CodebuffAI/codebuff)

### Enterprise adoption and evaluation
- [VentureBeat on Ask AT&T and multi-agent orchestration](https://venturebeat.com/orchestration/8-billion-tokens-a-day-forced-at-and-t-to-rethink-ai-orchestration-and-cut/)
- [TheAgentCompany paper summary](https://huggingface.co/papers/2412.14161)
- [LM Arena](https://lmarena.ai/leaderboard/text)
- [Artificial Analysis leaderboards](https://artificialanalysis.ai/leaderboards/models)

### Policy and governance
- [Anthropic statement on the Department of War](https://www.anthropic.com/news/statement-department-of-war)
- [TechCrunch follow-up on Pentagon negotiations](https://techcrunch.com/2026/03/05/anthropic-ceo-dario-amodei-could-still-be-trying-to-make-a-deal-with-pentagon/)
- [CBS interview transcript with Dario Amodei](https://www.cbsnews.com/news/anthropic-ceo-dario-amodei-full-transcript/)

## Reliability Notes
- The video is a curated weekly digest, not a single-claim source. It is useful for topic discovery and for mapping what matters to practitioners.
- The slide deck is more structured than the auto-captions and provides most of the key external links.
- The cleaned transcript is adequate for narrative context, but some product names and timestamps likely contain auto-caption errors.
- Several ecosystem items in the video point to YouTube demos or community repositories rather than primary vendor documentation. Those are included as signals, not as fully verified product specs.

## Initial Observations
- The strongest through-line is not model intelligence alone. It is the shift toward agent operating layers built on top of interchangeable models.
- The deck repeatedly centers skills, memory, scheduling, remote control, and orchestration as the new product surface.
- The most actionable enterprise evidence in the set is AT&T's cost reduction via model routing and worker-agent decomposition.
- The strongest policy signal is that AI safety commitments weaken under state pressure and competitive pressure.
- For builders, the strategic question is shifting from "Which model should we use?" to "What harness, permissions, memory, and workflow stack will make agents reliable enough to trust?"

## Questions For Deeper Research
- Which parts of the "skills instead of SaaS" thesis are already visible in real products, and which parts are still speculative?
- How much of agent progress is actually coming from better models versus better harnesses?
- What does a trustworthy desktop agent stack require in memory, sandboxing, and approvals?
- What is the most credible enterprise evidence that multi-agent systems reduce cost without unacceptable complexity?
- What does the Anthropic and Pentagon dispute imply for enterprise procurement, governance, and safety expectations?
