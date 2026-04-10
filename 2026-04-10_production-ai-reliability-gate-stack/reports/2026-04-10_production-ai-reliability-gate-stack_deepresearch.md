# Production AI Reliability Gate Stack

## Executive Summary
이번 Pulse의 두 항목은 사실상 하나의 operational design으로 묶인다.
- `ECE·Brier 기반 모델 캘리브레이션 CI 게이트`
- `Conformal Risk 기반 선택적 예측 게이팅`

검증 결과, 이 묶음은 기술적으로 타당하다. 다만 두 항목은 같은 층위의 도구가 아니다.

가장 실용적인 해석은 다음이다.
- `Layer 1`: CI에서 calibration regression을 잡는 gate
- `Layer 2`: release 또는 runtime에서 abstention / deferral을 제어하는 selective prediction gate

이 구조가 좋은 이유는 역할 분리가 명확하기 때문이다.
- calibration gate는 `model confidence quality`를 본다.
- conformal / selective gate는 `operating risk under uncertainty`를 본다.

결론부터 말하면, production-ready baseline은 이미 있다.
- reliability diagram
- ECE / RMSCE / MCE
- Brier / log-loss
- temperature scaling

그 위에 frontier 확장으로 들어가는 것이 있다.
- Conformal Risk Control
- Selective Conformal Risk Control

즉, 지금 조직이 해야 할 일은 최신 논문을 바로 전면 도입하는 것이 아니라, `검증된 calibration baseline` 위에 `risk-bounded abstention layer`를 점진적으로 얹는 것이다.

## 1. Calibration Gate: What It Should Actually Measure

### 1.1 Reliability diagrams are still the correct first view
scikit-learn 문서는 calibration curve, 즉 reliability diagram을 예측 확률과 실제 빈도 비교의 기본 도구로 둔다. 핵심은 각 bin에서 평균 confidence와 실제 positive frequency가 얼마나 맞는지를 보는 것이다.

이게 중요한 이유는 단순 accuracy나 F1로는 `확신의 질`을 볼 수 없기 때문이다. 예측이 맞더라도 confidence가 계속 과장되어 있으면, release gate 관점에서는 위험하다.

Source:
- https://scikit-learn.org/stable/modules/calibration.html

### 1.2 Brier is useful, but not sufficient
scikit-learn은 `brier_score_loss`가 calibration, discrimination, data uncertainty를 함께 반영한다고 명시한다. 즉 Brier가 낮아져도 calibration이 좋아졌다고 단정할 수 없다.

이 점은 production에서 특히 중요하다.
- feature가 더 많아져 discrimination이 좋아지면 Brier는 내려갈 수 있다.
- 하지만 probability shape 자체는 더 과장될 수도 있다.

따라서 Brier는 `probabilistic quality composite metric`으로 쓰되, calibration-only gate로 단독 사용하면 안 된다.

Source:
- https://scikit-learn.org/stable/modules/calibration.html

### 1.3 ECE / RMSCE / MCE provide the CI-friendly scalar layer
TorchMetrics는 calibration error를 production code에 바로 넣기 쉽게 정리해둔다.
- `l1`: ECE
- `l2`: RMSCE
- `max`: MCE

문서가 주는 실용적 가치가 크다.
- bin-based 정의가 명확하다.
- binary / multiclass 둘 다 지원한다.
- CI에서 regression metric으로 자동화하기 좋다.

하지만 역시 caveat가 있다.
- bin choice에 민감하다.
- class imbalance가 심하면 top-label ECE가 중요한 subgroup failure를 가릴 수 있다.
- 표본 수가 적으면 metric variance가 커진다.

Source:
- https://lightning.ai/docs/torchmetrics/stable/classification/calibration_error.html

## 2. The Baseline Calibration Recipe That Is Actually Defensible

### 2.1 Guo et al. 2017 is still the anchor
`On Calibration of Modern Neural Networks`는 modern deep net이 종종 poorly calibrated하다고 보였고, 실무적으로는 `temperature scaling`이 surprisingly effective하다고 제안했다.

이 논문의 현재적 의미는 여전히 크다.
- calibration을 fancy uncertainty framework 이전에 먼저 챙겨야 한다.
- post-hoc scaling은 cheap하고 reproducible하다.
- baseline으로 두기 좋다.

Source:
- https://proceedings.mlr.press/v70/guo17a.html

### 2.2 Recommended calibration baseline
실전 baseline은 아래 정도면 충분히 강하다.
- frozen calibration split 유지
- reliability diagram 생성
- ECE + RMSCE + Brier + log-loss 기록
- pre- and post-temperature-scaling 비교
- multiclass라면 overall뿐 아니라 classwise summary도 저장

여기서 중요한 것은 threshold의 절대값보다 `baseline 대비 regression`이다.

권장 운영 방식:
- absolute threshold 하나만 두지 말 것
- last-good model 대비 상대 회귀량을 함께 볼 것
- calibration split은 학습 루프와 분리할 것

## 3. Why Calibration Gate and Deployment Gate Must Be Separate

### 3.1 Calibration is about confidence quality
Calibration gate의 질문은 이렇다.

`이 모델의 0.8 confidence가 정말 80% correctness에 가까운가?`

이건 확률 해석 가능성 문제다.

### 3.2 Selective prediction is about risk-managed action
Selective prediction 또는 abstention gate의 질문은 다르다.

`불확실할 때 이 모델이 예측을 내지 않도록 하거나, fallback / human review로 넘길 수 있는가?`

즉 action policy 문제다.

둘을 섞으면 안 되는 이유:
- calibration이 좋아도 high-risk region에서 abstention policy가 없으면 운영상 위험하다.
- abstention policy가 있어도 base confidence가 심하게 miscalibrated면 threshold 자체가 흔들린다.

따라서 `good confidence`와 `safe action`은 분리해서 다뤄야 한다.

## 4. Conformal Risk Control Changes the Release-Gate Conversation

### 4.1 CRC is more than miscoverage
Angelopoulos 계열 `Conformal Risk Control`은 conformal prediction을 miscoverage 하나에 국한하지 않고, `false negative rate`, `token-level F1` 같은 bounded loss까지 다루게 확장한다.

이게 실무적으로 중요한 이유는 release criteria가 실제로는 `업무 손실 함수`에 가깝기 때문이다.
- fraud 탐지면 false negative risk
- moderation이면 unsafe miss rate
- retrieval/QA면 answer-level or token-level quality loss

즉 CRC는 `confidence 예쁘게 맞추기`보다 `운영상 손실 상한 관리`에 더 가깝다.

Source:
- https://people.eecs.berkeley.edu/~angelopoulos/publications/downloads/conformal-risk.pdf

### 4.2 SCRC makes abstention more explicit
`Selective Conformal Risk Control`은 conformal prediction과 selective classification을 통합한다고 설명한다. 이건 practically useful하다. 전통 conformal set이 너무 커지는 문제를 피하면서, `predict vs abstain` 구조를 더 현실적으로 만들기 때문이다.

다만 이건 아직 frontier에 가깝다.
- 논문은 신선하고 의미 있다.
- 하지만 production 표준 라이브러리 / 조직 운영 규약으로 완전히 굳은 상태는 아니다.

따라서 SCRC는 `next layer to evaluate`, not `default first deployment choice`다.

Source:
- https://arxiv.org/abs/2512.12844

## 5. A Practical Two-Layer Reliability Gate

### Layer 1: CI calibration gate
목적:
- 학습 변경이나 feature 변경 뒤 confidence quality regression을 조기에 잡는다.

최소 체크:
- reliability diagram
- ECE
- RMSCE
- Brier
- log-loss / NLL

권장 규칙:
- frozen eval set 유지
- same binning scheme 유지
- last-good baseline과 비교
- classwise or subgroup slice도 함께 저장

### Layer 2: release / runtime selective gate
목적:
- 잘 모를 때는 예측하지 않거나 fallback으로 넘긴다.

옵션:
- simple confidence threshold + fallback
- calibrated confidence threshold
- CRC-based risk-bounded gate
- frontier: SCRC-style abstention framework

fallback 경로 예시:
- stronger model
- retrieval augmentation
- human review
- safe refusal

## 6. What Can Go Wrong

### 6.1 ECE can hide the wrong failure
overall ECE가 좋아도 특정 클래스나 minority subgroup만 망가질 수 있다.

### 6.2 Brier can improve for the wrong reason
더 discriminatory해졌기 때문에 Brier가 좋아졌는데, confidence reliability 자체는 나빠질 수 있다.

### 6.3 Calibration split leakage ruins the gate
train set 신호가 calibration set까지 새면, gate가 지나치게 낙관적이 된다.

### 6.4 Conformal guarantees are conditional
exchangeability가 무너지고 shift가 심해지면, nominal guarantee를 그대로 믿으면 안 된다.

### 6.5 Label delay breaks clean monitoring
온라인 환경에서는 정답 라벨이 늦게 들어오므로, runtime confidence와 delayed ground truth를 연결하는 운영 설계가 필요하다.

## 7. Recommended Rollout Path
1. Start with proven baseline
   - reliability diagram
   - ECE / RMSCE / Brier / log-loss
   - temperature scaling

2. Add CI promotion rule
   - absolute threshold + relative regression threshold
   - slice-level summary required on every build

3. Add explicit abstention path
   - fallback model or human queue
   - abstention reason logging

4. Pilot CRC on one bounded-loss use case
   - e.g. false negative risk or answer-quality loss

5. Evaluate SCRC only after the baseline is stable
   - treat it as a frontier enhancement, not the first line of defense

## 8. Concrete Initial Recommendations
- Use `temperature scaling` as the first calibration baseline unless there is strong evidence that isotonic gives stable gains on enough data.
- Treat `ECE + reliability diagram` as the primary calibration gate.
- Keep `Brier` and `log-loss` as secondary composite metrics.
- Require a frozen acceptance set and disallow threshold retuning on the same set without versioning.
- Define abstention destinations before setting the abstention threshold.
- For high-stakes workflows, shift from pure confidence thresholding toward CRC-style risk bounding.

## Bottom Line
이번 Pulse 묶음은 좋은 방향이다. 하지만 실무적으로는 이렇게 번역해야 한다.

`먼저 calibration을 CI에서 규율하고, 그 다음 uncertain case를 release/runtime에서 안전하게 버리거나 넘기는 2층 gate를 설계하라.`

이 구조가 있어야 reliability가 metric 장식이 아니라 실제 운영 제어 수단이 된다.

## Sources
- scikit-learn calibration docs:
  - https://scikit-learn.org/stable/modules/calibration.html
- TorchMetrics calibration error docs:
  - https://lightning.ai/docs/torchmetrics/stable/classification/calibration_error.html
- Guo et al. 2017:
  - https://proceedings.mlr.press/v70/guo17a.html
- Conformal Risk Control:
  - https://people.eecs.berkeley.edu/~angelopoulos/publications/downloads/conformal-risk.pdf
- Selective Conformal Risk Control:
  - https://arxiv.org/abs/2512.12844
