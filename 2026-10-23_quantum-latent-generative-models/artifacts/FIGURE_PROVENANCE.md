# Figure data and limited CPU experiment

`build_figures.py` creates original KO/EN SVGs in desktop and mobile layouts.
Text is outlined; the preview PNGs stay outside the publication assets.

- `sampling_pipeline`: explanatory data flow, based on the paper's QM9 setup.
  Changing the latent distribution entails retraining with the same generator
  architecture and training recipe. Arrows represent data, not computational
  speedup or a training gradient through the QPU.
- `hom_interference`: exact ideal two-photon probabilities for a lossless 50:50
  beam splitter, with one photon in each spatial input. The indistinguishable
  photons have matching wave packets and polarization and arrive simultaneously.
  This is a teaching calculation, not a hardware result or speedup benchmark.
- `qm9_results`: author-reported Table 4 values, separately preserved in
  `qm9_table4.json` and `.csv`. Error bars are standard errors over 20 training
  seeds. Counts are per 10,000 generation attempts. The hardware samples come
  from one fixed optical circuit; these are not 20 independent device runs.
  All 32 input time bins were populated, and detections with fewer than 16
  photons were discarded. The selected pool contained 500,000 samples.
- `toy_latents`: a limited CPU run described below. Its points and diagnostic
  values are review-generated and are not the published QM9 measurements.

Published sources:

- Bacarreza et al., *Quantum latent distributions in deep generative models*,
  [arXiv:2508.19857v3](https://arxiv.org/html/2508.19857v3),
  Table 4, sections IV.2.3, Appendix B.3, C and E.
- [Final ICML/PMLR paper](https://proceedings.mlr.press/v306/bacarreza26a.html).
- [Official code, pinned commit](https://github.com/orcacomputing/quantum-latent-distributions/tree/b950127d3584561fee4aea4af566bcce697d6946).

## CPU run: exact scope

The public notebook currently demonstrates a **single-loop**, lossless,
8-photon / 16-incoming-bin simulator. The paper's Figure 1 uses three loops in
the 1-3-9 configuration. This run therefore does **not** independently reproduce
that published optical circuit, physical QPU sampling, QM9 training or protein
generation. The single-loop simulator is classically efficient at this scale;
running it does not test computational hardness.

`run_toy.py` loads four inspected upstream source files at commit
`b950127d3584561fee4aea4af566bcce697d6946` (2026-06-23), checking their SHA-256
hashes before import. They are downloaded into ignored temporary storage and
are not redistributed here. Upstream uses the
[Apache-2.0 license](https://github.com/orcacomputing/quantum-latent-distributions/blob/b950127d3584561fee4aea4af566bcce697d6946/LICENSE.txt).
The public runner and small-case checks are original review code; no upstream
source is embedded in them. The public notebook informed the runner interface
and settings; its copyright and license are retained in
`upstream_APACHE_2_0.txt` as an attribution precaution.

The runner follows the public notebook: WGAN-GP, two 256-unit LeakyReLU hidden
layers in generator and critic, batch 32, learning rate 0.0005, gradient penalty
10, five critic updates per generator update, and 5,000 generator steps for each
latent. It forces CPU with one thread. Seed 20261023 fixes model initialization;
circuit, sampler, loader and evaluation seeds are separately recorded in
`toy_results.json`. All three models start from the same network initialization
and use the same training data. Photonic occupancies are shifted by -0.5 as in
the notebook; the final residual-loop occupancy is discarded from the latent.

The review adds a distinguishable-photon control for the **same single-particle
unitary**. Independent labelled photons are sampled from |U_ji|^2; the sequential
binomial implementation is exactly equivalent for this single-loop network.
`verify_toy_sampler.py` constructs the full optical unitary and compares exact
two-photon probabilities in three cases. Maximum categorical-versus-binomial
probability error is 1.12e-16, and the upstream quantum transition probabilities
agree with a two-photon permanent calculation within 2.78e-17. The full 17x17
unitarity error is 2.23e-16. Results are in `sampler_checks.json`. These are small
correctness checks, not a full proof of implementation correctness at all sizes.

## Observed review data

Each trained model generated 10,000 evaluation points. A review-defined
diagnostic counts points within Euclidean distance 0.75 of the nearest ideal
target center. It is not a metric reported in the paper. Mode coverage counts
centers with at least 100 such points (1% of generated points).

| Latent | Within radius 0.75 | Mode coverage | Training seconds |
|---|---:|---:|---:|
| Gaussian | 70.50% | 7/7 | 52.29 |
| Distinguishable photons | 80.87% | 7/7 | 55.18 |
| Indistinguishable photons, simulated | 95.20% | 7/7 | 77.28 |

This is one seed and one optical circuit, with no significance test. The
diagnostic is sensitive to its chosen radius and measures concentration near
target centers, not complete distributional fidelity. In particular, it does
not test whether each generated cluster has the correct covariance or weights.
It establishes no general superiority, QPU speedup, or molecular/protein benefit.
Training seconds are observations on this CPU run, not a performance benchmark.

`toy_points.npz` contains the target and three generated point arrays;
`toy_results.json` records parameters, seeds, versions, measured results and
elapsed training times; `.csv` provides the diagnostic summary.

## Re-running

Use Python 3.12 with these tested versions:

```text
numpy==1.26.4
torch==2.2.2
numba==0.61.2
matplotlib==3.10.8
```

From the review package directory:

```sh
python artifacts/verify_toy_sampler.py
python artifacts/run_toy.py --steps 5000 --seed 20261023 --threads 1
python artifacts/build_figures.py --font /path/to/NanumGothic-Regular.ttf
```

Bitwise agreement across different hardware/library versions is not claimed.
The SVG generation is deterministic for the same data, font and plotting stack.
