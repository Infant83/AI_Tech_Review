---
title: "TabPFN 데이터 provenance 및 활용 시나리오 보강 메모"
date: 2026-05-17
slug: tabpfn-data-provenance-usecases
status: source-note
language: ko
tags:
  - ai-tech-review
  - tabpfn
  - data-provenance
  - materials-informatics
  - dft
  - manufacturing-ai
---

# TabPFN 데이터 provenance 및 활용 시나리오 보강 메모

이 메모는 `2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md`를 DFT 중심 리뷰에서 산업 표 데이터 전반의 활용성, 값의 출처와 계산·측정 조건, 암묵지를 표에 기록하는 방식까지 확장하기 위해 확인한 자료와 반영 판단을 기록합니다.

## 핵심 판단

- DFT 계산값은 universal value가 아니라 계산 조건의 산물입니다. Functional, pseudopotential, DFT+U, reference state, convergence, post-processing이 다르면 같은 이름의 property도 달라질 수 있습니다.
- 실험값도 장비, 시료 이력, 측정 조건, 실험 순서, lot, recipe, operator, aging protocol 같은 맥락에 민감합니다.
- TabPFN은 결측, 범주형, mixed feature를 다룰 수 있고, TabPFN-3-Plus API는 text feature를 지원합니다. 그러나 기록되지 않은 암묵지를 자동으로 복원하지는 못합니다.
- 따라서 TabPFN PoC의 첫 단계는 모델 선택보다 `어떤 암묵지를 column으로 승격할 것인가`를 정하는 것입니다.

## DFT provenance 참고자료

- [Materials Project: Anion and GGA/GGA+U Mixing](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/thermodynamic-stability/anion-and-gga-gga+u-mixing)
  - GGA와 GGA+U 계산 에너지는 그대로 비교 가능하지 않으며, Materials Project는 보정 항을 사용해 비교 가능성을 높입니다.
- [Materials Project: GGA/GGA+U Calculations](https://docs.materialsproject.org/methodology/materials-methodology/calculation-details/gga+u-calculations)
  - GGA/GGA+U 계산 상세 문서와 관련 parameter 문서의 출발점입니다.
- [Quantifying uncertainty in high-throughput DFT](https://arxiv.org/abs/2007.01988)
  - AFLOW, Materials Project, OQMD를 같은 초기 구조 기준으로 비교했을 때 formation energy, volume, band gap, magnetization에서 차이가 나타나며 일부 차이는 pseudopotential, DFT+U formalism, elemental reference state와 연결됩니다.

## Metadata/provenance 참고자료

- [FAIR Guiding Principles](https://www.nature.com/articles/sdata201618)
  - metadata, provenance, reuse 조건을 포함해 데이터가 machine-actionable하게 재사용될 수 있어야 한다는 원칙을 제시합니다.
- [Automated reproducible workflows and data provenance with AiiDA](https://www.nature.com/articles/s42254-022-00463-1)
  - 계산 workflow에서 입력과 변환 과정의 complete record가 재현성을 보장한다는 점을 설명합니다.
- [AiiDA 1.0](https://www.nature.com/articles/s41597-020-00638-4)
  - high-throughput computational workflow에서 자동 provenance 기록과 query 가능한 graph 구조를 설명합니다.
- [Shared Metadata for Data-Centric Materials Science](https://arxiv.org/abs/2205.14774)
  - computational materials data와 experimental metadata의 FAIRification 문제를 다룹니다.
- [The Materials Experiment Knowledge Graph](https://pubs.rsc.org/en/content/articlepdf/2023/dd/d3dd00067b)
  - 재료 실험 데이터는 장비 설정, 시약 순도, 실험 단계 순서에 민감하며, sample과 실험 data/metadata의 complete provenance를 graph로 표현해야 한다고 설명합니다.
- [Material Data Hub documentation](https://materialhub.org/docs/materialhub_documentation)
  - `conditionObserved`, `parameterControlled`, `process`, `processReference`, `uncertainty` 같은 재료 데이터 schema 항목을 제공합니다.

## TabPFN 관점의 반영

- [Nature 2025 TabPFN 논문](https://www.nature.com/articles/s41586-024-08328-6)
  - TabPFN은 mixed type, missing value, categorical feature를 처리하지만, domain expertise와 feature engineering/problem framing은 여전히 필요하다고 설명합니다.
- [Prior Labs Models documentation](https://docs.priorlabs.ai/models)
  - TabPFN-3는 local OSS package에서 numerical/categorical/missing value를 다루고, TabPFN-3-Plus는 API/enterprise 배포에서 thinking mode와 native text feature를 제공합니다.
- [TabPFN-3 changelog](https://docs.priorlabs.ai/changelog/tabpfn-3)
  - TabPFN-3의 scale, API, text feature, migration guidance를 확인했습니다.

## 활용 시나리오별 데이터 설계 방향

| 활용 영역 | 행 단위 | 핵심 맥락 column |
|---|---|---|
| DFT 기반 역설계 | 후보 분자 또는 후보 구조 | functional, pseudopotential, DFT+U, dispersion, code/version, convergence, reference state, fidelity/source |
| 소자/제품 설계 | stack 후보 또는 실험 조건 | host/dopant, layer thickness, doping concentration, device area, initial luminance, measurement protocol |
| 공정 AX | lot, run, recipe execution | tool/chamber, recipe version, setpoint/actual trace, maintenance, substrate lot, operator/time |
| 검사/품질 | panel, image tile, defect candidate | inspection recipe, optics, image pipeline version, threshold, defect taxonomy, reviewer |
| SCM/원재료 | supplier shipment 또는 material batch | supplier, lot genealogy, CoA, purity, storage/transport, material age, incoming QC |
| 설비/예지보전 | equipment time window 또는 event sequence | sensor summary, alarm sequence, maintenance action, calibration, product mix, environment |

## 본문 반영 위치

- 제목/부제: DFT/OLED 중심에서 산업 표 데이터와 조건/provenance 중심으로 수정
- 도입부: 값보다 조건을 잘 담은 표가 먼저라는 메시지 반영
- 신규 섹션: `계산값과 실험값은 조건까지 같이 학습해야 합니다`
- 신규 섹션: `TabPFN은 암묵지를 feature로 바꾸는 작업을 빠르게 시험하게 해줍니다`
- 기존 제조 섹션 확장: 공정, SCM, 검사, 설계 활용 표 추가
- 마무리 섹션 수정: 활용 시나리오를 넓히고 한 행이 무엇을 뜻하는지, 예측값이 언제 확정되는지, 예측 당시 알 수 없는 정보가 입력에 섞였는지를 데이터 설계 기준으로 정리
