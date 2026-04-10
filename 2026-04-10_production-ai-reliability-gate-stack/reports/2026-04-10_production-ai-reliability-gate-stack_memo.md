# Memo

## One-Line View
`Production AI reliability`는 하나의 metric으로 푸는 문제가 아니라, `CI-stage calibration gate`와 `runtime selective prediction gate`를 분리한 2층 구조로 설계하는 것이 맞다.

## What Is Solid
- scikit-learn 문서는 calibration curve / reliability diagram을 확률 예측의 적합도 점검 기본기로 둔다.
- 같은 문서는 `Brier`가 calibration과 discrimination을 함께 섞어 보므로 calibration 단독 판단에는 한계가 있다고 분명히 말한다.
- TorchMetrics는 실제 production code에 넣기 쉬운 `ECE / RMSCE / MCE` 구현을 제공한다.
- Guo et al. 2017은 modern neural network가 종종 poorly calibrated하며, `temperature scaling`이 강력한 baseline이라고 보여준다.
- `Conformal Risk Control`은 false negative rate, token-level F1 같은 bounded loss에 대한 risk control 관점을 제공한다.

## Practical Architecture
- Layer 1: `CI calibration gate`
  - frozen eval set
  - ECE + reliability diagram + Brier / log-loss regression checks
- Layer 2: `release/runtime gate`
  - abstain / defer / fallback policy
  - CRC / SCRC or simpler selective prediction rule

## Main Cautions
- `Brier만 좋아졌다`로 승인하면 안 된다.
- `ECE만 낮다`고 안전해지는 것도 아니다.
- conformal guarantee는 calibration split과 데이터 조건이 무너지면 쉽게 약해진다.

## Recommended Next Move
- 다음 단계는 실제 배포 파이프라인 기준으로:
  - 어떤 split을 유지할지
  - 어떤 threshold를 baseline 대비 regression gate로 둘지
  - abstention 시 fallback 경로를 어디로 둘지
를 구체화하는 것이다.
