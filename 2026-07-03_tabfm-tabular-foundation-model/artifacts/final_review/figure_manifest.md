---
type: figure-manifest
author: "김현중, AI Governance 팀"
date created: 2026-07-03
date modified: 2026-07-03
status: active
tags:
  - ai-tech-review
  - tabfm
  - tabular-foundation-model
  - figure-manifest
---

# TabFM 리뷰 Figure Manifest

| Figure | File | Purpose | Method | Source basis | Review notes |
|---|---|---|---|---|---|
| 그림 1 | `figures/tabfm_context_pipeline.svg` | TabFM이 labeled rows와 target rows를 하나의 context로 읽고 예측하는 구조 설명 | Deterministic SVG | Google Research blog, Hugging Face model card, GitHub README | 정확한 한글 라벨과 구조 관계가 중요해 생성 이미지 대신 SVG 사용 |
| 그림 2 | `figures/tabular_fm_landscape.svg` | TabPFN, TabICL, TabPFN-3, TabFM, BeyondArena를 한 장에서 비교 | Deterministic SVG | TabPFN Nature 논문, TabICL/TabICLv2 arXiv, TabArena/BeyondArena, TabFM 공식 자료 | 연구 흐름과 적용 경계를 함께 보이도록 구성 |
| 그림 3 | `figures/tabfm_license_gate.svg` | 회사 사용 시 코드와 weight 라이선스 경계 설명 | Deterministic SVG | GitHub Apache-2.0 license, Hugging Face TabFM Non-Commercial License | commercial/production 경계를 독자가 빠르게 확인하도록 구성 |
| 그림 4 | `figures/tabfm_poc_evaluation_matrix.svg` | TabFM PoC에서 모델·split·metric·운영 조건을 함께 평가하는 틀 제시 | Deterministic SVG | TabArena, BeyondArena, robustness 논문, TabFM/TabPFN/TabICL docs | report의 적용 체크리스트를 시각 요약 |

## 채택 판단

- 이 리뷰는 모델 구조, 라이선스, 벤치마크 경계를 비교하는 글이므로 정확한 텍스트 라벨이 중요합니다.
- hero 역할도 장식적 장면보다 구조 이해가 우선이라고 판단해 SVG를 채택했습니다.
- 향후 공유용 webzine 또는 발표자료로 확장할 때는 Skywork Image나 imagegen으로 텍스트 없는 editorial hero 후보를 만들고, 한글 라벨은 HTML/SVG로 후처리하는 방식을 권장합니다.
