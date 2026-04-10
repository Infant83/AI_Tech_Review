# Deep Research Prompt v1

## Topic
- `Production AI reliability gate stack`
- Date sensitivity: `as of 2026-04-10 Asia/Seoul`

## Audience
- ML platform engineers
- MLOps / model-governance leads
- technical managers responsible for safe model release

## Research Objective
Build a practical, technically defensible blueprint for a production reliability gate stack that combines calibration monitoring in CI with selective prediction / abstention control at release time and runtime.

## Core Questions
1. What is the minimal calibration gate that should exist in CI before a model can be promoted?
2. What roles should `ECE`, `MCE`, `RMSCE`, `Brier`, `log_loss`, and reliability diagrams each play?
3. Why is `Brier` useful but insufficient as a standalone calibration gate?
4. What calibration methods are operationally strongest today for common classifier outputs, and when is temperature scaling enough?
5. How should conformal risk control be used to bound deployment risk beyond simple miscoverage?
6. What is the difference between:
   - confidence calibration
   - uncertainty estimation
   - selective prediction
   - conformal risk control
7. How should a real release gate be structured across:
   - offline validation
   - CI regression checks
   - runtime abstention / fallback
   - post-deploy monitoring
8. What are the main failure modes under:
   - class imbalance
   - label delay
   - distribution shift
   - non-exchangeability

## Required Source Priorities
1. Official documentation and foundational papers first:
   - scikit-learn calibration docs
   - TorchMetrics docs
   - Guo et al. 2017
   - Conformal Risk Control paper
2. Use more recent selective-conformal papers to extend the frontier.
3. Prefer implementation-ready sources over vague blog-style summaries.

## Required Deliverables
- A concise architecture for a two-layer reliability gate:
  - CI calibration gate
  - release/runtime selective prediction gate
- A metrics matrix explaining:
  - what each metric measures
  - what it misses
  - where it should be used
- Implementation guidance for:
  - data splits
  - thresholds
  - failure escalation
  - model comparison
- A section on what is production-ready now vs what is still frontier research
- A final recommended rollout path for an engineering org

## Explicit Comparison Points
- ECE vs Brier vs log-loss
- temperature scaling vs isotonic vs no recalibration
- calibration gate vs conformal gate
- abstention-to-human vs abstention-to-fallback-model
- static release threshold vs risk-bounded selective prediction

## Risks / Uncertainty To Validate
- Do not present ECE as a complete reliability measure.
- Do not treat Brier improvement as automatically meaning better calibration.
- Do not ignore class-conditional or subgroup-specific calibration drift.
- Do not treat conformal guarantees as magic under clear distribution shift or broken exchangeability assumptions.
- Mark recent selective conformal work as frontier when appropriate.

## Output Style
- Write for practitioners who need to implement gates, not just discuss theory.
- Prefer exact operational recommendations, decision criteria, and failure modes.
- Distinguish clearly between:
  - proven baseline practice
  - recommended pragmatic default
  - research frontier option
