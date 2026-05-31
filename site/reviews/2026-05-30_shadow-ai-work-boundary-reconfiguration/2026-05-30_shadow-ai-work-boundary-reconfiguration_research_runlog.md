# Research Runlog

- Date: 2026-05-30
- Workspace: `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review`
- Topic folder: `2026-05-30_shadow-ai-work-boundary-reconfiguration`
- Input URL: https://chatgpt.com/c/6a16cba6-a838-83a4-840b-f3059716c8a4

## Capture

- Opened the shared ChatGPT conversation in the Playwright browser.
- Page title resolved as `AI 업무 경계 재편`.
- The general web fetch path did not expose the conversation text, so browser automation was used.
- Captured the visible page text into `sources/2026-05-30_chatgpt_conversation_visible_text.txt`.
- Exported the latest Deep Research iframe result through the ChatGPT `마크다운으로 내보내기` control.
- Saved latest Deep Research export as `sources/2026-05-30_chatgpt_deepresearch_latest_export.md`.
- Saved accessibility snapshot as `sources/2026-05-30_chatgpt_accessibility_snapshot.md`.
- Saved page screenshot as `artifacts/2026-05-30_chatgpt_shared_page_full.png`.

## Observations

- The conversation contains multiple Deep Research frames. The latest exported report is titled `생성형 AI 시대의 일 방식 전환과 보안민감 한국 대기업의 병목과 해법`.
- Earlier conversation material introduces stronger conceptual frames than the latest report title alone suggests, especially `AI FOMO Cascade`, `Governance Latency`, `Approval Debt`, `Governance Workload`, and `FOMO-driven Hidden Work`.
- Exported Deep Research citations remain in ChatGPT internal marker form such as `turn28view0`, not direct URLs. Final review work should reconstruct and verify source URLs before treating the claims as report-ready.
- No NotebookLM step was used.
- No Skywork generation was started in this intake pass.

## Final Review Pass

- Created final review markdown: `reports/2026-05-30_shadow-ai-work-boundary-reconfiguration_final_review.md`.
- Created final review HTML companion: `reports/2026-05-30_shadow-ai-work-boundary-reconfiguration_final_review.html`.
- Added final-review figure set under `artifacts/final_review/figures/`:
  - `imagegen/shadow_ai_enterprise_boundary_hero.png`
  - `imagegen/shadow_ai_hidden_work_cascade.png`
  - `imagegen/shadow_ai_governed_paths_room.png`
  - `shadow_ai_absorption_gap_hero.svg`
  - `shadow_ai_mechanism_flow.svg`
  - `shadow_ai_governance_model.svg`
  - `shadow_ai_reference_map.svg`
- Added figure manifest: `artifacts/final_review/figure_manifest.md`.
- Visual style guide checked:
  - `.codex/rules/visuals-and-image-generation.md`
  - `.codex/rules/writing-harness.md`
  - Published reference article: `https://infant83.github.io/AI_Tech_Review/reviews/2026-05-23_ai-scientist-execution-harness/index.html`
- Updated visual composition to match the public `AI Tech Review Letters` pattern:
  - 3 `imagegen` PNG illustrations for article hero and section openers.
  - 4 deterministic SVG diagrams for precise Korean labels, mechanisms, governance model, and reference map.
- Regenerated the third imagegen section opener once because the first generated candidate contained a readable `AI Gateway` label. The adopted version avoids in-image text; exact labels are handled by SVG and captions.
- Regenerated the intro hero once more after visual review:
  - New file: `artifacts/final_review/figures/imagegen/shadow_ai_enterprise_boundary_hero_v2.png`.
  - Reason: the previous hero conveyed enterprise security boundaries, but did not show enough contrast between external AI speed and internal adoption friction, nor enough Shadow AI / AI burnout pressure on the employee.
  - Adopted v2 because it shows fast external AI work on one side, locked internal approval and verification burden on the other, and a tired employee caught between paperwork and a subtly glowing personal device.
- Regenerated the intro hero again after user review:
  - New adopted file: `artifacts/final_review/figures/imagegen/shadow_ai_burnout_unrecognized_cycle_v4_loop.png`.
  - Reason: v2/v3 still made the burden look mostly like an in-office problem. The user clarified that the image should show the employee also struggling outside the office, doing after-hours AI work that is not recognized as official work, and then returning inside where FOMO, locked tools, and burnout reappear.
  - Adopted v4 loop because it shows the outside-night personal AI work, the company gate boundary, and the inside-office locked-tool / paperwork / meeting-pressure scene in one continuous visual cycle.
- Replanned and regenerated the intro hero again around `보이지 않는 두 번째 근무`:
  - New adopted file: `artifacts/final_review/figures/imagegen/shadow_ai_invisible_second_shift_v5_section.png`.
  - Reason: prior versions still felt like a tired-office-worker image. The revised planning target was: `회사 밖에서 이미 일을 했는데, 회사 안에서는 그 시간이 사라진다`.
  - Adopted v5 section because the night AI work appears as a blue flow that reaches the company gate, turns into a black shadow rather than an official record, and follows the employee into the inside-office FOMO / locked-tool / approval-paper scene.
- Regenerated the intro hero again after user review of the spatial metaphor:
  - New adopted file: `artifacts/final_review/figures/imagegen/shadow_ai_same_level_gap_v8_shared_burden.png`.
  - Reason: v7 made the company appear too elevated and detached, while the user wanted same-level contrast: the company and individual are both working hard, but light and outputs are blocked by a broken operating bridge rather than by hierarchy or a security gate.
  - Adopted v8 shared-burden because it shows personal AI output on one side, company-side validation / checklist / process labor on the other, and a broken bridge between them that both sides try to patch.
- Regenerated the intro hero again after user review of the DX / AX metaphor:
  - New adopted file: `artifacts/final_review/figures/imagegen/shadow_ai_ax_native_bottleneck_v9.png`.
  - Reason: v8 made the company side look too much like a paperwork pile. The user clarified that many companies have achieved DX, but AX still fails to run natively across approval, verification, decision, and workflow handoff points. Some AI adoption can appear successful only because someone's shadow AI and shadow effort keep the path alive.
  - Adopted v9 because it shows a modern digital operation room with green success signals, a red/blocked handoff point, and an exhausted worker whose personal AI work and shadow effort temporarily sustain the glowing AX flow. This better connects partial AX success, unsustainable hidden labor, and AI burnout.
- Regenerated the intro hero again after user review of tone and silo visibility:
  - New adopted file: `artifacts/final_review/figures/imagegen/shadow_ai_calm_silo_night_v11_clean.png`.
  - Reason: v10 better showed home/night work and enterprise silos, but its bright AI streams were too flashy for the existing AI Tech Review Letters visual style. The user asked to keep the calmer existing style and make the company internally segmented rather than fully smooth.
  - Adopted v11 clean because it uses a muted watercolor style, keeps the late-night home worker, shows modern DX office silos and partial AX connection, and removes readable in-image text after an edit pass.
- Revised the Figure 1 caption to reduce explanatory wording and let the image carry more of the mood.
- Reviewed figures 2, 3, 6, and 7 before public deployment:
  - Figure 2: shortened the top explanatory sentence to remove meta-review phrasing.
  - Figure 3: split the bottom result statement into two lines so the text stays inside the red result box.
  - Figure 6: shortened the title/subtitle and success-condition sentence for better mobile scaling.
  - Figure 7: adjusted the title to match the final `References` structure.
  - Browser verification after cache-busting SVG image reload: all four SVGs reported `viewOverflowCount: 0`; desktop and mobile page checks reported `overflowCount: 0`.
- Added `작성 정보` and reorganized references into `직접 검증 참고자료`, `처음 참고한 자료`, and `문체와 시각자료 참고` to match the published AI Tech Review Letters pattern.
- Created distribution package:
  - Command: `python scripts\html_to_dist.py .\2026-05-30_shadow-ai-work-boundary-reconfiguration\reports\2026-05-30_shadow-ai-work-boundary-reconfiguration_final_review.html --dist .\2026-05-30_shadow-ai-work-boundary-reconfiguration\dist --zip --zip-path .\2026-05-30_shadow-ai-work-boundary-reconfiguration\dist.zip`
  - Result: `[local-ref-check] ok`.
- Published to local public site staging:
  - Added the review to `scripts/publish_public_site.py`.
  - Command: `python scripts\publish_public_site.py`
  - Result: `[public-site-check] ok`, `reviews=6`.
- Browser-checked staged public site:
  - Hub latest card points to `reviews/2026-05-30_shadow-ai-work-boundary-reconfiguration/index.html`.
  - Public review contains `작성 정보`, `References`, `직접 검증 참고자료`, and `문체와 시각자료 참고`.
  - Desktop and mobile checks reported all images complete and `overflowCount: 0`.
- Reconstructed and verified the external reference layer with current public sources, including Microsoft Work Trend Index 2024/2025, Microsoft Infinite Workday, McKinsey State of AI 2025, KPMG/University of Melbourne AI trust report, Netskope Cloud and Threat Report 2026, Upwork 2024/2025 research, NIST AI RMF, NIST AI 600-1, NIS DeepSeek security notice, PIPC/DeepSeek service suspension notice, Korea policy briefings, and the CNBC Samsung ChatGPT restriction report.
- Updated one older intake claim during verification: the review uses McKinsey 2025's current `88%` regular AI-use figure and the approximately `6%` high-performer distinction, rather than treating the earlier exported `78%` framing as current.

## Verification

- Rendered HTML with the shared workspace renderer:
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-30_shadow-ai-work-boundary-reconfiguration\reports\2026-05-30_shadow-ai-work-boundary-reconfiguration_final_review.md`
- Ran editorial audit harness:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-30_shadow-ai-work-boundary-reconfiguration\reports\2026-05-30_shadow-ai-work-boundary-reconfiguration_final_review.md`
  - Result after imagegen revision: `finding_count: 0`, `h2_count: 11`, `figure_count: 7`, `figure_density: ok`.
- Browser-checked local HTML through a temporary local server:
  - Server: `python -m http.server 8775 --bind 127.0.0.1 --directory C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review`
  - Desktop check after imagegen revision: `1440x1200`, `figureCount: 7`, `imageCount: 7`, all images complete, `overflowCount: 0`.
  - Mobile check after imagegen revision: `390x1000`, `figureCount: 7`, `imageCount: 7`, all images complete, `overflowCount: 0`.
  - Desktop full-page screenshot: `artifacts/final_review/verification/shadow_ai_final_review_desktop_imagegen.png`.
  - Mobile viewport screenshot: `artifacts/final_review/verification/shadow_ai_final_review_mobile_imagegen_viewport.png`.
  - Mobile full-page screenshot failed due a browser protocol screenshot capture limitation after the DOM/image/overflow checks had already passed.
  - Hero v2 check: `artifacts/final_review/verification/shadow_ai_final_review_hero_v2_check.json`; desktop and mobile both reported `figureCount: 7`, `imageCount: 7`, all images complete, and `overflowCount: 0`.
  - Hero v4 loop check: `artifacts/final_review/verification/shadow_ai_final_review_hero_v4_loop_check.json`; desktop and mobile both reported `figureCount: 7`, `imageCount: 7`, all images complete, and `overflowCount: 0`.
  - Hero v5 section check: `artifacts/final_review/verification/shadow_ai_final_review_hero_v5_section_check.json`; desktop and mobile both reported `figureCount: 7`, `imageCount: 7`, all images complete, and `overflowCount: 0`.
  - Hero v8 shared-burden check: `artifacts/final_review/verification/shadow_ai_final_review_hero_v8_shared_burden_check.json`; desktop and mobile both reported `figureCount: 7`, `imageCount: 7`, all images complete, and `overflowCount: 0`.
  - Hero v9 AX-native bottleneck check: `artifacts/final_review/verification/shadow_ai_final_review_hero_v9_ax_native_bottleneck_check.json`; desktop and mobile both reported `figureCount: 7`, `imageCount: 7`, all images complete, and `overflowCount: 0`.
  - During the v9 check, local Node did not have the `playwright` module available; verification continued through the MCP Playwright browser tool.
  - Hero v11 calm silo/night check: `artifacts/final_review/verification/shadow_ai_final_review_hero_v11_calm_silo_night_check.json`; desktop and mobile both reported the updated title, `figureCount: 7`, `imageCount: 7`, all images complete, and `overflowCount: 0`.
  - Screenshots and browser check JSON are stored under `artifacts/final_review/verification/`.
  - Temporary local server was stopped after verification.

## Sync

- Obsidian mirror created at `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-30_shadow-ai-work-boundary-reconfiguration`.
- Mirrored final review markdown, HTML companion, final-review figure assets including `imagegen/`, figure manifest, source note, discussion-understanding note, and runlog.
- OpenProject sync was not performed because no target work package ID was available in the topic package or workspace metadata. To avoid updating the wrong work package, this remains pending until the target work package is provided.

## Current Status

- Intake capture: complete
- Source note: complete
- Discussion understanding memo: complete
- External source verification: complete
- Memo/deepresearch/final_review normalization: final review complete
- HTML companion: complete
- Skywork deck: pending
- Obsidian sync: complete
- OpenProject sync: pending target work package

## 2026-05-31 Figure 2 Arrow Fix

- Revised `artifacts/final_review/figures/shadow_ai_absorption_gap_hero.svg` after reader review.
- Removed the small curved arrows inside the three cards because they made the flow direction ambiguous.
- Replaced them with two clear card-to-card arrows and one bottom cumulative phase arrow.
- Verification screenshot: `artifacts/final_review/verification/shadow_ai_figure_2_arrow_fix.png`.

## 2026-05-31 Heading Revision

- Changed the closing section heading from `이 리뷰를 읽고 남겨야 할 질문` to `해결해야 할 숙제`.
- Re-rendered final-review HTML, regenerated `dist/`, refreshed `dist.zip`, and rebuilt the public site package.

## 2026-05-31 Reference Link Audit

- Updated `scripts/html_to_dist.py` so copied Markdown files inside `dist/` rewrite local image and document links to flat relative paths.
- Updated `scripts/publish_public_site.py` so public review folders keep clickable local reference links for copied `.md`, `.py`, `.txt`, `.json`, and other safe support files instead of disabling them.
- Rebuilt `dist/`, `dist.zip`, and `site/reviews/2026-05-30_shadow-ai-work-boundary-reconfiguration/`.
- Local link audit passed with no missing local references in:
  - source final-review Markdown
  - `dist/index.html`
  - `dist/2026-05-30_shadow-ai-work-boundary-reconfiguration_final_review.md`
  - public review `index.html`
  - public review copied final-review Markdown
- After rebuilding all public review `dist/` packages with the updated packaging script, the full public review set passed the same local link audit for review HTML and copied final-review Markdown files.
