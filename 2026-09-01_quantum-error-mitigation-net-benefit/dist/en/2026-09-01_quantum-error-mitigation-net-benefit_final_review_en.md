---
title: "When Does Error Mitigation Pay Off?"
subtitle: "What readout repetition coding and IBM Heron studies reveal about accuracy, qubit, and shot costs"
type: final review
author: "Hyun-Jung Kim"
date created: 2026-09-01
date modified: 2026-11-13
status: checked
language: en
canonical url: "https://infant83.io/AI_Tech_Review/reviews/2026-09-01_quantum-error-mitigation-net-benefit/en/"
alternate ko url: "https://infant83.io/AI_Tech_Review/reviews/2026-09-01_quantum-error-mitigation-net-benefit/"
alternate en url: "https://infant83.io/AI_Tech_Review/reviews/2026-09-01_quantum-error-mitigation-net-benefit/en/"
alternate x-default url: "https://infant83.io/AI_Tech_Review/reviews/2026-09-01_quantum-error-mitigation-net-benefit/"
social image url: "https://infant83.io/AI_Tech_Review/reviews/2026-09-01_quantum-error-mitigation-net-benefit/quantum_error_mitigation_hero-web.webp"
writing assistance: "OpenAI Codex Work Mode multi-agent workflow; exact model identifier not retained"
agent roles: "main: evidence integration, Korean narrative, figures, PDF correction, publication; verify_mitigation: primary-source audit of readout mitigation and ZNE; verify_adjacent: primary-source audit of photonics, routing, AI-for-quantum, and cavity materials; repo_pattern: repository and pipeline audit; narrative_outline: human-readable article structure; pdf_audit: source-PDF layout and content audit; english_draft: English translation; boundary_audit: final bilingual claim-boundary review"
editorial harness: "AI Tech Review Editorial Harness v2026.08"
verification sources: "Two error-mitigation papers and four adjacent primary research papers; article text, tables, corrected PDF, bilingual figures, metadata, and local-reference validation"
human review record: "topic, writing direction, and publication request confirmed; detailed line-by-line human review not separately retained"
evidence cutoff: "2026-09-01"
tags:
  - ai-tech-review
  - quantum-error-mitigation
  - measurement-error
  - zero-noise-extrapolation
  - shot-allocation
  - IBM-Heron
  - photonic-quantum-circuits
  - AI-for-quantum
  - cavity-materials
  - OLED
---

# When Does Error Mitigation Pay Off?

Saying that a quantum computer's error has decreased may sound like enough. But if the result required eleven times as many qubits, circuits repeated at three noise levels, and several times as many measurement shots, it is not yet clear that the computation as a whole improved. The relevant test is whether the same hardware and time produced a more useful answer.

This problem will not disappear soon. On the devices considered here in September 2026, gate errors, readout errors, and decoherence alter computational results. Instead of building logical qubits that continually detect and correct physical errors, error mitigation reruns circuits or post-processes measurements to reduce errors in expectation values and samples. The implementation threshold is lower, but the price is paid in shots, circuit count, variance, or auxiliary qubits.

Two studies made public in late August 2026 expose these costs in different places. A peer-reviewed paper calculated whether measurement errors could be sharply reduced by adding up to 10 auxiliary qubits per data qubit and reading the result by majority vote. A separate preprint ran small circuits on an IBM Heron device, then used a noise model built from device calibration data to compare how a limited shot budget should be allocated across ZNE circuits.<span class="citation">[<a href="#ref-1">1</a>, <a href="#ref-2">2</a>]</span>

Encoding just before readout and extrapolating after repeated runs add costs at different stages of a calculation. I read the two studies as examples of how accuracy and resources change together. Bringing additional qubits, CNOTs, circuit repetitions and shots into the same budget is what makes a useful choice visible.

<figure class="article-hero-figure">
  <img src="quantum_error_mitigation_hero-web.webp" alt="Concept illustration balancing a cleaner quantum measurement signal against additional qubits, circuit repetitions, and measurement shots" width="1536" height="1024" loading="eager">
  <figcaption>Figure 1. AI-generated concept illustration. A balance places a cleaner measurement signal on the left and the additional qubits, circuit repetitions and measurement shots needed to obtain it on the right.</figcaption>
</figure>


## Resources added at readout and extrapolation

<div class="data-panel" tabindex="0" role="region" aria-label="Comparison of readout repetition coding and adaptive ZNE studies" markdown="1">

| Category | Readout repetition coding | IBM Heron and adaptive ZNE |
|---|---|---|
| Research status | Peer-reviewed paper in npj Unconventional Computing | arXiv v1 preprint |
| Error being addressed | Readout errors that mistake 0 for 1 or 1 for 0 at final measurement | Bias and variance when extrapolating expectation values from several noise levels |
| Method actually used | Classical numerical calculations with an independent-error analytic model and published device error rates | Ideal and noisy numerical calculations, plus small-circuit runs on ibm_marrakesh |
| Additional cost | Up to 10 auxiliary qubits per data qubit and encoding CNOTs | Circuits at several noise factors, pilot shots, and extrapolation that can increase variance |
| Representative result | Predicted readout errors of \(10^{-8}\)–\(10^{-9}\) at \(k=9,11\) for two low-error device profiles | Adaptive MSE was lower in only 2 of 6 shot budgets in the noise model; the Table 6 ratios average about 2.32, although the paper reports 2.16 |
| Conditions for interpretation | Model predictions treat final bit flips as independent; encoding-error propagation and physical-chip costs need checking | Six budgets compared in a calibration-based noise model; physical runs used small circuits at one calibration |

</div>

## 1. Why readout errors can ruin an entire sample

When estimating one expectation value, many shots are averaged, leaving room to correct statistically for some misread bits. In tasks such as random-circuit sampling or measurement-based quantum computing, by contrast, the **bit string itself is the answer**. Every bit must be correct to obtain one intact sample. If each qubit has an independent readout error rate \(e_m\), the probability that all bits in an \(n\)-bit sample are correct falls approximately as \((1-e_m)^n\).

[He-Liang Huang's paper](https://www.nature.com/articles/s44335-026-00094-0)<span class="citation">[<a href="#ref-1">1</a>]</span> adds a repetition code familiar from classical communications immediately before readout. CNOTs act on each data qubit and ancillas initialized to zero, encoding its computational-basis readout value across an odd number \(k\) of physical qubits. All are measured, and the majority value is selected as the answer. If fewer than half the readouts flip, the majority vote recovers the original value.

If the encoding gates are ideal and readout errors are independent, the dominant term in the residual error falls as \(e_m^{\lceil k/2\rceil}\). The paper maps two-qubit depolarizing errors \(e_g\) after CNOTs into an effective readout error and treats the final bit flips as independent. The resource requirement is explicit: at \(k=11\), reading one data qubit uses 11 physical qubits—10 of them auxiliary—as well as additional CNOTs.

### Device-profile predictions and errors during encoding

For the Zuchongzhi 3.0 profile, the paper calculated an effective readout error of \(4.11\times10^{-8}\) at \(k=9\) and \(1.91\times10^{-9}\) at \(k=11\). The corresponding Willow-profile values were \(3.65\times10^{-8}\) and \(1.66\times10^{-9}\). These are the authors’ effective-independent-noise model predictions using previously reported readout and two-qubit gate error rates.

The results change when the same equations are applied to other profiles. At \(k=11\), the calculated values for Zuchongzhi 2.0 and Sycamore were \(8.61\times10^{-6}\) and \(3.64\times10^{-6}\), respectively. The benefit changes with the input error rates even at the same ancilla count.

The propagation of encoding errors to the final measurements also needs checking. In this source recheck, we followed the supplementary circuit \(\mathrm{CNOT}_{1\to2}\), then \(\mathrm{CNOT}_{2\to3}\). Starting from 000, one X error on the second bit just after the first gate gives 010; the next CNOT produces 011. Majority vote returns 1 instead of the original 0. A single independent gate fault can therefore create correlated final errors. This is a small error-propagation check by the review, not a reproduction of the full noise model. Assessing the net benefit of the reported estimates requires including this propagation, routing and correlated readout errors, together with shots and runtime.

## 2. ZNE can reduce bias while increasing variance

Zero-noise extrapolation (ZNE) runs the same circuit at its original noise level \(\lambda=1\) and at deliberately amplified levels such as \(\lambda=3,5\), then extrapolates the trend in the measurements to \(\lambda\to0\). The idea is to infer the noise-free value from how the observable changes as noise increases.

The difficulty is that extrapolation adds and subtracts several noisy estimates with large coefficients. Systematic bias may decrease while sampling variance increases. If the total shot budget \(B\) is fixed, giving more shots to one point leaves fewer for another. The paper therefore compares mean squared error rather than absolute error alone:

$$
\mathrm{MSE}=\mathrm{Bias}^2+\mathrm{Variance}
$$

[Sumit Chongder's preprint](https://arxiv.org/abs/2608.28535v1)<span class="citation">[<a href="#ref-2">2</a>]</span> compared uniform allocation across \(\lambda=1,3,5\) with ASB-ZNE, which changes the allocation using variance estimates from a 100-shot pilot at each point. The paper proposes Neyman allocation proportional to the product of each extrapolation coefficient’s magnitude and that point’s standard deviation. The idea is to give more shots to statistically uncertain points that contribute strongly to the extrapolated value.

Extrapolation bias and uncertainty in the finite pilot’s variance estimate both remain in the final MSE. The noise model based on Heron calibration data reported these adaptive-to-uniform MSE ratios:

| Final allocated shot count \(B\) | 900 | 1,500 | 3,000 | 6,000 | 12,000 | 21,000 |
|---|---:|---:|---:|---:|---:|---:|
| Adaptive / uniform MSE | 5.96 | 0.998 | 1.47 | 0.988 | 2.08 | 2.43 |

The improvements in the two cases below 1 were only approximately 0.2% and 1.2%. The paper reports a mean adaptive-to-uniform MSE ratio of 2.16, but the six ratios in Table 6 have an arithmetic mean of about 2.32. The reported 2.16 instead matches the mean adaptive MSE, \(2.16\times10^{-3}\), suggesting an arithmetic or labeling error in the manuscript. Either calculation leaves the qualitative result unchanged: adaptive allocation was worse in four of the six budgets. The comparison is **between adaptive ZNE and uniform ZNE**. Reading the ratios as a direct comparison of raw and mitigated measurement would change their meaning.

The public simulation code needs to be distinguished from the proposed formula. Its allocation rule uses estimated standard-deviation ratios without multiplying by the extrapolation coefficient magnitudes. The table’s \(B\) is the final allocated shot count, distinct from the all-in cost of the separately executed pilots. The table therefore evaluates the published test rule; it does not establish the general performance of optimal Neyman allocation under matched pilot-inclusive costs.<span class="citation">[<a href="#ref-2">2</a>]</span>

### What the physical Heron runs actually established

ibm_marrakesh is a 156-qubit Heron-family processor, but the researchers selected a low-error 8-qubit chain from a calibration snapshot. The hardware circuits included 2-, 4-, and 6-qubit GHZ circuits; repeated-layer circuits with up to \(L=8\); and a 4-node, \(p=1\) QAOA circuit. The total QPU allowance was approximately 10 minutes.

The clearest hardware result concerned placement. The \(ZZ\) measurement was 0.909 on the low-error coupler \(\{33,39\}\) and 0.751 on the deliberately selected high-error coupler \(\{119,133\}\). Even within the same calibration snapshot, the choice of connection changed the observable by approximately 0.16. This device measurement shows that changing qubit and coupler placement may be cheaper than selecting a more elaborate post-processing method.

The paper's abstract and conclusion place the 2-of-6 finding within wording that says “on our device.” Section 5.5 of the main text, however, explicitly labels the comparison as a “simulation with a hardware-anchored noise model.” Reproduction and subsequent comparisons should use the latter method description. It should also remain clear that this is a single-author preprint that has not yet undergone peer review.

<figure class="figure-panel figure-panel-fit">
  <img src="mitigation_resource_ledger_en.svg" alt="Diagram comparing the resources, numerical results, and boundary between physical-QPU runs and numerical calculations in the readout repetition-coding and adaptive-ZNE studies, followed by seven reporting fields" width="1600" height="1060" loading="lazy">
  <figcaption>Figure 2. The review compares the reported results and resources from Refs. [1, 2]. The first study spends additional qubits and CNOTs; the second spends additional circuits and shots. The \(10^{-8}\)–\(10^{-9}\) values, the 2-of-6 result, and the recomputed Table 6 mean of about 2.32× all come from numerical calculations. The manuscript reports the last mean as 2.16.</figcaption>
</figure>

## 3. What belongs on an error-mitigation scorecard?

The statement “error fell by 30% after mitigation” is not enough to choose a method. If the result used three times as many circuits and ten times as many shots, it must be compared with giving the same computation time to the raw method. Experimental records for VQE, SQD, and optimization circuits should retain the following items together.

| Field to record | Why it is needed |
|---|---|
| Raw and mitigated errors | Directly compares the magnitude and direction of the change produced by mitigation |
| Variance and confidence interval across repeated runs | Distinguishes one favorable run from a stable improvement |
| Total shots | Captures the most direct cost paid to reduce statistical error |
| Additional circuit count and noise factors | Exposes the additional runs created by ZNE, PEC, and twirling |
| Compiled two-qubit depth and SWAP count | Records the error burden of the logical circuit on the physical backend |
| Postselection and discard rate | Accounts for both the accuracy of retained samples and the cost of discarded ones |
| Compile, queue, QPU, and post-processing wall-clock time | Compares the full time experienced by the researcher |

A fairer question than “Was it more accurate after mitigation?” is more specific: **Under the same total budget, did it reach the target error sooner, or produce a lower MSE in the same time?** The answer must be measured again when the problem, observable, backend, or calibration changes.

## 4. Costs and baselines in circuits, data and materials

The other studies released that day change what should be optimized together and which baseline matters. Their comparisons concern optical-component counts and success probabilities, energy routes and solver time, masked outcomes and learned measurement distributions, and interlayer structures inside a cavity.

### Success probabilities fall as photonic gates are chained together

Two-qubit gates in linear-optical quantum circuits often rely on postselection. If a completed logical circuit is translated one component at a time into gates such as CNOT, the number of optical elements and ancillas rises, while the success probabilities at each stage multiply and rapidly reduce the overall success rate.

[The APS Open Science paper by Javier Osca and Jiri Vala](https://doi.org/10.1103/xjrz-csmx)<span class="citation">[<a href="#ref-3">3</a>]</span> began with a broad optical ansatz comprising 7 layers with 3 beam splitters per layer. After optimizing the parameters, the method repeatedly pruned beam splitters and phase shifters that were no longer necessary. In the SOQCS numerical design, the approximate CNOT used 6 beam splitters, had a maximum output error of 0.6%, and succeeded with probability 5.7%. The CNOT that the authors call “numerically exact” used 7 beam splitters and had a 7.4% success probability.

Designing a two-qubit Grover circuit as a whole required 8 beam splitters and produced a 7.4% success probability. A gate-by-gate substitution would use 18 components and reduce the success probability to \((2/27)^2\). These figures explain why the entire physical circuit is optimized together.

Taking the SOQCS numerical design of beam splitters, phase shifters and ancillas to a physical chip requires reevaluating success probability with photon loss, detector efficiency and fabrication variations.

### The same energy route had different solver costs

[The Energy Internet routing preprint](https://arxiv.org/abs/2608.28401v1)<span class="citation">[<a href="#ref-4">4</a>]</span> converted energy routers and transmission losses into binary variables and constructed QUBO and Ising Hamiltonians. In the 9-node case, every method found the path 1–3–7–8–9 with a loss of 74.687 W.

The runtime difference was clearer than the agreement on the answer. Dijkstra took 0.00002524 s, Qiskit Sampler with COBYLA took 539 s, and D-Wave simulated annealing took 0.02229 s. The 30-node case required 112 binary variables; Dijkstra took 0.00005223 s and simulated annealing took 1.391 s. QAOA and the Ocean exact solver could not be run at this size.

Every calculation ran on classical hardware, using Qiskit Sampler and NumPyEigenSolver alongside Ocean exact, Tabu and simulated-annealing solvers; no gate-model QPU or quantum annealer was run. The QUBO formulation recovered the routes and losses in two small cases, but solving it took longer than Dijkstra. A grid-scale comparison would need matched network constraints and stopping conditions.

### M-Diffushadow fills gaps in quantum data with classical AI

When one quantum state is measured in different bases such as X, Y, and Z, each record captures a different part of the state. [The M-Diffushadow paper](https://doi.org/10.1103/4tft-d7gf)<span class="citation">[<a href="#ref-5">5</a>]</span> asks whether a generative model can learn the related distributions and reconstruct missing parts when some measurement outcomes are masked while the state parameter and measurement axes are supplied.

The researchers jointly trained on classical-shadow records and nearest-neighbor spin-product records from a 10-qubit periodic transverse-field Ising model. They trained at 8 values of \(g\) and evaluated at 41. When the two modalities were generated together, the mean absolute difference in \(\langle Z_iZ_{i+1}\rangle\) was below \(2.92\times10^{-3}\). With 80% of the records masked in the ferromagnetic region, the mean reconstruction accuracy for the spin products was 98.78%; the two lowest points were 90%.

A classical Transformer and discrete diffusion model were trained on numerically generated many-body measurement data. The 80% masking test hides spin outcomes while retaining the supplied parameters and axes, and it uses the ferromagnetic setting with every axis fixed to Z. Testing physical-device noise and other distributions is a further step. At the time, the official repository described its reproduction package as incomplete.

### An ab initio prediction that a cavity can alter interlayer coupling

An optical cavity retains vacuum fluctuations even when no external light is injected. If coupling between this electromagnetic field and matter changes long-range van der Waals interactions, it may also change the spacing and vibrations of layered materials. [The pMBD–QEDFT preprint](https://arxiv.org/abs/2608.28521v1)<span class="citation">[<a href="#ref-6">6</a>]</span> extends photon many-body dispersion from molecules to periodic solids.

The researchers calculated bilayer hBN and graphene in a single 2 eV cavity mode polarized out of plane. For hBN at coupling strength \(\lambda=0.1\) a.u., the interlayer distance increased by approximately 0.15 Å and the layer-breathing frequency decreased by 18%. At \(\lambda=0.2\) a.u., the hBN distance increase reached approximately 0.8 Å. In the calculations, hBN's preferred stacking changed from AB to AA′ near \(\lambda=0.14\) a.u.; graphene did not change over the same range.

The absolute stacking prediction needs care. Even without the cavity, the hBN calculation found AB to be the most stable configuration, whereas the experimentally established preference is AA′. The authors explain that the calculated energy difference between the two structures is below 0.5 meV/atom and therefore within the accuracy limits of DFT. In this calculation, the stronger conclusion concerns the different relative responses of the stackings to the cavity.

The classical ab initio predictions for hBN and graphene use a single mode, the long-wavelength approximation and \(\Gamma\)-point coupling. Comparison with a physical cavity experiment is a next step. I would also carry the question into organic optoelectronic materials: which structural and vibrational observables change when a cavity environment is included as a boundary condition in an OLED-material calculation?

## 5. A practical change in how research and PoCs are judged

The goal of an error-mitigation PoC should be to obtain a more reliable answer within a fixed device budget, not merely to show that “mitigation was applied.” Before an experiment, fix the raw baseline, target MSE, maximum shot count, and wall-clock time. Afterward, record not only the successful configuration but also the depths, observables, and calibrations for which the method did not help.

For OLED and materials VQE or SQD, energy error alone is insufficient. Variance across repetitions, the effective sample count after postselection, compiled two-qubit depth, and total time must also be stored before the result can be compared with a classical solver, a different ansatz, or another backend. A method that helped under one calibration will not automatically retain that benefit after the calibration changes.

The Energy Internet case calls for the same practical discipline. Separate the fact that a problem can be represented as a QUBO from the claim that a particular solver is faster, and first fix Dijkstra, MILP, CP-SAT, and metaheuristic baselines under the same problem and stopping conditions. For M-Diffushadow and cavity pMBD–QEDFT, the next baselines are physical-device data and experimental structures, respectively.

## Final assessment

The repetition-code paper made explicit that lowering readout error costs qubits and CNOTs. It predicted \(10^{-8}\)–\(10^{-9}\) for two low-error device profiles, but these are not yet results from physical chips. The IBM Heron preprint measured the effect of coupler selection using small physical-device circuits. In a separate numerical experiment with a device-calibrated noise model, its simple adaptive ZNE shot allocation did not consistently outperform uniform allocation.

For repetition readout, the account must include propagation of encoding faults; for ZNE, it must include the implemented allocation and pilot cost. The task is to compare which error was reduced and how many extra qubits, gates, circuits, shots and units of time were used under matched conditions. What I seek from error mitigation is **a better computation under the same total budget**.

## References

<ol class="reference-list">
<li id="ref-1"><a href="https://doi.org/10.1038/s44335-026-00094-0">H.-L. Huang, Exponential measurement error mitigation in quantum sampling, npj Unconv. Comput. 3, 47 (2026).</a></li>
<li id="ref-2"><a href="https://arxiv.org/abs/2608.28535v1">S. Chongder, Hardware-efficient error mitigation and shot-efficient sampling on IBM Quantum hardware, arXiv:2608.28535v1 (2026)</a>; <a href="https://github.com/Sumitchongder/hardware-efficient-error-mitigation-ibm-quantum/tree/472b4454917491e2294daa867d5a822a95106d2a">S. T. Chongder and K. R. Hiremath, Hardware-aware error mitigation and shot-efficient sampling on IBM Quantum hardware, version 1.0.0 (2026), commit 472b4454917491e2294daa867d5a822a95106d2a.</a></li>
<li id="ref-3"><a href="https://doi.org/10.1103/xjrz-csmx">J. Osca and J. Vala, Automated design of photonic two-qubit quantum gates and circuits via optimization and pruning, APS Open Sci. 1, 000115 (2026).</a></li>
<li id="ref-4"><a href="https://arxiv.org/abs/2608.28401v1">A. A. Tehrani, M. Boroushaki, and A. Rajabi, Energy Internet routing using quantum optimization algorithms, arXiv:2608.28401v1 (2026).</a></li>
<li id="ref-5"><a href="https://doi.org/10.1103/4tft-d7gf">Y. Li and H.-K. Tang, Multimodal discrete diffusion for quantum measurement generation in the one-dimensional transverse-field Ising model, APS Open Sci. 1, 000116 (2026).</a></li>
<li id="ref-6"><a href="https://arxiv.org/abs/2608.28521v1">M. Hassan, C. Tasci, L. A. Cunha, and J. Flick, Modifying van der Waals materials via cavity vacuum fluctuations, arXiv:2608.28521v1 (2026).</a></li>
</ol>

[Download the revised six-page Daily Quantum Brief PDF](daily_quantum_brief_2026-09-01.pdf)


## Authoring, verification and revision history

The original publication date and evidence cutoff are September 1, 2026. The original team and harness records are retained; detailed human line-by-line review was not separately preserved at publication. The source comparison uses Huang’s published article and supplement, two other published articles and three arXiv v1 preprints. Chongder’s arXiv metadata title differs from the PDF cover title; the bibliography uses the metadata title.

On November 13, 2026, AEDAUT edited repeated introductory/result explanations and broad negative caption wording, aligned APS citations and credited the software creators. It made the final-independent-bit-error assumption behind the noisy-encoding readout estimates explicit and checked a single-fault propagation path in the supplementary CNOT chain. It distinguished the ZNE proposal from the published allocation code and separate pilot cost, and corrected masked-outcome wording and the attribution of numerical cavity results to hBN. Existing numbers were not recast as new performance measurements.

root edited and integrated both languages. legacy0901_mitigation checked the two core papers, supplement, selected code and CSV files; legacy0901_adjacent independently checked the four adjacent papers and the single-fault example; legacy0901_prose reviewed bilingual prose, captions and summaries. Calculations were limited to table-ratio arithmetic and a small CNOT error-propagation check. No original noise model, experiment, QPU, training run or regression fit was rerun, and no human reader study was conducted. AI assistance: OpenAI Codex; the exact model identifier was not retained.
