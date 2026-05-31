---
title: "TabPFN-3 및 라이선스 업데이트 검증 메모"
date: 2026-05-17
slug: tabpfn-3-license-update
status: source-note
language: ko
tags:
  - ai-tech-review
  - tabpfn
  - tabpfn-3
  - license-review
  - company-use
---

# TabPFN-3 및 라이선스 업데이트 검증 메모

이 메모는 `2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md`의 2026-05-17 업데이트를 위해 확인한 자료와 반영 판단을 기록합니다.

## 확인한 변경점

- 2026-05-11 리뷰에서는 TabPFN-2.6을 OSS 패키지의 기본 모델로 설명했습니다.
- 2026-05-17 확인 기준 [Prior Labs Models documentation](https://docs.priorlabs.ai/models)은 TabPFN-3를 OSS 패키지의 기본 모델로 설명합니다.
- [PyPI tabpfn release history](https://pypi.org/project/tabpfn/)는 8.0.0이 2026-05-12, 8.0.3이 2026-05-16에 배포되었음을 보여줍니다.
- [TabPFN-3 changelog](https://docs.priorlabs.ai/changelog/tabpfn-3)는 TabPFN-3의 주요 변경점으로 더 큰 in-context row capacity, 160-class classification, sub-millisecond prediction, API의 thinking mode와 native text feature, `/tabpfn/*` JSON endpoint, migration guidance를 제시합니다.
- [TabPFN-3 License v1.0](https://huggingface.co/Prior-Labs/tabpfn_3/blob/main/LICENSE)은 TabPFN-3 model weight와 derivative를 non-commercial, non-production use로 제한하고, output도 production system, business process, client deliverable, revenue-generating activity에 쓰려면 commercial license가 필요하다고 설명합니다.

## 회사 사용 관점의 반영 판단

TabPFN을 회사에서 검토할 때는 `코드 공개 여부`와 `기본 모델 weight 사용 권리`를 분리해야 합니다. [PriorLabs/TabPFN GitHub](https://github.com/PriorLabs/TabPFN)는 코드와 TabPFN-2 model weights를 Prior Labs License, 즉 Apache 2.0에 attribution requirement가 붙은 license로 설명하지만, TabPFN-2.5, TabPFN-2.6, TabPFN-3 model weights는 non-commercial license로 설명합니다.

따라서 내부 PoC는 다음 범위로 제한하는 것이 안전합니다.

- 공개 데이터 또는 반출 가능한 샘플 데이터로 기술 가능성만 확인합니다.
- 결과를 next experiment, production workflow, vendor/procurement, product roadmap, client deliverable, budget decision에 직접 연결하지 않습니다.
- 실제 OLED 후보 선별, 공정 품질 dashboard, 사내 플랫폼 통합, 고객 프로젝트에 연결하기 전에는 commercial license 또는 API agreement를 확인합니다.
- API 사용 시 데이터 반출, 영업비밀, 개인정보, 보안 심사를 별도로 진행합니다.
- TabPFN output을 이용해 상업 목적의 별도 모델을 train, fine-tune, distill하지 않습니다.

## 반영 위치

- `reports/2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md`
  - 모델 업데이트 문단: `TabPFN은 표 데이터에서 튜닝 시간을 줄이는 모델입니다`
  - 활용 조건: `활용 전에 확인할 조건`
  - 신규 섹션: `회사에서 사용할 때는 PoC와 업무 의사결정을 분리해야 합니다`
  - `작성정보`와 `References`

## 참고자료

- [Prior Labs Models documentation](https://docs.priorlabs.ai/models)
- [TabPFN-3 changelog](https://docs.priorlabs.ai/changelog/tabpfn-3)
- [PyPI tabpfn release history](https://pypi.org/project/tabpfn/)
- [TabPFN-3 License v1.0](https://huggingface.co/Prior-Labs/tabpfn_3/blob/main/LICENSE)
- [PriorLabs/TabPFN GitHub](https://github.com/PriorLabs/TabPFN)
- [Accessing Model Weights](https://docs.priorlabs.ai/how-to-access-gated-models)
- [API metering](https://docs.priorlabs.ai/api-reference/metering)
- [Thinking mode](https://docs.priorlabs.ai/capabilities/thinking-mode)
