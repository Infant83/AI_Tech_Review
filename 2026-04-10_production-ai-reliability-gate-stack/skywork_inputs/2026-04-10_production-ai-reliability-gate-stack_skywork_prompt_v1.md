업로드된 자료와 `LGD_Template.pptx` 템플릿을 기반으로 새로운 한국어 PowerPoint deck을 생성하라.

프로젝트명: Production AI Reliability Gate Stack
청중: ML 플랫폼 엔지니어, MLOps 리더, 모델 거버넌스 담당자, 기술전략 매니저
목적: calibration gate와 selective prediction gate를 분리한 production AI reliability architecture를 실무적으로 설명하고, 무엇이 production-ready baseline이며 무엇이 frontier인지 명확히 정리하는 기술 브리핑 deck을 만든다.
권장 분량: 13장
비율: 16:9

반드시 사용할 템플릿:
- `LGD_Template.pptx`

사용할 업로드 자료:
1. `2026-04-10_production-ai-reliability-gate-stack_deepresearch.md`
2. `2026-04-10_production-ai-reliability-gate-stack_memo.md`
3. `2026-04-10_production-ai-reliability-gate-stack_sources.md`

소스 우선순위:
1. 업로드된 deep research report
2. 업로드된 source note
3. 업로드된 memo
4. 필요한 경우에만 문서에 이미 인용된 공식 문서와 논문

리서치 정책:
- 업로드된 자료가 이미 충분히 구조화되어 있으므로 외부 리서치는 최소화하라.
- calibration metric과 conformal method의 역할 구분을 흐리지 말고, 업로드 자료의 검증 수준을 유지하라.
- frontier paper는 production standard처럼 과장하지 말라.

LGD 템플릿 적용 원칙:
- LGD 템플릿의 white-grid background, red thesis bars, rounded-card rhythm, corporate readability를 유지하라.
- dense briefing memo, evidence matrix, process-action mapping, annotated workflow 유형 레이아웃을 우선 사용하라.
- annotation은 작은 짙은 녹색 text로 텍스트 옆이나 아래에 붙이고, reference는 작은 짙은 회색 text로 표기하라.
- 템플릿 안에서 정보 밀도를 높이고, 큰 공백 중심의 카드형 마케팅 슬라이드는 피하라.

핵심 편집 원칙:
- deck의 thesis는 `Production reliability는 하나의 metric이 아니라, CI-stage calibration gate와 runtime selective prediction gate를 분리한 2층 구조로 다뤄야 한다` 여야 한다.
- `ECE/Brier`와 `CRC/SCRC`를 같은 층위 도구처럼 보이지 않게 하라.
- `temperature scaling`은 strong baseline으로, `SCRC`는 frontier option으로 위치시켜라.
- `Brier가 좋아졌다 = calibration이 좋아졌다`는 식의 오해를 막아라.

반드시 반영할 verified / high-confidence facts:
- scikit-learn calibration docs는 reliability diagram을 probability calibration 기본 도구로 둔다.
- 같은 문서는 `brier_score_loss`가 calibration과 discrimination을 함께 반영한다고 설명한다.
- TorchMetrics는 `ECE`, `RMSCE`, `MCE` 계열 calibration error 구현을 제공한다.
- Guo et al. 2017은 modern neural networks가 poorly calibrated할 수 있고, temperature scaling이 강력한 baseline이라고 보였다.
- `Conformal Risk Control`은 miscoverage를 넘어 false negative rate, token-level F1 같은 bounded loss에 대해 risk control 관점을 제공한다.
- `Selective Conformal Risk Control`은 의미 있는 frontier이지만 아직 일반적인 production standard라고 보기는 어렵다.

반드시 피할 것:
- ECE 하나만으로 reliability를 모두 판단하는 구조
- Brier를 calibration 전용 metric처럼 소개하는 표현
- conformal guarantee를 distribution shift와 무관한 만능 보장처럼 묘사하는 서술
- frontier method를 이미 널리 채택된 best practice처럼 보이게 하는 과장
- 빈 카드형, 슬로건형 슬라이드

필수 장표 구성:
- 1장: 제목 + 한 줄 결론 + 왜 지금 중요한가
- 2장: executive summary 3x3
- 3장: reliability problem decomposition `confidence quality vs safe action`
- 4장: calibration metrics matrix `ECE / RMSCE / MCE / Brier / log-loss`
- 5장: reliability diagram과 calibration gate 설계
- 6장: Guo 2017과 temperature scaling baseline
- 7장: practical CI calibration gate architecture
- 8장: 왜 calibration gate와 deployment gate를 분리해야 하는가
- 9장: conformal risk control 핵심 개념과 bounded loss
- 10장: CRC vs SCRC vs simple thresholding 비교
- 11장: practical two-layer production architecture
- 12장: failure modes `imbalance / shift / label delay / exchangeability`
- 13장: rollout roadmap + go-forward recommendations

시각 정책:
- metrics matrix, workflow diagram, comparison board, rollout roadmap, failure-mode matrix를 적극 사용하라.
- 기술적 caveat는 작은 짙은 녹색 annotation으로 붙여서 얇아 보이지 않게 하라.
- 출처는 작은 짙은 회색 text로 관련 블록 근처 또는 하단에 명시하라.
- 같은 카드형 반복보다 목적별 sub-template 다양성을 사용하라.

좋은 슬라이드의 조건:
- 각 장표는 하나의 명확한 thesis line을 갖되, supporting evidence block은 충분히 밀도 있게 배치한다.
- 엔지니어가 바로 구현 판단에 쓸 수 있어야 하고, 매니저도 정책 구조를 읽을 수 있어야 한다.
- production-ready baseline과 frontier research option의 경계가 분명해야 한다.
- corporate readability를 유지하면서도 technical nuance를 숨기지 않아야 한다.

이 기준으로 LGD 템플릿에 맞는 전체 deck을 생성하라.
