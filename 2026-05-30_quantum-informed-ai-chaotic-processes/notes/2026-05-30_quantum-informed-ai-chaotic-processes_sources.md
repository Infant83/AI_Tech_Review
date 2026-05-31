# Quantum-Informed AI for Chaotic Processes - Source Note

Date: 2026-05-30 KST  
Workspace package: `2026-05-30_quantum-informed-ai-chaotic-processes`  
Seed: https://www.youtube.com/watch?v=na-sQ-g2MAc

## Intake

| Item | Value |
| --- | --- |
| Video | [Exciting AI Updates Weekly - May 29, 2026](https://www.youtube.com/watch?v=na-sQ-g2MAc) |
| Channel | Lev Selector |
| Upload date | 2026-05-29 |
| Duration | 37:02 |
| Local metadata | `sources/na-sQ-g2MAc.info.json` |
| Local transcript | `sources/na-sQ-g2MAc.en-orig.vtt`, `sources/na-sQ-g2MAc.en.vtt` |

## Relevant Video Segment

The relevant chapter is `26:20-27:16`, titled `Quantum-informed AI for Chaotic Processes` in the YouTube chapter metadata. The adjacent chapter at `27:47-28:26` is `Multiverse Computing - LLM + quantum blocks`, which is related to quantum/AI integration but is a separate topic from chaotic-process forecasting.

The video presents the UCL/Science Advances paper as an example where quantum is used as part of the ML pipeline to improve prediction of chaotic and complex systems. The auto-caption mentions weather, turbulence, and disease spread as examples, then gives a rounded "about 20%" improvement claim. This should be treated as an intake summary, not as the final evidence wording.

## Claim Status

| Claim | Status | Notes |
| --- | --- | --- |
| A UCL-led paper on quantum-informed ML for chaotic systems exists. | confirmed | Paper: [Quantum-Informed Machine Learning for Predicting Spatiotemporal Chaos with Practical Quantum Advantage](https://arxiv.org/abs/2507.19861), Science Advances 2026, DOI [10.1126/sciadv.aec5049](https://doi.org/10.1126/sciadv.aec5049). |
| The paper uses a quantum component as part of a larger classical ML pipeline. | confirmed | The quantum generator learns a `Q-Prior` once, offline; the classical Koopman-style model then uses it as a statistical regularizer. |
| The headline improvement is "about 20%". | caution | The paper reports up to 17.25% predictive distribution accuracy improvement and up to 29.36% full-spectrum fidelity improvement against classical baselines. "About 20%" is a rounded media/video expression. |
| The evaluated systems include weather, turbulence, and disease spread. | partially confirmed / caution | The paper directly evaluates Kuramoto-Sivashinsky, 2D Kolmogorov flow, and 3D turbulent channel-flow inflow. Weather/climate and biomedical flows are plausible application domains, but disease spread is not one of the direct benchmark cases in the paper. |
| The quantum prior was trained on real superconducting quantum hardware. | confirmed | For turbulent channel flow, the authors report training the Q-Prior on IQM superconducting hardware, with hardware-efficient circuits and measurement mitigation. |
| This proves a general quantum advantage for chaotic prediction. | unconfirmed / caution | The paper argues practical quantum advantage for this framework and benchmark setting. Independent replication, broader baselines, and cost-accounted hardware comparisons remain important. |

## Primary Sources

- Wang, Xue, Gao, Coveney, [Quantum-Informed Machine Learning for Predicting Spatiotemporal Chaos with Practical Quantum Advantage](https://arxiv.org/abs/2507.19861), arXiv v5, Science Advances 2026.
- Science Advances DOI listing via ALCF: [Argonne publication page](https://www.alcf.anl.gov/publications/quantum-informed-machine-learning-predicting-spatiotemporal-chaos-practical-quantum).
- Official code: [UCL-CCS/QIML](https://github.com/UCL-CCS/QIML).
- Data DOI noted by the paper/code: [10.5281/zenodo.16419085](https://doi.org/10.5281/zenodo.16419085).

## Related Research Sources

### Classical chaos prediction baseline

- Pathak et al., [Model-Free Prediction of Large Spatiotemporally Chaotic Systems from Data: A Reservoir Computing Approach](https://doi.org/10.1103/PhysRevLett.120.024102), Physical Review Letters, 2018.
- Pathak et al., [Hybrid Forecasting of Chaotic Processes: Using Machine Learning in Conjunction with a Knowledge-Based Model](https://doi.org/10.1063/1.5028373), Chaos, 2018.

### Quantum reservoir computing and chaotic forecasting

- Fujii and Nakajima, [Harnessing Disordered-Ensemble Quantum Dynamics for Machine Learning](https://doi.org/10.1103/PhysRevApplied.8.024030), Physical Review Applied, 2017.
- Negoro et al., [Natural quantum reservoir computing for temporal information processing](https://www.nature.com/articles/s41598-022-05061-w), Scientific Reports, 2022.
- Mujal et al., [Time-series quantum reservoir computing with weak and projective measurements](https://www.nature.com/articles/s41534-023-00682-z), npj Quantum Information, 2023.
- Ghosh et al., [Quantum reservoir computing implementation on coherently coupled quantum oscillators](https://www.nature.com/articles/s41534-023-00734-4), npj Quantum Information, 2023.
- Ahmed, Tennie, Magri, [Prediction of chaotic dynamics and extreme events: A recurrence-free quantum reservoir computing approach](https://arxiv.org/abs/2405.03390), Phys. Rev. Research 6, 043082, 2024.
- Steinegger and Raeth, [Predicting three-dimensional chaotic systems with four qubit quantum systems](https://www.nature.com/articles/s41598-025-87768-0), Scientific Reports, 2025.
- Ahmed, Tennie, Magri, [Optimal training of finitely sampled quantum reservoir computers for forecasting of chaotic dynamics](https://link.springer.com/article/10.1007/s42484-025-00261-9), Quantum Machine Intelligence, 2025.
- Kobayashi and Motome, [Edge of Many-Body Quantum Chaos in Quantum Reservoir Computing](https://arxiv.org/abs/2506.17547), Physical Review Letters, 2026.
- Li et al., [Quantum reservoir computing for predicting and characterizing chaotic maps](https://arxiv.org/abs/2509.12071), arXiv, 2026 revision.

### Adjacent quantum/LLM signal

- Multiverse Computing, [Talking to a Quantum Computer: Quantum Hardware Inside a Production Large Language Model](https://multiversecomputing.com/papers/talking-to-a-quantum-computer-quantum-hardware-inside-a-production-large-language-model), 2026.
- Tomut et al., [CompactifAI: Extreme Compression of Large Language Models using Quantum-Inspired Tensor Networks](https://arxiv.org/abs/2401.14109), arXiv / ESANN 2025.

## Search Artifacts

- `sources/skywork_search_quantum-informed_AI_for_chaotic_processes_paper_result.txt`
- `sources/skywork_search_quantum_reservoir_computing_chaotic_time_series_prediction_result.txt`
- `sources/skywork_search_quantum_machine_learning_chaotic_dynamical_systems_papers_result.txt`
