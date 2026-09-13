# Evidence ledger — 2026-09-13

Primary source: Hong et al., *Multiphoton Quantum Reservoirs For Robust Multidimensional Computing*, Advanced Science e77225, DOI 10.1002/advs.77225, first published 2026-08-19. Main PDF p1 explicitly licenses the article under Creative Commons Attribution. Full publisher HTML, main PDF and 15-page Supporting Information (SI) reviewed. No raw data or experimental replication.

| Claim | Location | Editorial decision |
|---|---|---|
| Classical coherent/thermal sources; passive wave plates and q-plates | Main §§2,4; SI Notes 2,4 | Separate source configurations: coherent input for regression, thermal inputs for walks/statistics. |
| 861 features | Main Fig4; SI Note4,7 | 21 OAM projections × 41 number entries (0–40); not qubits or independent dimensions. |
| 91 input states, 80/20 splits, ridge readout | SI Notes4,7 | One scalar polarization scan; validation interpolation, not temporal forecasting. |
| R² pairs quadratic .92/.94; cubic .89/.93; quartic .90/.94; exponential .96/.97; logarithmic .97/.97; damped sinusoid .69/.94 | SI Table S2 (p14) | Use table over prose that groups quartic and damped sinusoid under .69→.94. Mean row .89/.95 as reported. |
| PCA first PC75%,16 PCs99%, participation ratio1.7; rank91 claimed | SI Note7C (p14) | Distinguish algebraic rank, nominal feature count, variance-based dimension. No guarantee of generalization from rank. |
| 1μs windows;1s per polarization/OAM; approximately32min whole dataset | SI Note4,7D | 91×21=1911s=31.85min raw acquisition; excludes overhead, dataset reused across targets. |
| 30μs training | SI Table S1 | Author-reported readout training only, not complete runtime; hardware/timing protocol insufficient for broad benchmark. |
| APD50ns dead time; B20 bins in1μs; distribution fidelity≈97% at mean4.1 | SI Note5,FigS2 | Model fidelity = sum sqrt(pq), not state fidelity. High-number calibration cannot be inferred from low-mean agreement. |
| Number entries0–40 vs B20 model and two-arm selections21,21 | Main Fig2/4; SI Note5 | Flag need to reconcile per-arm counts/window/multiplexing/calibration. Do not declare fabrication or silently treat all as ideal resolved events. |
| Selected N statistical costs | SI Note6 EqS72 | Derived ideal-thermal illustration only; excludes dead time/correlations. |
| Walk width ballistic vs diffusive | Main Fig2; SI Note4 | Observable scaling versus steps, not end-to-end processor speed. n7 is conditional P(OAM|n7), not seven prepared single-photon coincidence. |
| Bosonic/fermionic-like joint patterns | Main Fig2 | Conditional correlation patterns; photons remain bosons. Caption(21,21) totals42 despite abstract up-to40 phrasing. |
| Permanent/#P-hardness | Main and SI Note1 | Distinguish exact probabilities from sampling actual source family. SI Note2 EqS19,S29,S35 itself supplies positive Gaussian mixture route. |
| Classical phase-space sampler | Rahimi-Keshari et al., PRX6,021039 (2016), arXiv1511.06526v2; independent construction using SI Note2 | Draw Gaussian amplitudes, propagate linearly, sample conditional Poisson counts. Efficient for specified finite-mode positive-P inputs with efficient distributions; rare postselection still costs. Not a benchmark reproduction. |
| Data access | Main Data Availability | On reasonable request; independent raw-data validation remains outstanding. |

Discovery: publisher paper and LSU official release established the research title. LinkedIn body was not directly accessible. No claim to have inspected unavailable LinkedIn text.

Writing/model: one Codex agent in OpenAI Codex Work Mode; exact model identifier unavailable in runtime. No additional agents and no independent human line edit. Original imagegen conceptual hero, deterministic SVG plots, original explanatory equations. All application proposals explicitly editorial.
