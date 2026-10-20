# 한영 용어집: 정의, 사용 예와 혼동하기 쉬운 말

2.0판의 용어집이다. 한국어 번역 하나를 외우기보다 **대상을 나타내는 말인지, 계산 방법인지, 오차나 자원을 나타내는 말인지** 먼저 확인한다. 영어 원어·약어를 함께 실어 논문에서도 찾을 수 있게 했다. 같은 기호가 문헌마다 달라질 수 있으며, 아래 정의와 각 강의의 명시적인 규약을 우선한다. 식의 계산이 막히면 [수학 보충편](math-primer.md)으로 돌아간다.

144개 항목은 해당 용어를 처음 이해하기 위한 설명이다. 모든 용례를 포괄하는 사전이나 새로운 연구 결과의 주장은 아니다. 각 묶음 끝의 강의에서 정의를 사용해 직접 계산한다. 특정 알고리즘의 효율·일반화·우위는 정의만으로 따라오지 않는다.

## A. 복소수와 선형대수

### G001. 스칼라·벡터 — scalar, vector

스칼라는 수 하나, 벡터는 정해진 기저에서 여러 성분을 갖는 대상이다. 예를 들어 \(x\in\mathbb R^d\)는 d개 실수 특징을 모은다. 벡터의 차원 d와 데이터 표본 수 N은 다른 축이다.

### G002. 복소수·켤레 — complex number, complex conjugate

\(z=a+ib\), \(i^2=-1\)이고 켤레는 \(z^*=a-ib\)다. \(|z|^2=z^*z\)는 음수가 아닌 실수다. \(z^2\)와 \(|z|^2\)는 다르며 양자 확률에는 후자를 사용한다.

### G003. 내적 — inner product

두 복소 열벡터의 내적은 \(u^\dagger v\)다. 방향의 겹침을 수로 나타내며 0이면 직교한다. 첫 인자의 켤레를 빠뜨리는 단순 전치 곱은 복소 공간의 내적이 아니다.

### G004. 노름·정규화 — norm, normalization

\(\|v\|_2=\sqrt{v^\dagger v}\)는 벡터 크기다. 영벡터가 아니면 \(v/\|v\|_2\)로 단위 길이를 만든다. 정규화는 크기를 지우므로 원 데이터의 norm이 정답을 결정한다면 별도 보존이 필요하다.

### G005. 외적 — outer product

\(uv^\dagger\)는 행렬이며 내적처럼 스칼라가 아니다. 정규화한 v의 \(vv^\dagger\)는 그 방향으로의 projector다. 두 벡터를 단순 이어 붙인 배열과도 다르다.

### G006. 텐서곱 — tensor product

복합계를 나타내는 곱이다. 길이 m과 d의 벡터는 길이 md의 \(u\otimes v\)가 된다. 차원을 더하는 직합이나 성분별 곱과 구별한다. 모든 복합 상태가 단일 텐서곱으로 분리되지는 않는다.

### G007. 기저·직교정규 — basis, orthonormality

기저는 공간의 모든 벡터를 표현하는 독립 방향들의 집합이다. 각 길이가 1이고 서로 내적이 0이면 직교정규다. 기저를 바꿔도 물리 상태는 같을 수 있지만 측정의 의미는 함께 변환해야 한다.

### G008. 켤레전치·adjoint — conjugate transpose

\(A^\dagger=(A^*)^T\)는 성분을 켤레 처리하고 행·열을 바꾼다. 행렬의 adjoint가 항상 역행렬인 것은 아니다. 유니터리일 때에만 \(U^{-1}=U^\dagger\)다.

### G009. 에르미트 — Hermitian

\(A=A^\dagger\)인 행렬이다. 고유값은 실수이며 관측량을 나타낸다. 실수 대칭 행렬은 특수한 예다. 에르미트라는 조건만으로 PSD이거나 게이트의 유니터리 조건을 만족하지는 않는다.

### G010. 유니터리 — unitary

\(U^\dagger U=I\)여서 내적과 norm을 보존하는 정사각 행렬이다. 닫힌 계의 가역 게이트가 이에 해당한다. 측정이나 환경을 버리는 잡음 채널 전체를 같은 크기의 유니터리 하나로 표현할 수는 없다.

### G011. 양의 준정부호 — positive semidefinite, PSD

에르미트 A에서 모든 z에 대해 \(z^\dagger Az\ge0\)인 조건이다. 고유값은 모두 0 이상이다. 대각이 양수인 것만으로 충분하지 않으며, PSD 행렬도 0 고유값 때문에 역행렬이 없을 수 있다.

### G012. 고유분해·trace·교환자 — eigendecomposition, trace, commutator

에르미트 행렬은 고유값과 projector의 합으로 분해한다. trace는 대각합이며 고유값의 합과 같다. \([A,B]=AB-BA\)는 연산 순서의 차이다. trace의 순환성은 임의의 두 행렬을 교환해도 된다는 뜻이 아니다.

**사용:** [수학 P1–P4](math-primer.md), [02강](lectures/02-qubits-gates-and-measurement.md), [03강](lectures/03-entanglement-and-circuits.md).

## B. 양자 상태와 측정

### G013. Ket·bra — Dirac notation

\(|\psi\rangle\)는 열벡터, \(\langle\psi|\)는 그 켤레전치다. \(\langle\phi|\psi\rangle\)는 내적, \(|\psi\rangle\langle\phi|\)는 외적이다. 꺾쇠의 방향은 장식이 아니라 행렬의 shape를 알려준다.

### G014. 진폭·Born 규칙 — amplitude, Born rule

순수 상태의 기저 성분이 진폭이며, 해당 기저 측정의 확률은 그 절댓값 제곱이다. 진폭은 음수·복소수일 수 있지만 확률은 그럴 수 없다. 측정 한 번으로 진폭 전체를 읽지는 못한다.

### G015. 전역 위상·상대 위상 — global phase, relative phase

전체 상태에 같은 \(e^{i\gamma}\)를 곱한 전역 위상은 관측 확률을 바꾸지 않는다. 성분 사이 상대 위상은 간섭을 바꿀 수 있다. v와 -v가 같은 양자 상태여도 두 원 데이터가 같은 label을 갖는 것은 아니다.

### G016. 중첩·코히런스 — superposition, coherence

중첩은 기저벡터의 선형결합이다. 특정 기저에서 밀도행렬의 비대각 성분은 coherence를 나타낸다. 코히런스는 선택한 기저와 관련하며, 확률적으로 두 상태를 섞는 고전적 혼합과 다르다.

### G017. 밀도행렬·순수·혼합 — density matrix, pure state, mixed state

상태 \(\rho\)는 PSD이고 trace 1이다. 순수하면 \(\rho=|\psi\rangle\langle\psi|\), 혼합이면 rank가 더 클 수 있다. 같은 \(\rho\)를 만드는 순수 상태의 확률적 분해는 유일하지 않다.

### G018. Bloch 벡터 — Bloch vector

한 큐비트의 \(\rho=(I+r_xX+r_yY+r_zZ)/2\)에서 r은 세 Pauli 평균이다. 물리 상태는 \(\|r\|\le1\), 순수 상태는 경계에 있다. 구의 좌표를 실제 입자의 공간 위치로 해석하지 않는다.

### G019. 축소 상태·부분 trace — reduced state, partial trace

복합 상태에서 일부 계만의 예측을 주는 상태다. \((\rho_A)_{aa'}=\sum_b\rho_{ab,a'b}\)처럼 버리는 계 인덱스를 합한다. 큰 행렬의 특정 block만 자르는 연산이 아니다.

### G020. 얽힘·Schmidt rank — entanglement, Schmidt rank

순수 복합 상태가 하나의 곱 상태로 쓰이지 않으면 얽혔다. Schmidt 분해의 양의 계수 개수가 2 이상이면 순수 상태의 얽힘이 있다. 혼합 상태에서는 곱 상태들의 확률적 혼합으로 표현 가능한지도 보아야 한다.

### G021. 관측량·기댓값 — observable, expectation value

관측량 O는 측정 결과 숫자의 규칙이며 평균은 \(\operatorname{Tr}(O\rho)\)다. 평균은 단일 측정 결과와 다를 수 있다. Z 평균 0은 결과가 0이었다는 뜻이 아니라 ±1 결과가 평균적으로 상쇄된다는 뜻이다.

### G022. 사영 측정·POVM — projective measurement, positive operator-valued measure

사영 측정은 서로 직교하는 projector들로, 일반 POVM은 양의 effect들 \(E_a\)와 \(\sum_aE_a=I\)로 정의한다. \(p(a)=\operatorname{Tr}(E_a\rho)\)다. POVM 효과만으로 측정 후 상태까지 유일하게 정해지지는 않는다.

### G023. 충실도·순도·trace distance — fidelity, purity, trace distance

순수 두 상태의 fidelity는 내적 절댓값 제곱이다. 일반 상태의 squared fidelity 규약은 \((\operatorname{Tr}\sqrt{\sqrt\rho\sigma\sqrt\rho})^2\)다. purity는 \(\operatorname{Tr}\rho^2\), trace distance는 \(\|\rho-\sigma\|_1/2\)다. 서로 다른 양이며 문헌의 fidelity 제곱 관례도 확인한다.

### G024. 계산 기저·wire 순서 — computational basis, wire order

계산 기저는 비트열로 붙인 직교정규 기저다. 본 노트 두 큐비트는 00,01,10,11 순서다. SDK의 bitstring 표시·endianness는 다를 수 있어, 회로 그림의 wire와 배열 인덱스를 먼저 대응시킨다.

**사용:** [02강](lectures/02-qubits-gates-and-measurement.md), [03강](lectures/03-entanglement-and-circuits.md), [13강](lectures/13-quantum-data-and-shadows.md).

## C. 확률·통계와 실험 오차

### G025. 확률변수 — random variable

무작위 결과에 숫자를 대응시킨 대상이다. 비트 B를 0/1로 세는 것과 \(Z=1-2B\)로 ±1을 세는 것은 같은 사건을 다른 숫자로 코딩한 것이다. 평균·분산도 이 변환에 맞춰 바뀐다.

### G026. 독립 동일분포 — independent and identically distributed, i.i.d.

표본들이 서로 독립이고 같은 분포를 따르는 가정이다. 시간에 따른 calibration drift가 있으면 어긋날 수 있다. 행이 여러 개라는 사실만으로 독립 표본이라고 할 수는 없다.

### G027. 추정량·실현값 — estimator, estimate

추정량은 데이터에 적용하는 통계적 규칙으로 무작위변수다. 관측 후 얻은 구체적인 숫자는 그 실현값이다. 하나의 결과가 참 값에 가깝다는 사실만으로 추정량이 불편하다고 결론내리지 않는다.

### G028. 편향 — bias

추정량 T의 bias는 \(\mathbb ET-\theta\)다. 표본 수를 늘리면 사라지는 경우도 있지만 장치·모형 불일치 때문에 남을 수도 있다. 통계적 bias와 사회적 편향, 모델의 inductive bias는 같은 개념이 아니다.

### G029. 분산 — variance

\(\operatorname{Var}(T)=\mathbb E(T-\mathbb ET)^2\)는 평균 주위의 흔들림이다. 평균이 참 값과 얼마나 떨어져 있는지는 직접 말하지 않는다. 분산이 작은데도 bias가 큰 추정량이 가능하다.

### G030. 표준편차·표준오차 — standard deviation, standard error

SD는 분포의 분산 제곱근, SE는 추정량의 SD다. i.i.d. 평균의 SE는 개별 결과 SD를 \(\sqrt S\)로 나눈 값이다. seed 사이 SD를 그대로 95% 신뢰구간이라고 표시하면 안 된다.

### G031. 신뢰구간 — confidence interval, CI

정해진 반복 표집 절차에서 참 값을 포함하는 비율을 제어하는 구간이다. 보통의 \(\widehat\theta\pm1.96\,SE\)는 정규 근사가 필요하다. 소표본·경계 확률이나 상관 표본에서는 별도 처리가 필요하다.

### G032. 농축 부등식 — concentration inequality

표본 평균 등이 기대값에서 멀어질 확률을 제한한다. Hoeffding은 독립 bounded 변수에 적용되는 예다. 데이터 상관이나 관측값 범위 조건을 뺀 채 샷 수 보장만 가져오지 않는다.

### G033. MSE·RMSE — mean squared error, root mean squared error

참 값 대비 제곱 오차의 평균과 그 제곱근이다. \(MSE=variance+bias^2\)다. 오류 완화의 성능을 분산만으로 판단하면 bias 감소의 효과를 놓칠 수 있고, 평균만 보면 분산 비용을 놓친다.

### G034. 공분산 — covariance

\(\operatorname{Cov}(A,B)=\mathbb E[(A-\mathbb EA)(B-\mathbb EB)]\)는 두 추정량의 공동 변동이다. 같은 샷·같은 calibration을 재사용하면 생길 수 있다. 합의 분산을 계산할 때 독립성을 확인하지 않고 이 항을 버리면 안 된다.

### G035. Bootstrap — 재표집 불확실성 추정

관측 자료를 다시 뽑아 통계량의 변동을 근사하는 방법군이다. 무엇을 단위로 재표집하는지가 중요하다. shots만 다시 뽑으면 고정한 calibration의 불확실성이나 환자 간 변동을 포함하지 못한다.

### G036. 짝지은 비교 — paired comparison

같은 테스트 표본에 대한 두 모델 결과의 차이를 분석한다. 각 표본에서 정오가 함께 변하므로 두 독립 비율의 오차식보다 공분산을 포함하는 접근이 적절할 수 있다. 차이를 본 뒤 유리한 검정만 고르지 않는다.

**사용:** [수학 P6](math-primer.md), [07강](lectures/07-gradients-and-training.md), [10강](lectures/10-generalization-and-benchmarking.md), [12강](lectures/12-noise-and-mitigation.md).

## D. 머신러닝의 문제 정의

### G037. 특징·정답 — feature, label, target

특징 x는 모델에 주는 입력 표현이고, y는 학습 목표다. Label은 주로 분류 범주를 뜻하며 target은 회귀값 등도 포함한다. 사람이 만든 전처리 특징과 모델이 학습한 내부 특징도 구별한다.

### G038. 표본·분포 이동 — sample, distribution shift

표본은 관측한 개별 데이터이고 분포는 데이터를 만드는 규칙이다. 훈련과 배포의 분포가 다르면 distribution shift다. 같은 벤치마크 테스트 점수가 새로운 실험실·장치·모집단에 그대로 적용되지는 않는다.

### G039. 가설 공간·모델 — hypothesis class, model

학습기가 선택할 수 있는 함수들의 집합과 그 중 특정 함수다. 같은 파라미터 수여도 함수 집합은 다를 수 있다. 회로가 표현 가능한 함수와 최적화기가 실제로 찾는 함수도 구별한다.

### G040. 손실·위험 — loss, risk

손실은 한 예측을 평가하는 규칙, 위험은 그 손실의 분포 평균이다. 정확도와 cross-entropy는 다른 평가량이다. 낮은 한 종류 손실이 모든 지표의 개선을 보장하지 않는다.

### G041. 경험 위험 최소화 — empirical risk minimization, ERM

관측한 훈련 표본의 평균 손실을 최소화하는 원리다. 수치 최적화는 근사해만 찾을 수 있다. 경험 위험이 작아졌다고 새 표본의 모집단 위험도 작다는 결론은 자동으로 나오지 않는다.

### G042. 일반화 차이 — generalization gap

같은 모델의 모집단 위험과 경험 위험 차이다. 작은 gap은 작은 훈련 손실이나 우수한 절대 성능을 뜻하지 않는다. 훈련·모집단 모두 나쁜 상수 모델도 gap은 작을 수 있다.

### G043. 근사·추정·최적화 오차 — approximation, estimation, optimization error

선택한 함수 집합의 한계, 유한 데이터의 한계, 탐색의 한계를 나눈다. 엄밀한 분해·상계의 형태는 정리에 따라 다르다. 여기에 측정 샷 오차와 장치 bias도 구별해 기록한다.

### G044. 훈련·검증·시험 — train, validation, test

파라미터 학습, 설정 선택, 선택 이후 평가에 각각 사용한다. Test를 반복 조회해 설정을 바꾸면 사실상 validation으로 사용한 것이다. 데이터가 적을 때는 적절한 교차검증 설계를 따로 정한다.

### G045. 데이터 누수 — data leakage

평가 때만 알아야 할 정보가 학습·모델 선택으로 들어오는 일이다. 전체 자료로 scaling을 맞춘 뒤 나누는 것도 사례다. 환자·분자·시간 등 상관 단위의 누수도 확인한다.

### G046. 규제·정규화 — regularization

학습 목적이나 함수 공간에 제약·penalty를 넣는 방법이다. Ridge의 \(\lambda\|w\|^2\)가 예다. 벡터 길이를 1로 만드는 normalization과 한국어 번역이 겹칠 수 있어 영어와 식을 확인한다.

### G047. 하이퍼파라미터 — hyperparameter

학습률·층 수·kernel 폭처럼 바깥 절차에서 고르는 설정이다. 학습 변수 θ와 같은 방식으로 취급하지 않을 수 있다. 탐색 횟수와 데이터 조회 비용도 비교 예산에 넣는다.

### G048. 귀납 편향 — inductive bias

관측하지 않은 입력에서 어떤 함수를 선호할지 정하는 구조적 가정이다. 국소성·대칭·주파수 제한이 예다. 가정이 문제와 맞으면 유리하지만 잘못 맞추면 정답을 표현하지 못할 수 있다.

**사용:** [01강](lectures/01-learning-problems-and-quantum-claims.md), [10강](lectures/10-generalization-and-benchmarking.md).

## E. 인코딩과 커널 방법

### G049. 기저 인코딩 — basis encoding

고전 비트열 b를 \(|b\rangle\)로 준비한다. 실수에는 precision·부호 표현을 정해야 한다. 무한 정밀도 숫자 하나를 큐비트 하나에 고전적으로 그대로 읽을 수 있는 방식이 아니다.

### G050. 각도 인코딩 — angle encoding

특징값을 회전 게이트의 각도로 보낸다. 예를 들어 \(R_y(x_j)\)를 쓴다. 주기적 중첩과 scaling이 geometry를 바꾸므로 원 데이터의 유클리드 거리와 같다고 가정하지 않는다.

### G051. 진폭 인코딩 — amplitude encoding

정규화한 벡터 성분을 상태의 진폭으로 쓴다. d차원 표현에는 \(\lceil\log_2d\rceil\)큐비트가 충분할 수 있다. 일반 입력의 준비 비용, norm과 전역 부호 손실을 별도로 다뤄야 한다.

### G052. 상태 준비·qRAM — state preparation, quantum random access memory

원하는 입력 상태를 만드는 물리·논리 과정과 coherent 주소 접근 메모리 개념이다. Python 배열 생성이나 classical RAM 조회와 같은 기능이 아니다. 초기 적재·업데이트·오류 비용을 명시한다.

### G053. 특징 사상 — feature map

입력 x를 다른 표현 \(\phi(x)\)로 보내는 규칙이다. 양자에서는 상태나 density operator를 특징으로 삼는다. 특징 공간이 크다는 사실만으로 좋은 label 구조나 계산 우위가 생기지는 않는다.

### G054. 커널·Gram 행렬 — kernel, Gram matrix

커널은 입력 쌍의 유사도를 주는 함수다. 표본들에 대해 \(K_{ij}=k(x_i,x_j)\)를 모은 것이 Gram 행렬이다. 머신러닝의 PSD kernel과 운영체제 kernel은 다른 용어다.

### G055. PSD 커널 — positive semidefinite kernel

어떤 유한 표본 집합에서도 Gram 행렬이 PSD인 커널이다. 내적 \(k(x,z)=\langle\phi(x),\phi(z)\rangle\)으로 구성하면 이 성질을 갖는다. 유한 샷으로 원소별 추정한 행렬까지 항상 PSD인 것은 아니다.

### G056. 재생 커널 Hilbert 공간 — reproducing kernel Hilbert space, RKHS

함수값 평가가 커널 내적으로 표현되는 함수 공간이다. 첫 인자에 켤레를 취하는 이 노트의 내적 관례에서는 평가 원소 \(k_x\)에 대해 \(f(x)=\langle k_x,f\rangle\)라는 재생 성질을 가진다. 커널을 \(k(x,z)=\langle k_x,k_z\rangle\)로 쓰면 함수로서 \(k_x(t)=k(t,x)\)다. 양자 상태 Hilbert 공간과 관련시킬 수 있지만 같은 대상이라고 무조건 동일시하지 않는다.

### G057. RBF 커널 — radial basis function kernel

대표적으로 \(e^{-\gamma\|x-z\|^2}\)를 쓴다. γ는 유사도가 줄어드는 길이 척도를 정한다. γ가 너무 크면 거의 단위행렬, 너무 작으면 거의 상수 행렬이 되어 학습의 성질이 달라진다.

### G058. SVM·마진 — support vector machine, margin

분류 경계와 표본 사이의 여유를 제어하는 학습법이다. Soft-margin은 일부 위반을 penalty와 절충한다. Feature map이 복잡해도 고전 최적화 문제가 볼록일 수 있으며 kernel 추정 비용은 별도로 남는다.

### G059. Hinge loss·쌍대 문제 — hinge loss, dual problem

이진 label ±1에서 hinge는 \(\max(0,1-yf(x))\)다. SVM 쌍대는 표본 계수와 Gram 행렬로 최적화를 쓴다. 쌍대식의 C·손실 정규화 규약을 코드와 맞춘다.

### G060. Kernel ridge·PSD projection — kernel ridge regression, PSD projection

Kernel ridge는 제곱 손실과 규제를 사용하며 SVM과 다르다. 추정 Gram의 음의 고유값을 잘라 PSD로 만드는 처리는 학습 규칙을 바꾼다. 보정이 수치적으로 유용해도 원래 추정량의 불편성을 그대로 보존하지는 않는다.

**사용:** [04강](lectures/04-data-encoding-and-loading.md), [05강](lectures/05-quantum-kmeans-and-distances.md), [08강](lectures/08-kernels-and-svm.md).

## F. 변분 모델과 최적화

### G061. Ansatz·매개변수화 회로 — ansatz, parameterized quantum circuit, PQC

탐색할 상태·연산의 구조를 미리 정하고 연속 파라미터를 넣은 회로다. Ansatz는 검증된 정답이라는 뜻이 아니라 선택한 함수 집합이다. 관측량에 보이지 않는 파라미터가 있을 수도 있다.

### G062. QNN·VQC — quantum neural network, variational quantum classifier

QNN은 양자 학습 모델의 넓은 이름이고 VQC는 변분 회로를 쓰는 분류기다. 고전 신경망의 모든 neuron·활성함수와 일대일 대응하지 않는다. 실제 함수·측정·고전 head를 식으로 적는다.

### G063. 하이브리드 모델 — hybrid quantum–classical model

양자 처리와 고전 처리를 함께 쓰는 모델이다. 양자 기대값 뒤의 logistic head와 고전 optimizer가 예다. 데이터 변환·loss·측정·업데이트 전체가 모델과 비용의 일부다.

### G064. 데이터 재업로드 — data re-uploading

학습 게이트 사이에 데이터를 여러 번 넣는다. 접근 주파수 집합이 커질 수 있으며 같은 축의 \(R_y(x)\)도 L번 반복하면 \(R_y(Lx)\)가 된다. 입력 업로드를 추가하지 않고 같은 축의 학습 게이트만 더하면 합각으로 축약되어 독립 학습 자유도가 늘지 않을 수 있다.

### G065. 표현력·학습 가능성 — expressivity, trainability

표현력은 담을 수 있는 함수·상태 범위, 학습 가능성은 정해진 자료·측정·최적화 예산에서 적절한 해를 찾을 수 있는 성질이다. 보편 근사 정리가 효율적인 학습 알고리즘을 자동 제공하지는 않는다.

### G066. 식별 가능성 — identifiability

서로 다른 파라미터가 서로 다른 관측 예측을 만드는지에 관한 성질이다. 동일 예측을 내는 θ들이 있으면 데이터만으로 구별하기 어렵다. 파라미터 수와 유효 자유도가 항상 같지는 않다.

### G067. 연쇄 법칙 — chain rule

합성 함수의 미분을 연결하는 규칙이다. \(L=\ell(f_\theta)\)에서 \(\nabla L=\ell'(f)\nabla f\)다. 양자 회로의 기울기만 계산한 뒤 고전 loss 미분을 빼먹으면 다른 갱신이 된다.

### G068. Parameter-shift rule — 매개변수 이동 규칙

특정 생성자 스펙트럼에서 shifted 회로들의 기대값으로 미분을 정확히 표현한다. Pauli 회전 한 번이면 ±π/2의 두 항이 대표적이다. 공유 변수가 여러 게이트에 나타나면 단순 동시 이동이 일반적으로 성립하지 않는다.

### G069. 유한차분·역전파 — finite differences, backpropagation

유한차분은 작은 변화의 함수 차이로 미분을 근사하고, 역전파는 계산 그래프의 chain rule을 역방향으로 계산한다. 시뮬레이터의 역전파가 물리 QPU에서 동일한 비용으로 가능한 것은 아니다.

### G070. SGD·Adam·SPSA — stochastic optimization

SGD는 잡음 있는 기울기를 쓰고 Adam은 모멘트 추정을 이용한다. SPSA는 두 함수 평가로 무작위 방향을 추정한다. 평가 두 번이라는 사실이 모든 좌표의 정확한 미분을 동시에 얻는다는 뜻은 아니다.

### G071. 양자 자연 기울기·QFI — quantum natural gradient, quantum Fisher information

파라미터 좌표보다 상태의 구별 가능성에 맞춘 계량을 사용한다. 순수 상태에서는 Fubini–Study 계량과 QFI가 관례에 따른 상수배 관계를 가진다. 계량 추정·정규화·선형계 비용도 든다.

### G072. Barren plateau·2-design — 기울기 집중과 무작위 회로 조건

정해진 회로·초기화 분포에서 기울기 분산이 크기에 따라 매우 작아지는 현상이다. 2-design은 Haar 분포의 특정 2차 모멘트를 재현하는 앙상블이다. 단일 정상점의 영 기울기나 모든 깊은 회로를 같은 현상으로 부르지 않는다.

**사용:** [06강](lectures/06-qnn-and-expressivity.md), [07강](lectures/07-gradients-and-training.md), [09강](lectures/09-trainability-and-barren-plateaus.md).

## G. 장치와 자원

### G073. CPU·GPU·TPU·QPU — processing units

CPU는 범용 제어, GPU·TPU는 특정 고전 병렬·행렬 계산, QPU는 양자 연산·측정에 사용된다. 하나의 QML workflow에 여러 장치가 참여할 수 있다. 같은 입력과 출력·정확도 없이 칩 이름만으로 비교하지 않는다.

### G074. 물리·논리 큐비트 — physical qubit, logical qubit

물리 큐비트는 실제 정보 단위이고 논리 큐비트는 오류정정 코드에 보호된 정보 단위다. 하나의 논리 큐비트에 필요한 물리 자원은 코드·오류율·목표 실패 확률에 따라 달라진다.

### G075. Native gate·컴파일 — native gate, compilation/transpilation

Native gate는 장치가 직접 제공하는 연산 집합이다. 컴파일은 추상 회로를 이를 사용한 실행 회로로 바꾼다. 논리 게이트 하나가 물리 연산 하나라는 보장은 없으며 변환의 정확성과 잡음 효과도 별개다.

### G076. 배치·routing — qubit placement, routing

논리 wire를 물리 위치에 놓고 연결 제약에 맞추는 과정이다. 먼 두 큐비트의 연산에 SWAP이 추가될 수 있다. 같은 모델도 배치·컴파일 seed·장치 topology에 따라 실행 자원이 다르다.

### G077. 폭·깊이·게이트 수 — circuit width, depth, gate count

폭은 사용 wire 수, 깊이는 병렬 실행을 고려한 순차 층 수, gate count는 연산 총수다. 깊이의 layer 정의가 서로 다를 수 있다. 세 숫자 중 하나만으로 회로 비용을 대신하지 않는다.

### G078. 샷 — shot

정해진 회로를 준비·실행·측정해 얻는 한 표본이다. 회로 설정 수와 shots는 다르다. 미분·입력·측정 그룹별 회로에 샷을 배정하면 총수는 여러 축의 곱으로 커진다.

### G079. 측정 그룹 — measurement group

같은 설정에서 함께 얻을 수 있는 관측량을 묶은 것이다. 가환성만으로 모든 장치의 측정 비용이 동일해지는 것은 아니다. 추가 basis rotation·연결·공분산을 확인한다.

### G080. 보정 — calibration

게이트·측정 등의 장치 파라미터를 추정·조정하는 과정이다. 한 번 추정한 보정값을 재사용하면 그 불확실성이 여러 결과에 공유된다. 실제 실행 사이 장치 drift도 기록한다.

### G081. 판독 오류 — readout error

준비한 상태 또는 측정 결과가 다른 고전 bit로 보고되는 오류를 뜻한다. Assignment 행렬의 행·열 규약을 명시한다. 읽기 오류와 게이트 이전의 상태 준비 오류를 모든 실험에서 분리할 수 있는 것은 아니다.

### G082. QV·CLOPS·RB — quantum volume, circuit-layer throughput, randomized benchmarking

각각 정해진 회로 품질, 처리량, 무작위 시퀀스 오류 특성을 평가하는 protocol이다. 정의·버전·가정을 같이 읽는다. 이 지표가 특정 QML task의 정확도나 실용 우위를 직접 보증하지는 않는다.

### G083. 전체 경과 시간 — end-to-end wall-clock time

사용자가 작업을 시작해 결과를 얻을 때까지 걸린 시간이다. 적재·컴파일·대기·실행·고전 후처리를 포함할 수 있다. QPU의 순수 gate time만 보고 전체 시간이라고 하지 않는다.

### G084. 전력·에너지 — power, energy

전력은 순간 소비율, 에너지는 전력의 시간 적분이다. W와 J 또는 Wh를 구별한다. 냉각·제어·고전 계산을 포함한 시스템 경계를 정하지 않고 서로 다른 장치의 에너지를 비교하지 않는다.

**사용:** [11강](lectures/11-hardware-and-resources.md), [실습 4](labs/README.md).

## H. 잡음·완화·오류정정

### G085. 양자 채널·Kraus·CPTP — quantum channel, Kraus representation, completely positive trace preserving

물리 상태를 상태로 보내는 선형 map은 보조계와 결합해도 양성을 보존하고 trace를 보존해야 한다. \(\mathcal E(\rho)=\sum_kK_k\rho K_k^\dagger\), \(\sum_kK_k^\dagger K_k=I\)가 Kraus 표현이다.

### G086. 유니탈 — unital

채널이 \(\mathcal E(I)=I\)를 만족하는 성질이다. 같은 입력·출력 차원에서는 완전 혼합 상태를 보존한다. 모든 CPTP 채널이 유니탈인 것은 아니며, amplitude damping이 대표적인 반례다.

### G087. Depolarizing 잡음 — depolarizing channel

본 노트 한 큐비트 규약은 \(\mathcal D_p(\rho)=(1-p)\rho+pI/2\)다. Bloch 벡터가 \(1-p\)배로 줄어든다. Pauli 오류 확률로 정의한 다른 p와 수치가 다를 수 있다.

### G088. 위상 감쇠 — dephasing

특정 기저의 population보다 coherence를 감소시키는 잡음이다. 이 노트에서 식을 지정한 기저·확률 규약을 확인한다. 모든 coherence 감소가 같은 물리 채널이나 같은 T2 원인을 뜻하는 것은 아니다.

### G089. 진폭 감쇠 — amplitude damping

여기서 보통 \(|1\rangle\)에서 \(|0\rangle\)로 이완하는 채널을 뜻한다. Population과 coherence를 함께 바꿀 수 있고 유니탈이 아니다. 단순 depolarizing 수축과 같은 식으로 대체하지 않는다.

### G090. 결맞는 오류·확률 오류 — coherent error, stochastic error

잘못된 회전각처럼 일관된 unitary 오차와 무작위 오류 사건 모형을 구별한다. 같은 평균 gate infidelity라도 회로 반복에 따른 누적은 다를 수 있다. 오류율 숫자 하나로 최종 예측 bias를 결정하지 않는다.

### G091. 오류 완화·판독 보정 — error mitigation, readout mitigation

추가 실험·가정·후처리로 관측량 bias를 줄이는 방법군이다. 판독 행렬 역산은 한 예다. 보정이 분산을 키울 수 있고 결과가 물리 확률 범위 밖으로 나올 수도 있다. 오류정정 코드로 보호했다는 뜻은 아니다.

### G092. ZNE·Richardson 외삽 — zero-noise extrapolation, Richardson extrapolation

여러 잡음 scale의 값을 결합해 0잡음 값을 추정한다. 가중치가 낮은 차수 항을 소거하도록 정한다. 잡음 확대의 물리적 타당성·높은 차수 잔여항·가중치 분산 비용을 확인한다.

### G093. PEC — probabilistic error cancellation

이상 연산을 구현 가능한 noisy 연산들의 부호 있는 결합으로 나타내 추정한다. 확률 혼합과 달리 음의 계수가 가능해 샘플 오버헤드가 생긴다. 정확한 잡음 모형과 sampling 규약이 필요하다.

### G094. QEC·syndrome — quantum error correction, error syndrome

코드 공간에 정보를 부호화하고 오류 관련 parity 정보를 측정해 복구하는 방법이다. Syndrome은 논리 상태의 모든 진폭을 읽는 값이 아니다. 오류 채널·코드·decoder의 가정을 함께 지정한다.

### G095. 코드 거리·문턱값 — code distance, error threshold

코드 거리는 구별·정정 가능한 오류 구조와 관련한 코드 성질이다. Threshold는 특정 fault model과 반복 구조에서 규모를 키워 논리 오류를 줄일 수 있는 조건이다. 모든 장치에 공통인 하나의 상수가 아니다.

### G096. Magic state — 매직 상태

일부 오류정정 scheme에서 비Clifford 연산을 구현하는 데 공급하는 특수 자원 상태다. 생산·증류·주입 비용이 전체 자원에서 클 수 있다. 논리 큐비트 수만 세면 이 비용을 놓칠 수 있다.

**사용:** [12강](lectures/12-noise-and-mitigation.md), [17강](lectures/17-fault-tolerant-qml.md).

## I. 계산 모형과 우위 주장

### G097. Oracle·query — 접근 oracle, 질의

허용한 입력 접근이나 함수를 추상적으로 제공하는 장치와 그 호출이다. Query 한 번이 물리 gate 하나나 파일 읽기 한 번이라는 뜻은 아니다. 실제 구현 비용과 접근의 강도를 따로 기술한다.

### G098. 표본 복잡도 — sample complexity

정해진 오차·성공 확률을 얻는 데 필요한 독립 자료·상태 준비 횟수다. 측정 설정·장치 시간과 같지 않을 수 있다. 복사본 하나를 여러 샷에 무제한 재사용한다고 가정하지 않는다.

### G099. 시간·공간 복잡도 — time complexity, space complexity

연산 시간과 계산 중 유지하는 메모리의 입력 크기 의존성이다. 고전 bit, 정밀도 고정 register, 논리 qubit을 명시한다. 메모리 우위를 곧바로 시간 우위로 바꾸어 말하지 않는다.

### G100. 점근 표기 — asymptotic notation

O는 상한, Ω는 하한, Θ는 같은 차수의 양쪽 경계를 나타낸다. 숨긴 상수·로그·정밀도 의존성이 실용 비용을 좌우할 수 있다. 작은 실험의 시간 순위와 정리의 점근 차이는 별개다.

### G101. 정밀도·실패 확률 — accuracy/tolerance, failure probability

보통 ε는 허용 오차, δ는 그 보장을 벗어날 확률이다. 가산·상대 오차나 분포 거리 중 무엇인지 정해야 한다. 같은 정확도라는 말이 분류 accuracy와 수치 precision을 동시에 뜻하지 않는다.

### G102. 양자 우위 — quantum advantage

같은 과제·입출력·오차·허용 자원에서 명시한 고전 비교보다 어떤 자원을 줄인 주장이다. 정리·제한된 알고리즘군 대비 결과·장치 proof of concept·실용 이득을 구별한다.

### G103. 탈양자화 — dequantization

양자 알고리즘의 이점을 비슷한 고전 접근 자원에서 재검토해 효율적 고전 알고리즘을 찾는 일이다. 모든 QML의 불가능성 정리가 아니다. 입력 접근이 정말 동등한지도 다시 확인해야 한다.

### G104. Sample-and-query access — 표본·원소 조회 접근

벡터의 원소·norm 조회와 길이제곱에 비례한 인덱스 sampling 등을 허용하는 고전 접근 모형이다. 허용 동작·비용을 정해야 한다. 아래 statistical-query learning과 약자 SQ만 같고 개념은 다르다.

### G105. Statistical query — 통계 질의

학습 분포에 대한 특정 함수 평균을 허용 오차 안에서 묻는 접근 모형이다. 표본 각각을 전부 직접 받는 모형과 구별된다. Correlational SQ는 다시 제한된 질의 종류다.

### G106. Quantum example·QSQ — 양자 예제 상태, quantum statistical query

분포·label 정보를 coherent하게 담은 상태나 그에 대한 기대값 질의를 허용하는 학습 모형이다. 저장된 고전 데이터가 무료로 이 접근을 제공하지는 않는다. 준비·정밀도·질의의 범위를 논문에서 확인한다.

### G107. 고전 surrogate — classical surrogate

원래 회로의 손실·예측을 대신 계산하는 고전 표현이다. 필요한 초기 특징을 QPU에서 얻었다면 양자 자료 획득을 포함하는 방법이다. 완전히 고전 입력만 쓰는 모델과 구별한다.

### G108. 비교 기준선·절제 실험 — baseline, ablation

경쟁 방법과 특정 구성 요소를 제거해 원인을 조사하는 실험이다. 얽힘 gate를 뺀 모델이나 같은 Fourier feature를 쓰는 고전 모델이 예다. 파라미터 수만 같게 맞추는 것이 항상 공정한 비교는 아니다.

**사용:** [01강](lectures/01-learning-problems-and-quantum-claims.md), [14강](lectures/14-advantage-and-dequantization.md), [18강](lectures/18-frontiers-2025-2026.md).

## J. 양자 데이터와 측정 재사용

### G109. 양자 데이터·복사본 — quantum data, copy

아직 측정하지 않은 상태·과정에 접근하는 자료다. 여러 copy는 미지 상태 하나를 복제했다는 뜻이 아니라 같은 준비 과정을 반복한 독립 표본이다. 고전 기록처럼 무제한 복제 가능하다고 가정하지 않는다.

### G110. 집단 측정 — collective/joint measurement

여러 계나 상태 복사본에 공동 연산 후 측정하는 방법이다. 각 복사본을 따로 측정하는 방법보다 많은 정보를 얻을 수 있는 과제가 있다. 허용한 메모리·접근이 결과의 조건이다.

### G111. Classical shadow — 고전 그림자 기록

무작위 측정 설정·결과를 저장해 여러 관측량을 나중에 추정하는 방법이다. 기록 하나가 전체 상태를 정확히 복원한 것은 아니다. 선택한 측정 앙상블과 예측할 관측량이 비용을 정한다.

### G112. 측정 채널·역채널 — measurement channel, inverse map

측정으로 평균적으로 어떤 정보를 남기는지 나타내는 선형 map과 그 통계적 역변환이다. Shadow의 역변환은 개별 추정자를 비물리적인 행렬로 만들 수 있다. 실제 장치에서 잡음을 역으로 되돌린다는 뜻이 아니다.

### G113. Shadow norm — 관측량별 측정 비용 척도

선택한 shadow 측정 방식에서 관측량 추정의 분산을 제어하는 양이다. 관측량 개수의 log 의존성만 보아서는 안 된다. 비국소 관측량에서 이 norm이 커지면 샷 비용이 커질 수 있다.

### G114. Pauli 문자열·무게 — Pauli string, Pauli weight

I,X,Y,Z의 텐서곱과 항등이 아닌 인자 수다. 예를 들어 \(X\otimes I\otimes Z\)는 무게 2다. 큐비트 총수와 같지 않을 수 있고 국소 잡음·shadow 분산의 의존성을 정한다.

### G115. 토모그래피 — quantum state tomography

여러 측정에서 상태 자체를 복원하는 작업이다. 일반 n큐비트 상태의 자유도는 \(4^n-1\)이다. 일부 국소 기대값을 예측하는 더 제한된 과제와 전체 상태 복원을 혼동하지 않는다.

### G116. 선형·비선형 상태 함수 — linear/nonlinear state functional

\(\operatorname{Tr}(O\rho)\)는 ρ에 선형이지만 \(\operatorname{Tr}\rho^2\)는 아니다. 불편한 상태 추정자를 얻었다고 그 제곱을 대입한 추정도 자동 불편한 것은 아니다. 독립 copy 또는 교차항 처리가 필요할 수 있다.

### G117. 상태·채널 학습 — state learning, channel learning

준비된 상태의 성질을 배우는 문제와 입력을 출력으로 보내는 미지 과정을 배우는 문제다. 후자는 어떤 probe·입력·보조계 사용이 허용되는지 정해야 한다. 두 과제의 샘플 수를 같은 단위로 비교하지 않는다.

### G118. 양자 메모리 — quantum memory

측정 전 상태를 보관해 나중에 공동 처리할 수 있는 자원이다. 저장 시간·잡음·접근·정정 비용이 든다. 고전 bitstring을 RAM에 저장하는 것과 같은 가정이 아니다.

### G119. Bell 측정·SWAP test — Bell measurement, SWAP test

전자는 얽힌 Bell 기저에서 측정하는 절차, 후자는 상태 겹침과 관련한 확률을 읽는 절차다. 서로 다른 회로다. SWAP test는 보통 내적의 복소 위상이나 부호를 직접 제공하지 않는다.

### G120. 복제 불가능 정리 — no-cloning theorem

미지의 임의 상태 모두를 완벽하게 복제하는 하나의 물리적 보편 연산은 없다. 알려진 준비 회로를 반복하는 것은 가능하다. 직교 상태의 복사와 임의 비직교 상태의 보편 복제를 구별한다.

**사용:** [03강](lectures/03-entanglement-and-circuits.md), [05강](lectures/05-quantum-kmeans-and-distances.md), [13강](lectures/13-quantum-data-and-shadows.md).

## K. 생성 학습과 대칭

### G121. Born machine·QCBM — quantum circuit Born machine

\(p_\theta(z)=|\langle z|U_\theta|0\rangle|^2\)로 분포를 정의해 측정 샘플을 생성하는 모델이다. 샘플 생성이 쉬워도 특정 bitstring의 확률을 효율적으로 계산하는 것은 별도 문제다.

### G122. KL divergence·총변동 거리 — Kullback–Leibler divergence, total variation distance

KL은 분포 비율의 log 평균이며 방향이 있고, TV는 확률 차이 절댓값 합의 절반이다. q가 0인 곳에 p가 양수이면 \(D_{KL}(p\|q)\)는 무한대다. 둘 다 fidelity와 같은 양이 아니다.

### G123. MMD — maximum mean discrepancy

커널 특징 평균의 차이를 비교하는 분포 discrepancy다. 샘플 쌍의 커널 평균으로 추정할 수 있다. 좋은 학습 신호·전체 분포 구별 능력은 커널 선택에 달려 있다.

### G124. U-statistic·V-statistic — 표본 쌍 평균의 두 규약

MMD 추정 등에서 자기 자신과의 쌍을 제외하는지 포함하는지 구별한다. 불편한 제곱 MMD 추정값은 유한 표본에서 음수가 나올 수도 있다. 그 사실만으로 계산 오류라고 하지 않는다.

### G125. Characteristic kernel — 분포 구별성이 있는 커널

확률분포의 평균 임베딩이 서로 다른 분포를 구별하는 커널이다. 고정 특징 몇 개만 보는 kernel은 이 성질이 없을 수 있다. 표현상 구별 가능해도 유한 샷에서 쉽게 학습된다는 뜻은 아니다.

### G126. 지지집합·mode collapse — support, mode collapse

지지집합은 확률이 놓이는 영역이고 mode collapse는 생성기가 일부 양상만 내는 현상을 가리킨다. 모든 낮은 차수 주변분포가 맞아도 전역 분포의 일부를 놓칠 수 있다.

### G127. Parity·고차 상관 — parity, higher-order correlation

여러 비트의 합을 mod 2로 본 parity는 전역 구조의 작은 예다. 세 비트 짝수·홀수 분포는 1·2차 주변분포가 같아도 3차 상관이 다르다. 국소 평가량만으로 전체 분포를 인증할 수 없는 반례다.

### G128. 군·표현 — group, representation

군은 닫힌 합성 연산·결합법칙·항등원·역원을 갖는 집합이고, 표현은 그 합성 구조를 행렬·연산으로 실현한다. 물리적 입력 변환과 encoding 후의 표현이 어떻게 대응하는지 먼저 정해야 한다.

### G129. 불변성 — invariance

변환해도 출력이 같은 성질이다. 분자 에너지는 적절한 전체 공간 회전에 불변일 수 있다. 상태의 물리적 대칭, 라벨의 대칭, 회로의 대칭은 각각 확인해야 한다.

### G130. 등변성 — equivariance

입력을 변환하면 출력도 정해진 법칙으로 변하는 성질이다. 힘 벡터는 회전하면 함께 회전해야 한다. 불변 스칼라 출력과 같은 제약을 쓰면 필요한 정보를 잃을 수 있다.

### G131. Twirling — 군 평균

상태·관측량·채널을 군의 작용에 대해 평균해 대칭 성분을 추출한다. 두 wire 교환에 대한 \(Z_1\)의 평균은 \((Z_1+Z_2)/2\)다. 평균은 방향 정보도 지울 수 있고 구현 비용도 있다.

### G132. 대칭 부문 — symmetry sector

보존량·대칭 표현 등에 따라 나뉜 부분공간이다. 대칭 보존 회로는 초기 부문을 벗어나지 못할 수 있다. 정답이 다른 부문에 있으면 최적화기를 바꾸는 것만으로 해결되지 않는다.

**사용:** [15강](lectures/15-generative-quantum-models.md), [16강](lectures/16-symmetry-and-scientific-learning.md).

## L. 과학 계산과 내결함성 QML

### G133. Neural quantum state — 신경망 양자 상태, NQS

구성 s에 대한 파동함수 진폭 \(\psi_\theta(s)\)를 고전 신경망으로 표현한다. 학습 대상이 양자 상태라는 뜻이며 계산 장치가 반드시 QPU라는 뜻은 아니다.

### G134. VMC·local energy — variational Monte Carlo, 국소 에너지

\(|\psi|^2\)에 비례해 구성을 뽑아 \(E_{loc}(s)=\sum_{s'}H_{ss'}\psi(s')/\psi(s)\)를 평균한다. Local이라는 이름이 반드시 작은 공간 영역의 에너지만 뜻하지는 않는다. 샘플링 혼합·해밀토니안 희소성도 중요하다.

### G135. Block encoding — 블록 부호화

더 큰 유니터리의 특정 보조계 block에 \(A/\alpha\)를 넣는 표현이다. 보조 wire 수·정규화 α·구현 오차를 명시한다. 큰 행렬이 주어졌다는 사실만으로 이 유니터리를 무료로 구현할 수는 없다.

### G136. QSVT — quantum singular value transformation

Block encoding과 phase 연산을 조합해 행렬의 특잇값에 다항식 변환을 구현하는 틀이다. 역수·필터 등의 근사는 구간·차수·오차 조건이 필요하다. 임의의 함수를 한 번에 적용하는 기능은 아니다.

### G137. HHL·해 상태 — quantum linear systems algorithm, solution state

선형계의 해 방향을 양자 상태로 만드는 알고리즘 계열의 출발점이다. 해 벡터의 모든 계수를 고전 숫자로 출력하는 작업과 다르다. 입력 접근·조건수·정밀도·출력 목적이 비용의 일부다.

### G138. 특잇값·조건수 — singular value, condition number

특잇값은 \(A^\dagger A\) 고유값의 제곱근이다. 가역 A에서 2-norm 조건수는 최대/최소 특잇값 비다. 정규방정식은 조건수를 제곱할 수 있어 표현 선택이 중요하다.

### G139. 진폭 추정 — amplitude estimation

적절한 coherent oracle 접근에서 성공 확률 같은 양을 추정하는 양자 절차다. 이상적인 query 차수 개선에는 oracle·역연산·긴 일관된 연산 조건이 붙는다. 일반 finite-shot 평균과 같은 비용 모형이 아니다.

### G140. 내결함성 — fault tolerance

허용한 물리 오류 아래에서도 논리 계산을 목표 실패 확률로 수행하도록 설계하는 성질이다. 보호된 처리기가 외부에서 들어오는 미지의 데이터를 자동으로 무잡음으로 바꾸지는 않는다.

### G141. Quantum uploading — 양자 자료의 보호 메모리 부호화

이 노트에서는 2026년 연구가 다룬 외부 실험 상태의 즉시 보호 부호화 맥락으로 사용한다. 상태 준비·고전 파일 업로드와 다른 개념이다. 비교 전략·잡음·부호화 시점이 결과의 조건이다.

### G142. 논리 자원 추정 — logical resource estimate

알고리즘의 논리 wire·gate·비Clifford 공급·목표 오류 등을 계산한 추정이다. 물리 큐비트 수와 시간으로 바꾸려면 코드·오류·하드웨어 가정이 더 필요하다. 장치 실험 결과로 표시하지 않는다.

### G143. 사전공개·출판본 — preprint, version of record

심사·출판 상태와 문헌 판본을 나타낸다. arXiv 최초일·수정일·학술지 온라인 공개일·권 연도는 다를 수 있다. 제목이 같아도 어느 판의 정리·실험을 읽었는지 기록한다.

### G144. 재현·독립 검증 — reproduction, independent verification

같은 코드·자료·조건을 실행해 결과를 대조하는 것과 별도 계산·증명·실험으로 확인하는 범위를 구별한다. 논문의 서지나 작은 교육 예제를 검산한 일을 전체 장치 결과의 독립 재현으로 부르지 않는다.

**사용:** [16강](lectures/16-symmetry-and-scientific-learning.md), [17강](lectures/17-fault-tolerant-qml.md), [18강](lectures/18-frontiers-2025-2026.md).

## 혼동을 줄이는 사용법

논문에서 새로운 용어를 만날 때 “무엇의 정의인가”, “식의 입력·출력은 무엇인가”, “어떤 유사한 말과 다른가”, “어느 조건에서 쓰는가”를 적는다. 예를 들어 *efficient*는 실제 초 단위로 빠르다는 말일 수도, 입력 크기의 다항 시간이라는 이론 용어일 수도 있다. 정리를 읽을 때는 후자의 변수·접근 모형을 먼저 확인한다.

약자 SQ는 **sample-and-query access**와 **statistical query**를 모두 가리킬 수 있다. Fidelity는 제곱 관례가 다를 수 있고, depolarizing p도 정의가 다르며, regularization과 normalization은 모두 정규화로 번역되기도 한다. 이 네 가지는 영어 원어와 식을 함께 메모한다.

이 용어집의 표준 수학·양자정보 정의에 대한 추가 읽기는 [Watrous의 저자 제공 교재 안내](https://cs.uwaterloo.ca/~watrous/TQI/)와 [IBM Quantum Learning](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/density-matrix-basics)다. 원문 파일은 재배포하지 않는다. QML의 특정 정리·최신 용례는 각 강의의 원 논문과 [출처 확인 범위](sources.md)를 따른다. 단어의 정의와 그 단어를 포함한 우위 주장의 검증은 별개다.

[전체 목차](README.md) · [수학 보충편](math-primer.md) · [학습 안내](study-guide.md)
