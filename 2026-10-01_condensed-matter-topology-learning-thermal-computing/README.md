# Layered topological order and the statistical physics of AI

Bilingual AI Tech Review, published 2026-10-01. Korean is canonical; English is at `dist/en/`. The public build includes only HTML, CSS and explanatory image assets.

## Scope and source ledger

The September 2026 Journal Club for Condensed Matter Physics selection comprises three commentaries and six selected papers. The selection pages were read; the commentary PDFs returned an access restriction and were not reviewed. Technical analysis uses the six original papers below, not an inferred reconstruction of the commentaries. No experiments, paper computations or hardware measurements were independently reproduced.

| Selected paper | Technical version reviewed | Evidence boundary |
|---|---|---|
| Das et al., Three-dimensional Foliated Fractional Quantum Hall Phases | arXiv:2606.19426v1, 2026-06-17 | Finite-stack exact diagonalization, perturbative and trial-state theory; no device observation |
| Jin et al., Three-Dimensional Non-Foliated Fractional Quantum Hall Phases with Irrational Anyons in Twisted van der Waals Multilayers | arXiv:2607.13127v1, 2026-07-14 | Variational/Monte Carlo comparison and infinite-layer effective theory; not an exhaustive ground-state proof |
| Cagnetta et al., How Deep Neural Networks Learn Compositional Data: The Random Hierarchy Model | arXiv:2307.02129v5, 2024-07-03; PRX 14, 031001 (2024) | Synthetic classification model; sample complexity, not universal training-time complexity |
| Cagnetta and Wyart, Towards a theory of how the structure of language is acquired by deep neural networks | arXiv:2406.00048v3, 2024-10-29; NeurIPS 2024 | Synthetic hierarchy plus corpus comparisons; natural-language extension is not a universal theorem |
| Whitelam, Generative Thermodynamic Computing | arXiv:2506.15121v3, 2025-10-30; PRL 136, 037101 (2026) | Numerical proof of concept using classical stochastic dynamics; technical text reviewed is the preprint |
| Whitelam, Training thermodynamic computers by gradient descent | arXiv:2509.15324v1, 2025-09-18; PNAS 123, e2528413123 (2026) | Numerical learning demonstration and energy estimates; final publisher full text unavailable |

## Protected claims and quantities

- Foliated Fibonacci order and non-foliated irrational-statistics order are different constructions. Irrational quantum dimension is not the same property as an irrational exchange angle.
- The nine-layer trimer example uses the repeated occupancy pattern `[1/3, 1/3, 0]`, with mean filling 2/9 per layer. It must not be silently described as uniform filling 1/3.
- Fibonacci fusion: tau × tau = 1 + tau, with quantum dimension (1 + sqrt(5))/2.
- Irrational exchange angles refer to the infinite-layer limit. Inverting a finite nonsingular integer K matrix gives rational entries. Non-foliation does not establish unrestricted three-dimensional quasiparticle motion.
- Random hierarchy: d = s^L; sample threshold P* ~ n_c m^L = n_c d^(log_s m), at fixed rule parameters. Polynomial in input dimension, exponential in depth; not a general polynomial-time result.
- Correlation signal C(r) ~ r^(-beta) and independent-sample noise ~ P^(-1/2) motivate useful context r* ~ P^(1/(2 beta)) within the model assumptions.
- Langevin convention: dx_i = -mu partial_i V dt + sqrt(2 mu k_B T) dW_i; independent Wiener increments with variance dt. The illustration uses no measured trajectories.
- Gradient-descent paper: teacher MNIST top-1 97.3%; student single-trajectory top-1 91.7%, ten-trajectory averaged top-1 92.0%. The estimated energy ratio exceeds 10^7 under the paper's accounting assumptions, not a measured wall-plug comparison at matched accuracy.

## Build and provenance

Run `python build_review.py --hero INPUT_IMAGE.png` once to create the compressed cover derivative, then `python build_review.py` for a reproducible HTML/SVG build. Run the repository publisher with `--review 2026-10-01_condensed-matter-topology-learning-thermal-computing`.

The cover is an AI-generated conceptual illustration; the three SVGs are deterministic, author-created explanatory schematics. None is an experimental image, numerical result or copied paper figure. See `IMAGEGEN_MANIFEST.md` for cover provenance. Source fragments and the builder contain no private correspondence or intake metadata.

One Codex agent performed source research, bilingual synthesis, scientific copyediting and publication checks in OpenAI Codex Work Mode. No independent review agent or separate line-by-line human review was used. The exact authoring-model identifier was not retained. The public page carries the AI Tech Review Editorial Harness 2026.08 disclosure.
