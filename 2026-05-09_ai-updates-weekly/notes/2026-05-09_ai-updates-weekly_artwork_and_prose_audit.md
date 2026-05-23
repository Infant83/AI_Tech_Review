---
title: AI Updates Weekly Final Review Prose and Artwork Audit
date: 2026-05-09
status: active
scope:
  - reports/2026-05-09_ai-updates-weekly_final_review.md
  - reports/2026-05-09_ai-updates-weekly_final_review.html
  - artifacts/final_review/figures/
  - artifacts/final_review/figure_audit/
---

# Prose and Artwork Audit

## Prose Finding

The review previously used repeated contrast pivots such as `A-not-B` sentences. This pattern can sound persuasive at first, but it often weakens technical prose because the rejected position is not always a real claim in the source material.

Revision rule applied:

1. Start from the observed work situation.
2. Name the source-backed change.
3. Explain the technical concept.
4. Let the conclusion follow from evidence and workflow consequences.

Current result:

- `아니라` occurrences in the reader-facing review: `0`
- automated prose audit: `finding_count: 0`
- main replacement style: contrast pivot -> observation, evidence, concept refinement

Example replacement:

- Before: `기억은 저장소의 크기 문제가 아닙니다. 업무에서 필요한 것은 많은 기억이 아니라 다시 쓸 수 있는 기억입니다.`
- After: `장기 작업의 기억은 저장 용량보다 재사용성에 더 가깝습니다. 실패한 작업, 좋은 결정, 사용자의 선호, 반복되는 검토 기준이 다음 작업에 도움이 되려면 다시 꺼내 쓸 수 있는 형태로 정리되어야 합니다.`

## Artwork Inventory

| Figure | Type | Current role | Decision |
|---|---|---|---|
| Figure 1 | imagegen bitmap | Opens the subject with a concrete agent workbench scene | Keep |
| Figure 2 | deterministic SVG | Explains the harness stack around the model | Keep; watch for slide-like density |
| Figure 3 | imagegen + SVG number badges and legend | Explains the execution conditions around an agent harness: source-of-truth materials, procedure, app connections, open-source tools, developer workflow, and governance | Revised after label-occlusion and label-semantics audit |
| Figure 4 | imagegen-selected hybrid SVG | Shows the enterprise operating path: business data, permission scope, AI output, human review, approval/audit | Replaced atmospheric bitmap with relationship-first infographic |
| Figure 5 | deterministic SVG control-flow | Explains memory selection, evaluation, retry, and approval | Replaced the imagegen icon-flow hybrid because the process depends on exact control relationships |
| Figure 6 | Skywork Image + embedded SVG labels | Explains connector as convenience path plus permission gate | Replaced the imagegen candidate with a Skywork editorial infographic, then covered generated English headings and added Korean labels |
| Figure 7 | imagegen bitmap | Gives the coding/merge section a visual break | Keep |
| Figure 8 | deterministic SVG | Compares one-model procedural flow and multi-agent split | Keep; caption revised |
| Figure 9 | deterministic SVG | Shows high-risk domain safety harness | Keep; caption and embedded text revised |

## Visual Route Judgment

The current article uses three editorial bitmap scenes and six exact diagrams. That balance is acceptable for a technical review because the argument depends on precise labels: permission, memory, evaluation, approval, connector, merge, and safety boundary.

The updated editorial rule is stricter: Skywork Image and GPT Image 2/imagegen should be treated as primary candidates for magazine-style artwork infographics. Deterministic SVG stays useful for exact Korean labels, arrows, source maps, timelines, and post-annotation, but it should not become the default visual style just because it is easier to control.

Good future Skywork/GPT Image 2 candidates:

- `reference-map` as a more editorial infographic.
- `connector-permission-surface` as a poster-like one-cut explainer.
- `harness-stack` as a cleaner magazine-style concept graphic.

Selection rule:

- Use Skywork Image first for polished one-cut infographics, poster-style section openers, and magazine-like concept cards.
- Use GPT Image 2/imagegen first for article atmosphere, concrete scenes, high-quality object metaphors, and text-free infographic bases.
- Use deterministic SVG for exact labels, arrows, workflow, and source maps.
- Use hybrid composition when the generated image is visually strong but the claim needs exact Korean labels or arrows.
- Do not use a generated image when the reader needs exact Korean labels unless labels are added afterward in SVG/HTML.

## Render Verification

Rendered HTML checked through Playwright at `1280 x 900`.

Artifacts:

- `artifacts/final_review/figure_audit/figure-audit-records.json`
- `artifacts/final_review/figure_audit/figure-contact-sheet.png`
- `artifacts/final_review/figure_audit/figure-01.png` through `figure-09.png`

Observed after revision:

- All 9 figures load.
- No broken images.
- Figures 3, 5, and 6 load in browser/HTML rendering. Figure 3 now uses small number markers and an external legend so labels do not cover the main image clusters.
- Figure 5 no longer has arrows covering node text.
- Captions for Figures 1, 4, 8, and 9 were revised to avoid contrast-driven framing.

## 2026-05-09 Graphics Generation Pass

Generated with local `imagegen` using `gpt-image-1.5`:

- `reference-map-imagegen.png` / `reference-map-imagegen-web.png`
- `connector-permission-imagegen.png` / `connector-permission-imagegen-web.png`
- `memory-evaluation-loop-imagegen.png` / `memory-evaluation-loop-imagegen-web.png`
- `memory-evaluation-loop-no-text.png` / `memory-evaluation-loop-no-text-web.png`

Selected assets:

- Figure 3: `reference-map-legend.svg`
- Figure 5: `memory-evaluation-control-loop.svg`
- Figure 6: `connector-permission-skywork-magazine.svg`

Rejected or non-final candidates remain archived under `artifacts/final_review/figures/candidates/imagegen/`. The first memory-loop candidate was not selected because generated English labels appeared inside the image. The later no-text imagegen candidate was also replaced because the section needed a control-flow figure, not an object-based process illustration.

## 2026-05-09 Figure 5 Logic Revision

Figure 5 was re-audited after the Skywork/Image generation pass.

Finding:

- The imagegen memory-loop candidate looked immature because it treated a control-loop figure as an object parade: workbench, memory cards, checklist, loop track, approval stamp.
- The adjacent section needs the reader to understand control relationships: which records become usable memory, how the output is evaluated, what becomes a retry condition, and where human approval sits.

Revision:

- Replaced `memory-evaluation-loop-magazine.svg` with `memory-evaluation-control-loop.svg`.
- The new figure starts from a deterministic control-flow skeleton rather than an image-generated object scene.
- The normal path and retry path are visually separated, and `기억 선별`, `평가 기준`, `재시도 계획`, `사람 승인` are treated as responsibility points.

Harness update:

- Added a Process Figure Rule to `.automation/editorial-graphics-audit-harness.md`.
- Updated `ai-tech-review-editorial-harness/references/review-artwork-editor.md` so future process/loop figures start with deterministic information architecture before image generation.
- Updated the topic artwork brief so Skywork/Image candidates for memory loops are compared against the control-flow skeleton rather than used directly.

Render check:

- `artifacts/final_review/figure_audit/figure-05-control-loop-v2.png` confirmed the new Figure 5 in the rendered article.

## 2026-05-09 Figure 3 Label-Occlusion Revision

Figure 3 was re-audited after a rendered screenshot showed that the label chips covered the generated image clusters.

Finding:

- The generated reference-map artwork had useful visual clusters: papers, enterprise announcements, connectors, open-source tools, workflow tools, and domain safety objects.
- The first hybrid SVG placed large Korean label boxes directly over those clusters, so the exact labels were readable but the underlying scene became harder to understand.

Revision:

- Replaced the reader-facing path from `reference-map-magazine.svg` to `reference-map-legend.svg`.
- Kept the generated artwork as the main scene.
- Moved full Korean labels into a two-row legend below the image.
- Left only small numbered badges and thin leader lines on the image.
- Covered only the accidental generated `Review` text on the bottom-right stamp, without adding a new large callout over the safety cluster.
- Revised the legend wording from source-type labels such as `기업 발표` and `커넥터` to harness-condition labels such as `기준 자료`, `작업 절차`, `업무 앱 연결`, and `거버넌스`.

Harness update:

- Added a Label Occlusion Rule to `.automation/editorial-graphics-audit-harness.md`.
- Updated `ai-tech-review-editorial-harness/references/review-artwork-editor.md` so future hybrid imagegen/Skywork figures prefer `small badge + legend` or outer callouts when the generated scene is already information-rich.
- Updated the topic artwork brief so future reference-map post-processing checks whether labels cover the source clusters.

## 2026-05-10 Figure 4 Purpose Audit

Figure 4 was re-audited after the surrounding section was checked again.

Finding:

- The adjacent section argues that enterprise agents must pass through data access, permission scope, document output, human review, approval, and auditability.
- The current `enterprise-harness-illustration-v2-web.png` includes relevant objects: business documents, a lock, a checklist, an ID badge, a stamp, and records.
- But the image reads mainly as an atmospheric desk scene. It does not clearly show the operating path from data access to approval and audit.

Interpretation:

- This is not simply an imagegen limitation. Imagegen can be used for `infographic-diagram` prompts, but if the prompt asks for many symbolic objects without a fixed relationship, the model tends to produce a polished still-life.
- Figure 4 needs a relationship-first route: Skywork `인포그래픽`, deterministic workflow, or hybrid `generated base + SVG labels/arrows`.

Preferred replacement direction:

- Message: enterprise AI becomes useful when data access, permission scope, AI output, human review, approval, and audit log become one operating path.
- Recommended labels: `업무 데이터`, `권한 범위`, `AI 산출물`, `사람 검토`, `승인·감사 기록`.
- Recommended route: generate a Skywork `인포그래픽` or GPT Image 2 `infographic-diagram` candidate, then add Korean labels and arrows in SVG/HTML.

Harness update:

- Added a Figure Purpose Gate to `.automation/editorial-graphics-audit-harness.md`.
- Updated `ai-tech-review-editorial-harness/references/review-artwork-editor.md`.
- Added `Candidate C2. Enterprise Agent Operating Path` to the artwork infographic briefs.

## 2026-05-10 Figure 4 Replacement Pass

Generated candidates:

- Imagegen candidate 1: `artifacts/final_review/figures/candidates/enterprise-operating-path/imagegen/image_1-web.png`
- Imagegen candidate 2: `artifacts/final_review/figures/candidates/enterprise-operating-path/imagegen/image_2-web.png`
- Selected crop: `artifacts/final_review/figures/candidates/enterprise-operating-path/imagegen/enterprise-operating-path-selected-crop.png`
- Prompt: `artifacts/final_review/figures/prompts/enterprise-operating-path-imagegen.txt`

Skywork attempt:

- Prompt: `artifacts/final_review/figures/prompts/enterprise-operating-path-skywork.txt`
- Screenshot: `artifacts/final_review/figures/candidates/enterprise-operating-path/skywork/skywork-prompt-filled-v2.png`
- Result: prompt entry was possible, but the session showed a login/signup modal before generation. No Skywork export was produced in this pass.

Selection:

- Candidate 2 was selected because it showed the clearest left-to-right operating path: documents/data, permission boundary, AI draft, human review, audit/compliance record.
- The raw image was not inserted directly. It was cropped and embedded in `enterprise-operating-path-hybrid.svg`, then Korean labels and arrows were added deterministically.
- Reader-facing Figure 4 now uses `enterprise-operating-path-hybrid.svg`.

Render check:

- `artifacts/final_review/figure_audit/figure-04-enterprise-operating-path-v1.png` confirmed the rendered replacement.
- `figure-04.png`, `figure-contact-sheet.png`, and `figure-audit-records.json` were refreshed.

## 2026-05-09 Skywork Image Pass

Skywork Image was re-tested after login was confirmed in the browser session.

Login evidence:

- URL: `https://skywork.ai/?skill_id=119`
- Visible state: membership reward, coin balance, `Basic` badge, and user avatar were shown in the top-right account area.

Generated candidate:

- Project: `https://skywork.ai/project/2053110941997887488?from=home_query&is_new_project=false`
- Prompt archive: `artifacts/final_review/figures/prompts/connector-permission-skywork.txt`
- Original export: `artifacts/final_review/figures/candidates/skywork/connector-permission-skywork-original.png`
- Size: `2752 x 1536`
- Final hybrid figure: `artifacts/final_review/figures/connector-permission-skywork-magazine.svg`

Selection note:

- The Skywork image was more directly aligned with the connector section than the previous imagegen candidate because it separated workplace data, permission gate, and AI output in one readable composition.
- Skywork still inserted English headings even though the prompt requested no readable text. The final review therefore uses a hybrid figure: Skywork for the editorial base, deterministic SVG for Korean labels and precise review language.
- Render check: `artifacts/final_review/figure_audit/figure-06-skywork-v3.png` confirmed that the figure loads in the HTML page. `figure-06.png`, `figure-contact-sheet.png`, and `figure-audit-records.json` were refreshed after the Skywork replacement.
