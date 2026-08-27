# Source and claim ledger

Checked: 2026-08-27

## Primary sources

- AshN: arXiv:2608.24084 v1, submitted 2026-08-25. Actual superconducting-QPU experiments plus larger compilation-only study.
- Classiq synthesis: arXiv:2412.07372 v2, revised 2025-01-22. Classical compilation/synthesis only. Use v2 baseline caveat, not v1 scaling wording.
- Classiq control skips: arXiv:2505.18256 v1, submitted 2025-05-23. Classical circuit/transpiler benchmarks only.
- Qmod: arXiv:2502.19368 and IEEE QSW 2025 proceedings, DOI 10.1109/QSW67625.2025.00026. Language foundation; not used as evidence for the headline resource reductions.
- Depth caveat: arXiv:2505.16908 v3, revised 2025-09-16.

## Hard boundaries preserved

- Classiq 274→120 and 1,480→842 are CX-count/width trade-offs, not measured depth or QPU runtime.
- Classiq control-skip reductions are workload-dependent: over 50% for state preparation, about 8% for random brickwork in classical compiled metrics.
- AshN 45.2% and 43.7% are geometric-mean native two-qubit gate-count reductions on 1D and 2D topologies, not wall-clock reductions.
- AshN larger-scale gate/depth overhead results are compilation-only; all-to-all is a compilation reference.
- Dicke fidelity and entanglement witness are actual QPU results under the tested topology and calibration conditions.
- Neither line of work establishes quantum advantage or end-to-end application acceleration.

