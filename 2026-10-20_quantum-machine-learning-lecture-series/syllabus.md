# CMU 17-620 공개 실라버스와 독립 학습 시리즈의 대응

책임 편집: 김현중 · AI 보조: OpenAI Codex · 확인일: 2026-10-20 · [작성·검증 원칙](https://infant83.github.io/AI_Tech_Review/methods/)

## 어떤 강좌인가

사용자가 제공한 [LinkedIn 단축 링크](https://lnkd.in/p/gjMVib4j)는 Daniel Justice의 [강좌 소개 게시물](https://www.linkedin.com/posts/daniel-justice-620b7841_can-quantum-computers-actually-make-machine-share-7518063313293987840-Bsee/)로 연결된다. 게시물 안의 강좌 링크를 따라 [The Quantum Turtle의 공식 강좌 홈페이지](https://thequantumturtle.github.io/courses/2026-Fall-17620/homepage/)와 세션별 공개 개요 12개를 확인했다. 검색 결과에 함께 나오는 11-860 및 과거 연도 강좌는 이번 수업과 구별했다.

| 항목 | 공개 페이지에서 확인한 내용 |
|---|---|
| 강좌 | Carnegie Mellon University, 17-620: Quantum Machine Learning |
| 담당 | Daniel Justice, Rita Singh |
| 학기 | Fall 2026, Mini-2 |
| 기간 | 2026-10-20–2026-12-03 |
| 수업 | 화·목 08:00–09:20 미국 동부 현지시간, 대면 |
| 분량 | 6 units, 강의 7회·실습 5회, 각 80분으로 총 16시간 |
| 핵심 도구 | PennyLane; 공개 개요에 Qiskit·Cirq·TensorFlow Quantum·Braket도 언급 |
| 목표 | 양자 학습 모델의 구현, 인코딩·군집·분류, 실제 장치 비교, 잡음과 완화의 효과·한계 |
| 공개 범위 | 홈페이지의 시간표와 각 세션의 주제 개요. 과제·추가 공지는 Canvas로 안내 |

미국 동부는 이 기간 중 서머타임이 바뀐다. 한국 시각은 10월 수업 21:00–22:20, 11월 5일 이후 수업 22:00–23:20에 해당한다. 이것은 시간대 변환 설명이며 원격 수강 가능 여부를 확인했다는 뜻이 아니다. 공개 Zoom·Canvas·Piazza 주소와 접속 정보는 이 배포본에 옮기지 않았다.

페이지의 마지막 갱신 표시는 2026-10-19다. 다음 표는 2026-10-20에 확인한 계획이며 실제 진행·향후 변경을 보증하지 않는다. 강의 영상·슬라이드·비공개 과제에 접근하거나 수업을 청강하지 않았다. 성적 배점과 공식 선수 과목은 확보한 페이지에서 확인하지 못해 만들지 않았다.

## 원 강좌의 세션별 계획

아래 내용은 공개 항목을 간결하게 한국어로 요약한 것이다. 상세 유도·연습·코드는 원 수업을 복제하지 않고 이 시리즈에서 새로 작성했다. 기존 URL slug가 화면 제목과 다른 경우에는 현재 화면의 제목·날짜를 우선했다.

| 날짜 | 구분·공개 세션 | 확인한 주제의 요약 | 우리 노트 |
|---|---|---|---|
| 10-20 | [Lecture 1: Foundations 1](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/1-Introduction/) | 큐비트·Bloch 구·게이트·측정 | 02 |
| 10-22 | [Lab 1: PennyLane Fundamentals](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/2-Pennylane/) | 환경·회로·미분·Bell 실험 | 02–03, 07, 실습 1 |
| 10-27 | [Lecture 2: Foundations 2](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/3-Foundations-ML-QC/) | 얽힘·보편 게이트·복제 불가·SDK | 03 |
| 10-29 | [Lecture 3: Encoding and k-means](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/4-QC-Algos-ML-Basics/) | 인코딩·적재 비용·군집 복잡도 | 04–05 |
| 11-03 | 휴강 | Democracy Day | — |
| 11-05 | [Lecture 4: Perceptrons, MLPs, QNNs](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/5-Data-Encoding/) | 고전 신경망·하이브리드·재업로드·표현력 | 06–07 |
| 11-10 | [Lab 2: Encoding and k-means](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/6-Classical-SVM-NN/) | 작은 군집 실험·고전 비교 | 실습 2 |
| 11-12 | [Lab 3: Hardware and Benchmarking](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/7-Hybrid-QC-ML/) | QPU 실행·샷·대기·시간·에너지 | 10–11, 실습 4 |
| 11-17 | [Lecture 5: Linear and Variational Classifiers](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/8-QML-Optimization-Sampling/) | 분류·최적화·커널·학습 가능성 | 07–10 |
| 11-19 | [Lab 4: VQC in PennyLane](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/9-QSVM-Practical/) | 변분 모델·자동미분·MLP 비교 | 실습 3 |
| 11-24 | [Lecture 6: Hardware 1](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/10-QNN-Practical/) | 큐비트 구현·프로세서 비교·에너지 | 11 |
| 11-26 | 휴강 | Thanksgiving | — |
| 12-01 | [Lab 5: Noise and Mitigation](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/11-Guest/) | 잡음·깊이·샷·ZNE·측정 보정 | 12, 실습 5 |
| 12-03 | [Lecture 7: Hardware 2](https://thequantumturtle.github.io/courses/2026-Fall-17620/syllabus/12-Thanksgiving/) | 오류·완화와 정정·장치 지표 | 11–12 |

원강좌 Lab 3은 IBM Quantum·IonQ·Rigetti 및 Braket 경로를 언급한다. 해당 플랫폼 이용권·과금·현재 connector 지원을 우리가 확보했다는 뜻은 아니다. 원강좌 Lab 4는 PyTorch 또는 JAX와의 결합 및 MLP 비교를 제안한다. 우리의 필수 실습은 설치 부담이 적은 NumPy 참조 구현과 고전 RBF·삼각 특징 기준선을 사용하므로 공식 Lab 4의 과제를 동일하게 수행한 것이 아니다.

## 우리가 추가한 내용

원 계획의 세션을 그대로 18회라고 늘려 부르지 않는다. 공개 주제를 02–12강에서 더 작은 개념 단위로 풀고, 준비 강의 01과 연구 확장 13–18을 붙였다. 그 결과는 다음과 같은 독립 커리큘럼이다.

| 부분 | 범위 | 원 계획과의 관계 |
|---|---|---|
| 준비 | 01: 학습 문제·입출력·우위의 자원 정의 | 우리 추가 |
| 기초와 모델 | 02–06: 상태·얽힘·인코딩·군집·QNN | 원 강의 1–4를 보충 |
| 훈련과 검증 | 07–12: 미분·커널·plateau·일반화·장치·잡음 | 원 강의 5–7을 보충 |
| 연구 확장 | 13–18: 양자 데이터·우위·생성·대칭·내결함성·최신 논문 | 원 실라버스 밖의 우리 추가 |
| 실습·연구 | 자체 실습 5개와 프로젝트 3개 | 원 실습 주제를 참고한 별도 설계 |

원 페이지가 소개하는 도서명은 *Practical Quantum Machine Learning and Quantum Optimization*, *Machine Learning with Quantum Computers*, *A Gentle Introduction to Quantum Computing*이다. 공개 페이지의 도서 표기와 모든 연결 파일의 서지 일치까지 검증한 것은 아니며, 강의별 핵심 주장은 별도로 확인한 원 논문·공식 문서를 인용한다.

## 보존과 갱신

원강좌의 변경 이력과 우리 노트의 개정을 별도로 기록한다. 새 주제를 추가할 때에는 논문의 최초 공개일·채택본·수정일을 구별하고, 근거 기준일 뒤의 결과를 이번 판에 섞지 않는다. 이 문서의 원 페이지 대조는 Codex가 수행했으며 사람의 문장 단위 검토는 아직 받지 않았다.

[전체 목차](README.md) · [학습 안내](study-guide.md)
