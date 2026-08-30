# Source and claim ledger

Checked: 2026-08-30

## Primary sources

- Classiq Quantum Circuit Challenge, official challenge page. Challenge window 2026-08-28 through 2026-09-30; 64×64 binary image; 1,097 marked pixels; x and y use separate six-qubit address registers; correctness precedes depth ranking and CX is the tie-breaker; matching `.qmod` and `.qasm` submissions are required.
- D. Khan et al., arXiv:2608.23895v1, submitted 2026-08-24. KS-FNO replaces the repeated density component of the forward Kohn–Sham map inside SCF; it is classical GPU electronic-structure work, not a quantum-computing result.
- G. Aizpurua-Iraola et al., arXiv:2608.27045v1, submitted 2026-08-27. PTSET is an experimental CMOS charge-sensor proof of concept; the reported sensitivity improvement is not a measured spin-readout fidelity improvement.
- K. Bharti, T. Haug, and A. Tanggara, arXiv:2608.26272v1, submitted 2026-08-26. Information-theoretic quantum-memory spacetime bound under known-location erasure noise and optimistic recovery assumptions; not a QPU experiment or a general impossibility theorem for FTQC.
- Innovation, Science and Economic Development Canada, official release dated 2026-08-28. C$195 million Strategic Response Fund investment in a C$893 million Xanadu project; a manufacturing and industrial-capacity commitment, not evidence of completed fault-tolerant hardware.
- Pasqal official transaction-completion release dated 2026-08-27 and Pasqal Holding SA SEC Form 6-K. Approximately US$360 million of cash available at closing; not company valuation, revenue, or a pure-new-capital figure.

## Hard boundaries preserved

- The five items belong to different evidence layers: a classical GPU preprint, a circuit-design challenge, a physical charge-sensor PoC, a theory preprint, and industrial/capital announcements. They were not demonstrated as one integrated system.
- The Classiq challenge publishes a task and ranking procedure, not a winning circuit, QPU execution result, speedup, or public baseline. The two six-qubit address registers do not imply that every submission is a 12-qubit circuit because ancillas may be used.
- KS-FNO's largest Mg result used a fine-tuned model. The basic cross-domain model diverged on the tested dislocation cells. The fitted scaling comparison is not hardware matched, the largest cell lacks a PBE reference density, and energy or orbital-resolved quantities still require a fixed-density post-SCF diagonalization.
- The PTSET experiment mimicked a charge event with a gate-bias shift. It did not read an adjacent spin qubit, report assignment fidelity, resolve switching/recovery dynamics, or validate an array. The >350× SNR value is modeled, not measured.
- The memory lower bound assumes independent erasure noise below the Gilbert–Varshamov threshold, known erased locations, adaptive protocols, and ideal recovery. The paper also gives a matching positive-rate construction for memory.
- Xanadu and Pasqal figures use different currencies and transaction structures. They are not added, compared as performance metrics, or treated as technical validation.
- No item establishes quantum advantage or end-to-end acceleration. Any OLED/materials PoC must compare the bounded quantum component against the strongest classical baseline at matched accuracy and include encoding, state preparation, shots, readout, mitigation, postprocessing, queue time, and wall-clock.

## Primary links

1. https://get.classiq.io/quantum-circuit-challenge/
2. https://arxiv.org/abs/2608.23895
3. https://arxiv.org/abs/2608.27045
4. https://arxiv.org/abs/2608.26272
5. https://www.canada.ca/en/innovation-science-economic-development/news/2026/08/government-of-canada-invests-in-xanadu-to-build-up-advanced-quantum-manufacturing-in-canada.html
6. https://www.pasqal.com/newsroom/pasqal-and-bleichroeder-acquisition-corp-ii-complete-business-combination/
7. https://www.sec.gov/Archives/edgar/data/2119292/000121390026094393/ea0303667-6k_pasqal.htm
