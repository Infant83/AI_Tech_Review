# Source ledger · 2026-08-31

Evidence cutoff: 2026-08-31. All five core items are peer-reviewed APS journal articles published on 2026-08-28. The Fourier-LCU item added as optimization context is an arXiv v1 preprint with a physical-QPU experiment using 106 qubits; it is not one of the five core APS items.

| Item | Primary source | Evidence location | Quantitative anchors | Boundary |
|---|---|---|---|---|
| Quantum thermal-state preparation | [PRX 16, 031053](https://doi.org/10.1103/cbrd-ssnm); [arXiv:2506.21318](https://arxiv.org/abs/2506.21318) | Classical numerical simulation | 2D Ising up to 16 spins; free fermions to hundreds of sites; weak-coupling error (O(\theta^2)) | No QPU, reset overhead, mixing-time or end-to-end timing experiment |
| α-sexithiophene exciton | [PRX 16, 031054](https://doi.org/10.1103/3zmg-276c) | Femtosecond trPOT experiment plus model reconstruction | Delocalization across about three molecular units; radius contracts about 25% within 400 fs | Momentum space measured directly; real-space amplitude and phase reconstructed by a model; self-trapping is supported, not uniquely proved |
| 2D XY spin diffusion | [PRB 114, 094303](https://doi.org/10.1103/whhg-tfv4); [arXiv:2605.20124](https://arxiv.org/abs/2605.20124) | Optical-lattice hard-core-boson analog quantum simulator plus classical Dyn-HTE | Experiment (D=0.82(3)J); independently inferred (J/T=0.47^{+0.07}_{-0.09}); infinite-temperature theory about (0.72J) | No gate-model QPU or classical-speedup comparison |
| Fluxonium–transmon architecture | [PR Research 8, 033245](https://doi.org/10.1103/ts1j-nfg1); [arXiv:2508.09267](https://arxiv.org/abs/2508.09267) | Closed-system Hamiltonian simulation | At 30 ns, two-tone CZ reduces simulated infidelity by as much as four orders relative to single-tone; 50 ns spectator example (3.8\times10^{-5}) | No fabricated chip, measured fidelity, array yield or logical-error experiment |
| Geometric diabatic–adiabatic control | [PR Research 8, L032034](https://doi.org/10.1103/hfv7-3pxt); [arXiv:2602.14756](https://arxiv.org/abs/2602.14756) | Theory and numerical examples | Single-parameter design reduces to a first-order ODE; double-dot initialization above 99% and shuttling about 99% in simulation | No pulse-generator or spin-qubit hardware experiment |

## Added optimization context · Fourier-LCU

Discovery source: [LinkedIn post by Jay Gambetta](https://www.linkedin.com/posts/jay-gambetta-a274753a_quantum-optimization-is-ultimately-about-activity-7490780037571411969-F5za), posted 2026-08-05 14:45 UTC. The displayed page title on LinkedIn is automatically generated and is not treated as a headline authored by Gambetta.

Primary source: A. Carrera Vazquez, D. J. Egger, and S. Woerner, [*Efficient Fourier-Based Linear Combination of Unitaries and Applications in Quantum Optimization*](https://arxiv.org/abs/2605.18985), arXiv:2605.18985v1, submitted 2026-05-18. Publication status: preprint, not peer reviewed as of the evidence cutoff.

| Evidence item | Primary-source location | Preserved result or boundary |
|---|---|---|
| Cardinality penalty | Sec. III, Eqs. 20–23 | Standard coherent quadratic penalty uses \(O(n^2)\) pairwise \(R_{ZZ}\) gates; the Fourier expansion is an exact identity with \(n+1\) terms whose penalty layers are parallel single-qubit \(R_Z\) gates |
| Ancilla-free sampling promise | Sec. II.2, Eqs. 12–14 | Unlike the exact ancilla-and-control channel-QPD construction, this sampler does not reproduce the full target distribution; \(\widetilde p_x\ge p_x/\Gamma\), with up to roughly \(\Gamma\) more samples; repeated decompositions can multiply the overhead |
| Simulation | Secs. VI.1–VI.2 | 12-qubit statevector studies; the penalty-LCU uses all exact branches, while the continuous XY-LCU integral is Monte Carlo discretized; optimized single-basis circuits are heuristic ansätze |
| Physical QPU experiment | Sec. VI.3 and Table 3 | Densest-\(k\)-subgraph with \(n=106\), \(k=35\), \(p=1\) on 106 physical qubits of `ibm_boston`; 886 CZ, 2Q depth 25; 32,768 shots per circuit; ten repetitions; 107 Fourier branches; \(\Gamma=104.1328\) |
| Solution quality | Sec. VI.3 and Tables 3–4 | CPLEX optimum 98; hardware best/mean values: full Fourier-LCU 60/57.4, single penalty branch 80/72.3, single XY branch 81/76.8 |
| Feasible-sample probability | Sec. VI.3 and Table 3 | Initial-state value 8.22%; hardware mean values 2.72%, 4.87%, and 4.68% for the three experiments |
| Inferred shot totals | Derived from 107 branches × 32,768 shots × ten repetitions | Experiment 1 used approximately 3.51 million shots per full Fourier sweep and 35.1 million across ten repetitions; excludes optimization executions in Experiments 2–3 and is explicitly labeled as reviewer inference |
| Non-claim | Whole paper | No quantum advantage, no strong-classical time-to-solution comparison, no full coherent XY-QAOA hardware control, and no end-to-end wall-clock advantage |

## Editorial boundaries

- The exciton headline must not imply direct real-space microscopy: trPOT measures momentum-space photoelectrons and reconstructs real space through a model.
- Only the 2D XY item uses a physical analog quantum simulator.
- Gibbs preparation, the hybrid architecture, and geometric pulse control remain theory/numerics.
- Classiq, AshN, and geometric control are examples at different optimization layers, not the only methods and not direct substitutes.
- Fourier-LCU belongs near the problem-representation and algorithmic-decomposition layers. In this experiment it replaces the all-to-all part of the cardinality penalty with circuit branches, shots, and classical aggregation; the objective-and-SWAP portion of every branch still uses 886 CZ gates.
