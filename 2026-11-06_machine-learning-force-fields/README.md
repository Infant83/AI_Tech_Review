# Machine-learning force fields

Bilingual AI Tech Review article dated 6 November 2026. The Korean text is canonical; the complete English edition is in `dist/en/`.

- Final authored source: `artifacts/article-ko.json`, `artifacts/article-en.json`; Markdown exports in `reports/`.
- Final delivery: `dist/index.html`, `dist/review_ko.pdf`, `dist/en/index.html`, `dist/en/review_en.pdf`.
- Approved figure assets: `hero.webp`, `lj_energy_force.svg`, `lj_md_energy.svg`, `simulation_workflow.svg`, `barrier_accuracy.svg`. Eight generated `math_*.svg` assets and the self-contained `review.css` complete each language edition.
- Figure provenance and source versions: `artifacts/figure-manifest.json`. Scientific educational calculations: `build_intro_figures.py`, `build_figures.py` and their curated calculation data. The source datasets, paper captures and model weights are not distributed.
- Cover planning: `cover-art-brief.md`; explanation planning: `review-explanation-brief.md`. Font sources and complete SIL OFL notices are retained with the build assets.

The public article base is `https://infant83.io/AI_Tech_Review/reviews/2026-11-06_machine-learning-force-fields/`. The builder sets canonical, hreflang, language navigation and public citation/figure links to that base; it does not modify other articles or site-wide links.

Build from the repository root with Node.js, Python, Playwright/Chrome, FontTools with WOFF2 support, NumPy and Matplotlib installed:

```sh
TOPIC=2026-11-06_machine-learning-force-fields
npm install --prefix "$TOPIC/tmp/deps" --no-audit --no-fund mathjax-full@3.2.2 marked@16.4.2
python3 "$TOPIC/artifacts/export_manuscripts.py"
python3 "$TOPIC/artifacts/build_fonts.py" --regular "$TOPIC/artifacts/regular-source.ttf" --bold "$TOPIC/artifacts/bold-source.ttf"
node "$TOPIC/artifacts/build_review.mjs"
python3 "$TOPIC/artifacts/build_pdf.py" --node /path/to/node --modules /path/to/node_modules
REVIEW_BROWSER_MODULES=/path/to/node_modules node "$TOPIC/artifacts/check_output.mjs"
```

The existing figures are final assets. Regenerate their calculations with `python3 "$TOPIC/artifacts/build_intro_figures.py"` and `python3 "$TOPIC/artifacts/build_figures.py"`, then rebuild the HTML and PDFs. The PDF operation marker required by the active PDF skill belongs to the authoring workflow and should precede a new PDF authoring operation. Temporary dependencies and QA outputs stay under ignored `tmp/`.

The site publisher reads only `dist/` and resolves the explicitly referenced assets. Publication registry, hub metadata, archive records and deployment are maintained by the repository-level publisher.
