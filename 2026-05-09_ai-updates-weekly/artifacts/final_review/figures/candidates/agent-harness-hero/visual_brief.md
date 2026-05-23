---
title: Agent Harness Hero Visual Brief
date: 2026-05-09
status: selected
selected: ../../agent-harness-hero-v2-web.png
---

# Agent Harness Hero Visual Brief

## Section

Opening hero for `에이전트는 하네스 위에서 실무 도구가 됩니다`.

## One-Sentence Message

AI agent adoption becomes practical when the model is surrounded by permission, memory, tool connection, verification/approval, and merge/rollback structures.

## Must Show

- Abstract agent work core, not a robot or human face
- Permission/access
- Memory/work history
- Verification and approval
- Tool/data connectors
- Merge and rollback/change control

## Must Avoid

- Generic AI cloud or network-only imagery
- Fake words, fake UI labels, logos, brand marks
- Too abstract a scene where the argument is only understandable from the caption
- Dense slide-style boxes covering the illustration

## Candidate Routes

| Candidate | Route | Status | Note |
|---|---|---|---|
| `agent-harness-hero-v2-web.png` | imagegen | selected | Editorial quality is good, concrete work objects are visible, and the opening reads less like a slide. |
| `agent-harness-hero-annotated.svg` | hybrid imagegen + deterministic annotation | rejected | Exact labels help clarity, but the label layer feels awkward over the watercolor illustration and makes the hero too slide-like. |
| NotebookLM Studio | NotebookLM + Playwright CLI | exported, not selected | PNG export was archived, but internal text quality and watermark make it a candidate rather than a publish-ready figure. |
| Skywork PowerPoint skill | Skywork + Playwright CLI | attempted, not selected | UI access was confirmed, but login/auth issues blocked project/export creation. |

## Selection Reason

The original imagegen candidate keeps the publish-style illustration without overloading the first viewport. It does not explain every harness component by itself, but it gives the right entry point: an agent work engine surrounded by permission, documents, connectors, and checklists. The more exact explanation is handled by the following deterministic `harness-stack.svg` figure.
