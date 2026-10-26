# 시간발전 알고리즘 근거 및 교육 계산 대조

근거 확인: 2026-10-26. 원 논문 결과, 리뷰의 해석, 새 교육 계산을 구분한다. 이 기록과 계산은 flat-band 재료 결과의 재현이나 두 알고리즘의 결합 성능 주장이 아니다.

## 1. 원문과 비교하는 오차

- Carlos A. Piñeiro Moreno, Pascal Krause, Annika Bande, **Norm-Aware Product Formulas for Hamiltonian Simulations**, [arXiv:2610.31070v1](https://arxiv.org/abs/2610.31070v1), 제출 2026-10-22. PDF/HTML 표지 날짜는 10-21이다. [본문](https://arxiv.org/html/2610.31070v1) §II.2 식(13)–(17), §II.3 식(20)–(24), §II.4, §III.2 식(30)–(35)·Fig.3·Table1, Appendix B 식(51)–(53)을 대조했다. 동료평가 완료로 표시하지 않는다.
- Brian Coyle 외, **Problem-aware sampling for bias and variance reduction in randomised Hamiltonian simulation**, [arXiv:2610.31515v1](https://arxiv.org/abs/2610.31515v1), 제출 2026-10-22. [본문](https://arxiv.org/html/2610.31515v1) §II 식(1)–(7), §III 오류·타당성, §IV Fig.6, §V–VI, Appendix I·J를 대조했다.

| 항목 | Norm-aware product formulas | StateDRIFT |
|---|---|---|
| 바꾸는 대상 | 주어진 Hamiltonian 분해의 결정론적 지수함수 순서·시간 계수 | Pauli 시간발전 항의 선택 확률; 회전각도 확률에 맞춰 보정 |
| 활용할 정보 | 큰 항과 작은 항의 노름 계층 및 교환자 | 초기상태와 목표 관측량의 응답·교환자·저차 밀도 |
| 주요 오류 | 이론은 전파 연산자의 operator norm; XY 수치는 Frobenius norm; 분자 수치는 특정 초기상태 전파의 ℓ2 거리 | 특정 초기상태·관측량의 기대값 편향 B 및 trajectory 분산 V; MSE=B²+V/M |
| 제한 | 충분히 짧은 단계·분해·노름 비·교환자 및 항 구현 비용 | 4차 절단의 타당성, λT, 정보 추정·분포 최적화 비용; 다른 관측량 재사용의 조건 |
| 비용 해석 | 지수함수 개수는 native gate·라우팅·orbital rotation 비용과 다름 | 깊이 N과 trajectory 수 M은 별개; 측정 샷 잡음·상태준비도 별도 |

분자 4.5–8배는 H₂·LiH·BeH₂·H₂O·NH₃의 STO-3G/DF, T=1 au·N=100, Haar orbital rotation을 가한 HF determinant 초기상태 10개의 **평균 상태 ℓ2 전파오차 감소**다. 고전 ffsim 수치이며 QPU 속도 배수가 아니다. Table1의 분자별 αk는 고정 입자수 sector의 **Frobenius norm 비**이며 임의로 바꾼 공통 α의 실험이 아니다. v1 §V는 연구 코드 저장소가 당시 비공개라고 밝힌다. 여기서는 해당 분자 계산을 재실행하지 않았다.

StateDRIFT의 BeH₂ 11,201→983은 14-qubit·STO-3G/JW·짧은 시간의 가중 점유량 기준 수치에서 예상한 2-qubit gate 수다. 정확 밀도 입력 benchmark와 surrogate/shadow 배치를 구분한다. Appendix J는 두 기하 사이 궤도 정합을 하지 않은 quench를 방법 benchmark로 명시한다. 실제 결합 신장에 대한 분자 응답이나 평탄밴드 재료 계산으로 읽지 않는다. 실용 타당성 지표는 엄밀 절단오차 bound 자체와 구분한다.

## 2. ‘절반씩 감싼다’와 Strang 2차를 구분

δ=T/N, H=H₀+α(H₁+H₂)라 하자. 아래 곱은 쓰인 순서의 행렬곱이며 상태에는 오른쪽 인자부터 작용한다.

```math
L(δ)=e^{-iH₀δ}e^{-iαH₁δ}e^{-iαH₂δ}.
P(δ)=e^{-iH₀δ/2}e^{-iαH₁δ}e^{-iαH₂δ}e^{-iH₀δ/2}.
S(δ)=e^{-iH₀δ/2}e^{-iαH₁δ/2}e^{-iαH₂δ}e^{-iαH₁δ/2}e^{-iH₀δ/2}.
```

P는 논문의 **1차 Partial–Strang**이다. 가운데 H₁,H₂를 역순으로 대칭화하지 않았으므로 일반적으로 S와 같지 않다. 작은 항이 단 하나이거나 서로 가환하는 특별한 경우와 일반 L≥2를 구분한다. P의 국소 오차는 두 항을 남겨 읽어야 한다.

```math
||U(δ)-P(δ)|| ≤ C₁ α²δ² + C₂|α|δ³ + higher terms.
||U(T)-P(δ)^N|| ≤ C₁ α²T²/N + C₂|α|T³/N² + higher terms.
```

상수는 고정한 항·노름·교환자에 의존한다. δ→0에서 α를 고정하면 첫 항이 지배하지만, δ를 고정해 α만 아주 작게 하면 둘째 항이 지배할 수 있다. 따라서 ‘α가 작으면 언제나 α² 오차’라는 설명은 피한다. 원문 Appendix B도 이 교차를 다룬다.

S는 일반 완전 Strang 2차다. 논문의 별도 최적 λ 2차 공식(식22)은 작은 항의 대칭 블록을 두 번 배치하고 λ=1/2−√3/6를 써 선형 α의 leading third-order contribution을 소거한다. 이것을 P의 단순한 다른 이름으로 부르지 않는다. λ 공식도 항의 구현 비용과 더 많은 지수함수를 지불한다.

## 3. 새 교육 계산: 정확 평균과 노름을 섞지 않기

소스: `artifacts/compare_dynamics.py`. 결과: `artifacts/results/dynamics_comparison.json`. Python 3+numpy만 필요하다. 실행 예:

```sh
python3 2026-10-26_flat-bands-and-targeted-dynamics/artifacts/compare_dynamics.py
```

교육 모형은 **1-qubit H=Z+αX+αY**, ħ=1이며 단위 없는 모형이다. 초기상태는 cos(1.05/2)|0>+exp(0.38i)sin(1.05/2)|1>이다. H의 세 성분은 서로 비가환한다. 특정 분자나 두 논문의 benchmark 재현이 아니다.

- 고정 T=1·α=0.2에서 N을 늘렸을 때 전파 operator 2-norm 오차의 log-log 기울기는 Lie −0.99973, P −0.99266, S −2.00005, 최적 λ −1.99999였다(N=32–256 fitting). 이는 이 모형에서 1차와 2차를 구분한다.
- N=16의 상태 ℓ2 오차는 Lie 0.01485170, P 0.00238632, S 0.00017549, λ 0.00001408이다. 인접 같은 지수함수를 병합한 개수는 각각 48·49·65·129다. 같은 N이 같은 자원 예산을 뜻하지 않는다. 이 SU(2) 예에서는 state ℓ2와 operator 2-norm 값이 수치상 같지만 일반 성질로 확장하지 않는다.
- 확률 계산은 T=0.4·N=4·α=0.2에서 수행했다. `Vj=exp[-i cj δ Pj/qj]`, `E(ρ)=Σj qj VjρVj†`의 **정확 평균 채널 E^N**을 계산한다. 평균 unitary `ΣqjVj`를 N번 곱하는 방식이 아니다.
- 분산은 동일한 term index를 두 replica에 적용하는 **2-copy 평균 채널**로 `E[<O>trajectory²]`를 얻어 계산한다. 최종 양자 측정 샷 잡음은 포함하지 않는다. 표시한 M=200은 독립 회로 trajectory 개수다.
- 분포 최적화는 정확한 평균·분산을 모두 아는 교육용 oracle 탐색이다. `q≥0.2 qvan` 조건에서 `bias²+V/200`을 줄인다. **StateDRIFT의 4차 밀도 기반 allocator를 구현한 것이 아니며 전역 최적이라는 주장도 하지 않는다.** 새 모형으로 관측량 맞춤 설계의 이득과 재사용 손해를 분리한다.

| 분포 | q(Z,X,Y) | Z의 MSE | X의 MSE |
|---|---|---:|---:|
| 계수 기반 qDRIFT | 0.714286, 0.142857, 0.142857 | 0.00151577 | 0.00127419 |
| Z 목표 교육 탐색 | 0.315497, 0.354291, 0.330211 | 0.00078901 | 0.00464612 |
| X 목표 교육 탐색 | 0.776217, 0.041251, 0.182531 | 0.00485711 | 0.00084950 |

같은 H·초기상태·T·N에서 한 관측량에 맞춘 분포가 다른 관측량에는 손해를 줄 수 있다. 이 수치를 StateDRIFT 논문의 결과, 하드웨어 성능, 또는 최선의 일반 알고리즘 비교로 쓰지 않는다. 관측량 bias와 상태 ℓ2 오차는 다른 척도다. 정규화된 순수상태에서 `|<O>ψ−<O>φ|≤2||O||·||ψ−φ||` 같은 상계는 가능하지만 두 오차를 동일시할 수 없다. 확률 평균 결과는 일반적으로 혼합상태이므로 단일 근사 unitary의 오차로 표시하지 않는다.

## 4. flat bandwidth에서 알고리즘 노름으로 자동 연결하지 않기

교육 반례 `H(k)=A[cos(k)Z+sin(k)X]`는 모든 k에서 고유에너지가 ±A라 두 밴드의 폭 W가 모두 0이다. 그런데 operator 2-norm은 |A|이고 A는 얼마든지 클 수 있다. k=π/4에서 두 성분의 노름은 |A|/√2로 같고, 두 성분의 교환자 노름은 A²이다. 밴드폭 0만으로 ‘작은 Hamiltonian’, ‘분해 성분의 노름 계층’, ‘작은 Trotter 교환자’가 따라오지 않는다.

이 반례의 Pauli 행렬은 두 궤도/부분격자 Bloch 모형의 대수적 표현이다. 실제 재료의 다체 Hamiltonian을 JW 변환했다는 뜻이 아니다. 평탄밴드의 kinetic scale과 상호작용 비를 논하는 물리 설명에서, 특정 DF/Pauli 분해·저에너지 투영·초기상태·관측량을 지정한 뒤 별도로 알고리즘 조건을 점검해야 한다.

## 5. 실제 검증 범위 및 그림

실행 결과의 assertion은 모두 통과했다. Pauli 지수함수의 해석식 대조 최대 오차 1.76e−16, N=3의 27개 trajectory를 직접 열거한 독립 경로와 평균/분산 channel 결과의 최대 차이 4.17e−16, 평탄밴드 반례의 고유값 대조 최대 오차 1.12e−16이다. 이는 같은 제작 코드 안의 독립 계산 경로 대조이며 별도 사람의 독립 검토를 뜻하지 않는다. root는 별도 SO(3) 회전·1차 및 2차 모멘트 계산으로 교육용 확률 전파 결과를 재계산했고, 최대 차이 1.06e−15를 `independent-dynamics-audit.json`에 기록했다.

한영 SVG는 `artifacts/figures/`에 있다.

1. `product_formula_comparison_{ko,en}.svg`: 왼쪽 state ℓ2 오차 vs N, 오른쪽 operator 2-norm 오차 vs α; 분모·고정량이 다르다.
2. `observable_sampling_comparison_{ko,en}.svg`: 같은 선형 MSE 막대 축에서 bias²와 trajectory V/M을 분리; 교육용 oracle 분포임을 그림 안에도 표시했다.
3. `flat_band_norm_counterexample_{ko,en}.svg`: 고유에너지 ±A는 평평하지만 성분 계수는 k에 따라 변한다. 실제 재료 시뮬레이션이 아니다.

숫자 검증·SVG 생성·별도 렌더 출력 검수와 한국어 원고의 수치·문장 반영을 완료했다. 감수 범위는 `editorial-audit.md`에 기록했다. 표지·영문 전문·최종 리뷰 PDF와 리뷰허브 새 기사 게재는 아직 진행하지 않았다.
