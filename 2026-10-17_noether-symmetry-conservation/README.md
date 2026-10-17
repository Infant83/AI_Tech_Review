# Noether’s theorems in scientific computing

Bilingual AI Tech Review, prepared for public publication on 2026-10-17. Korean is canonical; English is provided alongside it. Public review: https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/ . Both PDFs are also registered in the document archive.

## Contents

- `reports/review_ko.md`, `reports/review_en.md`: complete article sources.
- `artifacts/hero.webp`: AI-generated conceptual cover, not experimental evidence.
- `artifacts/symmetry_*.svg`, `artifacts/integrator_*.svg`: deterministic explanatory figures.
- `artifacts/build_review.mjs`: self-contained bilingual HTML and static SVG equation generation.
- `artifacts/build_fonts.py`: local, openly licensed font subsets used by both HTML and PDF.
- `artifacts/build_pdf.py`: complete-article PDF output and desktop/mobile browser checks.
- `artifacts/build_figures.py`, `artifacts/oscillator_data.csv`, `artifacts/oscillator_results.json`: original numerical illustration and reproducible values.
- `figure-manifest.json`: cover prompt, built-in image-generation method, saved asset paths and figure provenance.
- `notes/source_checks.md`: local scholarly and bibliographic checking record.
- `dist/index.html`, `dist/review_ko.pdf`: Korean deliverables.
- `dist/en/index.html`, `dist/en/review_en.pdf`: English deliverables.
- `tmp/pdfs/`: local visual-QA material; excluded from deliverables.

## Rebuild

Use Node.js with `marked`, `mathjax-full` 3.2.2 and `playwright`; Chrome must be installed for PDF printing. Python fontTools and brotli are required for WOFF2 subsets. Matplotlib is used by the separate numerical-illustration builder. Dependency directories and font input paths are supplied at runtime and are not embedded as host paths in final output.

```sh
python artifacts/build_fonts.py --regular /path/to/open-font-regular.ttf --bold /path/to/open-font-bold.ttf
python artifacts/build_figures.py --font /path/to/open-font-regular.ttf
node artifacts/build_review.mjs
python artifacts/build_pdf.py --node /path/to/node --modules /path/to/node_modules
```

If dependencies are not installed next to the package, set `NOETHER_NODE_MODULES` to a directory containing `mathjax-full`, and `CODEX_PRIMARY_RUNTIME_NODE_MODULES` to the directory containing `marked` and `playwright`. For font input, use a compatible openly licensed Korean font, such as Nanum Gothic; the subset builder retains the font’s embedded copyright and licensing information in `artifacts/font-license.txt` and the deliverables.

The HTML builder uses relative language/PDF links by default. Supply `--public-base=https://.../` for canonical, hreflang, Open Graph and cross-language URLs. Openly licensed font subsets and their full license are embedded in the generated CSS so public assets do not depend on sibling font files. No upload, public-site registration, commit or deployment is performed by these builders. The registered review is published through the repository's existing GitHub Pages workflow.

## Editorial boundaries

Responsible editor: Hyun-Jung Kim / 김현중. AI assistance: OpenAI Codex. Actual roles are recorded as `root` (synthesis and writing), `academic_sources` (academic source checking), `applications_sources` (applications and primary-source research), and `review_format` (format, typesetting and output checks). The exact authoring-model identifier was not retained. The user requested the topic and writing; no line-by-line human approval is claimed. The review follows AI Tech Review Editorial Harness 2026.08.

The article distinguishes reported scientific results, explanatory reconstructions and proposed applications. The numerical illustration is a teaching example rather than a reproduction of a cited experiment. Fonts, equations and local figures are bundled so no browser-side math service or external font download is needed.

The cover was created with the built-in `image_gen` tool and saved as `artifacts/hero.webp` (1600 × 900). The complete final prompt is retained in [figure-manifest.json](figure-manifest.json): it requests a text-free conceptual scientific editorial illustration of repeated brass rings and a continuous blue ribbon, evoking symmetry under translation, rotation and time evolution. The cover is not scientific data.
