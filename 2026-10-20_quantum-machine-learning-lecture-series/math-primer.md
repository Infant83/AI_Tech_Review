# 수학 보충편: 식을 읽고 직접 계산하기 위한 준비

이 보충편은 양자역학을 미리 배웠다고 가정하지 않는다. 복소수, 선형대수, 확률과 미분에서 본문에 실제로 쓰는 계산을 정리한다. 원 강좌의 공식 선수 과목이나 수업 자료가 아니라, 독립 학습 시리즈 2.0판을 위해 작성한 준비 과정이다. 개념별 정확한 뜻은 [용어집](glossary.md)에서 다시 찾을 수 있다.

처음 공부한다면 P1–P4에 2–4시간, P5–P8에 2–4시간을 배정한다. 이것은 제안 시간이며 숙련도를 측정한 결과가 아니다. 식을 눈으로 읽고 넘어가기보다 각 예제를 종이에 재계산한다. 마지막 준비도 문제에서 막히면 표시된 절로 돌아온다. 외부 교재는 추가 학습용이며 이 보충편의 예제를 푸는 필수 조건은 아니다.

<a id="primer-complex"></a>
## P1. 복소수와 진폭: 확률과 같은 수가 아니다

복소수는 \(z=a+ib\), \(i^2=-1\)로 쓴다. \(a\)와 \(b\)는 실수다. 켤레는 \(z^*=a-ib\), 절댓값은 \(|z|=\sqrt{a^2+b^2}\)다. 따라서 \(z^*z=a^2+b^2\)는 음수가 아니다. 양자 상태의 성분은 확률이 아니라 복소 진폭(amplitude)이며, 측정 확률에는 진폭의 절댓값 제곱을 쓴다.

예를 들어 \(z=(1+i)/2\)라면

$$
z^*z=\frac{(1-i)(1+i)}4=\frac{1-i^2}4=\frac12.
$$

반면 \(z^2=i/2\)는 복소수이며 확률로 사용할 수 없다. 제곱과 절댓값 제곱을 구별하는 것이 첫 번째 준비다.

복소수는 \(z=re^{i\phi}\)로도 나타낸다. Euler 관계 \(e^{i\phi}=\cos\phi+i\sin\phi\)에서 \(r\)는 크기, \(\phi\)는 위상이다. 위상각의 단위는 라디안이며 \(180^\circ=\pi\)다. 각도 인코딩에 원래 데이터의 물리 단위를 넣을 때에는 라디안으로 보내는 무차원 변환이 필요하다.

**간섭을 계산하는 예.** 진폭 \(a,b\)를 합친 뒤 확률을 구하면

$$
|a+b|^2=|a|^2+|b|^2+2\operatorname{Re}(a^*b).
$$

마지막 항은 간섭항이다. \(a=b=1/2\)이면 합친 확률은 1이며, \(a=1/2,b=-1/2\)이면 0이다. 두 경우에 개별 크기의 제곱은 모두 1/4이다. 어떤 회로의 경로 진폭을 더하는 상황인지 먼저 정해야 하며, 서로 구별되는 고전적 사건의 확률을 임의로 진폭처럼 더하지 않는다.

**준비 확인.** \((1+i)/\sqrt2\)의 절댓값은 1이다. 절댓값 제곱이 2라고 계산했다면 분모도 제곱해야 한다는 점을 다시 확인한다. [02강](lectures/02-qubits-gates-and-measurement.md)에서 위상을 측정 결과로 바꾸는 회로를 다룬다.

<a id="primer-linear-algebra"></a>
## P2. 벡터·내적·행렬: shape부터 확인한다

\(d\)차원 복소 열벡터 \(v\)는 \(d\times1\) 배열이다. 전치 \(v^T\)는 행과 열만 바꾸고, 켤레전치 \(v^\dagger\)는 성분을 켤레 처리한 뒤 전치한다. 복소 내적은 \(\langle u,v\rangle=u^\dagger v\)로 정의한다. 이 노트는 첫 번째 인자에 켤레가 들어가는 물리학 관례를 사용한다.

$$
u=\frac1{\sqrt2}\begin{pmatrix}1\\i\end{pmatrix},\qquad
v=\frac1{\sqrt2}\begin{pmatrix}1\\-i\end{pmatrix},\qquad
u^\dagger v=\frac{1+(-i)(-i)}2=0.
$$

이 두 벡터는 직교한다. 켤레를 빼고 \(u^Tv\)를 계산하면 1이 나와 잘못된 판정을 한다. 벡터 노름은 \(\|v\|_2=\sqrt{v^\dagger v}\)이며, \(v\ne0\)일 때 \(v/\|v\|_2\)로 정규화한다. 정규화는 방향을 남기고 전체 크기를 없애므로 원 데이터의 크기가 필요한 학습 문제에서는 추가 정보가 필요하다.

행렬 \(A\in\mathbb C^{m\times d}\)는 \(d\)차원 벡터를 \(m\)차원으로 보낸다. \(AB\)가 정의되려면 A의 열 수와 B의 행 수가 같아야 한다. 오른쪽 행렬이 먼저 작용한다. 행렬 곱은 일반적으로 교환하지 않는다. Pauli X와 Z로 직접 보면

$$
XZ=\begin{pmatrix}0&-1\\1&0\end{pmatrix},\qquad
ZX=\begin{pmatrix}0&1\\-1&0\end{pmatrix},\qquad XZ=-ZX.
$$

내적 \(u^\dagger v\)는 스칼라인 반면 외적 \(uv^\dagger\)는 행렬이다. \(u\)와 \(v\)의 길이가 각각 \(m,d\)라면 외적의 shape는 \(m\times d\)다. 이 차이가 상태벡터와 밀도행렬의 차이로 이어진다.

**손계산.** \(w=(1,2)^T\)일 때 \(ww^T=\begin{pmatrix}1&2\\2&4\end{pmatrix}\), \(w^Tw=5\)다. 정규화한 \(\widehat w=w/\sqrt5\)의 projector는 \(\widehat w\widehat w^T=ww^T/5\)이며 trace가 1이다. [04강](lectures/04-data-encoding-and-loading.md)에서는 이 표현이 원래 벡터의 norm을 잃는다는 점을 사용한다.

<a id="primer-spectral"></a>
## P3. 고유값·양의 준정부호·trace: 상태와 커널을 판정한다

\(Av=\lambda v\), \(v\ne0\)이면 \(\lambda\)가 고유값이다. 행렬이 에르미트이면 \(A=A^\dagger\)이며 고유값은 실수이고 서로 직교하는 고유벡터를 선택할 수 있다. 유한차원에서

$$
A=\sum_j\lambda_j|v_j\rangle\langle v_j|
$$

로 쓴다. 이 식은 spectral decomposition이다. 이 노트의 \(|v\rangle\)는 열벡터를 쓰는 Dirac 표기일 뿐 별도의 새로운 연산은 아니다.

양의 준정부호(positive semidefinite, PSD)란 모든 \(z\)에 대해 \(z^\dagger A z\ge0\)인 에르미트 행렬이다. 이는 고유값이 모두 0 이상인 것과 동치다. 양의 정부호는 0이 아닌 모든 \(z\)에서 엄격히 양수인 경우다. \(\begin{pmatrix}1&1\\1&1\end{pmatrix}\)의 고유값은 2와 0이라 PSD지만 가역이 아니다. 반면 \(\begin{pmatrix}1&2\\2&1\end{pmatrix}\)의 고유값은 3과 -1이므로 PSD가 아니다. 대각 원소가 양수라고 PSD인 것은 아니다.

Trace는 대각 원소의 합이다. 두 행렬의 곱이 정의되고 trace를 취할 수 있으면 \(\operatorname{Tr}(AB)=\operatorname{Tr}(BA)\)다. 인덱스로 쓰면 \(\sum_{ij}A_{ij}B_{ji}=\sum_{ji}B_{ji}A_{ij}\)라서 성립한다. 그러나 \(ABC\)에서 임의의 두 행렬을 바꿀 수 있다는 뜻은 아니다. 허용되는 것은 \(ABC\to BCA\to CAB\)라는 순환 이동이다.

행렬에도 서로 다른 노름이 있다. 특잇값을 \(s_j\)라 할 때 연산자 노름은 \(\|A\|=\max_js_j\), trace norm은 \(\|A\|_1=\sum_js_j=\operatorname{Tr}\sqrt{A^\dagger A}\), Hilbert–Schmidt norm은 \(\|A\|_{\rm HS}=\sqrt{\sum_js_j^2}=\sqrt{\operatorname{Tr}(A^\dagger A)}\)다. 에르미트 행렬에서는 특잇값이 고유값의 절댓값이다. 예를 들어 \(A=\operatorname{diag}(3,-4)\)의 세 노름은 각각 4, 7, 5다. 상태 구별에 쓰는 trace distance \(\|\rho-\sigma\|_1/2\)와 커널에서 쓰는 Hilbert–Schmidt 거리를 구별한다.

유니터리 \(U\)는 \(U^\dagger U=I\)를 만족하며, \(\|Uv\|^2=v^\dagger U^\dagger Uv=\|v\|^2\)로 노름을 보존한다. 에르미트와 유니터리는 다른 조건이다. Pauli 행렬은 둘 다 만족하지만 일반 회전 게이트는 에르미트가 아니다. 관측량과 게이트를 무조건 같은 종류의 행렬로 취급하면 안 된다.

**행렬 지수.** 에르미트 생성자 H로 \(U(\theta)=e^{-i\theta H}\)를 만들면 고유값별로 위상이 붙으므로 유니터리다. \(P^2=I\)이면 지수의 짝수·홀수 항을 묶어

$$
e^{-i\theta P/2}=I\cos(\theta/2)-iP\sin(\theta/2)
$$

를 얻는다. 이것이 회전 게이트와 [07강](lectures/07-gradients-and-training.md)의 미분식을 계산하는 출발점이다.

<a id="primer-tensor"></a>
## P4. 텐서곱과 부분계: 인덱스를 지우는 일이 아니다

두 독립 벡터 공간을 합치면 벡터의 성분 수는 곱해진다. \(a=(a_0,a_1)^T\), \(b=(b_0,b_1)^T\)에 대해

$$
a\otimes b=(a_0b_0,a_0b_1,a_1b_0,a_1b_1)^T.
$$

기저는 \(|00\rangle,|01\rangle,|10\rangle,|11\rangle\) 순서로 고정한다. \(A\otimes B\)는 A의 각 원소에 B를 곱한 block 행렬이다. 행렬이 작아도 크기가 빨리 커지므로, \((A\otimes B)(a\otimes b)=(Aa)\otimes(Bb)\) 같은 구조를 이용해 계산한다.

Bell 상태 \(|\Phi^+\rangle=(|00\rangle+|11\rangle)/\sqrt2\)의 밀도행렬을 직접 만들면

$$
\rho_{AB}=\frac12\begin{pmatrix}1&0&0&1\\0&0&0&0\\0&0&0&0\\1&0&0&1\end{pmatrix}.
$$

첫 계의 reduced state는 둘째 계 인덱스를 **합산**해 얻는다.

$$
(\rho_A)_{a,a'}=\sum_{b=0}^1(\rho_{AB})_{ab,a'b}.
$$

따라서 \((\rho_A)_{00}=1/2+0\), \((\rho_A)_{11}=0+1/2\), 비대각 원소는 0이다. 결과는 \(\rho_A=I/2\)다. 4×4 행렬에서 왼쪽 위 2×2 block만 떼는 것과 다르다. 실제로 그 block의 trace는 1/2여서 정규화된 상태조차 아니다.

이 계산은 전체 순수 상태의 부분계가 혼합 상태일 수 있음을 보여준다. 혼합 상태를 “실제로는 하나의 순수 상태인데 우리가 몰라서 그런 것”으로만 이해하면 얽힘의 부분계를 설명하지 못한다. 본문에서는 측정 가능한 예측을 주는 밀도행렬을 상태의 수학적 표현으로 사용한다. [03강](lectures/03-entanglement-and-circuits.md)에서 얽힘·Schmidt 분해와 연결한다.

<a id="primer-states-measurements"></a>
## P5. 밀도행렬과 측정: 양성·정규화를 함께 점검한다

유한차원 양자 상태 \(\rho\)는 PSD이며 trace가 1이다. 순수 상태는 \(\rho=|\psi\rangle\langle\psi|\), \(\langle\psi|\psi\rangle=1\)로 쓴다. 한 큐비트에서는

$$
\rho=\frac{I+r_xX+r_yY+r_zZ}{2}
=\frac12\begin{pmatrix}1+r_z&r_x-ir_y\\r_x+ir_y&1-r_z\end{pmatrix}.
$$

이 행렬의 고유값은 \((1\pm\|r\|)/2\)이므로 \(\|r\|\le1\)이어야 PSD다. 순수 상태는 \(\|r\|=1\), 중심 \(r=0\)은 \(I/2\)다. Bloch 구의 점은 공간에 있는 작은 구슬의 위치가 아니라 세 Pauli 기대값을 요약한 좌표다.

유한 결과 측정의 POVM은 PSD 행렬들 \(E_a\)가 \(\sum_a E_a=I\)를 만족하는 집합이다. 결과 확률은

$$
p(a)=\operatorname{Tr}(E_a\rho),\qquad
\sum_a p(a)=\operatorname{Tr}\left[\left(\sum_aE_a\right)\rho\right]=1.
$$

양성 때문에 각 확률도 음수가 아니다. POVM은 결과 확률을 지정하며, 측정 뒤 상태까지 유일하게 지정하지는 않는다. 후자의 설명에는 측정 연산자나 instrument가 더 필요하다. Projective measurement에서는 \(E_a\)들이 서로 직교하는 projector다.

관측량 \(O=\sum_a o_a\Pi_a\)를 projective하게 측정하면 결과 숫자는 고유값 \(o_a\), 평균은 \(\operatorname{Tr}(O\rho)\)다. Z 측정의 결과 숫자는 ±1이다. 출력 비트 0/1과 물리적 관측값 ±1을 코드에서 같은 배열로 섞지 않는다.

**완전 예제.** \(\rho=\operatorname{diag}(0.7,0.3)\)이면 Z의 평균은 \(0.7-0.3=0.4\), 분산은 \(1-0.4^2=0.84\)다. X의 평균은 0이다. 대각 원소만으로 모든 기저의 상태를 판정할 수 없다는 점은 [02강](lectures/02-qubits-gates-and-measurement.md)에서 다시 확인한다.

<a id="primer-statistics"></a>
## P6. 표본 평균과 불확실성: 어떤 양의 오차인가

**연속변수의 평균.** 각도 \(\theta\)가 \([a,b]\)에서 균등하면 확률밀도는 \(1/(b-a)\)이고 \(\mathbb E[h(\theta)]=(b-a)^{-1}\int_a^b h(\theta)\,d\theta\)다. 적분은 작은 구간의 함수값에 구간 길이를 곱해 합한 값의 극한이며, 정규화한 넓이가 평균이 된다. \([0,2\pi]\)에서 0이 아닌 정수 k에 대해 \(\int_0^{2\pi}\cos(k\theta)\,d\theta=[\sin(k\theta)/k]_0^{2\pi}=0\)이고 사인도 평균 0이다. \(\sin^2\theta=(1-\cos2\theta)/2\), \(\cos^2\theta=(1+\cos2\theta)/2\)이므로 두 제곱의 평균은 각각 1/2다. 곱을 합으로 바꾸는 삼각 항등식으로 서로 다른 정수 주파수의 직교성도 얻는다. 이것이 [06강](lectures/06-qnn-and-expressivity.md)의 Fourier 오차 하한과 [09강](lectures/09-trainability-and-barren-plateaus.md)의 초기화 분산 계산에 필요한 적분이다.

기댓값은 분포에 대한 평균이다. 유한한 측정 평균과 같다고 가정하지 않는다. 독립 동일분포(i.i.d.)인 \(Z_s\in\{-1,+1\}\)의 평균을 \(\mu\)라 하고, \(\widehat\mu=S^{-1}\sum_sZ_s\)로 추정하자. 선형성으로 불편성 \(\mathbb E\widehat\mu=\mu\)를 얻고, 독립성이 공분산 항을 지우므로

$$
\operatorname{Var}(\widehat\mu)=\frac{1-\mu^2}{S},\qquad
\operatorname{SE}(\widehat\mu)=\sqrt{\frac{1-\mu^2}{S}}.
$$

평균에 대한 표준오차(SE)는 개별 측정값의 표준편차(SD)를 \(\sqrt S\)로 나눈 것이다. \(\mu=0.4,S=400\)이면 SD는 약 0.9165, SE는 약 0.0458이다. 값의 흔들림과 평균 추정의 흔들림을 구별한다.

Bernoulli 비트 \(B\in\{0,1\}\)는 분산이 \(p(1-p)\)다. 같은 실험에서 \(Z=1-2B\)이면 \(\mu=1-2p\), 평균의 분산도 4배다. 결과의 숫자 규약을 바꾸면서 예전 분산 식을 그대로 쓰면 틀린다.

**확률 보장과 근사 구간.** Hoeffding 부등식을 ±1 결과에 적용하면

$$
\Pr(|\widehat\mu-\mu|\ge\epsilon)
\le2e^{-S\epsilon^2/2}.
$$

실패 확률을 \(\delta\) 이하로 만들기 위한 충분조건은 \(S\ge2\log(2/\delta)/\epsilon^2\)다. \(\epsilon=0.05,\delta=0.05\)이면 약 2,952샷이 필요하다. 이는 평균값을 몰라도 쓸 수 있는 보수적인 상한이며 최소 샷 수의 정확한 값이 아니다. 0/1 Bernoulli 평균에는 구간 길이가 1이어서 지수 상수가 다르다.

흔히 쓰는 \(\widehat\mu\pm1.96\,\widehat{\mathrm{SE}}\)는 큰 표본의 정규 근사에 의존한다. 경계 확률·소표본에서는 정확하지 않을 수 있다. 빈도주의 95% 신뢰구간은 같은 절차를 반복했을 때 참 값을 포함하는 비율에 관한 말이다. 관측한 구간에 대해 고정된 참 값이 95% 확률로 들어간다는 Bayesian 해석과 같지 않다.

**Bias와 RMSE의 유도.** 참 값 \(\theta\), 추정량 \(T\), 평균 \(m=\mathbb ET\)에 대해

$$
\mathbb E[(T-\theta)^2]
=\mathbb E[(T-m+m-\theta)^2]
=\operatorname{Var}(T)+(m-\theta)^2.
$$

가운데 교차항은 \(\mathbb E(T-m)=0\)이라 사라진다. RMSE는 이 MSE의 제곱근이다. 장치 bias가 0.1로 남아 있으면 샷을 무한히 늘려도 RMSE는 0으로 가지 않는다. [12강](lectures/12-noise-and-mitigation.md)에서 완화의 bias 감소와 분산 증가를 같이 계산한다.

<a id="primer-optimization"></a>
## P7. 미분·경사하강·정규화: 무엇을 최소화하는가

손실 \(L(\theta)\)가 미분 가능할 때 작은 변화의 일차 근사는 \(L(\theta+\Delta)\approx L(\theta)+\nabla L(\theta)^T\Delta\)다. 그래서 \(\Delta=-\eta\nabla L\), \(\eta>0\)를 선택한다. 하지만 고차항이 남으므로 임의의 큰 학습률에서 감소를 보장하지 않는다.

예를 들어 \(L(\theta)=\theta^2\)이면 갱신은 \(\theta_{t+1}=(1-2\eta)\theta_t\)다. \(0<\eta<1\)일 때 크기가 줄고, \(\eta=1\)이면 부호만 바뀌고, \(\eta>1\)이면 일반적으로 커진다. 영 기울기가 나오는 점을 찾는 것과 전역 최소를 찾는 것도 비볼록 손실에서는 다른 문제다.

양자 기대값 뒤의 고전 손실에는 chain rule이 필요하다. \(f(\theta)=\cos\theta\), \(L=(f-y)^2\)라면

$$
\frac{dL}{d\theta}=2(f-y)\frac{df}{d\theta}
=-2(\cos\theta-y)\sin\theta.
$$

회로의 미분만 구하고 앞의 \(2(f-y)\)를 빼먹으면 다른 목적을 최적화한다. 역전파·parameter shift·유한차분은 같은 미분을 구하려는 다른 방법이며 적용 조건과 실행 비용이 다르다.

선형 회귀에서는 \(X\in\mathbb R^{N\times d}\), \(y\in\mathbb R^N\), \(\beta\in\mathbb R^d\)를 쓰자. 다음 규약의 ridge 목적함수는

$$
L(\beta)=\|X\beta-y\|_2^2+\lambda\|\beta\|_2^2,
\qquad \lambda>0
$$

이며 미분해 \((X^TX+\lambda I)\beta=X^Ty\)를 얻는다. 손실 앞에 \(1/N\)을 넣었다면 같은 \(\lambda\) 기호라도 정상방정식은 \(X^TX+N\lambda I\)가 된다. 논문과 코드의 정규화 규약을 먼저 맞춘다. 역행렬을 실제로 만들기보다 선형 방정식 solver를 사용하는 편이 일반적으로 적절하다.

조건수 \(\kappa_2(A)=\sigma_{\max}(A)/\sigma_{\min}(A)\)는 가역 행렬의 입력 오차가 얼마나 증폭될 수 있는지와 관련한다. \(A=\operatorname{diag}(1,0.01)\)이면 조건수는 100이다. 작은 고유값의 역수를 키우는 계산은 오차에 민감할 수 있으며, 정규화는 안정성과 추정 bias 사이의 절충을 만든다. [17강](lectures/17-fault-tolerant-qml.md)의 해 상태·QSVT를 읽기 전 이 예제를 다시 계산한다.

<a id="primer-learning-complexity"></a>
## P8. 학습 이론·복잡도의 기호를 읽는 최소 준비

입력과 label의 분포를 \(\mathcal D\), 모델을 \(f\), 손실을 \(\ell\)라 쓰면 모집단 위험은 \(R(f)=\mathbb E_{\mathcal D}\ell(f(x),y)\), 경험 위험은 \(\widehat R_D(f)=N^{-1}\sum_i\ell(f(x_i),y_i)\)다. 일반화 차이는 같은 모델의 두 위험 사이 차이다. 테스트 정확도는 그 중 일부를 추정하는 통계이지 정리의 결론 자체가 아니다.

모델을 선택한 데이터와 성능을 평가할 데이터를 나눈다. Train은 파라미터 갱신에, validation은 모델·설정 선택에, test는 선택이 끝난 뒤의 평가에 쓴다. 표준화의 평균·분산도 train에서 계산한다. 같은 환자·분자·시간 구간의 가까운 자료가 두 분할에 섞이면 형식적으로 다른 행이라도 독립 표본 가정이 깨질 수 있다.

\(O(g(n))\)는 충분히 큰 n에서 어떤 상수배 g로 상한을 잡는 표기다. \(\Omega\)는 하한, \(\Theta\)는 양쪽이 같은 규모, \(\widetilde O\)는 보통 로그 인자를 숨기지만 정확한 관례는 논문을 따른다. 예를 들어 \(100n\)과 \(n^2\) 중 작은 n에서는 전자가 느릴 수 있다. 점근 표기만으로 실제 실행 순서를 판단하지 않는다.

복잡도 식에는 입력 크기뿐 아니라 정밀도 \(\epsilon\), 실패 확률 \(\delta\), 조건수 \(\kappa\), 데이터 접근 비용이 들어갈 수 있다. \(O(\log d)\)큐비트로 표현한다고 임의의 d차원 데이터를 \(O(\log d)\)시간에 준비할 수 있는 것은 아니다. Oracle query 한 번이라는 추상 비용과 실제 게이트·메모리·파일 읽기의 비용을 구별한다. [14강](lectures/14-advantage-and-dequantization.md)이 이 구별을 중심으로 구성된다.

## 준비도 문제: 힌트 뒤에 계산을 가리고 푼다

### 준비 문제 1. 켤레와 정규화

\(v=(1,i,1,-i)^T/2\)의 norm과 \(|v_1|^2\)를 계산하라. **힌트:** 인덱스는 0부터 쓰되 모든 성분의 절댓값은 1/2다. **풀이:** 네 성분의 제곱 크기가 각각 1/4이므로 norm 제곱은 1, norm은 1이다. 인덱스 1 성분은 i/2이고 확률은 1/4다. 복소 성분을 그냥 제곱해 -1/4로 보고하면 틀리다. 틀렸다면 P1–P2로 돌아간다.

### 준비 문제 2. 상태 조건

\(A=\begin{pmatrix}0.5&0.6\\0.6&0.5\end{pmatrix}\)는 상태인가? **힌트:** 대칭 벡터와 반대칭 벡터에 작용시킨다. **풀이:** 고유값은 1.1과 -0.1이다. 에르미트이고 trace는 1이지만 양성이 깨져 밀도행렬이 아니다. 모든 상태 조건을 함께 점검해야 한다. P3·P5를 복습한다.

### 준비 문제 3. 부분 trace

\(|\psi\rangle=\sqrt{3/4}|00\rangle+\sqrt{1/4}|11\rangle\)에서 첫 계 상태와 purity를 구하라. **힌트:** 둘째 계 기저가 다른 교차항은 부분 trace에서 사라진다. **풀이:** \(\rho_A=\operatorname{diag}(3/4,1/4)\). purity는 \(\operatorname{Tr}(\rho_A^2)=9/16+1/16=5/8\)로 1보다 작다. 전체 순수성과 부분계 순수성을 구별하지 못했다면 P4로 돌아간다.

### 준비 문제 4. 평균과 bias

실험 평균의 기대값은 참 값보다 0.03 크고 분산은 0.0016이다. MSE와 RMSE는? **힌트:** 제곱근은 합을 끝낸 뒤 취한다. **풀이:** MSE는 \(0.0016+0.03^2=0.0025\), RMSE는 0.05다. 분산의 제곱근 0.04만 보고 전체 오차라고 하면 bias가 빠진다. P6을 복습한다.

### 준비 문제 5. 샷과 표준오차

같은 i.i.d. 측정의 표준오차가 2,000샷에서 0.02였다. 8,000샷에서는? **힌트:** 표본 수 비율의 제곱근을 쓴다. **풀이:** \(0.02\sqrt{2000/8000}=0.01\). 독립성·정상성이 깨지거나 systematic bias를 보고 있다면 이 비례를 적용할 수 없다. P6을 복습한다.

### 준비 문제 6. Chain rule

\(f(\theta)=\sin\theta\), \(L=(f-1)^2\)에서 \(\theta=0\)의 기울기와 학습률 0.1의 다음 값은? **풀이:** \(L'=2(\sin\theta-1)\cos\theta\)라서 -2다. 새 각도는 \(0-0.1(-2)=0.2\). f의 미분만 구해 +1을 사용하면 반대 방향으로 간다. P7을 복습한다.

### 준비 문제 7. 정규화 규약

\(X=(1,1)^T,y=(1,3)^T\), 즉 표본 두 개·특징 하나이며 \(\lambda=2\)다. \(\|X\beta-y\|^2+\lambda\beta^2\)의 해는? **풀이:** \(X^TX=2\), \(X^Ty=4\)이므로 \((2+2)\beta=4\), \(\beta=1\)이다. 손실을 N으로 나누는 다른 규약에서는 같은 λ 숫자가 다른 문제를 정의한다. P7을 복습한다.

### 준비 문제 8. 복잡도 주장

알고리즘이 상태 준비 oracle을 \(O(\log d)\)번 호출한다. 이 정보만으로 저장된 일반 벡터에 대한 전체 실행이 polylog(d)라고 결론낼 수 있는가? **풀이:** oracle을 구현하는 비용과 준비 횟수별 재사용, 출력·정밀도 비용이 없다. 따라서 query 상한만 알 수 있다. P8과 04강을 다시 읽는다.

여덟 문제 중 여섯 개 이상을 해설 없이 설명하고, 틀린 문제를 다시 계산하면 본문을 시작할 준비가 된 것으로 **이 학습 안내에서** 제안한다. 이는 검증된 능력 평가나 공식 수강 요건이 아니다. 정답 숫자만 맞히지 말고 사용한 가정을 한 문장씩 적는다.

## 추가 읽기와 출처

위 작은 예제와 유도는 독립 교육용 구성이다. 표준 수학 정의의 심화 자료는 다음과 같다.

- [John Watrous, The Theory of Quantum Information](https://cs.uwaterloo.ca/~watrous/TQI/), Ch. 1 *Mathematical preliminaries*, Ch. 2 *Basic notions of quantum information*, Ch. 3 *Similarity and distance among states and channels*. 저자가 제공하는 개인 열람용 원고로 연결하며 파일을 이 아카이브에 재배포하지 않는다. 정확한 페이지는 판형에 따라 다르다.
- [IBM Quantum Learning, Density matrix basics](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/density-matrix-basics)와 [Multiple systems and reduced states](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/multiple-systems): 상태와 부분계의 공식 교육 자료. 이 보충편은 자체 예제로 설명한다.
- [IBM Quantum Learning, Mathematical formulations of measurements](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/general-measurements/formulations-of-measurements): projective measurement와 일반 측정의 구별을 더 읽을 수 있다.

[학습 순서](study-guide.md) · [용어집](glossary.md) · [01강 시작](lectures/01-learning-problems-and-quantum-claims.md)
