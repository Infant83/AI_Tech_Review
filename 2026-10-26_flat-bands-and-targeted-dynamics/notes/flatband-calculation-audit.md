# 평탄밴드 교육 계산 독립 감사

2026-10-26. 검토 대상: `artifacts/compare_flatbands.py`, `artifacts/results/flatband-toy.json`, `figures/flatness-and-topology.svg`. 검토자는 제작 코드의 eigenvector-link 함수와 다른 **해석 Berry 곡률 적분** 및 **해석 band projector**로 수치를 대조했다. 원 제작 코드나 결과 파일은 수정하지 않았다. 이 감사는 2-band 교육 모형의 수학·수치·표기 검토이며 실제 재료의 DFT·ED, fractional Chern insulator, FCI(full CI), QPU 실험의 재현이 아니다.

## 판정

차단할 오류는 발견하지 않았다. 명시된 격자 방향과 링크 convention에서 lower-band C=−1이 해석 곡률 적분과 일치한다. Spectral flattening·격자 수렴·무작위 gauge·양의 scale 변경 검사가 일관된다. 그림도 직접 렌더해 확인했다. 아래 부호 및 범위 조건을 본문·캡션에 유지한다.

## 1. 방향과 부호

코드의 `indexing="ij"`에서 axis 0은 kx, axis 1은 ky다. `roll(...,-1)`은 현재 점에서 양의 k 방향 이웃을 읽는다. 정규화 링크 `Ux=<u(k)|u(k+dx)>/|...|`와 Uy의 곱은

```math
Ux(k) Uy(k+dx) Ux(k+dy)* Uy(k)*
```

이므로 +kx→+ky→−kx→−ky의 양의 plaquette 방향이다. `C=sum(arg(loop))/(2π)`라는 명시된 convention에서 코드의 음의 부호는 맞다. 반대 Berry connection convention을 쓰는 문헌의 C 부호를 설명 없이 가져오지 않는다. 고유벡터 복소켤레가 C를 뒤집는 검사는 부호 일관성 검사이며, 복소켤레는 단순 U(1) gauge 변경과 같지 않다.

## 2. eigenvector 링크를 사용하지 않은 적분 대조

`d=(sin x,sin y,−1+cos x+cos y)`에 대해 lower-band 해석 곡률을 직접 계산했다.

```math
Omega_minus(x,y) = - d·(partial_x d × partial_y d)/(2 |d|^3)
                 = -[cos x + cos y - cos x cos y]/(2 |d|^3).
C = integral_BZ Omega_minus dx dy/(2 pi).
```

동일한 주기 격자 `k=−π+2πj/n`에서 직사각 적분한 결과는 다음과 같다. 이 계산에는 band eigenvector나 원 코드의 `chern` 함수를 사용하지 않았다.

| n×n | 원 코드 link C | 해석 곡률 적분 |
|---|---:|---:|
| 31×31 | −1.0 | −0.999999998123179 |
| 61×61 | −1.0 | −1.0 |
| 121×121 | −1.0 | −1.0 |
| 241×241 추가 감사 | — | −0.9999999999999999 |

별도 해석 projector `P_minus=(I−d_hat·sigma)/2`와 원 코드의 `|u_minus><u_minus|`도 비교했다. 최대 원소 오차는 n31 6.67e−16, n61 7.78e−16, n121 8.89e−16, n241 1.12e−15 이하였다. 이 검사로 lower-band 선택과 flattening 뒤 eigenvector의 의미를 함께 확인한다.

재실행 가능한 독립 적분의 핵심은 다음과 같다(Python+numpy).

```python
k = np.arange(n)*(2*np.pi/n)-np.pi
x, y = np.meshgrid(k, k, indexing="ij")
r2 = np.sin(x)**2 + np.sin(y)**2 + (-1+np.cos(x)+np.cos(y))**2
omega = -.5*(np.cos(x)+np.cos(y)-np.cos(x)*np.cos(y))/r2**1.5
c = omega.sum()*(2*np.pi/n)**2/(2*np.pi)
```

## 3. flattening·gauge·격자

- m=−1에서 d(k)는 0이 되지 않는다. `d/|d|`는 양의 크기를 바꾸고 projector를 유지하므로 원 Hamiltonian과 flattening 모형의 C가 같다. 원 JSON의 31/61/121 격자 모두 −1이다.
- 무작위 점별 U(1) 위상은 plaquette flux를 4.3e−16 이하에서만 바꾼다. 최소 이웃 overlap은 0.99487→0.99867→0.99966으로 singular-link 위험이 없다.
- link 방식에서 정확한 정수 C만 유지되는 것은 local curvature 수렴을 모두 보장하지 않는다. 여기서는 위의 독립 곡률 적분도 함께 확인했다.
- 그림은 **41×41** 격자다. 이 별도 격자도 C=−1이며 curvature 추정 범위는 −0.501958~+0.055628이다. 색 막대는 양·음 대칭 ±0.50(표시 반올림) 범위를 사용한다. JSON의 수렴 격자 31/61/121과 그림 격자를 혼동하지 않는다.

## 4. norm 반례의 범위

별도 감사 실행에서 `scale=20`을 실제로 넣었다. n61에서 lower bandwidth는 3.20e−14(부동소수점 오차), operator spectral norm은 20.000000000000018, gap은 39.99999999999998, C는 −1이었다. scale=1에서는 norm≈1, gap≈2다. 따라서 양의 rescaling으로 W=0과 C를 유지하면서 norm을 바꾸는 문장은 성립한다.

이것은 밴드폭 W가 Hamiltonian norm을 정하지 않는다는 반례다. spectral flattening은 일반적으로 장거리 hopping을 필요로 하므로, 해당 flat model이 짧은 범위 재료에서 실현되거나 효율적인 양자 회로를 준다는 주장으로 확대하지 않는다. 또한 flat-band 폭이 작다는 사실만으로 선택한 다체 DF/Pauli 분해의 항별 norm hierarchy나 작은 교환자를 보장하지 않는다.

## 5. 출력 확인

`flatness-and-topology.svg`를 sharp로 1200×620 PNG에 렌더한 뒤 직접 보았다. 에너지 ±1, 두 모형의 C=0/−1, kx/ky 방향, curvature 부호·대칭 색 범위, W=0·gap=2 및 scale 조건, 장거리 hopping 한계와 교육 모형 표기가 읽히며 잘림·겹침을 발견하지 않았다. 렌더 QA PNG는 임시 경로에만 두었다. 실제 공개 페이지의 모바일·PDF 검토는 이 감사에 포함하지 않는다.
