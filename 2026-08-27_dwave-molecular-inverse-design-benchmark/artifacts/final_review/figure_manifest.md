# Figure manifest

| Figure | Role | Production route | Evidence source | Public-use boundary |
| --- | --- | --- | --- | --- |
| `molecular_inverse_design_hero.png` | 주제형 hero | OpenAI image model; unlabeled second-pass edit | Editorial interpretation of the pipeline | Illustration only; not a molecule, QPU, or DFT result screenshot |
| `molecular_inverse_design_infographic.svg` | 기술형 detailed infographic | Deterministic SVG authored from recorded metrics | `benchmark_results.csv` and the real-molecule evidence package | Solid blocks are executed; dashed live loop is proposed |
| `01_evidence_layer_pipeline.png` | 기술형 pipeline | Project-produced deterministic figure | Evidence package figure manifest | QPU appears only at acquisition; generated-DFT retraining is not run |
| `02_qm9_surrogate_parity.png` | 증거형 chart | Project-produced figure | Held-out QM9 labels and predictions | Interpolation evidence, not generated-molecule or experimental accuracy |
| `03_generator_metrics.png` | 증거형 chart | Project-produced figure | Generator counters and timings | Proposal/inference timings are not matched training-cost benchmarks |
| `04_acquisition_comparison.png` | 증거형 chart | Project-produced figure | Exact, classical SA, and one QPU result | BQM score is not molecular energy; one run does not establish speedup |
| `05_dft_molecule_validation.png` | 증거형 chart | Project-produced figure | QPU-selected batch and PySCF results | Single-point orbital-gap screen, not optical gap or experiment |
| `06_qm9_replay_convergence.png` | 증거형 chart | Project-produced figure | Fixed-pool hidden-label replay | No new DFT, QPU, or generated-space expansion |
| `07_exact_vs_qpu_dft_batch.png` | 증거형 chart | Project-produced figure | Exact/QPU batches and PySCF results | Three molecules per batch; no optimizer superiority claim |

## Image-generation record

- Selected output: `molecular_inverse_design_hero.png`
- Tool: OpenAI image model through the local `imagegen` workflow
- First pass: rejected for embedded Korean labels and numbers.
- Second pass: selected after removing all embedded text and leaving exact labels to deterministic SVG/HTML.
- Prompt intent: depict candidate molecules and ML scoring, a QUBO/quantum-annealing batch selector, and quantum-chemistry validation as separate stages on a restrained white/light-blue editorial field.
- Review note: the central hardware object is illustrative and must not be read as a photograph of the D-Wave machine used in the run.
