# 출처와 확인 범위

근거 기준일: 2026-10-20. 원 강좌 주제는 공식 홈페이지·공개 세션 개요에서 확인했다. 과학 내용은 원 논문·저자 원고·공식 SDK 문서를 우선했다. 아래 목록은 길잡이이며 강의별 원문 링크와 설명이 함께 참고문헌을 구성한다. 원문·도표·강의 자료를 통째로 재배포하지 않는다.

## 원 강좌

- Daniel Justice, [CMU 17-620: Quantum Machine Learning, Fall 2026 Mini-2](https://thequantumturtle.github.io/courses/2026-Fall-17620/homepage/). 홈페이지와 12개 세션의 공개 개요를 확인했다. 웹 검색 도구의 일부 접근 실패를 공개 HTML 직접 열람으로 보완했다. 확인일 2026-10-20, 페이지 갱신 표시 2026-10-19. 비공개 Canvas 과제·영상·성적 기준은 확보하지 않았다.
- [강좌 소개 LinkedIn 게시물](https://www.linkedin.com/posts/daniel-justice-620b7841_can-quantum-computers-actually-make-machine-share-7518063313293987840-Bsee/). 원 강좌를 찾는 출발점이며 과학적 우위를 입증하는 근거로 사용하지 않았다.

## 기초·모델·미분

| 문헌 | 읽을 이유·확인 범위 |
|---|---|
| [IBM Quantum Learning: Basics of Quantum Information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/quantum-information) | 상태·측정·유니터리의 공식 교육 자료. 작은 예제는 별도로 유도 |
| [Lloyd, Mohseni, Rebentrost, quantum supervised/unsupervised learning (2013)](https://arxiv.org/abs/1307.0411) | 초기 군집 제안. oracle과 출력 가정 확인용 |
| [Kerenidis et al., q-means, NeurIPS 2019](https://arxiv.org/abs/1812.03584) | qRAM·정밀도·조건수·군집 조건. 초록의 복잡도와 서지 확인 |
| [Pérez-Salinas et al., Data re-uploading, Quantum 2020](https://arxiv.org/abs/1907.02085) | 재업로드·근사 능력. 초록 확인, 전체 정리 재증명 없음 |
| [Schuld, Sweke, Meyer, data encoding, PRA 2021](https://arxiv.org/abs/2008.08605) | Fourier 관점. 초록·공개 본문 검색 대조, 작은 회로 직접 전개 |
| [Schuld et al., analytic gradients, PRA 2019](https://arxiv.org/abs/1811.11184) | Parameter shift. 초록·본문 검색 대조, 특수 경우 직접 계산 |
| [Stokes et al., Quantum Natural Gradient, Quantum 2020](https://arxiv.org/abs/1909.02108) | 상태공간 계량. 정의 확인, 수렴 성능 독립 재현 없음 |

## 커널·학습 가능성·평가

| 문헌 | 읽을 이유·확인 범위 |
|---|---|
| [Havlíček et al., feature spaces, Nature 2019](https://arxiv.org/abs/1804.11326) | 실제 장치 proof of concept. 초록·출판 서지 대조 |
| [Huang et al., Power of data, Nature Communications 2021](https://www.nature.com/articles/s41467-021-22539-9) | 데이터·projected kernel·고전 비교. 본문 식과 discussion 확인 |
| [Thanasilp et al., kernel concentration, Nature Communications 2024](https://arxiv.org/abs/2208.11060) | 커널 집중의 조건. 초록·공개 본문 검색 확인 |
| [McClean et al., barren plateaus, Nature Communications 2018](https://www.nature.com/articles/s41467-018-07090-4) | 무작위 회로의 기울기 분산. 초록 확인, 노트의 product 예제는 자체 유도 |
| [Caro et al., generalization, Nature Communications 2022](https://www.nature.com/articles/s41467-022-32550-3) | 조건부 일반화 gap. 본문 framework·정리·discussion 확인 |
| [Bowles, Ahmed, Schuld, benchmarking (2024)](https://arxiv.org/abs/2403.07059v2) | 고전 기준선·튜닝의 역할. 초록 확인, 대규모 benchmark 재실행 없음 |
| [Cerezo et al., absence of plateaus and simulability, Nature Communications 2025](https://www.nature.com/articles/s41467-025-63099-6) | Perspective의 본문·예외 확인. 보편 불가능성 정리가 아님 |
| [Mele et al., non-unital noise and plateaus, Nature Physics 2026](https://www.nature.com/articles/s41567-026-03245-z) | 본문 Theorems 1, 5, 8·Proposition 3 확인. 국소 관측량·앙상블·정확도 조건 유지 |

## 양자 데이터·생성·내결함성

| 문헌 | 읽을 이유·확인 범위 |
|---|---|
| [Huang, Kueng, Preskill, classical shadows, Nature Physics 2020](https://www.nature.com/articles/s41567-020-0932-7) | 원 방법·서지 확인. 로컬 Pauli 예제는 직접 유도 |
| [Huang et al., learning from experiments, Science 2022](https://arxiv.org/abs/2112.00778) | 양자 데이터 접근·표본 우위. 초록·서지 확인, 장치 결과 독립 재현 없음 |
| [Tang, quantum-inspired recommendation, STOC 2019](https://arxiv.org/abs/1807.04271) | Sample-and-query 접근과 탈양자화. 입력 가정 구별 |
| [Liu and Wang, differentiable Born machine, PRA 2018](https://arxiv.org/abs/1804.04168) | 샘플 기반 생성 학습. 수식의 작은 예는 자체 구성 |
| [Harrow, Hassidim, Lloyd, linear systems, PRL 2009](https://arxiv.org/abs/0811.3171) | 해 상태·조건수·출력 비용. 전체 자원 추정 재현 없음 |
| [Gilyén et al., QSVT, STOC 2019](https://arxiv.org/abs/1806.01838) | Block encoding과 다항식 변환의 원문 |
| [Temme, Bravyi, Gambetta, error mitigation, PRL 2017](https://arxiv.org/abs/1612.02058) | 완화의 원 연구. 실습의 ZNE·분산은 별도 toy 계산 |
| [Quek et al., mitigation limitations, Nature Physics 2024](https://www.nature.com/articles/s41567-024-02536-7) | Worst-case 하한. 모든 현실 회로의 동일 비용을 뜻하지 않음 |

## 최신 선택 문헌

| 문헌·상태 | 이번 노트의 확인과 한계 |
|---|---|
| [Liu et al., photonic learning, Science 2025](https://arxiv.org/abs/2502.07770) | 최초 2025-02-11, 온라인 2025-09-25. 초록·논문 서지·공개 본문의 핵심 비교 조건 대조. 장치 재실행 없음 |
| [Lewis, Gilboa, McClean, shallow networks, Nature Communications 2026](https://www.nature.com/articles/s41467-025-68097-2) | 온라인 2025-12-31. 본문의 QSQ 접근·gradient/ correlational SQ 하한·미해결 범위 확인 |
| [Zhao et al., massive classical data, arXiv v2](https://arxiv.org/abs/2604.07639v2) | 최초 2026-04-08, v2 2026-10-01, 프리프린트. 초록·문제 설정·주 정리 서술·실자료 및 자원 설명 대조. 전체 169쪽 증명·공식 코드 독립 재현 없음 |
| [Cotler, Gong, Kannan, Noisy quantum learning theory, Nature Communications 2026](https://www.nature.com/articles/s41467-026-73693-x) | 온라인·VOR 날짜 구별. 잡음 인터페이스·허용 메모리·측정 설정의 조건 대조. 모든 학습의 불가능성으로 확대하지 않음 |
| [Kannan, Putterman, Cotler, fault-tolerant experiments, arXiv v2](https://arxiv.org/abs/2605.02057v2) | 최초 2026-05-03, v2 2026-09-06, 프리프린트. 즉시 부호화와 비교 기준·수치 사례 확인. 실제 내결함성 센서 실험이 아님 |

위 최신 연구를 포함했다고 해서 기준일의 모든 QML 논문을 검토한 것은 아니다. 저자의 보고, 노트의 해설, 후속 프로젝트 제안을 구별한다. 논문의 전체 증명이나 원 데이터를 독립 검증했다고 주장하지 않는다.

## 2.0 개정에서 추가 확인한 13–18강의 문헌

아래는 위 표의 기존 확인 범위를 보존하면서 추가한 독해 기록이다. ‘본문 확인’은 명시한 절·식·그림의 대조를 뜻하며 논문 전체 증명의 검증이나 장치·대규모 계산의 독립 재현을 뜻하지 않는다. 본문의 작은 회로, 분산, 패리티, 두 스핀 VMC와 block encoding 예제는 노트가 별도로 유도한 교육 자료다.

| 1차 문헌·연결 강의 | 2.0에서 확인한 위치와 한계 |
|---|---|
| [Huang, Kueng, Preskill, classical shadows 공개본](https://arxiv.org/html/2002.08953v2), 13강 | **Procedure**, **Rigorous performance guarantees**, <strong>Predicting expectation values of global observables (non-example)</strong>와 Supplementary **1 B, Example 2**를 대조했다. 측정 앙상블·shadow norm·관측량 locality가 표본 비용을 함께 정한다. 전체 정보이론적 하한 증명을 재검증하지 않았다. |
| [Tang, quantum-inspired recommendation 공개본](https://arxiv.org/html/1807.04271), 14강 | **2.2 Sampling**, **3 Data Structure**, **4.1 Vector Sampling**의 접근·구축 조건을 확인했다. 노트의 내적 불편 추정은 자체 교육 유도이며 추천 알고리즘 전체의 증명·실행을 대신하지 않는다. |
| [Cotler, Huang, McClean, Revisiting dequantization and quantum advantage in learning tasks](https://arxiv.org/abs/2112.00811), 14강 | 초록·서지에서 sample-and-query 접근과 양자 상태 복사본 입력의 비대칭을 확인했다. 학습 과제별 접근 모델을 구분하는 자료이며 모든 탈양자화 결과의 부정으로 사용하지 않는다. |
| [Liu, Wang, Differentiable Learning of Quantum Circuit Born Machine 공개본](https://arxiv.org/html/1804.04168), 15강 | **II Model and Learning algorithm**, **II.1 Quantum Circuit Architecture Design**의 Born 분포·표본 기반 손실·회전 규약을 확인했다. 노트의 두 큐비트 생성기와 MMD 표본 계산은 원 실험의 재현이 아니다. |
| [Rudolph et al., Trainability barriers and opportunities in quantum generative modeling](https://www.nature.com/articles/s41534-024-00902-0), npj Quantum Information 10, 116 (2024), 15강 | 초록·공개 본문 검색의 **Framework**, **Trainability analysis on loss functions**, **Discussion**에서 explicit·implicit 손실과 고차 상관의 식별 문제를 대조했다. 훈련 표본·측정 예산·손실 구조에 따른 조건부 결과이며 일반화 성공이나 모든 생성기의 불가능성을 보장하지 않는다. |
| [Huang et al., Generative quantum advantage for classical and quantum problems 공개본](https://arxiv.org/html/2509.09033), 2025-09-10 v1 프리프린트, 15강 | **Fig. 2** 설명과 **Appendix C.3**의 실험 설정을 확인했다. 새 68물리 큐비트 실험·816 shallow 큐비트 표현, 기존 결과에 근거한 34,304 shallow 규모의 추론을 구분했다. 816 규모 자체에 대한 저자의 beyond-classical 제한을 유지하며 대형 학습·샘플링을 독립 재현하지 않았다. |
| [Schatzki et al., Theoretical guarantees for permutation-equivariant quantum neural networks](https://www.nature.com/articles/s41534-024-00804-1), npj Quantum Information 10, 12 (2024), 16강 | 초록·공개 본문 검색의 **Definitions 2–3**, **Lemma 1**, **Theorem 1**, **Methods: Building S_n-equivariant operators**를 대조했다. 특정 생성자·측정·블록별 무작위화 조건을 모든 대칭 회로로 확대하지 않는다. 그래프 분류 수치 실험은 재실행하지 않았다. |
| [Wiersema et al., Geometric quantum machine learning with horizontal quantum gates 공개본](https://arxiv.org/html/2406.04418), Physical Review Research 7, 013148 (2025), 16강 | **II.3 Equivariant Quantum Gates**, **II.4 Horizontal Quantum Gates**, **III Starting from a symmetry: Homogeneous spaces**를 확인했다. 엄격한 교환 조건과 다른 설계의 구분을 읽었으며 원 논문의 최적화 성능·전체 기하학적 구성을 재현하지 않았다. |
| [Carleo, Troyer, Solving the Quantum Many-Body Problem with Artificial Neural Networks](https://arxiv.org/abs/1606.02318), Science 355, 602 (2017), 16강 | 서지·초록에서 신경망 파동함수의 변분 표현과 지정된 스핀계 적용을 확인했다. 노트의 VMC 식·두 스핀 손계산은 자체 유도이며 원문의 수치 정밀도·동역학 결과를 재현하지 않았다. |
| [Zaklama, Guerci, Fu, Attention-Based Foundation Model for Quantum States](https://arxiv.org/abs/2512.11962v2), v2 2026-06-17 프리프린트, 16강 | v2 날짜·초록의 입력 구성과 해밀토니안 매개변수·계 크기 사이의 상태 예측 목적을 확인했다. 전체 훈련·자료·모든 물질계에 대한 일반화를 검증하지 않았다. 고전 신경망으로 양자 상태를 표현하는 연구를 QPU 학습 결과와 구분한다. |
| [Gilyén et al., QSVT 공개본](https://arxiv.org/html/1806.01838), STOC (2019), 17강 | **1 Introduction**, **3.1 Quantum signal processing**, **3.2 Singular value transformation**의 구성과 공개 본문의 다항식 boundedness·parity 설명을 확인했다. 노트의 작은 block encoding은 직접 검산했으나 전체 QSVT 구성 증명·최적 선형계 복잡도·논리 자원 추정을 재현하지 않았다. |
| [Brassard et al., Quantum Amplitude Amplification and Estimation 공개본](https://arxiv.org/html/quant-ph/0005055), 17강 | **2 Quantum amplitude amplification**, **4 Quantum amplitude estimation**, **Theorem 12**의 coherent 준비·역연산, 쿼리 단위와 상수 성공확률 조건을 확인했다. 쿼리 개선을 짧은 샷 수나 실제 장치 총시간의 동일한 개선으로 바꾸어 적지 않는다. |
| [Liu et al., photonic learning 공개본](https://arxiv.org/html/2502.07770), 18강 | **Process reconstruction**, **Provable, scalable quantum advantage**, **Fig. 2·3**를 구분했다. 100모드 재구성의 11.8 orders 비교는 작은 모드 수 fit에서 외삽한 기준선이며, 별도 가설 검정의 entanglement-free 하한 비교와 같은 증거가 아니다. 원문 측정 자료·장치를 재현하지 않았다. |
| [Kannan, Putterman, Cotler, quantum uploading v2 공개본](https://arxiv.org/html/2605.02057v2), 17–18강 | **II.1 Surface-Code State Injection**, **II.2 Uploading and noisy quantum learning theory**, **III.1 Classical shadow tomography**, 비형식 **Theorem 2**와 보충 **S5**의 위치·범위를 확인했다. 18강의 완료 양식은 즉시 부호화·raw 비교와 잡음 조건을 적고, 완전한 정밀도·실패확률·상수 범위는 추가 확인 항목으로 남겼다. 기술 증명 전체와 천문 영상 수치 예시는 독립 재현하지 않았다. |

최근 논문 독해에서는 서지·초록 확인, 지정 본문 대조, 노트의 독립 손계산, 실제 실험 재현을 서로 다른 수준으로 기록했다. 최신 사례의 미확인 기술 가정은 18강 읽기 양식에 남기며, 노트에 익숙한 오차 척도나 비용식을 원 정리의 가정 대신 채워 넣지 않는다.

## 소프트웨어·그림·재현 자료

[PennyLane 공식 문서](https://docs.pennylane.ai/en/stable/)와 해당 [AmplitudeEmbedding](https://docs.pennylane.ai/en/stable/code/api/pennylane.AmplitudeEmbedding.html)·[RY](https://docs.pennylane.ai/en/stable/code/api/pennylane.RY.html) 규약을 확인했다. 실제 실행 버전과 고정 의존성은 실습 안내·결과 JSON을 따른다. API의 현재 문서와 설치 버전은 다를 수 있다.

코드·합성 데이터·손계산은 이 노트용 교육 예제다. 수식은 MathJax로 조판했고 교육용 그래프 3개는 본문의 해석식을 NumPy·Matplotlib로 계산했다. 물리 장치 사진·논문 도표를 가져오지 않았다. 생성 코드와 식·조건·버전 기록은 `artifacts/build_figures.py`와 `artifacts/figure-manifest.json`에 보존한다. 본문 글꼴은 Google Fonts 배포 Nanum Gothic의 OFL 허용 범위에서 별도 이름으로 subset하여 내장했고 라이선스를 배포본에 포함했다.

[목차](README.md)
