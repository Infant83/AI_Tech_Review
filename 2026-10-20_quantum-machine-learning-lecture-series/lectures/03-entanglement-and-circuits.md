# 03. 텐서곱, 얽힘과 양자 회로의 계산 능력

> 독립 집필한 80분 학습 단원 · 2026-10-20 기준. 원강좌 Lecture 2·Lab 1의 공개 개요를 확장한 자체 교육 자료다.

## 시작하기 전에

[2강](02-qubits-gates-and-measurement.md)의 상태벡터, 밀도행렬, Pauli 측정과 trace를 사용한다. 행렬의 고유값과 특잇값이 낯설면 [수학 준비 노트](../math-primer.md)를 참조한다. 이 강의의 목표는 두 큐비트 상태를 정확한 기저 순서로 전개하고, 부분계 상태를 직접 구하고, 순수 상태의 얽힘을 Schmidt 계수로 판정하며, 얽힘과 고전 계산 난도를 구별하는 것이다.

양자 학습에서 데이터의 상호작용을 설명할 때 “큐비트들이 서로 연결된다”는 말만으로는 부족하다. 어떤 상태가 만들어지고 어떤 측정에서 고전적 상관과 구별되는지를 계산해야 한다. 반대로 큰 얽힘을 만들었다는 사실만으로 학습이 어려운 고전 문제를 해결했다고 결론 내릴 수 없다.

## 80분 학습 순서

| 시간 | 수행할 활동 | 남길 결과 |
|---|---|---|
| 0–10분 | 용어와 기저 순서 확인 | 텐서곱 벡터 전개 |
| 10–25분 | Bell 상태·부분 trace 계산 | 전체와 부분 상태 |
| 25–45분 | Schmidt 예제와 상관 반례 계산 | 얽힘 판정의 근거 |
| 45–60분 | 복제 불가능성과 모사 비용 확인 | 가정과 반례 목록 |
| 60–75분 | 문제 1·2부터 풀고 선택한 문제의 해설만 대조 | 독립 계산 기록 |
| 75–80분 | 완료 점검을 회상으로 수행 | 다음 강의 진행 여부 |

네 문제와 심화 읽기를 모두 완수하려면 별도의 복습 시간을 둔다. 처음부터 빠르게 읽어 80분을 맞추기보다 표에 있는 계산 활동을 남기는 것이 중요하다.

강의 후 **60–90분**에는 남은 문제를 해설 없이 풀고, 유도 하나를 재작성하고, 오답을 수정한다. 원문 전문 독해와 코딩 실습은 별도 시간이다.

## 핵심 용어

| 한국어·영어 | 정의·기호·직관 |
|---|---|
| 텐서곱·tensor product | 부분계 공간을 결합하는 연산 \(\mathcal H_A\otimes\mathcal H_B\). 두 계의 기저쌍을 새 기저로 만든다. |
| 곱 상태·product state | \(|a\rangle\otimes|b\rangle\)로 분리되는 순수 상태. |
| 분리 가능 상태·separable state | \(\sum_jp_j\rho_A^{(j)}\otimes\rho_B^{(j)}\)로 쓸 수 있는 혼합 상태. 고전적 상관을 포함할 수 있다. |
| 얽힘·entanglement | 위 분리 가능 표현이 없는 상태의 성질. 순수 상태에서는 곱으로 분리되지 않음과 같다. |
| 부분 trace·partial trace | 다른 부분계를 무시한 통계를 주는 연산 \(\rho_A=\operatorname{Tr}_B\rho_{AB}\). 행렬 원소 일부를 단순히 지우는 것이 아니다. |
| Schmidt 분해·Schmidt decomposition | 순수 이분 상태를 \(\sum_rs_r|u_r\rangle|v_r\rangle\)로 쓰는 표현. 양쪽 벡터 집합이 각각 정규직교다. |
| Schmidt 계수·Schmidt coefficient | \(s_r\ge0\)이며 \(\sum_rs_r^2=1\). 0이 아닌 계수 수가 Schmidt rank다. |
| 국소 연산·local operation | 한 부분계에만 작용하는 연산. 여기서 local은 물리적 거리의 모든 의미를 포함하지 않는다. |
| 복제 불가능성·no-cloning | 모든 미지의 상태를 동일하게 복제하는 하나의 물리 연산이 존재하지 않는다는 제약. |
| Clifford·클리퍼드 | Pauli 연산자를 켤레변환으로 Pauli 연산자로 보내는 게이트의 부류. H·S·CNOT이 대표적이다. |
| 고전 모사·classical simulation | 양자 과정의 특정 출력이나 샘플을 고전 계산으로 얻는 일. 모든 진폭 출력과 샘플 생성은 다른 과제다. |
| 회로 깊이·circuit depth | 동시에 실행 가능한 게이트들을 층으로 묶었을 때 필요한 순차 층 수. 게이트 총수와 다르다. |

특히 혼합 상태의 “분리 가능”을 하나의 곱 상태와 혼동하지 않는다. 다른 용례는 [통합 용어집](../glossary.md)에서 확인한다.

## 유도 1: 두 큐비트와 부분계의 상태

기저 순서는 \(|00\rangle,|01\rangle,|10\rangle,|11\rangle\)로 고정한다. 첫 큐비트는 왼쪽 비트다. 그러면

$$
(a|0\rangle+b|1\rangle)\otimes(c|0\rangle+d|1\rangle)
=ac|00\rangle+ad|01\rangle+bc|10\rangle+bd|11\rangle.
$$

복소수 네 개가 곱의 형태를 만족하지 않으면 단일 큐비트 두 개의 독립 상태로 설명할 수 없다. 첫 큐비트에 H, 첫 큐비트를 control로 CNOT을 적용하면

$$
|00\rangle\xrightarrow{H\otimes I}
\frac{|00\rangle+|10\rangle}{\sqrt2}
\xrightarrow{\mathrm{CNOT}_{A\to B}}
|\Phi^+\rangle=\frac{|00\rangle+|11\rangle}{\sqrt2}.
$$

이를 곱으로 쓴다고 가정하면 \(ac=bd=1/\sqrt2\)지만 \(ad=bc=0\)이어야 한다. 앞 조건은 네 계수를 모두 0이 아니게 만들므로 뒤 조건과 모순이다. Bell 상태는 얽혔다.

부분 trace를 계산하려면 먼저 규칙을 적는다.

$$
\operatorname{Tr}_B\bigl(|a\rangle\langle a'|\otimes
|b\rangle\langle b'|\bigr)
=|a\rangle\langle a'|\langle b'|b\rangle.
$$

Bell 밀도행렬은 \((|00\rangle\langle00|+|00\rangle\langle11|+|11\rangle\langle00|+|11\rangle\langle11|)/2\)다. 가운데 두 항은 B의 \(\langle1|0\rangle\) 또는 \(\langle0|1\rangle\) 때문에 0이 된다. 따라서

$$
\rho_A=\frac12(|0\rangle\langle0|+|1\rangle\langle1|)=I/2.
$$

전체 순도는 1인데 부분계 순도는 1/2다. 전체가 순수하다는 사실과 각 부분이 순수하다는 사실은 다르다. 부분 trace의 정의는 모든 A 관측량에 대해 \(\operatorname{Tr}(\rho_AO_A)=\operatorname{Tr}[\rho_{AB}(O_A\otimes I)]\)를 보장한다. 실제로 “B를 보지 않는다”는 실험 의미와 일치한다.

## 완전 예제 1: 같은 상관이지만 다른 상태

Bell 상태와

$$
\rho_{\rm mix}=\frac12|00\rangle\langle00|+
\frac12|11\rangle\langle11|
$$

를 비교하자. 두 상태 모두 Z를 측정하면 00·11이 각각 절반이며, 각 부분계는 \(I/2\)다. 하지만 \(X\otimes X\)는 00과 11을 교환하므로 \((X\otimes X)|\Phi^+\rangle=|\Phi^+\rangle\)이고 Bell의 XX 평균은 1이다. 혼합에서는 \(\langle00|XX|00\rangle=\langle11|XX|11\rangle=0\)이므로 평균이 0이다. 두 큐비트 모두 H 후 Z 측정을 하면 이 차이를 읽는다.

더 엄밀하게, 모든 분리 가능 상태는 \(\langle XX+ZZ\rangle\le1\)을 만족한다. 곱 상태의 Bloch 벡터를 \(\mathbf a,\mathbf b\)라 하면 왼쪽은 \(a_xb_x+a_zb_z\)다. Cauchy–Schwarz 부등식으로 \(\sqrt{a_x^2+a_z^2}\sqrt{b_x^2+b_z^2}\le1\)이다. 혼합해도 평균의 상계는 유지된다. Bell은 2이므로 이 상계를 위반한다. 따라서 \(W=I-XX-ZZ\)는 이 예제의 얽힘 witness다. 실제 데이터에서 1을 조금 넘었다면 측정 편향과 통계 오차까지 확인해야 한다. 계산 기저 상관 하나만으로 얽힘을 선언하는 것과는 근거가 다르다.

## 유도 2와 완전 예제 2: Schmidt 계수로 판정하기

일반 순수 상태를 \(|\psi\rangle=\sum_{a,b}C_{ab}|a\rangle|b\rangle\)라 쓰자. 계수 행렬 C의 특잇값 분해 \(C=UDV^\dagger\)에서 \(D_{rr}=s_r\)라 두면

$$
|\psi\rangle=\sum_rs_r|u_r\rangle|v_r\rangle,
\quad
|u_r\rangle=\sum_aU_{ar}|a\rangle,
\quad |v_r\rangle=\sum_bV_{br}^*|b\rangle.
$$

복소 켤레가 B 쪽에 들어간다는 점을 확인한다. 직교성으로 부분 trace를 취하면 \(\rho_A=\sum_rs_r^2|u_r\rangle\langle u_r|\)다. 따라서 부분계의 고유값은 Schmidt 계수의 제곱이다. 계수가 하나만 있으면 곱 상태이고, 두 개 이상이면 얽힌 순수 상태다.

예를 들어 \(|\psi\rangle=(\sqrt3|00\rangle+|11\rangle)/2\)는 이미 Schmidt 형태다. 계수는 \(\sqrt3/2,1/2\)이며 부분 상태는 \(\operatorname{diag}(3/4,1/4)\)다. 순도는 5/8이고 얽힘 엔트로피는

$$
S(\rho_A)=-\sum_rs_r^2\log_2s_r^2
=-\frac34\log_2\frac34-\frac14\log_2\frac14\simeq0.811
$$

비트다. Bell은 두 계수가 같아 엔트로피가 1이다. 반면 \((|00\rangle+|01\rangle)/\sqrt2=|0\rangle|+\rangle\)는 계수 행렬의 rank가 1이어서 얽히지 않았다.

중요한 반례가 있다. 위 고전 혼합도 부분 상태가 \(I/2\)여서 엔트로피 1이다. 그러나 분리 가능하다. 부분 엔트로피를 얽힘의 양으로 직접 읽는 규칙은 여기서 다룬 전체가 순수한 이분 상태에 한정된다. 혼합 상태 전체에 그대로 적용하면 틀린다.

## 유도 3: 복제 불가능성과 무신호성

모든 상태를 복제하는 하나의 유니터리 U가 있다고 가정하자. 두 입력에 대해 \(U|\psi\rangle|0\rangle=|\psi\rangle|\psi\rangle\), \(U|\phi\rangle|0\rangle=|\phi\rangle|\phi\rangle\)다. 유니터리는 내적을 보존하므로 \(c=\langle\psi|\phi\rangle\)에 대해 \(c=c^2\)여야 한다. 서로 다른 비직교 상태는 \(0<|c|<1\)이어서 불가능하다. 예를 들어 0과 +의 내적 \(1/\sqrt2\)는 복제 후 1/2가 되어 내적 보존과 모순이다. 보조 환경까지 포함한 복제 채널도 이 모순을 피하지 못한다. 환경의 최종 상태 내적을 e라 두면 \(c=c^2e\)이고 \(|e|\le1\)이어야 하므로, \(0<|c|<1\)에서 모순은 유지된다.

CNOT이 \(|0\rangle|0\rangle\to|00\rangle\), \(|1\rangle|0\rangle\to|11\rangle\)을 수행하는 것은 모순이 아니다. 두 입력이 직교하기 때문이다. +를 입력하면 \(|+\rangle|+\rangle\) 대신 Bell 상태가 나온다. 알려진 회로를 다시 실행하는 일도 미지 상태를 복제하는 것과 다르다. 따라서 양자 데이터 학습의 표본 수에는 매번 새 상태를 공급할 수 있는지도 적어야 한다.

B에 trace-preserving 연산을 적용해도 결과를 A로 보내지 않으면 A의 상태는 바뀌지 않는다. 상태 변화를 여러 행렬로 나누어 나타내는 Kraus 연산자 \(K_m\)가 \(\sum_mK_m^\dagger K_m=I\)를 만족하면 A 관측량의 평균은

$$
\sum_m\operatorname{Tr}[\rho_{AB}(O_A\otimes K_m^\dagger K_m)]
=\operatorname{Tr}[\rho_{AB}(O_A\otimes I)]
$$

로 유지된다. 특정 B 결과에 조건을 걸면 A의 조건부 상태가 달라질 수 있지만 그 결과를 고전 통신으로 알려야 한다. 얽힘 자체가 초광속 메시지를 제공하지 않는다.

## 얽힘과 고전 계산 난도 사이의 간격

complex128 진폭은 16바이트이므로 일반 \(n\)큐비트 상태벡터는 \(16\times2^n\)바이트다. 30큐비트는 16GiB, 40큐비트는 16TiB이며 작업 버퍼는 별도다. 그러나 이는 일반 상태를 전부 저장하는 모사 방식의 비용이다. 모든 회로에 필요한 최소 고전 비용의 하한이 아니다.

Clifford 게이트와 계산 기저 초기화·Pauli 측정으로 제한한 stabilizer 회로는 얽힘이 커도 다항 자원으로 모사할 수 있다. 이 반례는 [Gottesman의 Heisenberg 표현](https://arxiv.org/abs/quant-ph/9807006)의 핵심 맥락이다. 비Clifford 게이트가 하나 있다고 바로 어렵다는 역명제도 성립하지 않는다. 깊이, 연결성, 측정 대상, 요구 정밀도와 회로 구조를 같이 봐야 한다. 얽힘이 제한된 상태에서는 tensor network가 유리할 수 있지만 어떤 bipartition의 얽힘이 제한되는지도 중요하다.

QML 보고서에는 “얽힘을 사용했다”와 함께 얽힘이 어느 예측 성분을 바꾸었는지, 같은 효과를 고전 모델이 재현하는지, 무엇을 측정했는지를 기록한다. 단일 큐비트 회전과 얽힘 게이트의 보편성도 임의 연산을 적은 게이트로 합성할 수 있다는 보장은 아니다.

## 연습문제와 풀이

### 문제 1. 곱 상태 찾기

\((|00\rangle+|01\rangle+|10\rangle+|11\rangle)/2\)의 Schmidt rank와 부분 상태를 구하라. **힌트:** 네 진폭을 2×2 행렬로 놓는다.

**풀이:** 모든 원소가 1/2인 계수 행렬은 rank 1이다. 상태는 \(|+\rangle\otimes|+\rangle\)로 분리된다. A 부분 상태는 \(|+\rangle\langle+|\)이며 순도는 1이다. 계산 기저 결과가 네 가지라고 해서 얽힘이 있는 것은 아니다. 가능한 결과 수와 Schmidt rank는 다른 양이다.

### 문제 2. 얽힘 검출의 통계

이상 측정으로 \(\langle ZZ\rangle=0.9\), \(\langle XX\rangle=0.7\)을 얻었다. 분리 가능 상계와 비교하라. 각 평균에 절대오차 0.1 보장이 있다면 결론은 유지되는가? **힌트:** 가장 불리한 실제 평균을 사용한다.

**풀이:** 관측합은 1.6으로 상계 1보다 크다. 각각 0.1씩 과대추정했더라도 실제 합은 1.4 이상이므로 여전히 얽힘을 검출한다. 다만 이 오차 보장이 동시에 성립하는 신뢰도와 측정 편향 처리가 전제다. Z 자료만으로는 같은 결론이 나오지 않는다. 분리 가능 혼합도 큰 ZZ 상관을 가질 수 있다.

### 문제 3. 복제와 재준비

알려진 회로로 Bell 상태를 1,000개 준비하는 일과, 주어진 미지 상태 하나를 1,000개로 복제하는 일의 차이를 설명하라. **힌트:** 입력 자원과 반복 가능한 준비 절차를 구별한다.

**풀이:** 첫 과정은 매번 새 \(|00\rangle\)에 알려진 H·CNOT 회로를 적용한다. 소비하는 초기화·게이트 자원을 1,000번 지불하며 원본을 복제하지 않는다. 둘째 과정은 준비 정보를 모르는 단일 상태만으로 새 사본을 얻으려 하므로 일반적으로 no-cloning에 막힌다. 따라서 “shots 1,000회”에는 재준비 접근의 존재가 숨어 있다.

### 문제 4. 메모리 계산과 과도한 결론

25큐비트 순수 상태벡터와 일반 밀도행렬을 complex128로 저장하는 메모리를 구하라. 이 결과로 모든 25큐비트 회로가 어려운가? **힌트:** 밀도행렬 원소 수는 진폭 수의 제곱이다.

**풀이:** 상태벡터는 \(16\times2^{25}=2^{29}\)바이트, 즉 512MiB다. 밀도행렬은 \(16\times4^{25}=2^{54}\)바이트, 즉 16PiB다. 이 값은 해당 자료구조를 조밀하게 저장하는 비용이며 stabilizer나 낮은 rank 구조까지 강제로 이 방식으로 모사할 필요는 없다. 저장 표현의 지수 증가가 모든 과제의 계산 하한을 증명하지 않는다.

## 학습 완료 점검

- Bell 상태의 부분 trace에서 사라지는 두 항에 직교 내적을 명시하면 통과다. 실패하면 유도 1로 돌아간다.
- 순수 상태의 Schmidt 계수와 부분 밀도행렬의 고유값 관계를 제곱으로 연결하면 통과다. 혼합 상태 엔트로피를 무조건 얽힘으로 읽으면 예제 2를 반복한다.
- CNOT이 고전 기저 비트를 복사하면서 미지 중첩을 복제하지 못하는 이유를 + 입력으로 보이면 통과다.
- 얽힘이 커도 모사 가능한 회로 부류를 조건과 함께 하나 제시하면 통과다. “모든 양자 회로가 쉽다”로 반대로 확대하지 않는다.

## 원문 읽기

- [IBM Quantum Learning, Multiple systems: Quantum information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/multiple-systems/quantum-information): tensor products와 entanglement 설명을 읽고 본문의 기저 순서로 다시 쓴다. SDK의 비트열 순서는 별도로 확인한다.
- [Watrous 공개 원고](https://cs.uwaterloo.ca/~watrous/TQI/): Chapter 1의 tensor product·singular value decomposition과 Chapter 6의 bipartite entanglement는 선택 심화 읽기다. 위 두 큐비트 유도는 이 노트만으로 따라갈 수 있다.
- [Wootters and Zurek, A single quantum cannot be cloned (1982)](https://doi.org/10.1038/299802a0): 복제 불가능성의 원 논문. 본문의 내적 증명은 교육용 재구성이다.
- [Gottesman, The Heisenberg Representation of Quantum Computers (1998)](https://arxiv.org/abs/quant-ph/9807006): stabilizer·Clifford 표현의 원문을 읽는 심화 자료다. 본 노트는 일반 모사 알고리즘을 구현하거나 성능을 재측정하지 않았다.

[이전](02-qubits-gates-and-measurement.md) · [목차](../README.md) · [다음: 데이터 인코딩](04-data-encoding-and-loading.md)
