---
title: GPT-5.5 final review figure manifest
date: 2026-05-10
status: final-review-v4
---

# Figure Manifest

| Figure | File | Purpose | Tool | Review notes |
|---|---|---|---|---|
| Hero | `figures/gpt55_agent_workbench_hero-web.png` | GPT-5.5를 긴 작업, 권한, 검증, 되돌리기 구조 안에서 읽어야 한다는 첫 화면 신호 | OpenAI image model via `imagegen` skill | Existing accepted image reused. It is text-free and keeps the article from becoming a slide-style diagram deck. |
| Development arc | `figures/gpt55_development_arc.svg` | 모델 평가가 답변에서 긴 작업과 통제된 위임으로 이동한다는 전체 논지 | Deterministic SVG | New v4 figure; supports the first conceptual section. |
| GPT-5.5 vs Opus | `figures/gpt55_opus_comparison.svg` | GPT-5.5와 Opus 4.7의 비교를 단일 승패 관점에서 벗어나 작업 조건 차이로 설명 | Deterministic SVG | New v4 figure; avoids a redundant score chart. |
| Hallucination lens | `figures/gpt55_hallucination_lens.svg` | 사실 정확도, 근거 연결, 보류 능력, 운영 신뢰가 서로 다른 층위임을 설명 | Deterministic SVG | New v4 figure; directly addresses the high-hallucination interpretation question. |
| Engineering harness | `figures/gpt55_engineering_harness.svg` | 모델의 실제 행동이 검색, 도구 권한, 평가, 승인, 롤백에 의해 결정됨을 설명 | Deterministic SVG | New v4 figure; anchors the engineering section. |
| Safe delegation matrix | `figures/gpt55_safe_delegation_matrix.svg` | 위험과 되돌리기 가능성에 따라 AI 위임 방식을 나누는 의사결정 도식 | Deterministic SVG | New v4 figure; supports the practical deployment section. |

## Retired Assets

- `figures/gpt55_benchmark_surface.svg`: removed from the active article flow because it repeated benchmark evidence without adding a distinct interpretive function.
- `figures/gpt55_variant_map.svg`, `figures/gpt55_release_timeline.svg`, `figures/gpt55_evidence_map.svg`, `figures/gpt55_hallucination_methods.svg`, `figures/gpt55_deployment_matrix.svg`: superseded by the v4 question-led structure.

## Imagegen Prompt Record

Accepted hero prompt summary:

> A completely text-free editorial science and technology illustration for a Korean technical review about GPT-5.5, showing an AI agent workbench as a circular mechanical desk with tool connectors, abstract code-branch rails, blank document stacks, checklists with check marks only, permission badges without words, audit ledgers without writing, rollback rails, and locked containers. Warm paper texture, refined ivory background, charcoal ink linework, muted teal and deep red accents, no letters, numbers, words, UI labels, logos, or watermarks.

Rejected candidate:

- `figures/candidates/hero_agent_workbench/imagegen/candidate1_with_text-web.png`
- Reason: contained readable English text on a badge, which violates the no-fake-label rule for reader-facing review artwork.
