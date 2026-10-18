# 보고 성과와 검증 경계 그림

- 파일: `reported_results_boundaries.svg`, `reported_results_boundaries.png`
- 제작 스크립트: `build_evidence_figure.py` (matplotlib, Apple SD Gothic Neo, 1000 × 1100 px)
- 형식: 서로 다른 단위의 독립 3패널. 모든 수치축은 선형·0 시작. 패널 간 성능 순위나 공통 축을 만들지 않는다.
- 성격: 아래 논문에 보고된 값을 별도 도식으로 재작성한 원본 그림. 원 논문 그림을 복사하지 않았으며, 실험·학습·회로 합성·실기기 실행을 독립 재실행한 결과가 아니다.
- 원문 대조일: 2026-10-19.

## A. Anthropic / Gu 등의 가역 Gaussian 회로

- Primary: [Discovering state-of-the-art quantum circuits with large language models](https://arxiv.org/html/2610.22367v1), Table 1 및 SI III.3.
- 고정소수점 Gaussian 회로: Toffoli `24,000 → 1,583`, 최대 동시 논리 큐비트 `362 → 139`.
- 단위: Toffoli 게이트 수 및 논리 큐비트 수. 서로 독립된 작은 차트로 표현.
- 논문은 `TQ = Toffoli 수 × 최대 동시 논리 큐비트 수`의 39배 개선을 보고. 원시 값으로 계산한 `8,688,000 / 220,037 ≈ 39.48`에 대응하는 반올림된 값이다. 실제 QPU 실행시간이나 금전적 비용 배수가 아니다.
- 해당 benchmark의 절대오차 허용 기준 `< 10^-7`, 입력/출력 `39/39` 큐비트, 무작위 검사 `9,000`회는 원문의 Table 1에 명시. 그림은 자원 비교만 표시한다.

## B. DQAOA-GPT의 학습 후 생성·평가 시간

- Primary: [DQAOA-GPT: AI-Accelerated Distributed Quantum Optimization for Combinatorial Problems](https://arxiv.org/html/2607.20225v1), §III-E, §IV, Fig. 3.
- 원래 결정변수 `N = 100`, 부분문제 `n = 12`, DQAOA 반복 `T = 100`, 한 반복에 부분문제 `m = 1`.
- 기존 DQAOA `약 683.99초`, DQAOA-GPT `약 28초`. 28초는 논문 본문에서 근삿값으로 보고하므로 그림에도 ‘약’을 명시.
- 단일 NVIDIA H200 GPU에서 CUDA-Q/cuQuantum으로 양자회로를 모사한 결과. 실제 QPU 실행시간이 아니다.
- 생성기 쪽 시간은 그래프 투영·FEATHER 임베딩·토큰 생성·후보 회로 10개의 시뮬레이션·HUBO 에너지 평가를 포함하는 추론 파이프라인. 사전 데이터 생성과 모델 학습을 포함한 전체 개발 비용은 아니다.

## C. ADAPT-GQE Gemma 생성 회로의 장치 정확성

- Primary: [Learning to Prepare Molecular Ground States with Transformer Models](https://arxiv.org/html/2607.22468v1#S4.SS3), §4.3, Table 1.
- RL 미세조정 Gemma의 12큐비트·18연산자 회로. canonical two-qubit gates 1,440개를 pytket으로 244개까지 최적화.
- CASCI 대비 `E − E_CASCI` 오차: statevector 이상적 모사 `1.15 mHa`, Helios-1 실제 장치 `200.4 mHa`. 작은 값이 좋다.
- 실제 장치 에너지는 500 shots/회로 operator averaging 및 PMSV 대칭 검증을 적용. 보고 shot noise `18.1 mHa`, 폐기 비율 `48.74%`. 그림은 총에너지 오차를 막대로 표시하고 shot noise를 별도 주석으로 명시하여 총오차와 혼동하지 않는다.
- 이 비교는 모델의 회로 생성·평가 속도 배수와 다른 지표이며, 해당 회로 1개의 이상적 모사와 실기기 정확성 차이를 보여준다. 전체 12–16큐비트 연구의 평균이나 일반적인 모든 실기기 회로의 성능을 뜻하지 않는다.

## 시각 검토

- PNG를 `view_image`로 열어 한글, 값 라벨, 패널 독립성, 모든 막대의 0 시작, 여백, 잘림 여부를 확인했다. 라벨 중첩·잘림 없음. C의 작은 이상적 오차 막대에는 수치 라벨을 별도로 붙였다.
- SVG는 글자를 path로 내보내 게시 환경의 한글 폰트 유무와 무관하게 표시되도록 했다.
