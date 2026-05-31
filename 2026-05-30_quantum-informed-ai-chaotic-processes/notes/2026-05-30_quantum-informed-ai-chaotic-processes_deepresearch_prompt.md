# Deep Research Prompt - Quantum-Informed AI for Chaotic Processes

## Role

You are a technical research analyst preparing a Korean AI_Tech_Review report for engineers and research leaders. The goal is to evaluate whether "quantum-informed AI" is becoming a credible method for forecasting chaotic or turbulent processes, and how to separate demonstrated value from quantum-AI hype.

## Seed Context

The user supplied a Lev Selector video:

- Video: [Exciting AI Updates Weekly - May 29, 2026](https://www.youtube.com/watch?v=na-sQ-g2MAc)
- Relevant chapter: `26:20-27:16`, `Quantum-informed AI for Chaotic Processes`
- The video appears to summarize the UCL/Science Advances paper by Wang, Xue, Gao, and Coveney on quantum-informed machine learning for spatiotemporal chaos.

## Research Question

How should we understand quantum-informed AI for chaotic processes as a practical research topic? Specifically:

1. What did the 2026 QIML paper actually demonstrate?
2. How does QIML differ from quantum reservoir computing, quantum-inspired tensor networks, and ordinary physics-informed ML?
3. Which related papers form the minimum reading list for a credible review?
4. What are the strongest technical insights and the main unresolved risks?
5. For engineering readers, what evaluation checklist should be used before believing "quantum advantage" claims?

## Source Priority

Use primary sources first:

1. Science Advances / arXiv paper: [Quantum-Informed Machine Learning for Predicting Spatiotemporal Chaos with Practical Quantum Advantage](https://arxiv.org/abs/2507.19861)
2. Official code: [UCL-CCS/QIML](https://github.com/UCL-CCS/QIML)
3. Pathak et al. PRL 2018 and Chaos 2018 reservoir-computing baseline papers
4. QRC papers by Fujii/Nakajima, Negoro et al., Mujal et al., Ghosh et al., Ahmed/Tennie/Magri, Steinegger/Raeth, Kobayashi/Motome
5. Use media sources only to understand how the claim is being framed publicly.

## Required Distinctions

Separate the following:

- confirmed results in the paper
- author claims and framing
- media/video simplifications
- plausible application domains
- unverified or extrapolated claims

Do not treat "weather, turbulence, disease spread" as all directly evaluated unless the source explicitly does so. The QIML paper directly evaluates Kuramoto-Sivashinsky, 2D Kolmogorov flow, and turbulent channel flow.

## Expected Deliverables

Write a Korean review with:

- one-page executive memo
- deep research report with paper map
- reading order for 5-10 papers
- claim-status table
- technical explanation of Q-Prior, invariant measure, Koopman model, QRC, and Lyapunov-time metrics
- evaluation checklist for future quantum-AI chaos papers
- concise recommendation on whether this is worth tracking for AI_Tech_Review

## Tone

Use friendly professional Korean. Avoid quantum-magic language. Be precise about what is demonstrated and what remains open.
