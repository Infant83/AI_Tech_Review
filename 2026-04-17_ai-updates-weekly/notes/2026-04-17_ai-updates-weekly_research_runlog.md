---
title: Research Run Log - 2026-04-17 AI Updates Weekly
date: 2026-04-23
topic: ai-updates-weekly
tags:
  - runlog
  - ai
  - youtube
  - skywork
---

# Research Run Log

## Run Summary

- Workspace root: `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review`
- Package: `2026-04-17_ai-updates-weekly`
- Review date: `2026-04-23`
- Video: https://www.youtube.com/watch?v=Aa9pHSriSW0
- Video title: `Have you heard these exciting AI news? - April 17, 2026 AI Updates Weekly`
- Channel: `Lev Selector`
- Published: `2026-04-17`
- Duration: `24:31`

## Source Acquisition

1. Used `yt-dlp` to fetch video metadata, description, and automatic English captions.
2. Converted YouTube VTT captions into a clean transcript text file.
3. Used GitHub API/tree lookup to locate `lselector/seminar/2026/2026-04-17-AI-Updates.pptx`.
4. Downloaded the companion deck into `sources/2026-04-17-AI-Updates.pptx`.
5. Extracted slide text into `sources/2026-04-17-AI-Updates_slide-extract.md`.
6. Extracted companion deck hyperlinks into `sources/2026-04-17-AI-Updates_links.txt`.
7. Copied the default Skywork template to `skywork_inputs/LGD_Template.pptx`.

## Validation Sources Consulted

- Anthropic Claude Opus 4.7 page: https://www.anthropic.com/claude/opus
- Claude Agent SDK docs: https://code.claude.com/docs/en/agent-sdk/overview
- Anthropic Agent SDK engineering note: https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- Claude Code releases: https://github.com/anthropics/claude-code/releases
- Claude plugin marketplace docs: https://code.claude.com/docs/en/plugin-marketplaces
- Anthropic plugin repositories:
  - https://github.com/anthropics/knowledge-work-plugins
  - https://github.com/anthropics/financial-services-plugins
- MCP architecture docs: https://modelcontextprotocol.io/docs/learn/architecture
- Claude Mythos Preview: https://red.anthropic.com/2026/mythos-preview/
- Claude Mythos Preview system card: https://www-cdn.anthropic.com/8b8380204f74670be75e81c820ca8dda846ab289.pdf
- OpenAI enterprise AI note: https://openai.com/index/next-phase-of-enterprise-ai/
- OpenClaw repo and releases: https://github.com/openclaw/openclaw and https://github.com/openclaw/openclaw/releases
- Google Workspace CLI: https://github.com/googleworkspace/cli
- Cognee: https://github.com/topoteretes/cognee
- Seedance 2.0: https://seed.bytedance.com/en/seedance2_0
- Railway pricing: https://railway.com/pricing
- Layoff and job-market sources:
  - https://layoffs.fyi
  - https://trueup.io/layoffs
  - https://jobloss.ai
  - https://gizmodo.com/report-says-software-engineer-job-listings-are-up-30-this-year-2000742638

## Execution Notes

- The review did not insert a NotebookLM step because the user did not request NotebookLM.
- The video and creator deck were treated as a discovery layer; final conclusions were based on official pages, repositories, documentation, and source-methodology caveats.
- A live ChatGPT deep-research browser run was not used in this pass. The deep-research prompt was saved for reproducibility, and Codex performed the source-bound validation directly from the local source pack and web references.
- Skywork is the default slide-generation target for this workspace. A Skywork prompt packet was prepared with `LGD_Template.pptx` as the default template.
- Correction on `2026-04-24`: the PPTX/PDF generated on `2026-04-23` were local fallback artifacts, not confirmed live Skywork exports. They were moved out of `skywork_exports/` into `artifacts/` to avoid mislabeling.
- Live Skywork generation was retried with Playwright on `2026-04-24`, but was blocked before generation by Skywork authentication/device-limit state. See `skywork_inputs/2026-04-24_skywork_live_attempt_runlog.md`.

## Output Paths

- Source note: `notes/2026-04-17_ai-updates-weekly_sources.md`
- Deep research prompt: `notes/2026-04-17_ai-updates-weekly_deepresearch_prompt.md`
- Memo: `reports/2026-04-17_ai-updates-weekly_memo.md`
- Deep research report: `reports/2026-04-17_ai-updates-weekly_deepresearch.md`
- HTML companions:
  - `reports/2026-04-17_ai-updates-weekly_memo.html`
  - `reports/2026-04-17_ai-updates-weekly_deepresearch.html`
- Skywork prompts:
  - `skywork_inputs/2026-04-17_ai-updates-weekly_skywork_prompt_v1.md`
  - `skywork_inputs/2026-04-17_ai-updates-weekly_skywork_prompt_v2.md`
- Live Skywork attempt log:
  - `skywork_inputs/2026-04-24_skywork_live_attempt_runlog.md`
- Local fallback slide artifacts, not live Skywork exports:
  - `artifacts/2026-04-17_ai-updates-weekly_local_fallback_v1.pptx`
  - `artifacts/2026-04-17_ai-updates-weekly_local_fallback_v1.pdf`
- Live Skywork exports:
  - pending, because Skywork authentication is blocked.

## Follow-Up State

- Obsidian mirror target: `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-04-17_ai-updates-weekly`
- Obsidian mirror completed:
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-04-17_ai-updates-weekly\2026-04-17_ai-updates-weekly_memo.md`
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-04-17_ai-updates-weekly\2026-04-17_ai-updates-weekly_deepresearch.md`
- OpenProject synchronization completed in project `TechReview`:
  - Work package: `#57` / `2026-04-17 AI Updates Weekly 리뷰 패키지`
  - Attached PDF: attachment `#66`, `2026-04-17_ai-updates-weekly_skywork_v1.pdf`
  - Attached PPTX: attachment `#67`, `2026-04-17_ai-updates-weekly_skywork_v1.pptx`
  - Correction pending: attachments `#66` and `#67` should be treated as local fallback artifacts until a live Skywork export is generated and uploaded.
