# Quantum software platforms and AI agents

Bilingual AI Tech Review published on 2026-10-25. Korean is canonical; the English edition preserves the same conditions, evidence levels, reported values and verification limits.

Public destinations: [한국어 리뷰](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-25_quantum-software-platforms-ai-agents/), [English edition](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-25_quantum-software-platforms-ai-agents/en/), and [document archive](https://infant83.github.io/AI_Tech_Review/archive/). The original GitHub Pages addresses currently redirect to the service domain infant83.io.

## Contents

- `reports/review_ko.md`, `reports/review_en.md`: complete article manuscripts.
- `artifacts/hero.webp`: original AI-generated conceptual cover, distinct from a device, circuit or quantitative benchmark.
- `artifacts/check_oracle.py`, `artifacts/oracle_results.json`: independent NumPy teaching calculation and its results.
- `artifacts/synthesis_reported.json`: attributed historical compiler values reported in the cited preprint.
- `artifacts/build_figures.py`: 12 original, outlined SVG figures, comprising three concepts in two languages and desktop/mobile layouts.
- [Figure provenance and scope](artifacts/FIGURE_PROVENANCE.md): original geometry, source data, labels and license boundaries.
- `artifacts/build_review.mjs`: bilingual HTML, content-hashed SVG equations and a strict asset allowlist.
- `artifacts/build_fonts.py`: renamed openly licensed WOFF2 subsets, with the complete source license retained.
- `artifacts/build_pdf.py`: complete A4 PDFs and desktop/mobile browser checks.
- `dist/index.html`, `dist/review_ko.pdf`: Korean outputs.
- `dist/en/index.html`, `dist/en/review_en.pdf`: English outputs.

Private source captures and research notes remain in ignored `notes/`. Screenshots, page renders and local checks remain in ignored `tmp/`. Those files do not enter the public article output.

## Rebuild

Dependencies: Node.js with `marked`, `mathjax-full` 3.2.2 and `playwright`; Chrome for PDF printing; Python with NumPy, Matplotlib, fontTools and brotli. PDF inspection uses pypdf, Pillow and Poppler. Runtime and font paths are supplied as arguments or environment variables, rather than embedded in public outputs.

From this package directory:

```sh
python artifacts/check_oracle.py
python artifacts/build_figures.py --font /path/to/NanumGothic-Regular.ttf --bold /path/to/NanumGothic-Bold.ttf
node artifacts/build_review.mjs --check-math-stability
python artifacts/build_fonts.py --regular /path/to/NanumGothic-Regular.ttf --bold /path/to/NanumGothic-Bold.ttf
node artifacts/build_review.mjs --public-base=https://infant83.github.io/AI_Tech_Review/reviews/2026-10-25_quantum-software-platforms-ai-agents/
python artifacts/build_pdf.py --node /path/to/node --modules /path/to/node_modules
```

Set `REVIEW_NODE_MODULES` and/or `CODEX_PRIMARY_RUNTIME_NODE_MODULES` for Node dependencies installed outside this package. Both HTML and PDF builds support selecting one language. Rebuild font subsets after changing either manuscript or the disclosure.

Equation filenames and internal SVG IDs depend on TeX content and display mode. Adding an unrelated equation therefore leaves existing equation bytes unchanged. Figure text is converted to glyph outlines, while article text uses two WOFF2 subsets embedded in CSS. The full Nanum Gothic SIL Open Font License is embedded in the generated CSS and retained separately in production sources.

Only final HTML, PDF, CSS, `hero.webp` and referenced approved SVGs enter each language's `dist/` directory. The only figure stems are `program_paths`, `oracle_semantics` and `synthesis_tradeoff`; responsive variants use explicit `src` attributes. PDF printing selects desktop figures. Public canonical and cross-language links retain directory trailing slashes and absolute public destinations.

## Verification and publication record

Responsible editor: 김현중 / Hyun-Jung Kim. AI assistance: OpenAI Codex; the exact authoring-model identifier was not retained. The review follows Editorial Harness 2026.08 and Scientific Explanation and Visual Communication Principles 1.0 (2026-10-22). Topic, writing and public posting were requested; no line-by-line human approval is claimed.

The production record assigns Korean writing, the original cover, the NumPy example, ecosystem research and publication integration to `root`; Qiskit HLS/Target/agent documentation and scientific audit to `academic_sources`; benchmark denominators to `academic_sources/theory_crosscheck`; Classiq papers, SDK, guarantees, reported data and full English translation to `applications_sources`; original bilingual figures, typesetting and output QA to `review_format`. `applications_sources/translation_audit` independently crosschecked bilingual sources, notation, equations and conditions. Independent explanation and conceptual-cover review, and publication audit are assigned to `publish_audit`.

The NumPy result is an ideal three-qubit teaching calculation, not a QPU, vendor or LLM benchmark. The two Classiq points are author-reported compilation results for historical Classiq 0.60.0; this review did not execute synthesis or establish current performance, global optimality or physical quantum advantage. No account, paid API or QPU was invoked.

The short byline uses `p.byline-disclosure`; the full record uses the standard authoring-disclosure comment markers for centralized publication replacement. These builders do not register archive entries, commit, upload or deploy. A video is not added by default.

## Final local checks

The final PDFs have 11 Korean pages and 13 English pages. All 24 pages were rendered and visually inspected. Desktop/390px output, the original cover and three responsive figure pairs, six equations, 18 references, seven actual production roles, canonical/hreflang, embedded fonts and web-only PDF links passed. There are no missing images, literal emphasis markers, PDF attachments or private paths.

The isolated publication checkout passed 90 repository tests: 89 passed and one optional Python-Markdown test was skipped because its dependency is unavailable. The reviewed PDFs were copied without any byte change from the production workspace. Concurrent, unrelated site-feature edits were excluded from this publication.

An independent final publication audit passed after restoring prior review files: the public-site validator returned no errors, all 46 prior review and 78 prior archive records were preserved, and each language has four byte-identical PDF copies. SVG path-line trailing spaces were normalized in production and reading copies; parsed XML geometry, attributes and text were unchanged, and the generator now applies the same normalization. The finalized PDFs were unchanged.

## Live publication · 2026-10-25

The [Korean review](https://infant83.io/AI_Tech_Review/reviews/2026-10-25_quantum-software-platforms-ai-agents/) and [complete English edition](https://infant83.io/AI_Tech_Review/reviews/2026-10-25_quantum-software-platforms-ai-agents/en/) are published with their PDFs in the review and document-archive catalogs. Publication source commit: `559225822b74613910ffe884f1866c91d4fecae0`. The [publish workflow](https://github.com/Infant83/AI_Tech_Review/actions/runs/40158428322) and [Pages deployment](https://github.com/Infant83/AI_Tech_Review/actions/runs/40158506190) succeeded.

Both original language addresses followed the existing redirect to infant83.io, returned HTTP 200 at their final destinations and matched the local reading copies. All 39 checked files—including review assets, both PDFs, archive copies, the hub and catalogs—matched their reviewed local SHA256 values. Domain settings and unrelated site-feature work were not changed by this publication.

Live Chrome QA also passed on the resolved infant83.io pages in both languages at 1440×1000 and 390×844. The cover and all images loaded, all three responsive figure pairs selected correctly, Korean → English → Korean links were clicked successfully, and both PDF links were correct. Document overflow, page errors and console errors/warnings were zero. Screenshots and detailed QA records remain outside public distribution.
