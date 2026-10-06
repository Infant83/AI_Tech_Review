# Excitons, effective models and structured quantum computation

Bilingual research letter, 2026-10-06. Korean is the canonical version.

The review is written for readers with a background in physics. It distinguishes physical-model accuracy from algorithmic resource cost, and an actual annealer run from simulation and offline re-decoding of experimental data.

## Contents

- `reports/review_ko.md`, `reports/review_en.md`: complete article sources.
- `artifacts/build_assets.py`: conceptual cover derivative, original diagram, embedded font subset and equation SVG generation.
- `artifacts/build_review.mjs`: static bilingual HTML generation.
- `artifacts/build_pdf.py`: complete article PDF typesetting; font and private render-cache paths are runtime arguments, not public inputs.
- `dist/`: final HTML and referenced public assets only.

The hero is an original conceptual image, not experimental evidence. Equations and the validation diagram are deterministic teaching material. All source papers are linked; no raw paper files or private messages are included.

The figure and typesetting builders require Pillow, fontTools, matplotlib, ReportLab and Inkscape. The HTML builder uses the runtime-provided `marked` module. Fonts are supplied at build time.
