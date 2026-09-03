# Weekly OLED Inverse Design Brief - 4 September 2026

Coverage: 28 August to 3 September 2026. Prepared for a DFT/ML materials-science workflow.

## Executive assessment

No credible paper newly posted or meaningfully revised in this window directly designed or validated a TADF emitter, PhOLED host, host-dopant system, or OLED device. The strongest work is methodological. LUSH learns a smooth latent Hamiltonian for several coupled excited states; QED-GW/BSE decomposes cavity effects on quasiparticles and excitons; AdaptNTK supplies a single-model uncertainty and acquisition rule. Reaction-aware and hierarchical generators add feasibility and environment layers. The two selected quantum papers are useful mainly for evidence discipline: one is a classical simulation of D-Wave annealing, while the other uses real IBM QPU sampling but not on-QPU VQE optimization or electronic-structure VQE.

Evidence note: all eight selected records are preprints. Numerical findings are source-reported. OLED translations, the proposed SOC head, and the practical experiment are reviewer inferences. The 21 and 28 August 2026 briefs were used for duplicate control; no item was intentionally repeated.

## Ranked shortlist

1. Latent unified smooth Hamiltonians for excited state chemistry - Juergens et al., arXiv:2609.01871v1, 1 September 2026. https://arxiv.org/abs/2609.01871
2. GW and Bethe-Salpeter Theory for Molecular Polaritons, Quasiparticles, and Excitons - Willow et al., arXiv:2609.00594v1, 1 September 2026. https://arxiv.org/abs/2609.00594
3. AdaptNTK: Adaptive Uncertainty Quantification and Active Learning for Neural Network Potentials - Ananth and Yue, arXiv:2609.00488v1, 31 August 2026. https://arxiv.org/abs/2609.00488
4. Mechanistic Reaction Prediction via Discrete Flow Matching on Graph-Structured Electron Occupation - Xuan-Vu et al., arXiv:2608.27429v2, revised 28 August 2026. https://arxiv.org/abs/2608.27429
5. HiPoly: a hierarchical polymer-native AI framework for property prediction and generative design - Sun et al., arXiv:2609.02746v1, 2 September 2026. https://arxiv.org/abs/2609.02746
6. Language-Informed Flow Matching for Trend-Guided Structure-Based 3D Molecular Generation - Gao et al., arXiv:2608.31009v1, 31 August 2026. https://arxiv.org/abs/2608.31009
7. Numerical simulation of D-Wave's quantum advantage experiment with time-dependent variational Monte Carlo - Wiersema, arXiv:2609.01719v1, 1 September 2026. https://arxiv.org/abs/2609.01719
8. Logarithmic-scale variational quantum eigensolver for off-lattice protein structure prediction in continuous torsional angle space - Cumbo et al., arXiv:2609.02113v1, 2 September 2026. https://arxiv.org/abs/2609.02113

## Direct OLED, TADF, and PhOLED evidence

No item met the selection threshold. Previously covered papers in the 21 and 28 August briefs were not repeated. All eight selections below are preprints and enabling methods rather than direct OLED demonstrations.

## 1. LUSH: a structured representation for coupled excited states

Method. LUSH maps atomic numbers and Cartesian coordinates through an SE(3)-invariant message-passing network, cross-attention into fixed latents, state-pair Pairformer blocks, and a symmetric latent Hamiltonian. Diagonalization yields adiabatic energies. Latent transition operators yield dipoles and oscillator strengths; a Hellmann-Feynman relation supplies nonadiabatic couplings. Buffer states above the states of interest reduce artifacts from a truncated spectrum.

Data and results. QM9 contains 134,000 B3LYP/6-31G(2df,p) molecules. A roughly 5.95-million-parameter model approaches 1 kcal/mol in about 48 hours on one Tesla V100; the supplement reports 0.059 eV energy MAE for a roughly 7.05-million-parameter setting. QeMFi contributes 135,000 CAM-B3LYP/def2-TZVP geometries from nine molecules. The azobenzene case uses 780,745 FOMO-hh-TDA-BHLYP/def2-SVP points.

Limitations. QeMFi uses a 90/10 random split and azobenzene a 99/1 random split. Sparse twisted and cis regions are less accurate. There is no OLED triplet, SOC, RISC, or host-environment validation. Code is promised after peer-reviewed acceptance.

Workflow translation. Compare a scalar multitask GNN against a four- to six-state latent Hamiltonian on scaffold- and torsion-held-out OLED families. Add triplet and SOC operators only as clearly labeled new research components. Measure state-order swaps and isomer-ranking errors, not random-split MAE alone.

## 2. QED-GW/BSE: cavity corrections with a demanding coupling regime

Method. A dipole-gauge Pauli-Fierz Hamiltonian and coherent-state QED-HF reference lead to QED-GW IP/EA and a static BSE. Cavity effects enter through a static dipole-self-energy shift, a DSE correction to screening, and a polaritonic pole.

Results. In comparable cases, QED-CCSD cavity-induced shifts agree with near-exact QED-DMRG within 1 meV. GW overestimates some IP redshifts for closed-shell or unbound-anion systems. EA shifts are nearly quantitative, without guaranteeing accurate absolute EAs. Only ammonia among the tested molecules shows an appreciable lowest-excitation effect.

Limitations. The central lambda of 0.05 a.u. corresponds to about 0.74 nm3, roughly a 0.9-nm cube. This is a picocavity or plasmonic-nanogap regime. At 110 nm, the estimated single-molecule coupling is about 1e-4; roughly 200,000 molecules would be needed for collective lambda 0.05. Ensemble disorder and cavity loss are not validated.

Workflow translation. Track IP, EA, optical gap, and exciton binding as separate correction channels. Do not use this benchmark as evidence that a conventional OLED cavity produces the reported single-molecule shifts.

## 3. AdaptNTK: uncertainty without an ensemble at selection time

Method. A regularized Mahalanobis distance in empirical NTK feature space defines uncertainty. Sherman-Morrison updates enable sequential batch selection without retraining after each chosen point, reducing redundancy.

Results. On held-out rMD17, Spearman is 0.683 plus or minus 0.018 and Pearson is 0.706 plus or minus 0.021. AURCn is 0.312 plus or minus 0.014 versus 0.310 plus or minus 0.013 for a three-model ensemble; ENCE is 0.0125 plus or minus 0.0018. The Transition-1X cycle is 2.6 times faster than the ensemble under matched MACE settings.

Limitations. This is ground-state force uncertainty, not excited-state, SOC, or rate uncertainty.

Workflow translation. Compare AdaptNTK and ensemble acquisition on an excited-state model. Calibrate each target separately and track selected-batch diversity across torsions, crossings, and scaffolds.

## 4. MAELLE: reaction prediction through electron-occupation flows

Method. Integer electron occupations on bonds, nonbonding sites, and hydrogen sites evolve through CTMC discrete flow matching. An edit mixture path with optimal transport produces mechanism-like changes without step labels.

Results. USPTO-480K top-1, top-3, top-5, and top-10 accuracies are 87.2, 93.0, 93.9, and 94.6 percent. Top-1 remains below Graph2SMILES at 90.3 percent and NERF at 90.7 percent. Across 37,583 bond-forming steps, 64 trajectories cover 63.0 percent; persistent and transient edit coverage are 99.6 and 29.6 percent. Directional agreement reaches 78.2 percent overall and 89.0 percent for correct top-1 predictions.

Limitations. Mechanism-like paths without elementary labels are not proof of mechanism. An LLM plausibility score around 81.1 plus or minus 0.1 percent is subjective. Product prediction is not route success.

Workflow translation. Use the score as a veto or reranker, then validate on OLED reaction families and track reagent availability, protecting-group complexity, and purification burden.

## 5. HiPoly: hierarchy across composition, structure, and MD validation

Method and data. G2RINS contains monomer, motif, and atom levels, stochastic connectivity, mole fraction, and molecular weight. About 6,000 unlabeled and 600 MD-labeled polymers support a shared predictive and generative latent space.

Results. Fivefold-CV R2 is 0.803 plus or minus 0.147 for Tg and 0.945 plus or minus 0.024 for density. Removing composition aggregation reduces Tg R2 to 0.291. The authors generate 25,000 PFAS-free candidates and reassess top candidates with OPLS MD.

Limitations. The validation remains simulation-level. NVT at 600 K, a 50-ns NPT ramp to 300 K, and 20-ns NVT at 300 K do not validate an OLED glass or an experimental synthetic route.

Workflow translation. Test a molecule-conformer-dimer-mixture hierarchy for host-dopant packing; do not transfer polymer accuracy metrics directly.

## 6. LiFT: a language prior for 3D flow matching

Method. An LLM agent generates target-aware SMILES conditions. A frozen chemical foundation model embeds the condition, and a lightweight projector plus adaptive normalization and routing modulates the 3D ODE flow.

Results. On CrossDocked2020, no-reference configurations report QED up to 0.757, SA score 2.659, RDKit/REOS pass rates above 71 percent, and PoseBusters up to 73.56 percent.

Limitations. These are protein-pocket ligand metrics. SA scores and filters do not prove synthesis, and language conditioning is not a numerical property oracle.

Workflow translation. Replace pocket geometry with aggregate or host-dopant context. Compare language conditioning with property tokens and latent control on a scaffold-held-out DFT blind set.

## 7. Classical t-VMC simulation of a D-Wave advantage experiment

Execution boundary. This is a classical GPU simulation, not a new QPU chemistry experiment.

Method and results. Correlator-state time-dependent VMC simulates frustrated transverse-field Ising anneals on 2D-cylinder, 3D-dimer, diamond, and biclique geometries at 7 and 20 ns. An N=72 biclique final two-spin correlation differs from the QPU result by about 7.6 percent. An N=128 diamond has a TDVP residual of 4.27e-3 but no exact ground truth. One N=72 estimate uses 4,194,304 samples and hundreds of GPU-hours, versus seconds of QPU execution.

Limitations. Larger systems require more samples and sweeps; the author makes no strong scalability claim. The paper neither formulates a molecular QUBO nor selects OLED candidates.

Workflow translation. Any chemistry annealing test should report instance-matched objective or correlation error, samples, GPU-hours, preprocessing, embedding, and QPU time against exact, simulated-annealing, and tensor or Monte Carlo baselines.

## 8. Logarithmic torsion VQE with actual IBM QPU sampling

Method. Torsions are phase encoded with O(log2 N) qubits and optimized with EfficientSU2 and multi-stage relaxation. Hardware reconstruction uses the empirical CDF of measurement probabilities instead of direct phase access.

Results. Statevector optimization yields retained-snapshot and final C-alpha RMSDs of 0.623 and 1.199 angstrom for chignolin, and 2.501 and 3.512 angstrom for Trp-cage. Hardware sampling uses 300 jobs each on ibm_cleveland and ibm_miami, with 8192 shots per job and the same six-logical-qubit circuit. Best RMSDs are 1.758 and 1.782 angstrom. Native-like results below 2 angstrom occur in 88 of 300 and 45 of 300 jobs.

Execution boundary. The QPU uses parameters optimized in simulation. There is no iterative on-QPU VQE. The problem is protein conformation, not molecular electronic structure. Logarithmic qubit count shifts cost into depth, shots, and classical reconstruction.

Workflow translation. A donor-acceptor torsion benchmark is possible, but it must beat classical conformer search in energy ranking and end-to-end time. It must not be described as electronic-structure VQE.

## Read first

Read LUSH first. It directly challenges the scalar-label assumption that dominates excited-state surrogate models and supplies a concrete architecture for smooth state crossings and unified transition operators. Its limitations also define the OLED research task clearly: add spin multiplicity and SOC, then test held-out chemical and conformational transfer.

## Practical experiment for the coming week

Build a 12-24-molecule OLED isomer set with multiple torsional geometries. Compare a scalar multitask GNN with a four- to six-state latent Hamiltonian and transition-operator head, retaining two buffer states. Use leave-one-scaffold-out and torsion-held-out tests. In one active-learning round, compare 20-40 geometries selected by AdaptNTK and a three-model ensemble. Record state-order swaps, isomer ranking, oscillator-strength error, uncertainty calibration, batch diversity, and TDDFT wall time.

**Coverage gaps.** No credible new item appeared for direct TADF or PhOLED design, host-dopant or exciplex validation, OLED degradation or lifetime, SELFIES-specific synthesis constraints, CRBM or Boltzmann sampling, chemistry-relevant D-Wave/QUBO or QAOA, OLED electronic-structure VQE, or quantum advantage. These are seven-day-window gaps, not claims that the broader fields are inactive.
