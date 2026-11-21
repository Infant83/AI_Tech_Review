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
From the repository root, prepare an independent candidate with:

```sh
python3 scripts/prepare_publication.py --review 2026-09-11_quantum-ai-brain-frontiers --output output/frontiers-candidate
```

Use a fresh output directory and follow `PUBLICATION_WORKFLOW.md` for the actual deployed baseline, candidate checks, source request and release. Candidate generation is separate from publication. The publisher exposes only the allowed HTML/image assets. Sources and CSV tables remain repository resources, not public-site attachments.

## Original evidence and reproducibility record (September 2026)

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

## Editorial revision (21 November 2026)

The original 11 September publication date and 10 September evidence cutoff remain. The bilingual manuscripts now clarify the introduction, statistical nonsignificance, highest-transverse-momentum constituents and historical status language. The original account of OpenAI data use is corrected against its explicitly dated 10 September investigative update and attributed as the company's account. Published APS bibliography, coauthors and DOI links are restored; NOAA points to its dated official archive. Original authorship/verification history is preserved and today's independent roles are recorded separately. The five used raster illustrations, six SVG figures, six equation blocks and source data are unchanged; no new cover, video or article PDF is created. The existing bilingual hub summaries remain unchanged.

Detailed source scopes and subsequent candidate/publication checks are recorded in `.automation/writing-reviews/legacy-refresh/2026-11-21-frontiers/`. This source-builder revision uses the current ATRL masthead and identifies the responsible human editor in author metadata. It does not rewrite historical PDF or third-party publication names.

