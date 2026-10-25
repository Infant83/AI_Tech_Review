# Figure provenance and interpretation limits

Evidence cutoff: 2026-10-25. All geometry, layouts and labels below were newly made for this review by `review_format`; earlier review figures and manuscript text were not reused. `build_figures.py` produces the Korean/English desktop and mobile SVGs from adjacent source data. The first raster cover is produced separately and recorded in the topic's cover brief and figure manifest.

## Program transformations

Files: `program_paths_ko.svg`, `program_paths_en.svg`, `program_paths_mobile_ko.svg`, `program_paths_mobile_en.svg`.

This is a conceptual diagram, with solid arrows for program transformations and dashed arrows for agent tool calls and check feedback. Qmod expresses intent and resource constraints, synthesis selects implementations and allocates resources, and the resulting restricted high-level program retains function hierarchy and symbolic control. Target-basis and connectivity transformations can follow through configured transforms and execution stages. Plain export does not always transpile; the final Classiq card is not a claim about default export behavior. The Qiskit row includes high-level blocks, HLS and Target operation/connectivity information, circuit transformations and execution. The two approaches are interoperable and do not form closed hardware camps. No arrow or label denotes a proof of global optimality, semantic intent correctness, speedup or universal automation.

Primary documentation represented in the diagram:

- [Qmod](https://docs.classiq.io/qmod-reference), [synthesis](https://docs.classiq.io/user-guide/synthesis), and [quantum-program transpilation](https://docs.classiq.io/user-guide/synthesis/quantum-program-transpilation).
- [Qiskit HighLevelSynthesis](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.passes.HighLevelSynthesis), [Target](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.Target), and [transpiler stages](https://quantum.cloud.ibm.com/docs/en/api/qiskit/transpiler). The review's current-code audit uses Qiskit 2.6.1, pinned to `2c4e5090d4eed225c8aab14e015864b0f8e26139`.

The diagram does not imply that every Qmod feature is identical to Qiskit HLS or that either framework has no other program representations or stages. Detailed equivalence and limitations remain in the article.

## Oracle semantics

Files: `oracle_semantics_ko.svg`, `oracle_semantics_en.svg`, `oracle_semantics_mobile_ko.svg`, `oracle_semantics_mobile_en.svg`.

Source: `oracle_results.json`, produced by the original NumPy calculation in `check_oracle.py` by `root`. The intended answer is `101`, using three qubits ordered `q2 q1 q0`. Both diagonal phase oracles are unitary, even when the second marks `111` instead of the intended `101`. Measuring directly after either oracle gives probability `1/8` for every basis string. After one Grover iteration, the marked string has probability `25/32` and each unmarked string `1/32`. Consequently, the intended `101` answer has probability 78.125% or 3.125%, depending on the specification.

The plotted probabilities are read from the JSON, not copied from chart pixels. The figure builder checks normalization, uniform post-oracle probabilities, zero reported unitarity error, and the exact expected fractions to numerical tolerance. The outlined bar always marks the intended answer `101`; the colored tall bar marks the oracle's chosen target. The reported distinction is semantic: an internally valid quantum operation can implement the wrong problem.

These are ideal, noiseless state-vector calculations, not measured QPU frequencies, a compiler comparison, a vendor result or an LLM success-rate benchmark. Mathematical context: Grover, [arXiv quant-ph/9605043v3](https://arxiv.org/abs/quant-ph/9605043v3).

## Reported synthesis tradeoff

Files: `synthesis_tradeoff_ko.svg`, `synthesis_tradeoff_en.svg`, `synthesis_tradeoff_mobile_ko.svg`, `synthesis_tradeoff_mobile_en.svg`.

Source: `synthesis_reported.json`, transcribed and checked by `applications_sources` from Goldfriend et al., *Design and synthesis of scalable quantum programs*, [arXiv:2412.07372v2](https://arxiv.org/html/2412.07372v2), 2025-01-22, Figure 3(b,c), §2.2 and Methods §4.1. The source is treated as a preprint. This figure redraws the numerical facts with original geometry; it does not reproduce the paper's artwork.

| Maximum width | Resulting circuit width | Logical CX gates |
|---:|---:|---:|
| 45 | 44 | 1,480 |
| 90 | 47 | 842 |

The figure uses a zero-baseline CX count axis and separate bars, with no interpolating curve or optimal frontier. `N = 20` sets the matrix dimension `2^20 × 2^20`; it is not the total circuit-qubit count. The compiler is the historical Classiq 0.60.0 used by the authors. These two reported compilation points were not independently executed here, are not current-version or cross-platform results, and do not establish physical runtime, fidelity or quantum advantage.

## Rendering, fonts and rights

The source font is Nanum Gothic, openly licensed under SIL OFL 1.1. The complete license is retained in `font-OFL.txt`; generated article-font derivatives have the distinct family name Review Sans Subset. Figure SVGs contain outlined glyphs and do not require the viewer to have that font installed. No logos, stock art or third-party figure pixels are included. The cited preprint's arXiv license is a perpetual non-exclusive distribution license, not a blanket permission to reuse its artwork; this review uses attributed numerical facts and independently drawn geometry. This record does not introduce a blanket reuse license for the repository.

The builder fixes the Matplotlib SVG hash salt, removes output dates and supplies no private host paths to SVG metadata. Local PNG previews and 390px QA screenshots are stored in ignored `tmp/figures/` and excluded from public distribution. Numerical and XML checks complement visual inspection; they do not constitute a human comprehension study.

## Completed output checks

All 12 diagram SVGs were parsed as XML and confirmed to contain outlined text, with no private host paths. A repeated build using Matplotlib 3.11.2 produced byte-identical SVGs. Korean and English desktop renders and all six mobile variants were visually inspected; the 390px browser checks selected the mobile images at 342px content width, without horizontal overflow or missing images. Final bilingual PDF inspection covered all 24 pages (Korean 11, English 13), including diagram labels and captions. The program-path semantics were separately reviewed by `root` and `academic_sources`; the two numerical figure types were also checked by `root`. These are AI-assisted production and scientific checks, not a line-by-line human approval or a reader comprehension study.
