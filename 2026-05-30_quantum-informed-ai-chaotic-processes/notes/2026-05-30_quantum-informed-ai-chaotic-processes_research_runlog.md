# Research Runlog - Quantum-Informed AI for Chaotic Processes

Date: 2026-05-30 KST  
Package: `2026-05-30_quantum-informed-ai-chaotic-processes`

## Intake

- User supplied YouTube URL: https://www.youtube.com/watch?v=na-sQ-g2MAc
- Focus requested: topic related to quantum-informed AI for chaotic processes; deliver related research papers and insights.

## Local Capture

Commands/tools used:

- `yt-dlp --write-auto-subs --sub-langs "en.*,ko.*"` to capture captions.
- `yt-dlp --write-info-json --skip-download` to capture video metadata.
- `Skywork Search` skill to run three paper-discovery searches.
- Web search/open for primary source verification.

Captured files:

- `sources/na-sQ-g2MAc.info.json`
- `sources/na-sQ-g2MAc.en-orig.vtt`
- `sources/na-sQ-g2MAc.en.vtt`
- `sources/skywork_search_quantum-informed_AI_for_chaotic_processes_paper_result.txt`
- `sources/skywork_search_quantum_reservoir_computing_chaotic_time_series_prediction_result.txt`
- `sources/skywork_search_quantum_machine_learning_chaotic_dynamical_systems_papers_result.txt`

Capture notes:

- English original/English caption files were downloaded successfully.
- Korean auto-caption download was blocked by YouTube HTTP 429/403 during the first attempt.
- `yt-dlp` warned that the local version is older than 90 days and that no supported JavaScript runtime is configured. Metadata and English captions were still sufficient for this review.

## Verified Source Highlights

- The video is `Exciting AI Updates Weekly - May 29, 2026`, Lev Selector, uploaded 2026-05-29, duration 37:02.
- The relevant chapter is `26:20-27:16`, titled `Quantum-informed AI for Chaotic Processes`.
- The key paper is Wang et al., `Quantum-Informed Machine Learning for Predicting Spatiotemporal Chaos with Practical Quantum Advantage`, Science Advances 2026 / arXiv `2507.19861`, DOI `10.1126/sciadv.aec5049`.
- The official repository is `https://github.com/UCL-CCS/QIML`.

## Outputs Created

- `notes/2026-05-30_quantum-informed-ai-chaotic-processes_sources.md`
- `notes/2026-05-30_quantum-informed-ai-chaotic-processes_deepresearch_prompt.md`
- `reports/2026-05-30_quantum-informed-ai-chaotic-processes_memo.md`
- `reports/2026-05-30_quantum-informed-ai-chaotic-processes_deepresearch.md`
- `reports/2026-05-30_quantum-informed-ai-chaotic-processes_final_review.md`
- `skywork_inputs/2026-05-30_quantum-informed-ai-chaotic-processes_skywork_prompt_v1.md`

## Rendering / Sync Status

- Markdown-to-HTML rendering: completed.
  - `reports/2026-05-30_quantum-informed-ai-chaotic-processes_memo.html`
  - `reports/2026-05-30_quantum-informed-ai-chaotic-processes_deepresearch.html`
  - `reports/2026-05-30_quantum-informed-ai-chaotic-processes_final_review.html`
- Final-review figures: added under `artifacts/final_review/figures/`.
- HTML local image references: checked, all four final-review figure paths resolved.
- Editorial audit: completed after revision; `finding_count: 0`, `figure_density: ok`.
- Obsidian mirror: completed.
  - `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-30_quantum-informed-ai-chaotic-processes\2026-05-30_quantum-informed-ai-chaotic-processes_index.md`
  - mirrored reports, source note, deep-research prompt, research runlog, and final-review figures.
- OpenProject update: not performed in this pass because no target work package was specified.
- Skywork PPTX/PDF export: superseded by the user direction on 2026-05-30 to use `AI Tech Review Letters` instead of Skywork.

## AI Tech Review Letters Conversion

- Direction change: user requested `Skywork 말고 AI Tech Review Letters 생성`.
- Converted `reports/2026-05-30_quantum-informed-ai-chaotic-processes_final_review.md` into `AI Tech Review Letters` format.
  - Added `type: ai-tech-review-letter`, `series: AI Tech Review Letters`, `issue date: 2026-05-30`.
  - Added article hero and section figures.
  - Added glossary and article metadata.
- Figure manifest:
  - `artifacts/final_review/figure_manifest.md`
- Final audit:
  - command: `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py reports\2026-05-30_quantum-informed-ai-chaotic-processes_final_review.md`
  - result: `finding_count: 0`, `figure_count: 5`, `figure_density: ok`
- Final HTML render:
  - `reports/2026-05-30_quantum-informed-ai-chaotic-processes_final_review.html`
- Distribution package:
  - command: `python scripts\html_to_dist.py reports\2026-05-30_quantum-informed-ai-chaotic-processes_final_review.html --dist dist --zip --zip-path dist.zip`
  - result: `[local-ref-check] ok`
  - path: `2026-05-30_quantum-informed-ai-chaotic-processes\dist`
  - zip: `2026-05-30_quantum-informed-ai-chaotic-processes\dist.zip`
- Public site:
  - updated `scripts/publish_public_site.py`
  - command: `python scripts\publish_public_site.py`
  - result: `[public-site-check] ok`, `reviews=5`
  - path: `site\reviews\2026-05-30_quantum-informed-ai-chaotic-processes\index.html`
- Browser verification:
  - `npx playwright screenshot --full-page file:///.../reports/2026-05-30_quantum-informed-ai-chaotic-processes_final_review.html %TEMP%\quantum_qiml_letters_final_review.png`
  - `npx playwright screenshot --full-page file:///.../site/reviews/2026-05-30_quantum-informed-ai-chaotic-processes/index.html %TEMP%\quantum_qiml_letters_site.png`
  - visual check: hero, section figures, side navigation, tables, references rendered correctly.

## Imagegen / Feynman-Style Revision

- Direction change: user requested a friendlier intro, `imagegen` explanatory images, Feynman-style explanation, and Kim Hyun-Jung style prose audit.
- Used `imagegen` skill with OpenAI Image API:
  - CLI: `C:\Users\angpa\.codex\skills\imagegen\scripts\image_gen.py`
  - model: `gpt-image-1.5`
  - command: `generate-batch --concurrency 2 --downscale-max-dim 1280`
  - temp JSONL: `tmp\imagegen\quantum_qiml_letters_prompts.jsonl`, deleted after successful generation.
- Generated article images:
  - `artifacts/final_review/figures/imagegen/qiml_hero_quantum_prior-web.png`
  - `artifacts/final_review/figures/imagegen/feynman_chaos_drop_analogy-web.png`
  - `artifacts/final_review/figures/imagegen/qprior_compact_memory_explainer-web.png`
  - `artifacts/final_review/figures/imagegen/long_rollout_physics_check-web.png`
- Updated article:
  - rewrote opening around the ink-drop analogy and sensitivity to initial conditions.
  - added Q-Prior explanation before the formal pipeline.
  - added long-rollout physical consistency explanation before the metric table.
  - updated `artifacts/final_review/figure_manifest.md` with imagegen prompts and validation notes.
- Final audit after rewrite:
  - result: `finding_count: 0`, `figure_count: 8`, `figure_density: ok`
- Render/package:
  - final HTML regenerated.
  - `dist/` and `dist.zip` regenerated, `[local-ref-check] ok`.
  - public site regenerated, `[public-site-check] ok`, `reviews=5`.
- Browser verification after imagegen revision:
  - `npx playwright screenshot --full-page file:///.../reports/2026-05-30_quantum-informed-ai-chaotic-processes_final_review.html %TEMP%\quantum_qiml_letters_imagegen_final_review.png`
  - `npx playwright screenshot --full-page file:///.../site/reviews/2026-05-30_quantum-informed-ai-chaotic-processes/index.html %TEMP%\quantum_qiml_letters_imagegen_site.png`
  - visual check: imagegen hero, analogy image, Q-Prior image, long-rollout image, SVG diagrams, tables, references rendered correctly.
