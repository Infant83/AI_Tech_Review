---
title: Research Run Log - 2026-04-25 AI Updates Weekly
date: 2026-04-25
topic: ai-updates-weekly
tags:
  - runlog
  - ai
  - youtube
  - weekly-review
---

# Research Run Log

## Run Summary

- Workspace root: `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review`
- Package: `2026-04-25_ai-updates-weekly`
- Review date: `2026-04-25`
- Videos:
  - https://www.youtube.com/watch?v=XDASSrE4348
  - https://www.youtube.com/watch?v=oVDfoWer_M4
- Channel: `Lev Selector`
- Published: `2026-04-24`

## Source Acquisition

1. Used `yt-dlp --dump-single-json --skip-download` to confirm titles, dates, durations, and chapter data.
2. Downloaded video descriptions, metadata JSON, and English auto captions for both videos with `yt-dlp`.
3. Converted both VTT caption files into cleaned transcript text files by removing caption tags and collapsing overlapping repeated cues.
4. Inspected video descriptions and found companion slide references on Google Drive and GitHub.
5. Queried the `lselector/seminar` GitHub repository tree and confirmed:
   - `2026/2026-04-24-AI-Updates-1.pptx`
   - `2026/2026-04-24-AI-Updates-2.pptx`
6. Downloaded both companion decks into `sources/`.
7. Used `python-pptx` to extract slide text into markdown files for fast review.

## Validation Sources Consulted

- OpenAI:
  - `GPT-5.5`
  - `ChatGPT Images 2.0`
  - `Agents SDK`
  - `GPT-Rosalind`
  - `GPT-5.4-Cyber`
- DeepSeek:
  - `DeepSeek V4 Preview Release`
- Cursor:
  - `Cursor 3`
  - `The third era of AI software development`
- Google / Google DeepMind:
  - `Deep Research and Deep Research Max`
  - `Advancing Gemini's security safeguards`
- Apple:
  - `John Ternus to become Apple CEO`
- Anthropic:
  - compute partnership / demand signal
- GitHub repositories:
  - `openclaw/openclaw`
  - `NousResearch/hermes-agent`
- Alibaba Cloud:
  - `Qwen3.6-Max-Preview`
- Moonshot AI:
  - `Kimi K2.6`

## Execution Notes

- The two YouTube videos and creator decks were used as a weekly discovery layer.
- Official product pages, docs, and repos were used to validate the highest-salience claims.
- No NotebookLM step was run because the user did not request NotebookLM.
- No live ChatGPT deep-research browser run was used in this pass; the prompt file was saved for reproducibility, while the analysis itself was performed from the local source pack plus primary web sources.
- No Skywork generation was run in this pass because the request was handled as a weekly summary package rather than a slide-delivery request.
- No OpenProject update was executed in this pass; document package first, project sync later if this weekly review is promoted to a formal delivery.

## Output Paths

- Source note: `notes/2026-04-25_ai-updates-weekly_sources.md`
- Deep research prompt: `notes/2026-04-25_ai-updates-weekly_deepresearch_prompt.md`
- Memo: `reports/2026-04-25_ai-updates-weekly_memo.md`
- Deep research report: `reports/2026-04-25_ai-updates-weekly_deepresearch.md`
- HTML companions:
  - `reports/2026-04-25_ai-updates-weekly_memo.html`
  - `reports/2026-04-25_ai-updates-weekly_deepresearch.html`

## Follow-Up State

- Obsidian mirror target: `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-04-25_ai-updates-weekly`
- Obsidian mirror scope for this pass:
  - memo markdown
  - deep research markdown
