# Evidence ledger — 2026-09-04 quantum review

Evidence cutoff: 2026-09-04. Primary sources were checked for publication status, execution setting, numerical denominator, classical workload, comparison baseline, and non-claims.

## 1. D-Wave spin-glass simulation with t-VMC

- Source: Roeland Wiersema, “Numerical simulation of D-Wave’s quantum advantage experiment with time-dependent variational Monte Carlo,” arXiv:2609.01719v1, submitted 2026-09-01. Preprint. <https://arxiv.org/abs/2609.01719>
- Execution: fully classical NetKet/JAX t-VMC; the D-Wave QPU result is comparison data, not a new QPU run.
- Denominator: the approximately 7.6% value is relative L2 error of the final two-spin correlation matrix against the QPU correlation matrix for the 72-spin precision-256 biclique. It is not error to a converged ground truth.
- Cost: reported aggregate 2,123.02 wall-clock hours across experiments; each run used 4 A100 or 8 H200 GPUs. The most expensive single run took about 109.25 hours on 8 H200s.
- Supported: expands the classical simulation frontier for selected topologies, anneal times, and correlation observables.
- Not supported: a general refutation of D-Wave quantum advantage, solution of the hardest bimodal J=±1 instances, or classical wall-clock advantage.
- Code: <https://github.com/therooler/dwave_vmc>

## 2. Self-consistent Pauli noise and gauge-optimized PEC

- Source: Edward H. Chen et al., “Disambiguating Pauli Noise in Quantum Computers,” PRX Quantum 7, 033045, published 2026-09-03. Peer reviewed. <https://journals.aps.org/prxquantum/abstract/10.1103/69wc-gzl6>
- Execution layers: 2Q calibration on `ibm_auckland`; up to 21Q GHZ and 92Q ring characterization on `ibm_strasbourg`; actual end-to-end PEC on a 20Q non-Clifford circuit on `ibm_fez`.
- 92Q boundary: the 92-qubit result is proxy mitigation on classically tractable Clifford circuits, not 92Q end-to-end PEC.
- Selected numbers: 92 local Z observables had median proxy-mitigation error 4.9% to 3.1%. In 20Q PEC, median absolute error was 21.8% unmitigated, 5.6% with an inconsistent model, and 2.4% with the gauge-optimized consistent model.
- Sampling norm: gamma was 48.68 in the default consistent gauge and 3.7 after optimization. Since predicted sampling overhead scales as gamma squared, this is a roughly 173-fold reduction in predicted overhead, not a measured 173-fold speedup.
- Boundary: this is error mitigation and model identifiability, not quantum error correction, logical qubits, fault tolerance, or algorithmic acceleration.

## 3. QuanONet

- Source: Ruocheng Wang et al., “Quantum neural operators with implicit quadratic frame and expressivity advantages,” Nature Machine Intelligence, published 2026-09-03. Peer reviewed. <https://www.nature.com/articles/s42256-026-01289-7>
- Theory: for latent dimension p, the density-matrix pair-product feature span can reach O(p²), compared with O(p) for the matched DeepONet output space under the stated assumptions.
- Denominator: p is not the qubit count. In the public implementation p=2^n, so p=256 corresponds to an 8-qubit statevector simulation.
- Hardware: a pretrained 2-qubit model performed qualitative inference on `ibm_fez`; there was no QPU training.
- Boundary: O(p²) is an expressivity-space result, not a learning-time, sample-complexity, wall-clock, energy, or end-to-end quantum speedup.
- Code: <https://github.com/Wang-Ruocheng/QuanONet> and archive <https://doi.org/10.5281/zenodo.21084057>.

## 4. Quantum MeanFlow

- Source: Ashish Joshi, Eshaan Mistry, Takahiko Koyama, “Quantum MeanFlow: single-shot generative sampling on NISQ hardware,” arXiv:2609.02186v1, submitted 2026-09-02. Preprint. <https://arxiv.org/abs/2609.02186>
- Execution: PQCs trained with PennyLane statevector simulation; pretrained parameters fixed for inference on IBM Heron R2 `ibm_pittsburgh` and Heron R3 `ibm_boston`.
- “Single-shot” boundary: one time-integration step, not one physical shot. QMF uses 11 qubits, 24 layers, and 240 CNOTs. One output needs X and Z measurement bases with 4,096 shots each, or 8,192 shots.
- BoN=8: one selected output therefore consumes 65,536 shots before queue and classical costs. On `ibm_boston`, raw QMF accuracy 0.20 rose to 0.60 after generating eight candidates and selecting with a separate classical MLP classifier.
- Classical stack: 16×16 MNIST, a roughly 2.2e5-parameter MLP autoencoder for 32D latents, and a 98.2%-accuracy MLP classifier used for evaluation and BoN selection.
- Boundary: supports a reduction in sequential time-integration submissions relative to multi-step QFM under this setup; does not establish training or end-to-end quantum advantage.

## 5. Logarithmic-scale torsion VQE for proteins

- Source: Fabio Cumbo et al., “Logarithmic-scale variational quantum eigensolver for off-lattice protein structure prediction in continuous torsional angle space,” arXiv:2609.02113v1, submitted 2026-09-02. Preprint. <https://arxiv.org/abs/2609.02113>
- Representation: 44 torsional degrees of freedom for chignolin map to 6 qubits; 88 for Trp-cage map to 7 qubits. Hardware ran only the 6-qubit chignolin circuit.
- Hardware: 300 jobs each on `ibm_cleveland` and `ibm_miami`, 8,192 shots per job; total 600 jobs and 4,915,200 shots.
- Execution boundary: QPU runs transferred parameters selected in statevector simulation and used a probability-CDF decoder different from the simulator phase decoder. There was no on-QPU iterative VQE optimization.
- Result boundary: best RMSD was 1.758 Å on Cleveland and 1.782 Å on Miami. These are best-of-repeats retrospective values against the known native structure; most repeats degraded the warm-start structure.
- Classical stack: NERF coordinate reconstruction, custom/Rosetta/OpenMM scoring, COBYLA/SLSQP relaxation, and molecular minimization.
- Boundary: trades qubit width for circuit, sampling, decoding, and classical evaluation cost; does not establish protein-prediction advantage or electronic-structure VQE.
- Code/data: <https://github.com/cumbof/qtf> and <https://doi.org/10.5281/zenodo.22088098>.

## 6. Programmable anharmonic potentials in an oscillator-transmon device

- Source: Clara Yun Fontaine et al., “Programming anharmonic potentials in a superconducting harmonic oscillator,” arXiv:2609.02405v1, submitted 2026-09-02. Preprint. <https://arxiv.org/abs/2609.02405>
- Hardware: one superconducting harmonic oscillator dispersively coupled to one transmon ancilla. Bosonic QSP compiled a potential phase gate into M=11–14 ECD gates plus transmon rotations.
- Demonstrated: cubic phase, symmetric/asymmetric/broken double wells, and a band-limited approximate Morse phase gate on the same calibrated device by changing control parameters.
- Cubic result: fitted coefficient 0.682±0.102 for target 0.6; reconstructed state fidelity at least 0.84 and Wigner negativity at least 0.11.
- Measurement outcomes: 4.4e6 for cubic, symmetric and broken double wells; 5.3e7 for the asymmetric double well; 6.7e7 for Morse.
- Morse boundary: actual coherent probes reliably reconstructed only low harmonics. Recovery of the steep repulsive wall with 10.9 dB squeezed probes was simulated; full M=13 reconstruction was estimated to need 16.3 dB and 29 probe positions.
- Compilation boundary: an omitted pi factor discovered after acquisition led to as-run target phase errors of 1.4%–10.8%, so experimental comparison uses the exact as-run compiled circuit.
- Boundary: demonstrates programmable non-Gaussian potential steps, not kinetic-plus-potential molecular dynamics, spectra, reaction rates, or a classical speed comparison.

## Cross-study editorial rules

1. Name the observable and denominator before using an accuracy percentage.
2. Separate simulation, QPU training, QPU inference, proxy mitigation, and component-level device experiments.
3. Count measurement bases, shots, repeated candidates, postselection, and mitigation norm.
4. Count classical encoding, training, optimization, decoding, and selection.
5. Compare matched wall-clock, energy, memory, and success criteria before using “advantage.”
6. Distinguish theorem-level expressivity, device-level programmability, task-level quality, and end-to-end utility.
