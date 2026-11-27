# 파운데이션 포텐셜과 연구 워크플로: 1차 자료 대조

2026-11-27 · 편집부(AEDAUT) 독립 조사·과학 감수 · foundation_sources

## 이번 조사의 범위

11월 24–25일 기획의 DOI·공개 본문·판본을 다시 확인하고, 집필에 쓸 물리적 대상·비교 지표·조건을 대조했다. 원 연구의 MLIP·DFT·MD·에이전트 시스템은 실행하지 않았다. 아래 결과는 저자 보고값이며, 리뷰의 조화 모형 교육 계산과 구별한다. 출판사·arXiv·PMC·저자의 공식 자료를 사용했다. 자료 원문·개인 메일·HTTP 세션 정보는 이 폴더에 보관하지 않았다.

출발 Perspective[1]의 Crossref 공식 기록은 세 저자, 2026-11-19 온라인 출판, accepted manuscript(am), CC BY 4.0, 아직 권·호·논문번호 미부여 상태다. Crossref가 제공한 공식 HTML·PDF URL을 모두 정상 공개 HTTP로 재시도했으나 403이었다. 공개 전문을 읽었다고 표시하지 않는다. 기획 소개와 서지를 출발점으로 삼고, 아래 공개 원 연구에서 개별 과학 주장을 구성한다.

## 모델 안에서 공유되는 것은 무엇인가

Li–Walsh[3]의 출판사 공개 본문과 식(1)–(2), 그림 1–4·표 1을 읽었다. 7개 MLIP에서 MP-20의 27,136구조·282,847원자 환경 표현을 추출했다. 원래 128·256차원 등 서로 다른 표현을 같은 원자 기준점(anchors)과의 cosine similarity로 바꾼다. DIRECT로 고른 기준점 100개 부근에서 전역 표현이 안정한다.

전역 Procrustes 정렬은 MACE 계열에서 0.86 이상이지만, 국소 이웃 mKNN 일치는 모든 쌍에서 0.38 미만이다. 물리량 감독 없이 구조 생성만 학습한 Chemeleon과의 대조도 수행했다. 이 결과는 공통 화학 구조와 남은 국소 차이를 함께 설명한다. 논문의 zero-shot stitching 실증은 반응·물질의 **embedding 산술 호환성**이다. 에너지·힘 예측을 유지하는 가중치 모듈의 임의 교환을 실증한 것으로 옮기지 않는다. 새 물질의 물성 정확도는 출력과 기준 계산으로 확인한다.

## 곡률을 읽는 관측량: 연화와 진동

Deng 등[4]의 출판사 공개 본문에서 그림 4·6과 Methods의 phonon·미세조정 조건을 읽었다. 대상은 M3GNet·CHGNet·MACE-MP-0 세 모델이다. CsF의 분산 관계와 229재료의 최대 phonon 진동수 비를 비교했고, 90% 이상 재료에서 참조 DFT보다 낮은 진동수를 보고했다. 재료·환경별 고에너지 구조와 힘의 체계적인 과소평가가 곡률 설명의 실제 근거다.

Phonon 비교는 비자성·U 보정 없는 재료, PhononDB의 PBEsol 참조와 비해석 보정(NAC) 제외 조건이다. 모든 2026년 모델·모든 물성으로 범위를 확대하지 않는다. 선형 재보정과 재료별 10구조 CHGNet 미세조정은 각각 별도 계산이다. 교육 예제 k→0.81k, ω→0.9ω는 리뷰가 정한 조화 모형이며 논문의 재료별 측정값으로 쓰지 않는다.

## 새 근거: 같은 작은 진동 오차도 다른 상으로 이어진다

Grandel·Benner·George[10]의 출판사 본문과 정식 PDF, PMC 보존 전문에서 표 1–4·그림 4–5·Methods를 읽었다. 현행 정식 서지는 **npj Computational Materials 12, 354 (2026)**다. 연구는 MACE-MP-0b3에서 재료별 10구조로 미세조정하며, 상변화·칼코게나이드 중심의 53재료를 비교했다. L²-TSP는 사전학습 가중치에서 멀어지는 갱신을 억제하고 앞의 두 표현 층을 선택적으로 조정한다.

큰 초격자 학습에서 phonon MAE 중앙값은 기초 모델 0.27 THz, L²-TSP 0.05 THz다. 그러나 새로운 상 복원의 F1은 각각 0.63·0.66이며, L²-TSP의 precision 68%·recall 65%다. 그림 4의 K₃Sb에서는 multihead와 L²-TSP가 모두 K점 허수 모드·이중 우물을 포착하지만, 이완 후 L²-TSP만 DFT의 P6₃cm 상을 복원하고 multihead는 다른 R−3 상으로 간다. **곡률→변위 경로→최종 구조**로 검증을 넓힐 직접적인 사례다. 검증은 9개 불안정 재료와 원자 수 제한으로 DFT 가능한 26/41 q점의 범위다.

## 새 배치를 선택하고 기준 계산을 더하는 루프

Rensmeyer 등[5]은 공식 RSC 본문·PDF가 다시 403이었다. 서지는 Crossref에서 확인했고, 방법·수치는 공개 **arXiv:2507.13805v1**[11]의 §5.3·그림 5·Appendix B.6에서 읽었다. 세부 수치를 쓸 때 이 읽은 판본을 함께 표시한다.

이 루프는 보정한 에너지 오차가 임계값을 넘을 예측 확률이 5%보다 크면 DFT를 추가하고, 후방분포에서 8개 모델을 다시 표본화한다. LaMnO₃의 6 kcal/mol 임계값을 힘 오차 단위로 바꾸지 않는다. 첫 구조의 DFT 값으로 에너지 영점의 상수 차이도 맞춘다.

LaMnO₃는 MACE-MP0 medium, 40원자 2×2×2 초격자로 150 ps를 계산했다. 300 K 25 ps→800 K 100 ps→300 K 25 ps, NPT 1 bar·0.5 fs, PBE+U(Mn U=3.9 eV)·500 eV cutoff다. 미세조정은 저온 구간의 세 Mn–O 결합 거리와 가열·냉각 구조 변화를 복원한다. 저자들은 1,800구조를 DFT로 다시 계산해 불확실성과 실제 오차를 대조했고, 낮은 예측 불확실성에 큰 오차가 있는 사례도 보였다. 불확실성–오차 보정과 독립 표본 검사를 본문에서 구체화할 근거다.

이 예제는 Jahn–Teller·궤도질서에 관련된 **구조 변화**로 설명한다. 원문의 저온 구조 일반 소개를 300–750 K 전체의 반강자성 질서 또는 750 K 자기 상전이로 바꾸지 않는다. 이 조사의 방법 읽기에서는 DFT의 자세한 자기 배치 지정을 찾지 못했다. 전자 상태·자기질서를 검증 기준의 선택으로 언급하되 실제 계산이 모두 검증했다고 주장하지 않는다.

## 탐색 속도와 에너지 순위의 대조

Tahmasbi 등[6]의 출판사 공개 본문에서 EOS·minima hopping·POA·불안정 지표·자료 공개를 읽었다. 전이금속의 평형 부피에 잘 맞는 모델도 알칼리·알칼리토금속·반응성 비금속에서 차이를 보였다. minima hopping으로 알려진 구조를 찾는 비율과, 그 구조들 사이의 상대 에너지 순위를 구별한다. POA는 비교 가능한 구조 쌍의 에너지 순서 일치 비율이며, DFT 에너지 차이가 5 meV/atom보다 작은 쌍은 제외한다. 적어도 두 구조가 맞아야 평가한다.

따라서 ‘빨리 최소점을 찾는다’와 ‘찾은 상들의 안정성 순위가 맞다’는 각각의 결과로 서술한다. 공개 입력·분석 스크립트는 RODARE DOI 10.14278/rodare.4596에 연결한다. 이번 조사는 그 코드를 실행한 재현이 아니다.

## 에이전트가 재사용하는 계산 절차

Potente[7] v1의 §2.1–2.2.3·Appendix A·SI Table S2를 읽었다. LLM은 기획·분기·맞춤 절차를 맡고, 검증한 Python 함수가 수치를 계산한다. 표준 typed graph와 기존 함수를 조합하는 coding mode가 연결된다. 500 Materials Project 구조를 동일 MACE-OMAT·설정으로 탄성·300 K 조화 Cᵥ 계산에 쓰고 수동 스크립트와 각각 5회 비교했다. 이 비교의 기준은 **같은 모델을 실행한 결과의 일관성**이다. 물성의 DFT 정확도는 별도 1,000구조·3모델 탄성 비교에서 다뤘다.

YbZn₂P₂(mp-9582)는 Niggli 표준화 경계 근처에서 간헐적으로 실패했고, 실패 자료형으로 남겨 나머지 계산을 계속했다. 입력·수치·단계·실패를 함께 보존하는 구체 사례다. 에이전트가 결정론적 도구를 호출해도 기준 계산·모델·수렴 조건을 정하는 연구자의 판단이 필요하다는 설명과 연결한다.

### 비용 표의 불일치 재확인

본문 Table 1과 SI Table S2의 Potente 요약행은 11월 27일에도 일치하지 않았다. 나열된 다섯 실행의 단순 산술 평균은 비용 $0.1522, 총 토큰 26,724, 흡착열 22.794 kJ/mol이다. SI 평균행은 각각 $0.12·22,541·17.21이다. 본문 비용·흡착열은 실행 행들의 평균과 대응한다. 두 비교군은 MLIP·GCMC 절차도 다르므로 비용 절감 배율·물리 정확도 우위를 새 그래프로 만들지 않는다. 논문의 비용은 API 토큰 비용이며 전력 계측이 아니다.

## 집필에 제안하는 근거의 연결

1. 리뷰의 조화 예제에서 같은 최저 에너지와 다른 곡률·진동수를 계산한다.
2. Deng의 실제 연화 결과와 Grandel의 곡률·경로·최종 상 비교를 이어, 필요한 물성을 기준으로 검증 범위를 정한다.
3. Li–Walsh의 공통 표현은 무엇을 재사용할 수 있는지 설명하고, Bayesian 루프는 부족한 배치를 어떻게 추가하는지 설명한다.
4. Potente는 검증한 절차의 재사용을 보여 준다. 연구자의 의도·참조 기준·모델 판본·결과·실패가 다음 실행까지 유지되는 구조를 본문과 그림으로 잇는다.

ASE·AiiDA[8,9]는 기존 과학 소프트웨어의 기반으로 두며, 자연어로 절차를 구성하는 새 기능과 수치 실행·이력 관리의 축적을 함께 설명한다. 이 조사에서 최신 버전 설치·동작을 시험하지 않았으므로 특정 API 동작을 보장하는 예시 코드는 제시하지 않는다.

## 참고문헌

[1] T. W. Ko, V. Bernales, and A. Aspuru-Guzik, Foundational potentials for molecules and materials: A game changer in atomistic simulations?, [AI for Science (2026)](https://doi.org/10.1088/3050-287X/aec468).

[2] I. Batatia et al., A foundation model for atomistic materials chemistry, [J. Chem. Phys. **163**, 184110 (2025)](https://doi.org/10.1063/5.0297006).

[3] Z. Li and A. Walsh, Platonic representation of foundation machine learning interatomic potentials, [Nat. Mach. Intell. **8**, 830 (2026)](https://doi.org/10.1038/s42256-026-01235-7).

[4] B. Deng, Y. Choi, P. Zhong, J. Riebesell, S. Anand, Z. Li, K. Jun, K. A. Persson, and G. Ceder, Systematic softening in universal machine learning interatomic potentials, [npj Comput. Mater. **11**, 9 (2025)](https://doi.org/10.1038/s41524-024-01500-6).

[5] T. Rensmeyer, D. Kramer, and O. Niggemann, On-the-fly fine-tuning of foundational neural network potentials: A Bayesian neural network approach, [Digital Discovery **5**, 1845 (2026)](https://doi.org/10.1039/D5DD00392J).

[6] H. Tahmasbi, A. Knüpfer, T. D. Kühne, and H. Mirhosseini, Benchmarking universal machine learning interatomic potentials on elemental systems, [npj Comput. Mater. **12**, 251 (2026)](https://doi.org/10.1038/s41524-026-02251-2).

[7] T. W. Ko, J. Bai, T. Swanick, Y. Kang, C. Choi, A. Q. Jiang, A. Yin, V. Bernales, and A. Aspuru-Guzik, El Agente Potente: High-throughput agentic atomistic simulations, [arXiv:2609.14840v1](https://arxiv.org/abs/2609.14840v1) (2026).

[8] A. H. Larsen et al., The atomic simulation environment—a Python library for working with atoms, [J. Phys.: Condens. Matter **29**, 273002 (2017)](https://doi.org/10.1088/1361-648X/aa680e).

[9] M. Uhrin, S. P. Huber, J. Yu, N. Marzari, and G. Pizzi, Workflows in AiiDA: Engineering a high-throughput, event-based engine for robust and modular computational workflows, [Comput. Mater. Sci. **187**, 110086 (2021)](https://doi.org/10.1016/j.commatsci.2020.110086).

[10] J. Grandel, P. Benner, and J. George, Targeted fine-tuning of machine-learning interatomic potentials for phonons and phase transitions, [npj Comput. Mater. **12**, 354 (2026)](https://doi.org/10.1038/s41524-026-02338-w).

[11] T. Rensmeyer, D. Kramer, and O. Niggemann, On-the-fly fine-tuning of foundational neural network potentials: A Bayesian neural network approach, [arXiv:2507.13805v1](https://arxiv.org/abs/2507.13805v1) (2025).
