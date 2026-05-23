# Skywork Prompt v2 - Live Skywork Generation

이 프롬프트는 Skywork.ai 웹 서비스에서 실제 파워포인트 산출물을 생성하기 위한 입력이다. 로컬 PPTX 생성이나 Python 기반 대체 렌더링을 하지 말고, Skywork의 `파워포인트` 모드에서 아래 파일을 업로드한 뒤 새 deck을 생성하라.

## Upload Order

1. `skywork_inputs/LGD_Template.pptx`
2. `reports/2026-04-17_ai-updates-weekly_deepresearch.md`
3. `reports/2026-04-17_ai-updates-weekly_memo.md`
4. `notes/2026-04-17_ai-updates-weekly_sources.md`
5. `sources/2026-04-17-AI-Updates_slide-extract.md`
6. `sources/2026-04-17_Have you heard these exciting AI news？ - April 17, 2026 AI Updates Weekly [Aa9pHSriSW0].clean.txt`

## Project

- Project name: `2026-04-17 AI Updates Weekly - Agent Operating Layer`
- Language: Korean
- Ratio: 16:9
- Target length: 14 slides
- Mode: `파워포인트`, professional / expert technical briefing
- Template: `LGD_Template.pptx`

## Audience

- senior engineers
- engineering managers
- technical product leaders
- strategy stakeholders tracking AI agents, Claude ecosystem, MCP, developer workflow, and enterprise AI adoption

## Core Thesis

이번 업데이트의 핵심은 모델 성능 경쟁이 아니라 `agent operating layer` 경쟁이다. Opus 4.7, Claude Agent SDK, plugins, MCP, Claude Code, Mythos Preview, Google Workspace CLI, memory systems, workflow builders, and deployment surfaces all point to the same shift: AI is moving from answering questions to executing work under permissions, memory, tools, and governance.

## Source Policy

- Treat the YouTube video and creator deck as discovery sources, not primary factual authority.
- Use the deep research report and memo as the main deck source.
- Use official pages, docs, GitHub repos, and system cards as factual anchors.
- Keep exact dates and uncertainty labels.
- Mark secondary market claims as secondary, not audited facts.

## Must-Use Facts

- Claude Opus 4.7 was announced on `2026-04-16`.
- Opus 4.7 is positioned for coding, AI agents, complex professional knowledge work, enterprise workflows, and a 1M context window.
- Claude Agent SDK exposes Claude Code capabilities including built-in tools, hooks, subagents, MCP, permissions, and sessions.
- MCP uses a host/client/server architecture and core primitives such as tools, resources, and prompts.
- Anthropic plugin repositories and marketplace docs show workflow packaging through plugins/skills, not just prompt sharing.
- Claude Mythos Preview should be described as a restricted cybersecurity-oriented preview, not as a generally available model.
- OpenAI's `2026-04-08` enterprise AI note says enterprise is more than 40% of revenue and is on track to reach consumer parity by the end of 2026.
- Anthropic `$30B ARR` should be labeled as a strong secondary market signal, not audited official financial disclosure.
- Google Workspace CLI, Cognee, OpenClaw, and Hermes Agent show the emergence of personal/enterprise digital employee stacks.
- Railway is a deployment/operation layer, not a vibe-coding tool.
- Labor-market signals are mixed: layoffs remain elevated, while software engineering job postings also show recovery in some datasets.

## Slide Structure

1. Title: `AI Updates Weekly: Agent Operating Layer로 이동하는 경쟁축`
2. Executive signal map: confirmed / secondary / weak / interpretation
3. Agent operating layer definition: model + harness + protocol + memory + deployment + governance
4. Anthropic stack: Opus 4.7 + Agent SDK + Claude Code
5. Plugins and MCP: prompt sharing에서 packaged workflow로
6. Mythos Preview: cybersecurity capability and controlled-release boundary
7. Personal digital employee stack: GWS, Obsidian, Cognee, OpenClaw, Hermes
8. Workflow and deployment: workflow builder, Railway, ship/operate layer
9. Market signal: Anthropic vs OpenAI enterprise operating-layer race
10. Labor-market signal: layoffs and job-posting recovery can coexist
11. Risk matrix: lock-in, cost, permissions, memory contamination, tool security
12. 30-90 day action plan
13. Recommended pilot architecture for one agent workflow
14. Final synthesis: what to track next

## Layout Policy

- Use the LGD template rhythm.
- Prefer dense briefing memo, evidence matrix, annotated workflow, source-comparison, and risk/action matrix layouts.
- Use small dark-gray source footers on fact-heavy slides.
- Use small dark-green inline annotations for definitions, caveats, and technical terms.
- Do not make sparse marketing slides.
- Do not use generic repeated cards when a table, flow, timeline, or matrix communicates more precisely.
- Every slide must converge to one decision-relevant insight.

## Avoid

- Hype language.
- Unlabeled speculation.
- Treating `$30B ARR` as audited official Anthropic disclosure.
- Treating Claude Mythos Preview as generally available.
- Presenting the YouTube video as primary evidence.
- NotebookLM artifacts or NotebookLM-specific language.

## Export Requirement

After generation, provide and download:

- PPTX export for editable handoff
- PDF export for visual fidelity review
- project URL and clean viewer URL, if available
