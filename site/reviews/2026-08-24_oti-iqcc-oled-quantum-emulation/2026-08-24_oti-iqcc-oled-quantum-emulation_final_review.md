---
title: "200 논리 큐비트 OLED 계산, 양자컴퓨터였나?"
type: final review
author: "김현중"
date created: 2026-08-24
date modified: 2026-08-24
status: checked
language: ko
tags:
  - quantum-chemistry
  - oled
  - iqcc
  - quantum-emulation
  - iridium-phosphor
  - platinum-phosphor
---

# 200 논리 큐비트 OLED 계산, 양자컴퓨터였나?

OTI Lumionics와 Samsung Advanced Institute of Technology(SAIT, 삼성종합기술원)의 JACS 연구가 Ir(III)·Pt(II) 인광체에서 달성한 것, 실제 QPU에서 실행하지 않은 것, 그리고 미래 양자 하드웨어가 넘어야 할 고전 에뮬레이션 기준선을 구분한다.

## 핵심 판단

- 실제 성취: 고전 컴퓨터에서 quantum-native iQCC solver를 실행해 약 200 spin-orbital qubit 규모의 active-space 문제와 실제 인광체 14종을 계산했다.
- 실제로 하지 않은 것: 200개의 오류정정 logical qubit 또는 1천만 개의 physical two-qubit gate를 QPU에서 실행하지 않았다.
- 성능: bare iQCC는 MAE 0.1180 eV를 기록했고, 비변분적 고전 EN-PT 보정을 더한 iQCC+PT가 MAE 0.0501 eV와 R² 0.9411을 기록했다.
- 의미: 양자 우위의 실증이 아니라 OLED 응용의 정확도·규모·고전적 tractability baseline이다. End-to-end 총비용 비교는 후속 QPU 평가 과제다.

## 연구의 경계

Iterative Qubit Coupled Cluster(iQCC)는 전자 Hamiltonian을 qubit Pauli operator로 바꾸고 unitary entangler를 반복 선택·최적화하는 quantum-native solver다. 이번 연구는 그 회로를 실제 QPU에 보내지 않고, Hamiltonian dressing과 Pauli-operator 구조를 이용해 특정 iQCC ansatz를 고전 CPU에서 에뮬레이션했다. 범용 200-qubit 상태벡터 시뮬레이션이나 일반 회로의 난이도 돌파가 아니다.

따라서 약 200 logical qubits는 활성공간 spin-orbital 수에 대응하는 이상적 logical-level register 규모이고, 1천만 two-qubit gates는 추상 ansatz의 logical-level gate count다. 물리 gate 실행 기록이나 QEC encoding·Clifford+T 컴파일·라우팅 비용을 포함한 fault-tolerant 자원 추정치가 아니다.

## OLED 계산의 의미

Ir/Pt 인광체에서는 T1 상태의 MLCT와 ligand-centered 성격, 다중참조와 spin contamination 때문에 DFT·TDDFT·single-reference CC의 안정성이 흔들릴 수 있다. iQCC는 에너지뿐 아니라 금속 중심 전하 변화를 통해 상태 character를 분석했다.

이번 비교에서 큰 정확도 향상은 순수 iQCC보다 비변분적 고전 보정인 Epstein-Nesbet perturbation theory를 결합한 iQCC+PT에서 나타났다. 비교값은 B3LYP 구조의 vertical Franck–Condon gap이며 Ir/Pt의 LANL2DZ ECP, 나머지 원자의 6-31G**를 사용했고 SOC와 ZPE는 제외했다. 실험 PL은 77 K 저유전 용매 조건이다. 실험과의 일치는 solver 오차와 active-space·basis·상대론·환경 모델 오차의 상쇄를 포함할 수 있으므로, 같은 Hamiltonian 안의 variational 비교와 실험 비교를 분리해야 한다.

## DFT·ML 역설계 파이프라인

현실적인 적용 위치는 전체 chemical-space 생성기가 아니라 고가치 후보의 고정밀 재판정층이다. GNN·surrogate와 DFT/TDDFT가 넓은 공간을 줄이고, spin contamination·다중참조·상태 ordering이 의심되는 후보를 iQCC, DMRG, selected CI, CASSCF/NEVPT2로 같은 조건에서 비교한다.

후속 QPU 평가는 동일 geometry, basis, active space, Hamiltonian과 관측량에서 state preparation, QEC, shots, queue, decoding, classical preprocessing까지 포함한 총비용으로 이 고전 기준선과 비교해야 한다. 이 end-to-end 비교는 원 논문이 수행한 결과가 아니라 본 리뷰의 평가 제안이다.

## References

1. Genin et al., *Large-Scale Quantum Computing Emulation for Accurate Triplet States of Ir(III) and Pt(II) Phosphorescent Emitters*, JACS (2026), https://doi.org/10.1021/jacs.6c04752
2. Scott N. Genin, LinkedIn research announcement, https://www.linkedin.com/posts/scott-genin-943a9118_large-scale-quantum-computing-emulation-for-activity-7495917046858276864-yjOW
3. Cao et al., *Quantum Chemistry in the Age of Quantum Computing*, Chemical Reviews (2019), https://doi.org/10.1021/acs.chemrev.8b00803
4. Mullinax et al., *Classical preoptimization approach for ADAPT-VQE*, JCTC (2025), https://doi.org/10.1021/acs.jctc.5c00150
