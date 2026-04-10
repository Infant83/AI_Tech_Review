# 2026-04-10 Production AI Reliability Gate Stack - Sources

## Topic
- `Production AI reliability gate stack`
- Seed date: `2026-04-10`
- Intake path: `GPT Pulse -> daily_research_review/2026-04-10_gpt-pulse-daily-review`

## Pulse Seed Items
- `ECE·Brier 기반 모델 캘리브레이션 CI 게이트`
- `Conformal Risk 기반 선택적 예측 게이팅`

## Local Seed Artifacts
- `sources/2026-04-10_gpt-pulse-daily-review_pulse_review.md`
- `sources/2026-04-10_gpt-pulse-daily-review_overview_snapshot.yml`

## Primary / High-Priority External Sources
1. scikit-learn probability calibration guide
   - URL: https://scikit-learn.org/stable/modules/calibration.html
   - Verified points:
   - calibration curves / reliability diagrams compare predicted probabilities to observed frequencies
   - `brier_score_loss` and `log_loss` assess both calibration and discrimination, so Brier alone is not a pure calibration measure

2. TorchMetrics calibration error docs
   - URL: https://lightning.ai/docs/torchmetrics/stable/classification/calibration_error.html
   - Verified points:
   - exposes `BinaryCalibrationError` and `MulticlassCalibrationError`
   - supports `l1` / ECE, `l2` / RMSCE, and `max` / MCE variants
   - gives the bin-based definitions explicitly

3. Guo et al. `On Calibration of Modern Neural Networks`
   - URL: https://proceedings.mlr.press/v70/guo17a.html
   - Verified points:
   - modern neural networks are often poorly calibrated
   - temperature scaling is a strong practical baseline

4. Angelopoulos et al. `Conformal Risk Control`
   - URL: https://people.eecs.berkeley.edu/~angelopoulos/publications/downloads/conformal-risk.pdf
   - Verified points:
   - extends conformal prediction to bounded loss functions beyond miscoverage
   - worked examples include false negative rate and token-level F1-score

5. `Selective Conformal Risk Control`
   - URL: https://arxiv.org/abs/2512.12844
   - Verified point:
   - integrates conformal prediction with selective classification to make risk-bounded abstention more practical
   - frontier / recent research, not yet a mature production standard

## Preliminary Validation Notes
- Pulse's `ECE·Brier 기반 CI gate` framing is credible if interpreted as:
  - calibration curve / ECE-based regression check
  - Brier / log-loss as secondary probabilistic quality indicators
  - a frozen acceptance dataset in CI
- Pulse's `Conformal Risk 기반 선택적 예측 게이팅` framing is also credible, but it belongs at a different layer:
  - post-training deployment gate
  - abstain / defer / escalate policy
  - distribution-free or risk-bounded operating envelope assumptions

## Operational Reading
- A useful implementation is a two-layer stack:
  - Layer 1: `CI calibration gate`
  - Layer 2: `runtime selective prediction gate`
- The main mistake to avoid is collapsing them into one scalar threshold.
- `Brier alone` is not enough.
- `ECE alone` is also not enough if class imbalance, small bins, or label shift are severe.
- Conformal methods require care around exchangeability, calibration-set choice, and business loss definition.

## Open Questions
- Which metrics should be global versus class-conditional?
- What data split is acceptable in production when labels arrive late?
- When should abstention route to a fallback model versus human review?
- Which conformal method is robust enough under distribution shift for the user's actual workload?
