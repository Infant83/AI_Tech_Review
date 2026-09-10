# Quantum vacuum, AI proofs and memory

Bilingual subject review for AI Tech Review, published 11 September 2026 (KST).
Evidence cutoff: 10 September 2026.

## Contents

- `reports/review.ko.md` and `reports/review.en.md`: authored source.
- `references.json`: public sources and actual reading scope.
- `figure-manifest.json`: original image prompts and provenance.
- `data/`: numbers behind the AUC and educational concentration figures.
- `scripts/build_figures.py`: six deterministic SVG figures.
- `scripts/build_review.mjs`: HTML build with Node.js and marked.
- `dist/`: bilingual source pages and illustration assets.

## Rebuild

Run `python scripts/build_figures.py`, then `node scripts/build_review.mjs` from this topic directory.
The HTML builder requires the `marked` package. It also supports the managed runtime module-root environment variable when present.
From the repository root, publish with:

```sh
python scripts/publish_public_site.py --review 2026-09-11_quantum-ai-brain-frontiers
```

The publisher exposes only the allowed HTML/image assets. Sources and CSV tables remain repository resources, not public-site attachments.

## Evidence and reproducibility

The five raster images are conceptual editorial illustrations generated with OpenAI image_gen.imagegen.
They are not apparatus specifications, observed events, anatomy instructions or scientific simulations.

The AUC chart reproduces Table I in arXiv:2502.17301v2. Its quantum circuits were classically simulated.
The concentration figure is the educational scaling U~epsilon^-1, V~epsilon^3, E~epsilon.
The interactive polarization relation assumes 45-degree incidence on the eigenaxes and an ideal crossed analyzer.

Magazine full text and the primary experiment behind the new facial-stimulation story were unavailable.
The review clearly identifies the earlier studies it can substantiate.
No private correspondence metadata or tracking links are included.

The full Lean proof, experimental results, execution costs and collider benchmarks were not independently reproduced.
One Codex agent performed research, writing, scientific copyediting, figures and publication checks; no independent second-agent or human line-by-line review is claimed.

