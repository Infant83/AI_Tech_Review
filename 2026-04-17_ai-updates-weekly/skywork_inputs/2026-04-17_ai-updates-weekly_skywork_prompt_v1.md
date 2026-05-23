# Skywork Prompt v1

Use `LGD_Template.pptx` as the presentation template. The template file is included in this package as `skywork_inputs/LGD_Template.pptx`.

업로드된 자료와 템플릿을 기반으로 새로운 Korean PowerPoint deck을 생성하라.

## Project

- Project name: `2026-04-17 AI Updates Weekly`
- Language: Korean
- Ratio: 16:9
- Recommended length: 12-14 slides
- Section mode: dense technology briefing / internal report

## Audience

- senior engineers
- engineering managers
- technical product leaders
- strategy stakeholders tracking AI agents, Claude ecosystem, MCP, developer workflow, and enterprise AI adoption

## Purpose

영상 요약이 아니라 `2026년 4월 중순 AI agent operating layer 전환`을 설명하는 기술동향 리뷰 deck을 만들어라. 청중이 회의 후 바로 30-90일 실행 과제를 정할 수 있게 해야 한다.

## Source Priority

1. `reports/2026-04-17_ai-updates-weekly_deepresearch.md`
2. `reports/2026-04-17_ai-updates-weekly_memo.md`
3. `notes/2026-04-17_ai-updates-weekly_sources.md`
4. `sources/2026-04-17-AI-Updates_slide-extract.md`
5. `sources/2026-04-17_Have you heard these exciting AI news？ - April 17, 2026 AI Updates Weekly [Aa9pHSriSW0].clean.txt`

The YouTube video and companion deck are discovery sources, not primary factual authority. Use official pages, GitHub repos, and docs as the factual baseline.

## Core Message

이번 업데이트의 핵심은 모델 성능 경쟁이 아니라 `agent operating layer` 경쟁이다. Opus 4.7, Claude Agent SDK, plugins, MCP, Claude Code, Mythos Preview, Google Workspace CLI, memory systems, workflow builders, and deployment surfaces all point to the same shift: AI is moving from answering questions to executing work under permissions, memory, tools, and governance.

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

## Cautions

- Do not present the video as primary evidence.
- Do not overclaim that traditional software is disappearing immediately.
- Do not treat `$30B ARR` as official audited data.
- Do not repeat unverified Mythos claims about emergency regulator meetings, internal 4x productivity, or architectural flywheels unless clearly marked as unverified.
- Do not make the deck sparse or marketing-like. It should be information-dense but readable.
- Use exact dates and source labels.

## Suggested Slide Structure

1. Title and one-line thesis
2. Executive signal map: what is confirmed, secondary, weak, and interpretation
3. The agent operating layer: model + harness + protocol + memory + deployment + governance
4. Anthropic stack: Opus 4.7 + Agent SDK + Claude Code
5. Plugins and MCP: from prompt sharing to packaged workflows
6. Mythos Preview: cybersecurity capability and controlled release boundary
7. Personal digital employee stack: GWS, Obsidian, Cognee, OpenClaw, Hermes
8. Workflow and deployment: workflow builder, Railway, ship/operate layer
9. Market signal: Anthropic vs OpenAI enterprise operating-layer race
10. Labor-market signal: layoffs and job-posting recovery can coexist
11. Risks: lock-in, cost, permissions, memory contamination, tool security
12. 30-90 day action plan
13. Recommended architecture for a pilot agent workflow
14. Final synthesis

## Visual / Layout Policy

- Use the LGD template rhythm.
- Prefer dense briefing memo, evidence matrix, annotated workflow, and source-comparison layouts.
- Use a small evidence footer on slides with factual claims.
- Use dark-green inline annotations for definitions or caveats.
- Avoid repeated generic cards. Vary tables, flow diagrams, risk matrix, and action roadmap.
- Every slide should converge to one decision-relevant insight.

## Good Slide Criteria

- A technical manager should understand what changed, why it matters, and what to do next.
- Engineers should see concrete implementation surfaces: SDK, MCP, CLI, memory, permissions, deployment.
- Strategy stakeholders should see why enterprise AI revenue is moving toward operating layers, not only chat subscriptions.

## Avoid

- Hype language.
- Unlabeled speculation.
- Overly large text with little substance.
- Treating all links in the original video as equally important.
- NotebookLM-specific output or artifacts.
