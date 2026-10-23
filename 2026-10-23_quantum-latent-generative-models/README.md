# Photonic sampling and quantum latent generative models

Bilingual AI Tech Review prepared for publication on 2026-10-23. Korean is canonical; the English edition preserves the same reported values, comparison conditions and execution boundaries.

Intended public destinations: [한국어 리뷰](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-23_quantum-latent-generative-models/), [English edition](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-23_quantum-latent-generative-models/en/), and [document archive](https://infant83.github.io/AI_Tech_Review/archive/).

## Contents

- `reports/review_ko.md`, `reports/review_en.md`: complete article manuscripts.
- `artifacts/hero.webp`: original AI-generated conceptual cover, distinct from experimental data and molecular structures.
- `artifacts/build_review.mjs`: self-contained bilingual HTML, stable static SVG equations and an explicit figure allowlist.
- `artifacts/build_fonts.py`: openly licensed Korean font subsets, renamed as Review Sans Subset, with the complete source license retained.
- `artifacts/build_pdf.py`: complete article PDFs and desktop/mobile browser output checks.
- `artifacts/review.css`: responsive reading layout and A4 print typography.
- `dist/index.html`, `dist/review_ko.pdf`: Korean deliverables.
- `dist/en/index.html`, `dist/en/review_en.pdf`: English deliverables.
- `tmp/pdfs/`: local PDF page renders, screenshots and verification records; excluded from publication and Git.

Figures are produced separately and registered by their exact stems in the HTML builder: `sampling_pipeline`, `hom_interference`, `qm9_results` and the optional `toy_latents`. Each may have Korean/English desktop and mobile SVG variants. Only referenced assets are copied, so an unused optional figure need not exist. Variants use explicit `src` attributes; the print layout uses the desktop figures. Internal notes, raw source captures and production records remain outside `dist/`.

The [figure and computation provenance](artifacts/FIGURE_PROVENANCE.md) records source data, reported values, the limited CPU run and verification checks.

## Rebuild

Dependencies: Node.js with `marked`, `mathjax-full` 3.2.2 and `playwright`; Chrome for PDF printing; Python fontTools and brotli for WOFF2 subsetting. PDF validation also uses pypdf, Pillow and Poppler. Supply runtime and font paths at build time rather than placing host paths in the public output.

From this package directory:

```sh
node artifacts/build_review.mjs --check-math-stability
python artifacts/build_fonts.py --regular /path/to/NanumGothic-Regular.ttf --bold /path/to/NanumGothic-Bold.ttf
node artifacts/build_review.mjs --public-base=https://infant83.github.io/AI_Tech_Review/reviews/2026-10-23_quantum-latent-generative-models/
python artifacts/build_pdf.py --node /path/to/node --modules /path/to/node_modules
```

Set `REVIEW_NODE_MODULES` and/or `CODEX_PRIMARY_RUNTIME_NODE_MODULES` for dependencies installed outside the package. HTML/PDF builds support `--language=ko` or `--language=en`. Rebuild the font subsets after changing either manuscript or the authoring disclosure. The bundled full OFL is for Nanum Gothic; pass another font's full license using `--license` when changing source fonts.

Equation filenames depend on TeX content and display mode. IDs and references inside each SVG are normalized using that content hash, and existing identical SVGs are left untouched. The stability check renders an unrelated formula between identical expressions and verifies that their resulting SVG bytes remain identical. Adding a caption equation therefore does not rewrite later equations.

The generated CSS embeds both WOFF2 subsets and the complete font license. Published pages use no external font or browser-side math service. Canonical directory URLs retain trailing slashes, with Korean/English/x-default hreflang and absolute public language links. Only final HTML, PDF, CSS, the hero and explicitly approved SVG assets enter `dist/`.

## Editorial and publication record

Responsible editor: 김현중 / Hyun-Jung Kim. AI assistance: OpenAI Codex; the exact authoring-model identifier was not retained. Production roles are recorded under `root`, `academic_sources`, `applications_sources`, `academic_sources/theory_crosscheck`, `review_format` and `publish_audit`, with actual work stated in the article disclosure and centralized publisher record. Topic, writing and public posting were requested; no line-by-line human approval is claimed.

The review follows AI Tech Review Editorial Harness 2026.08 and Scientific Explanation and Visual Communication Principles 1.0 (2026-10-22). It distinguishes paper-reported outcomes, original explanatory material and proposed applications. A synthetic point-data example was trained and run in a limited classical-CPU experiment with one training seed. The three-loop example in paper Figure 1, QM9, protein generation and QPU experiments were not independently reproduced. `applications_sources` performed the limited CPU run, exact probability checks and explanatory figures; `academic_sources` audited the science; `publish_audit` independently reviewed explanation and conceptual-cover meaning, translated the complete English article, and audited publication metadata, links, assets and disclosure. `root` synthesized primary sources, wrote the Korean article, produced the original cover, edited the science and integrated publication.

The short byline uses `p.byline-disclosure`. The full record uses the standard authoring-disclosure comment markers, allowing the public-site publisher to replace it without duplication. These builders do not register archive entries, upload, commit or deploy. Final PDFs are separately reviewed and registered as Korean and English archive articles before the existing repository publication workflow is run. A video is not added by default.

## Final local verification

The Korean PDF has 9 pages and the complete English PDF has 11 pages. Every page was rendered and visually inspected. Desktop and 390px HTML checks found no document overflow or missing image; equations, four figure pairs, captions, 14 references and six production roles were checked. All PDF fonts are embedded; each PDF has 22 public web links and no embedded attachments, private paths or file URIs.

The related repository test suite ran 78 tests: 77 passed and one optional Python-Markdown test was skipped because that dependency is absent. The limited CPU experiment and exact small-case checks have their own recorded scope in `artifacts/FIGURE_PROVENANCE.md`; they are not molecular or physical-QPU replications.

The finalized PDFs are registered in the review and document-archive catalogs. Korean and English each have four byte-identical copies: package output, source archive, public review and public archive. All 44 previous review records and 74 previous archive records were preserved. Live deployment is recorded separately after verification.

An independent publication audit passed after restoring all prior review files: the public-site validator returned no errors, the new language variants have single bylines/disclosures and six recorded roles, all local links/assets resolve, and both archive manifests match the final PDF sizes and SHA256 values.
