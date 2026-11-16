# Weekly OLED Inverse Design Brief - 4 September 2026

Original coverage and evidence cutoff: 28 August to 3 September 2026, checked 4 September 2026. Editorial revision: 16 November 2026, Agentic Tech Review Letters (ATRL).

## When the states change order

Rotate a donor relative to an acceptor and the excited states of a molecule can mix, exchange character, and change energy order. A model that predicts each energy independently has little structure with which to follow that exchange. LUSH [1] offers a different starting point: learn one smooth Hamiltonian whose spectrum represents the coupled states. Its results make the representation itself a useful design question for OLED surrogates.

The other seven papers develop complementary parts of that question: how to separate environmental corrections, choose new labels, retain reaction constraints, and compare quantum components with their classical costs. Their reported results concern adjacent molecular and materials problems. The small OLED comparison proposed at the end brings those ideas together as a research plan; it has not been executed.

## 1. LUSH: learn the operator behind the energies

LUSH [1] maps atomic numbers and Cartesian coordinates through an SE(3)-invariant message-passing network, cross-attention into fixed latents, state-pair Pairformer blocks, and a symmetric latent Hamiltonian. Diagonalization yields adiabatic energies; learned transition-dipole operators yield dipoles, from which oscillator strengths are derived with the excitation energies. With a geometry-independent latent basis, a Hellmann-Feynman relation supplies nonadiabatic couplings. The learned Hamiltonian is smooth, while its adiabatic eigenvalues retain the crossing geometry. Buffer states above the states of interest reduce artifacts from truncating the spectrum.

On the 134,000-molecule QM9 ground-state task with B3LYP/6-31G(2df,p) labels, a roughly 5.95-million-parameter model approaches 1 kcal/mol on a randomly selected 100-molecule validation set after about 48 hours on one Tesla V100. A separate roughly 7.05-million-parameter setting in the supplement reports 0.059 eV energy MAE, about 1.36 kcal/mol. QeMFi contributes 135,000 CAM-B3LYP/def2-TZVP geometries from nine molecules. The azobenzene case uses 780,745 FOMO-hh-TDA-BHLYP/def2-SVP single points.

QeMFi uses a 90/10 random split and azobenzene a 99/1 random split; sparse twisted and cis regions are less accurate. Those tests establish interpolation behavior, leaving new scaffolds and torsion families as the next comparison. An OLED extension would also need triplet states and spin-orbit coupling (SOC) operators. The original paper does not test triplet, reverse intersystem crossing (RISC), or host-environment behavior, and states that code will follow peer-reviewed acceptance.

## 2. QED-GW/BSE: identify which correction moves the excitation

QED-GW/BSE [2] starts from a dipole-gauge Pauli-Fierz Hamiltonian and coherent-state QED-HF reference. Cavity effects enter quasiparticle ionization potentials (IP), electron affinities (EA), and a static Bethe-Salpeter equation through dipole self-energy, screening corrections, and a polaritonic pole.

Across comparable cases, QED-CCSD cavity-induced shifts agree with near-exact QED-DMRG within 1 meV. GW overestimates some IP redshifts for closed-shell molecules with unbound anions. Its EA shifts are nearly quantitative even when absolute EAs remain less accurate. After separating the quasiparticle contribution, a substantial residual BSE-kernel correction reaches the lowest exciton only in ammonia among the five molecules examined in that analysis.

The main coupling lambda=0.05 a.u. corresponds to a mode volume of about 0.74 nm3, roughly a 0.9-nm cube: a picocavity or plasmonic-nanogap scale. At a free-space wavelength of about 110 nm (11.31 eV), a diffraction-limited planar-cavity estimate gives single-molecule coupling around 1e-4. The authors estimate roughly 200,000 molecules for collective coupling 0.05. For an OLED calculation, the useful transfer is therefore a correction ledger for IP, EA, optical gap, and exciton binding under specified conditions; an amorphous ensemble would add disorder and loss to this molecular benchmark.

## 3. AdaptNTK: choose diverse geometries for the next calculation

AdaptNTK [3] defines uncertainty by a regularized Mahalanobis distance in empirical neural-tangent-kernel feature space. Sherman-Morrison updates let it revise the remaining candidates' scores after each selection without retraining the model. Similar candidates become less attractive as a batch fills, connecting uncertainty with diversity.

On held-out rMD17, Spearman correlation with error is 0.683+/-0.018 and Pearson is 0.706+/-0.021. AURCn is 0.312+/-0.014 versus 0.310+/-0.013 for a three-model ensemble; post-hoc-calibrated ENCE is 0.0125+/-0.0018. For Transition-1X on a single A100, the compared model-training/pretraining, uncertainty, and batch-selection workload takes 2423.34 versus 6225.15 seconds, about 2.6 times faster. That timing excludes new reference-label calculations.

These are ground-state force-potential tests. Applying the rule to excited states would require separate calibration for energies, oscillator strengths, gaps, and SOC. A useful OLED comparison would track both the errors in those targets and whether acquisition covers torsions, crossings, and held-out scaffolds.

## 4. MAELLE: retain the electron moves behind a reaction prediction

MAELLE [4] models integer occupations on bonding, nonbonding, and hydrogen sites with continuous-time Markov-chain discrete flow matching. An edit-based mixture path and optimal transport construct mechanism-like electron moves without elementary-step annotations. The 28 August v2 clarifies that interpolation description in the abstract; comparison with v1 shows no new numerical result.

USPTO-480K top-1, top-3, top-5, and top-10 accuracies are 87.2%, 93.0%, 93.9%, and 94.6%. Top-1 is below literature baselines Graph2SMILES (90.3%) and NERF (90.7%). In the separate FlowER evaluation, pooling 64 trajectories recovers 63.0% of 37,583 annotated bond-forming steps: 99.6% of persistent and 29.6% of transient steps. Directional agreement among recovered steps is 78.2% when all trajectories are pooled, 84.6% for correct-product trajectories, and 89.0% for trajectories reaching the highest-confidence product, irrespective of whether that product is correct.

The LLM judge accepts 81.1+/-0.1% of injected ground-truth products, a sanity check on the judge rather than a model-success rate. Reaction plausibility and exact product agreement test different properties. For OLED candidate screening, a reaction score could help flag or rerank candidates before route-specific checks on reagents, protecting groups, and purification; it does not establish an experimentally successful synthesis.

## 5. HiPoly: make composition part of the representation

HiPoly [5] uses the G2RINS representation to connect atom, motif, and monomer graphs with stochastic inter-monomer connectivity, mole fractions, and molecular weight. On MD-derived thermophysical labels, fivefold-cross-validation R2 is 0.803+/-0.147 for glass-transition temperature and 0.945+/-0.024 for density. Removing composition aggregation reduces the former to 0.291, exposing the value of representing the mixture rather than only its monomers.

In a separate PFAS-replacement design demonstration, an approximately 6,000-polymer reference space includes about 600 polymers labeled for interfacial tension by MD. The shared latent space generates 25,000 candidates; top-ranked candidates receive further OPLS/OpenMM simulation. The preparation uses NVT at 600 K, a 50-ns NPT ramp from 600 to 300 K, and 20-ns NVT relaxation at 300 K.

This validation closes a prediction-to-simulation loop. Testing synthesized materials remains a further step. For OLED host-dopant packing, the transferable idea is to connect molecule, conformer, dimer, mixture, and morphology representations, with labels appropriate to those layers.

## 6. LiFT: use language to condition a geometric generator

LiFT [6] uses an LLM agent to generate target-aware SMILES conditions, a frozen SMI-TED encoder to embed them, and a lightweight projector plus adaptive routing to condition a pocket-aware 3D flow. This gives a concrete intermediate chemical representation between a verbal preference and a geometric candidate.

On CrossDocked2020, the Balanced-No-Reference prompt reports QED 0.757 and SA score 2.659. Vina-No-Reference reports PoseBusters validity 73.56%; combined RDKit/REOS pass rates exceed 71% across the no-reference variants. The maxima thus come from different prompt settings. The paper's arXiv record states acceptance to Findings of EMNLP 2026.

These are protein-pocket ligand metrics and synthesis proxies. An OLED extension would replace the pocket context with aggregate or host-dopant geometry, then compare language conditioning with simpler property-token or latent controls on a scaffold-held-out DFT set.

## 7. Classical t-VMC: put accuracy beside the simulation cost

Wiersema [7] simulates D-Wave's frustrated transverse-field Ising anneals with classical correlator-state time-dependent variational Monte Carlo. The study covers 2D-cylinder, 3D-dimer, diamond, and biclique geometries at anneal times of 7 and 20 ns. Parallel tempering, blurred sampling, and importance-weighted integration address sampling and solver failures.

For an N=72 biclique, the final two-spin correlations differ from the QPU result by about 7.6%; the final correlation-error estimate uses 4,194,304 samples. An N=128 diamond example has integrated TDVP projection error R2=4.27e-3 without an exact ground-truth comparison. This integrated diagnostic is distinct from an observable error or an instantaneous residual. The paper reports simulations costing hundreds of GPU-hours against QPU execution in seconds; larger instances remain prohibitively costly for the present implementation.

The contribution is a stronger classical baseline for selected observables. A chemistry-annealing comparison would still need the same molecular instances, objective accuracy, preprocessing, embedding, sampling budget, and total runtime on both sides.

## 8. Torsion-space VQE: follow the decoder and the saved parameters

Cumbo and colleagues [8] encode torsional variables in a circuit using O(log2 N) qubits, EfficientSU2, and multi-stage classical optimization. Statevector calculations decode relative phases; hardware uses an empirical probability-CDF decoder followed by classical coordinate reconstruction.

Retained-snapshot and final C-alpha RMSDs are respectively 0.623 and 1.199 angstrom for chignolin, and 2.501 and 3.512 angstrom for Trp-cage. The hardware test selects 30 simulation-optimized chignolin circuits and repeats each ten times per device: 300 jobs each on 156-physical-qubit Heron R2 ibm_cleveland and 120-physical-qubit Nighthawk R1 ibm_miami, with 8192 shots per job. Both compile the same six-qubit circuit. Miami circuits contain exactly 60 CZ gates but have poorer structural distributions and nearly seven times the reported job runtime. Best RMSDs are 1.758 and 1.782 angstrom, with 88/300 and 45/300 structures below 2 angstrom.

Each QPU job samples fixed parameters rather than continuing VQE optimization. Because simulation and hardware use different decoders, and no matched noiseless CDF baseline is provided, their differences do not isolate hardware noise. This is protein-conformation sampling with classical energy evaluation. A donor-acceptor torsion benchmark could test the compact representation against classical conformer search, including decoder, sampling, reconstruction, energy-ranking, and total-time costs.

## A small OLED comparison worth running

Start with 12-24 molecules or isomer families and several torsional geometries per molecule. Under a common TDA/TDDFT protocol, calculate S1, T1, T2/T3, oscillator strengths, and natural-transition-orbital charge-transfer/local-excitation descriptors. Add S1-Tn SOC for a smaller calibration tier.

Compare a scalar multitask GNN with a symmetric latent Hamiltonian and transition-operator head, using two to four target states plus two buffer states (four to six states in total). Treat an SOC head as a separate proposed component, with spin symmetry and phase conventions explicitly defined. Evaluate both leave-one-scaffold-out and torsion-held-out transfer.

At each active-learning round, compare 20-40 geometries chosen by AdaptNTK with those from a three-model ensemble. Record state-order swaps, isomer ranking, oscillator-strength error, uncertainty calibration, batch diversity, and TDDFT wall time alongside energy/gap error. The structured model earns a larger trial if it reduces severe ranking mistakes and retains that gain on new chemistry. This experiment turns the week's central insight into a test: whether learning the relationships between states improves the decisions made from their predicted energies.

## References

1. D. Juergens, M. Stöhr, A. E. Hillers-Bendtsen, O. J. Fajen, and T. J. Martínez, Latent unified smooth Hamiltonians for excited state chemistry, [arXiv:2609.01871v1](https://arxiv.org/abs/2609.01871v1) (1 September 2026).
2. S. Y. Willow, G. B. Sim, T. H. Park, T. I. Kim, D. C. Yang, M. Matoušek, J. Brabec, L. Veis, and C. W. Myung, GW and Bethe-Salpeter theory for molecular polaritons, quasiparticles, and excitons, [arXiv:2609.00594v1](https://arxiv.org/abs/2609.00594v1) (1 September 2026).
3. P. Ananth and S. Yue, AdaptNTK: Adaptive uncertainty quantification and active learning for neural network potentials, [arXiv:2609.00488v1](https://arxiv.org/abs/2609.00488v1) (31 August 2026).
4. X.-V. Nguyen, O. Susanu, D. Armstrong, and P. Schwaller, Mechanistic reaction prediction via discrete flow matching on graph-structured electron occupation, [arXiv:2608.27429v2](https://arxiv.org/abs/2608.27429v2) (28 August 2026).
5. G. Sun, G. Zaldivar, Y. Tian, G. Perez Lemus, J. Park, D. Safarian, M. Han, and J. J. de Pablo, HiPoly: A hierarchical polymer-native AI framework for property prediction and generative design, [arXiv:2609.02746v1](https://arxiv.org/abs/2609.02746v1) (2 September 2026).
6. T. Gao, Z. Su, J. Li, W. Gao, Z. Ying, Z. Zhao, F. Zhang, and Y. Wei, Language-informed flow matching for trend-guided structure-based 3D molecular generation, [arXiv:2608.31009v1](https://arxiv.org/abs/2608.31009v1) (31 August 2026).
7. R. Wiersema, Numerical simulation of D-Wave’s quantum advantage experiment with time-dependent variational Monte Carlo, [arXiv:2609.01719v1](https://arxiv.org/abs/2609.01719v1) (1 September 2026).
8. F. Cumbo, B. Raubenolt, V. Puram, N. Katzenmeyer, J. Joshi, and D. Blankenberg, Logarithmic-scale variational quantum eigensolver for off-lattice protein structure prediction in continuous torsional angle space, [arXiv:2609.02113v1](https://arxiv.org/abs/2609.02113v1) (2 September 2026).

## Publication and revision record

Author: Hyun-Jung Kim. Original AI assistance: OpenAI Codex Work Mode, 4 September 2026; the exact model identifier was not retained. The original eight records are preprints at the checked editions, with the LiFT acceptance note attributed above. Source-reported results and the proposed OLED comparison are distinguished throughout.

ATRL editorial revision, 16 November 2026: OpenAI Codex-assisted prose revision and independent source comparison corrected author counts and initials, the cavity-kernel interpretation, timing and sample scopes, and trajectory/decoder metric definitions. The original title, issue date, evidence window, and scientific figures in the accompanying web review are preserved. No new molecular calculation, synthesis, device experiment, or human reader evaluation was performed for this revision.
