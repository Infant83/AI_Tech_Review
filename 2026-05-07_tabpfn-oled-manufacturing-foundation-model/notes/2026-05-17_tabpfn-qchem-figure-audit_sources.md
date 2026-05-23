---
title: "TabPFN OLED 계산화학 표현 및 Figure 보강 메모"
date: 2026-05-17
slug: tabpfn-qchem-figure-audit
status: source-note
language: ko
tags:
  - ai-tech-review
  - tabpfn
  - oled
  - quantum-chemistry
  - figure-audit
---

# TabPFN OLED 계산화학 표현 및 Figure 보강 메모

이 메모는 `2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md`에서 OLED 계산화학 표현을 더 정확하게 조정하고, figure가 실제 메시지를 충분히 전달하는지 점검하기 위해 작성했습니다.

## 반영 판단

- 본문 전면에 있던 GGA/GGA+U 예시는 무기 고체 데이터베이스 provenance를 보여주는 보조 사례로 낮췄습니다. OLED 분자 계산 본문에서는 software workflow, functional/basis set, conformer, spin state, environment, TD-DFT/SOC-TDDFT, CT state, exciplex, GW/BSE reference의 의미를 먼저 다루는 편이 더 자연스럽습니다.
- Schrödinger Materials Science와 SCM AMS/ADF는 OLED·organic electronics 계산 workflow를 실제 산업 사용자가 접하는 solution layer로 제시했습니다. 다만 solution workflow를 그대로 쓰는 것만으로 충분하다고 쓰지 않고, preset과 protocol의 전제와 한계를 전문가가 검토해야 한다는 경계를 같이 넣었습니다.
- TabPFN은 계산화학 전문성을 대체하는 모델로 설명하지 않았습니다. 대신 전문가 검토를 거친 표 데이터에서 후보를 줄이는 빠른 predictor로 위치를 제한했습니다.
- 그림은 2026-05-17에 `tabpfn_qchem_provenance_gate.svg`를 추가했습니다. 정확한 한국어 라벨, method/protocol/review column, TabPFN output이 들어가야 해서 imagegen이 아니라 deterministic SVG로 제작했습니다.

## 새 Figure 설계

| 항목 | 설계 내용 |
|---|---|
| 파일 | `artifacts/final_review/figures/tabpfn_qchem_provenance_gate.svg` |
| 목적 | OLED 계산값이 TabPFN에 들어가기 전에 어떤 provenance와 전문가 검토 정보를 가져야 하는지 한눈에 보여줍니다. |
| 주요 라벨 | `software_ver`, `protocol_id`, `method_family`, `basis_set`, `environment`, `state_char.`, `review_level`, `label_fidelity` |
| 도메인 경계 | TD-DFT, SOC-TDDFT, GW/BSE, CT state, exciplex, TADF를 figure 안에 직접 배치해 계산화학 판단의 존재를 보이게 했습니다. |
| 시각 기준 | 세 단계 흐름, 낮은 채도의 teal/red/graphite 색상, 18px 이상 본문 글자, 브라우저에서 불러오는 SVG image 검증을 기준으로 삼았습니다. |

## 참고자료

- [Schrödinger: Modeling for Organic Electronics](https://www.schrodinger.com/materials-science/solutions/organic-electronics/)
  - organic electronic materials, OLED device ML, physics-based modeling과 ML을 함께 제시합니다.
- [SCM: OLEDs](https://www.scm.com/applications/oleds/)
  - AMS/ADF에서 OLED molecular process, charge transport, exciton coupling, phosphorescence, SOC-TDDFT, TADF, Bumblebee OLED stack simulation을 설명합니다.
- [SCM ADF 2026.1 documentation](https://www.scm.com/doc/ADF/General/Introduction.html)
  - ADF의 TDDFT excitation energy, oscillator strength, transition dipole, transport property, QM/MM 기능을 확인했습니다.
- [Double and Charge-Transfer Excitations in Time-Dependent Density Functional Theory](https://www.annualreviews.org/content/journals/10.1146/annurev-physchem-082720-124933)
  - TD-DFT가 spectra와 response property 계산에 널리 쓰이지만, charge-transfer excitation과 double excitation에서는 black-box 적용이 어렵다고 설명합니다.
- [Electronic excitations: density-functional versus many-body Green's-function approaches](https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.74.601)
  - TDDFT와 GW/BSE 접근의 차이, excited-state 계산의 이론적 배경을 확인했습니다.
- [The Bethe-Salpeter equation in chemistry: relations with TD-DFT, applications and challenges](https://pubs.rsc.org/en/content/articlelanding/2018/cs/c7cs00049a/unauth)
  - BSE가 molecular organic systems의 optical property 계산에서 중요해지고 있고 TD-DFT와 다른 장단점을 가진다는 점을 확인했습니다.
- [Molecular excited states through a machine learning lens](https://www.nature.com/articles/s41570-021-00278-1)
  - molecular excited-state simulation이 어렵고, ML이 property prediction과 optoelectronic material search를 보조할 수 있지만 critical issues가 남아 있다는 배경 자료로 확인했습니다.
