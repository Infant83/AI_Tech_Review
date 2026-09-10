# CASH-QSE evidence ledger

Evidence cutoff: 2026-09-10. Source: Artur F. Izmaylov, arXiv:2609.08170v1, first submitted 2026-09-08 02:59:48 UTC. Full text and appendices accessed through arXiv HTML. No molecular calculations rerun.

| Protected claim | Source | Boundary retained |
|---|---|---|
| Classical Hamiltonian block evaluated without quantum sampling; mutually orthogonal correction states | Sections II–V | Reference preparation may still be needed for classical–quantum transition measurements |
| First-defect occupation partition | Section II.2 | Different sectors orthogonal; additional states within a sector need refinement/orthogonal construction; physical noise may violate constraints |
| N2 1.8 Å CASH shots 1.1e6,1.6e5,850; ADAPT2.4e6; ratios2.1,15,2800; full CNOT342,333,328 | Tables6–7 | HF,CAS(4,4),CAS(6,6), STO–3G, all-to-all logical circuits; final-energy sampling only |
| N2 3 Å CASH2.3e6,8.1e5;ADAPT7.7e5;ratios.33,.94;CNOT338,328;CAS(6,6)classical stop | Tables6–7 | Failure case and classical stop preserved; counts are not depth |
| H2O .96,1.75,3 Å continuous CASH2.1e4,1.2e4,510;floor51800,32800,941;floor ratios560,630,4400 | Table8,AppendixC | Restricted14-spatial-orbital cc-pVDZ window; same one-shot floor for both; pilot excluded;3Å comparator sampling FCI proxy |
| FCI-guided selection and exact variances | SectionVII | Not scalable from-scratch state selection; no actual QPU |
| 1.6mEh wavefunction target and1.6mEh sampling uncertainty | SectionVII | Separate budgets; restricted-basis FCI accuracy does not imply experimental accuracy |
| No pilot, variance learning, optimization, noise, routing in reported shot ratio | SectionVII.4 | No total runtime or quantum advantage inference |
| CB-VQE precedent | Radin & Johnson arXiv2106.04755 | Classical reuse is not claimed as first invented by CASH-QSE |
| QSE excited-state direction | McClean etal PRA95,042308(2017), arXiv1603.05681 | OLED properties not benchmarked in CASH-QSE |
| DFT energy versus wavefunction expectation | PySCF DFT/MCSCF documents and independent analysis | DFT initial orbitals separated from replacing a Hamiltonian matrix element by a DFT total energy |

Independent educational calculations: binomial dimensions 853776 and34134779536; S=[[1,s],[s,1]] condition number199 at s=.99; two-state matrix with EC0,EqΔ,V real. Eigenvalue residual and Hellmann–Feynman finite-difference checks pass for four settings including zero coupling. These checks do not reproduce CASH-QSE.

Editorial audit: topic-first background; no two-method-only framing; sources distinguished from interpretation; reduced slogans and repetitive contrasts. Scores (1–10): directness9,rhythm8,trust9,naturalness9,density9,scientificprecision9,sourcefidelity9 =62/70. Human review: topic/publication approved; no line-by-line human validation in this task.
