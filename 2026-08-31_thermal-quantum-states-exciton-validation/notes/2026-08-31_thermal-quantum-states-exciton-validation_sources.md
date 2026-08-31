# Source ledger · 2026-08-31

Evidence cutoff: 2026-08-31. All five core items are peer-reviewed APS journal articles published on 2026-08-28.

| Item | Primary source | Evidence location | Quantitative anchors | Boundary |
|---|---|---|---|---|
| Quantum thermal-state preparation | [PRX 16, 031053](https://doi.org/10.1103/cbrd-ssnm); [arXiv:2506.21318](https://arxiv.org/abs/2506.21318) | Classical numerical simulation | 2D Ising up to 16 spins; free fermions to hundreds of sites; weak-coupling error (O(\theta^2)) | No QPU, reset overhead, mixing-time or end-to-end timing experiment |
| α-sexithiophene exciton | [PRX 16, 031054](https://doi.org/10.1103/3zmg-276c) | Femtosecond trPOT experiment plus model reconstruction | Delocalization across about three molecular units; radius contracts about 25% within 400 fs | Momentum space measured directly; real-space amplitude and phase reconstructed by a model; self-trapping is supported, not uniquely proved |
| 2D XY spin diffusion | [PRB 114, 094303](https://doi.org/10.1103/whhg-tfv4); [arXiv:2605.20124](https://arxiv.org/abs/2605.20124) | Optical-lattice hard-core-boson analog quantum simulator plus classical Dyn-HTE | Experiment (D=0.82(3)J); independently inferred (J/T=0.47^{+0.07}_{-0.09}); infinite-temperature theory about (0.72J) | No gate-model QPU or classical-speedup comparison |
| Fluxonium–transmon architecture | [PR Research 8, 033245](https://doi.org/10.1103/ts1j-nfg1); [arXiv:2508.09267](https://arxiv.org/abs/2508.09267) | Closed-system Hamiltonian simulation | At 30 ns, two-tone CZ reduces simulated infidelity by as much as four orders relative to single-tone; 50 ns spectator example (3.8\times10^{-5}) | No fabricated chip, measured fidelity, array yield or logical-error experiment |
| Geometric diabatic–adiabatic control | [PR Research 8, L032034](https://doi.org/10.1103/hfv7-3pxt); [arXiv:2602.14756](https://arxiv.org/abs/2602.14756) | Theory and numerical examples | Single-parameter design reduces to a first-order ODE; double-dot initialization above 99% and shuttling about 99% in simulation | No pulse-generator or spin-qubit hardware experiment |

## Editorial boundaries

- The exciton headline must not imply direct real-space microscopy: trPOT measures momentum-space photoelectrons and reconstructs real space through a model.
- Only the 2D XY item uses a physical analog quantum simulator.
- Gibbs preparation, the hybrid architecture, and geometric pulse control remain theory/numerics.
- Classiq, AshN, and geometric control are examples at different optimization layers, not the only methods and not direct substitutes.
