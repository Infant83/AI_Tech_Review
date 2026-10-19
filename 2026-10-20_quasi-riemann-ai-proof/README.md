# The quasi-Riemann hypothesis and AI mathematics

Bilingual AI Tech Review prepared for publication on 2026-10-20. Korean is canonical, with a complete English edition and a complete PDF for each language. Intended public destinations: [한국어 리뷰](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-20_quasi-riemann-ai-proof/), [English edition](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-20_quasi-riemann-ai-proof/en/), and [document archive](https://infant83.github.io/AI_Tech_Review/archive/).

The review examines the mathematical statement behind the quasi-Riemann hypothesis, its connection to prime-distribution error bounds, the reported AI research workflow and the conditions for checking a proof. Reporting a claimed result, assessing its mathematics and independently rebuilding a formal proof are separate activities. This production does not claim an independent Lean rebuild or independent verification of the reported proof.

## Package contents

- `reports/review_ko.md`, `reports/review_en.md`: complete article manuscripts.
- `artifacts/hero.webp`: AI-generated conceptual cover, not mathematical evidence.
- [figure-manifest.json](figure-manifest.json): cover generation mode and full prompt, figure provenance, teaching-data files and source revisions.
- `artifacts/zero_regions_*.svg`, `artifacts/prime_error_*.svg`, `artifacts/proof_path_*.svg`: original, deterministic explanatory figures.
- `artifacts/build_mobile_figures.py`: compact mobile variants with vertically stacked panels, a readable power plot and wrapped verification cards. The desktop figures remain the print/PDF versions.
- `artifacts/build_review.mjs`: bilingual HTML with static SVG equation rendering and a strict public-asset allowlist.
- `artifacts/build_fonts.py`: openly licensed Korean font subsets, renamed as Review Sans Subset; full source licensing is retained.
- `artifacts/build_pdf.py`: complete-article PDFs, desktop/mobile browser checks and screenshots.
- `artifacts/review.css`: responsive screen typography and A4 print layout.
- `dist/index.html`, `dist/review_ko.pdf`: Korean deliverables.
- `dist/en/index.html`, `dist/en/review_en.pdf`: English deliverables.
- `tmp/pdfs/`: local output checks and screenshots, excluded from publication and Git.

## Rebuild

Node.js dependencies are `marked`, `mathjax-full` 3.2.2 and `playwright`. PDF printing uses installed Chrome. Font subsetting requires Python fontTools and brotli. Runtime and source-font locations are supplied as arguments or environment variables and are not embedded as host paths in final HTML/PDF.

```sh
python artifacts/build_figures.py --font /path/to/NanumGothic-Regular.ttf
python artifacts/build_mobile_figures.py --font /path/to/NanumGothic-Regular.ttf
python artifacts/build_fonts.py --regular /path/to/NanumGothic-Regular.ttf --bold /path/to/NanumGothic-Bold.ttf
node artifacts/build_review.mjs --public-base=https://infant83.github.io/AI_Tech_Review/reviews/2026-10-20_quasi-riemann-ai-proof/
python artifacts/build_pdf.py --node /path/to/node --modules /path/to/node_modules
```

Set `REVIEW_NODE_MODULES` and/or `CODEX_PRIMARY_RUNTIME_NODE_MODULES` when dependencies are installed outside the package. The HTML and PDF builders support selecting a single language with `--language=ko` or `--language=en`. Rebuild font subsets after changing the manuscripts or disclosure text.

The font builder defaults to Nanum Gothic's bundled full OFL in `artifacts/font-OFL.txt`. When using another font, supply its complete license with `--license`. Generated CSS embeds both WOFF2 subsets and the complete license, so published pages need no external font download or sibling font file.

## Public output and verification

The HTML builder writes canonical directory URLs with trailing slashes, Korean/English/x-default hreflang links and absolute language-navigation links. Default canonical URLs point to the intended public location above. Static math SVGs make equations independent of external browser-side math services. Each language's output includes only its final HTML, CSS, PDF and referenced, explicitly allowed figures/equations. Internal notes, raw source captures, JSON, Markdown and QA screenshots are excluded from `dist/`.

The short initial disclosure uses the publisher's `p.byline-disclosure` convention. The full disclosure is surrounded by the standard AI Tech Review authoring-disclosure markers, allowing the repository publisher to replace it with the centralized publication record without duplicate bylines.

These builders do not register the review or PDFs, upload files, commit or deploy. Public registration uses the repository's existing publisher and archive commands after the full manuscripts, PDF pages, metadata, links and assets are checked. The final PDFs are registered separately as Korean and English articles in the document archive. Narrow screens use dedicated mobile SVGs through separate `src` attributes; print/PDF uses the desktop figures. The mobile builder checks every rendered label against the output canvas.

## Editorial record

Responsible editor: 김현중 / Hyun-Jung Kim. AI assistance: OpenAI Codex; the exact authoring-model identifier was not retained. Recorded roles are `root` for synthesis, Korean writing, conceptual cover, scientific editing and publication integration; `academic_sources` for mathematical source and claim review; `applications_sources` for AI research workflows, English translation, original figures and independent teaching calculations; `review_format` for equations, typesetting, responsive figures and publication QA; and `publish_audit` for publication metadata, link, asset and disclosure audit.

Writing and public posting were requested; no line-by-line human approval is claimed. The production follows AI Tech Review Editorial Harness 2026.08 and records the limits of source checking and formal-proof verification in both editions.
