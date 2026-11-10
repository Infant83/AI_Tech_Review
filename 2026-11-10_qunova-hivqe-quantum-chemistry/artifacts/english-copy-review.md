# English manuscript and correspondence review

Date: 2026-11-10. Agent: qunova_english_publication. Scope: English writing and comparison against the Korean manuscript; no additional literature search or QPU execution.

## Manuscript

Title: Qunova HI-VQE and the division of work in quantum chemistry.

The English manuscript follows the Korean argument and section order while using natural English sentence boundaries. The nitrogen example establishes the research problem and the quantum/classical division of work. Configuration selection, coefficient optimization, noise resilience, sample coverage, the full-versus-projected variance, and the conditions for industrial usefulness remain connected through the examples.

The distinction between circuit-specific EPA simulability and the scope of HI-VQE more generally is retained explicitly. The later 72-problem-qubit LUCJ calculation is kept separate. HSQD is described as spin-half-configuration sampling plus classical reconstruction, with its sub-mHa result attached to the study's classical HCI reference. The 77-physical-qubit IBM case is described as 72 problem qubits plus five auxiliary qubits.

The first uses of Hartree–Fock, QSCI, SQD, DMRG, HCI, EPA, and LUCJ are explained. The millihartree unit is defined as 0.001 hartree. HCI's coupling/coefficient threshold is described in words. These additions explain the existing subject without introducing a new benchmark claim.

## Correspondence checks actually performed

- All 18 bibliography entries are byte-identical to the Korean reference list, including author order, paper titles, DOI/arXiv versions, source commits, and URLs.
- First appearance of the numbered references is 1 through 18 in both versions.
- Four display-equation blocks are byte-identical.
- The benchmark numbers and scopes were checked: 258 s; 46,547 s; 6,009,350,400 determinants; 1.20 mHa; 0.55%; about 64 mHa; about 66,000 Fugaku node-hours; 52 to 26 qubits; 0.7429 mHa; 72 problem plus five auxiliary qubits.
- The educational energies, units, electron counts, and variance distinction were preserved. The model remains an independent explanatory calculation rather than a vendor reproduction.
- Both technical-figure captions and alternative text are in English. Expected sources are `../artifacts/handover_workflow_en.svg` and `../artifacts/support_and_energy_en.svg`; their generation and publication rendering are owned by the integrating agent.
- No private email, local absolute path, account identifier, or authentication material was added to the manuscript.

This check does not substitute for the final HTML/PDF rendering and source-to-publication checks. The integrating agent owns the cover, final dek, authoring disclosure, registration, PDF, and public deployment.

## Suggested hub introduction

Korean: 큐노바의 질소 분자 벤치마크에는 양자 프로세서 4분 18초와 전체 계산 약 13시간이 함께 기록돼 있다. HI-VQE는 양자 표본으로 계산할 전자배치를 고르고, 고전 컴퓨터가 파동함수와 에너지를 완성한다. 이 분업의 가치는 촉매와 철–황 계의 어려운 전자 문제에서 같은 정확도를 더 낮은 총비용으로 얻을 수 있느냐에 달려 있다.

English: A Qunova nitrogen benchmark records 4 minutes 18 seconds of QPU use and nearly 13 hours overall. HI-VQE uses quantum samples to choose electronic configurations; a classical computer then constructs the wavefunction and energy. Its practical value for difficult electronic problems in catalysts and iron–sulfur systems depends on whether this division of work delivers the required accuracy at lower total cost.

Suggested English dek: How electronic-configuration sampling and classical diagonalization shape the strengths of HI-VQE and the prospects for practical quantum advantage.
