# Flat-band source check · 2026-10-26

검토: dqb_today_materials_source. 내부 근거 노트이며 공개 배포 대상이 아니다. 원문·SI·공개 심사 답변·공개 코드·PES 원자료를 대조했다. DFT, ED, LLGS 계산을 독립 재실행하지 않았다. PDF 스킬로 원문 표·피규어를 렌더해 확인하고, XLSX는 원본을 수정하지 않고 셀 값을 읽었다.

## 1. 판본과 직접 출처

- Bao, K.; Shi, R.; Wang, H.; Guo, J.; Wang, J. *Flat Chern bands and correlated states in spiral magnet*. Communications Physics, accepted Article in Press, 2026-10-25. DOI: https://doi.org/10.1038/s42005-026-02924-w . 최종 조판본 전 accepted 판이다.
- Accepted PDF: https://www.nature.com/articles/s42005-026-02924-w_reference.pdf (10쪽).
- SI: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs42005-026-02924-w/MediaObjects/42005_2026_2924_MOESM2_ESM.pdf (34쪽).
- 공개 심사 파일: 같은 MediaObjects 경로의 `42005_2026_2924_MOESM1_ESM.pdf` (19쪽).
- 선행 프리프린트: https://arxiv.org/abs/2409.01741 ; v1 2024-09-03, v3 2025-11-05. 2026-10-25는 새 저널 공개일이며 연구 전체의 최초 공개일이 아니다. 저널 판에서 단순 s-orbital 기작·canting 검토·substrate/U 검토·LLGS 설명이 보강됐다.
- 원자료: https://doi.org/10.5281/zenodo.21199721 . 실제 record/API 확인. `Figure 4.xlsx`, `Fig3_1.txt`, `Table2.txt`, CIF 등 포함.
- 코드 실제 경로: https://github.com/kejie425/Supplementary_code/tree/10f4ecd1da985d629eab6c0707b9378951ef8ea6/Supplementary%20Code . 논문에 인쇄된 `/Supplementary` 경로와 다르다. 이 commit에 ED, PES, Berry curvature, quantum trace, FM TB, LLGS Python이 있다. `Exact_Diagonalization.py`는 별도 `DFT_data/frozen_afm/frozen` 입력을 참조하며 이 폴더는 코드 저장소에 없다.
- 재사용 권한: Zenodo record API는 `access_right=open`, `license.id=cc-by-4.0`을 반환했다. 따라서 이 데이터의 수치를 인용하고 독자적인 계수 도표를 만드는 것은 논문 그림의 NC-ND 재사용과 구별된다. 원자료 attribution과 DOI를 유지한다. 저널 accepted article의 표기 라이선스는 CC BY-NC-ND 4.0이며 원도표·PDF는 리뷰에 복사하지 않았다. 공개 GitHub tree에는 LICENSE 파일이 없으므로 공개됐다는 이유로 저자 코드의 복사·변형 배포 권한을 가정하지 않는다. 새 계수 script는 저자 코드를 복사하지 않고 표준라이브러리로 별도 작성했다.

## 2. 핵심 기작: 공면 스핀은 scalar chirality를 만들지 않는다

세 국소 스핀이 한 평면에 놓이면 `S1·(S2×S3)=0`이다. 여기서 (100) 평면은 단층 표면과 다른 수직 평면이다. 각 스핀에 표면 밖 성분이 있어도 세 스핀끼리는 공면일 수 있다. `out-of-plane component`를 noncoplanar texture로 바꾸어 쓰면 안 된다.

Accepted 본문 식(1)·Electronic structures and band geometry, SI S2.2.4 식(S7–S10)·Fig. S19가 기작의 직접 위치다. 공면 순서에서 scalar-chirality 항은 0이고, SOC gauge field와 공간적으로 바뀌는 스핀 방향의 결합 항이 남는다. 자기질서는 시간반전을 깨지만 SOC가 없는 공면 질서의 잔류 대칭 때문에 그것만으로 Chern 밴드가 보장되지는 않는다. SOC가 이 자성 배경과 함께 축퇴를 열고 비자명한 곡률을 만든다는 설명이 적합하다.

Fig. S19는 삼각격자 s-orbital 교육 모형을 단계적으로 비교한다: hopping → hopping+120° exchange → SOC 추가. 교환 배경에서 접힌 밴드의 축퇴가 남고 SOC 후 위상 갭이 열린다. 모형 값은 `J=10t, λi=t, λr=-2t`. Re 물질의 정량 fit 값이 아니라 기작을 보여주는 별도 단순 모형이다. 단순히 같은 밴드를 더 작은 BZ에 그리는 표기 변경만으로 분산이 물리적으로 줄어든다고 설명하지 않는다. 실제 자기 주기와 교환 배경이 Hamiltonian을 바꾼다.

## 3. 단입자 수치: Table 1·2, Fig. 2·3

ReAg2Cl6의 구조 원시격자 a=6.78 Å, 자기 초격자는 √3×√3×1, q=(1/3,1/3,0). Re moment는 약 2.9 μB. Table 1의 J1=2.35 meV, MAE=0.80 meV/unit cell, TN≈22 K, semiconductor gap Eg=1.24 eV는 각각 다른 양이다. 특히 Eg는 아래 인접 Chern 밴드 사이의 작은 분리 갭이나 many-body gap이 아니다.

| 밴드 | W (meV) | C | Berry-curvature fluctuation δB | 평균 trace T | 1/3 filling ED 판정 |
|---|---:|---:|---:|---:|---|
| 1st VB | 20.8 | −1 | 5.10 | 2.27 | FCI 근거, flux에 대한 전역 갭은 더 약함 |
| 1st CB | 22.7 | +2 | 3.81 | 2.87 | 이 논문의 해당 ED 대상 아님 |
| 2nd CB | 32.1 | −1 | 4.13 | 4.08 | commensurate 3×3×1 CDW |
| 3rd CB | 50.2 | −1 | 1.07 | 1.66 | FCI 근거, 더 견고한 flux gap |

T는 본문 식(3)의 BZ 적분 trace이며 국소 trace inequality 자체와 동일한 숫자 지표가 아니다. δB 하나만으로 phase를 결정할 수 없다. VB는 2nd CB보다 δB가 큰데도 다른 many-body 결과를 보인다.

저자들은 ε=10 가정에서 `U~e²/(εa)~0.12 eV`, `U/W≳2`를 제시한다. 이는 유전 환경을 가정한 상호작용 규모의 추정이다. DFT+U의 기본 U=1 eV와 구분해야 한다. 저널 표에는 각 밴드에 대한 최소 직접·간접 separation gap의 수치 표가 없다. Fig. 3에서 분리가 보인다는 사실만으로 `W≪U≪Δ_band`가 검증됐다고 쓰지 않는다. 제3 CB의 W=50.2 meV도 ‘정확히 평평’은 아니다.

## 4. 다체 계산: 무엇을 계산했고 무엇을 진단했나

Accepted Correlated states·Methods, Fig. 4, SI S3·Fig. S20가 직접 근거다. Re의 {a1g,eg} 중심 18 MLWF(3 sites×3 orbitals×2 spins)로 시작해 서로 다른 onsite orbital/spin 사이 density interaction만 남긴다. 장거리 Coulomb, band mixing과 완전히 채운 다른 밴드 기여는 이 계산에 포함되지 않는다. C=−1인 target band 하나에 투영한 ED다.

중요: 공개 심사 답변 PDF p.8(인쇄 p.6)의 flat-band-limit 설명과 공개 ED 코드의 Hamiltonian 조립을 대조했다. ED는 실제 W를 그대로 유지한 many-body 계산이 아니라 **분산을 제거한 flat-band limit**를 사용한다. 코드 `exact_diagonal`은 Bloch eigenvector의 form factor로 만든 상호작용 항을 조립하고 별도 ε(k) kinetic diagonal을 더하지 않는다. 따라서 Table 2의 W와 ED를 연결해 ‘50.2 meV의 실제 분산에도 FCI가 안정하다’고 주장할 수 없다.

대상은 ν=1/3, Nuc=4×6=24 및 3×9=27, Ne=8 및 9. 세 밴드 모두 3중의 낮은 상태군이 있으므로 **3중 축퇴만으로 FCI를 확정하지 않는다**. VB·3rd CB는 두 cluster의 ground-state momentum counting, PES, flux insertion으로 Laughlin-type FCI를 지지한다. 2nd CB는 27-cell momentum과 PES가 CDW 쪽이다. 두 크기의 결과는 유한계 근거이며 엄밀한 열역학극한 증명이 아니다.

PES는 Nuc=24, NA=3, NB=5로 나누고 3개 ground state의 혼합 density matrix를 부분 추적한다. SI S3.2·Fig. S20에서 2π flux마다 세 상태가 교환되고 6π 뒤 돌아오는 흐름을 확인한다. SI는 **3rd CB는 flux 전 구간의 global excitation gap, VB는 각 flux sector의 local gap**만 있다고 명시한다. VB와 3rd CB를 동일한 강도의 후보로 설명하지 않는다. Fig. 4·S20 에너지 축은 ΔE/U이며 many-body gap을 W나 1.24 eV semiconductor gap과 혼동하지 않는다. 실제 FCI 전이온도를 계산한 결과는 없다.

## 5. PES 원자료의 독립 계수 대조

Zenodo `Figure 4.xlsx`, `Sheet1`의 원자료를 읽었다. source workbook은 `/tmp/flatband-20261026/`에만 두고 저장소 공개 자산에 복사하지 않았다. ZIP XML numeric cell을 읽었으며 shared-string index를 숫자 0으로 잘못 포함하지 않도록 제외했다. 정확한 범위·SHA256·threshold는 후속 `artifacts/results/pes-counting.json`에 기록한다.

- VB: G3:G2026, 2024개 ξ. gap 아래 1088개. 경계 4.41856→5.10839.
- 3rd CB: O3:O2026, 2024개 ξ. gap 아래 1088개. 경계 3.72325→6.78571.
- 2nd CB: W3:W2026, 2024개 ξ. gap 아래 168개. 경계 2.01692→2.96012.
- (1,3)-admissible 원환계 3-particle counting: `24/(24−2·3) × binom(24−2·3,3) = 1088`.
- 서로 떨어진 세 CDW 배치에서 8 particles 중 3개를 남기는 counting: `3 × binom(8,3) = 168`.

이는 저자가 제공한 PES 숫자의 **독립 계수·조합식 산술 대조**이며 ED eigenstate나 PES를 재계산한 결과가 아니다. ξ threshold를 gap 내부에서 움직여도 count가 유지되는지 검사할 수 있다. count는 위상상 판정의 단독 증명이 아니라 다른 진단과 함께 읽는다.

재현 산출물: `artifacts/check_pes_counting.py`, `artifacts/results/pes-counting.json`, `figures/pes-counting.svg`. `python3 artifacts/check_pes_counting.py --download`로 고정 checksum의 source를 `/tmp`에 내려받아 실행할 수 있다. 원본 SHA256 `80c91a78e5dad9691dc5a839b497ae393ba7c307f2722d7c9de8ddcbea22de1f`, Zenodo MD5 `1a8f515450eb525bbd2c72074cf43032`, 98,461 bytes. G3:G2026/O3:O2026/W3:W2026의 2024개 numeric cell을 각각 ξ threshold 4.7/5.3/2.5 아래에서 셌고 ±0.1의 threshold 변경에도 결과가 유지됐다. (1,3) cyclic spacing 및 3개 sublattice의 모든 부분집합을 별도 열거해 조합식 1088/168도 대조했다. SVG는 원도표의 재현이 아니라 계수 두 막대를 새로 만든 것이며 MuPDF 렌더를 시각 확인했다.

## 6. 자기 안정성·전기 제어의 증거 수준

SI S1: phonon와 300 K AIMD(4×4, >10 ps, 5 fs step)는 구조 안정성 계산이다. 300 K의 AFM·FCI 안정성을 입증하지 않는다. TN≈22 K는 J1+single-ion anisotropy 모형의 50×50 classical Monte Carlo 추정(10^5 thermalization, 10^6 sampling)이며 실측 monolayer TN이 아니다. bulk 실험 TN≈26 K와 구분한다.

SI S1.2·Table S4의 DFT Hubbard U=0–4 eV 범위에서 선택한 경쟁 자기구조보다 공면 AFM이 낮다. MoSe2 substrate(2.1% mismatch) 사례에서는 J1=2.34 meV로 유지된다. 이것이 임의 substrate·domain-wall·doping에 대한 보편 안정성은 아니다. 공개 심사 답변은 domain-wall의 정량 큰 초격자 계산을 범위 밖이라고 설명한다.

SI S2.2.5: self-consistent ground state의 tiny net moment=0.05 μB/unit cell. 정확히 ideal coplanar 120°·zero net magnetization을 강제한 cDFT도 밴드·C를 유지한다. 따라서 작은 ferromagnetic canting이 Chern의 원인이라는 해석은 이 대조로 배제된다.

Accepted Fig. 5·Methods 및 SI S4.1·Fig. S21에는 SOT의 **LLGS dynamics simulation**이 있다. 단순 정적 회전 제안만 있는 것은 아니다. 사용 조건: J=5.29 meV, D=0.06 meV, K=0.11 meV; spin Hall angle 0.06, d=1 nm, Gilbert α=0.003, current j=3.9×10^8 A/m²와 external H≈0.1 T를 2 ns에 켜고 φ=0°→60°의 steady configuration으로 간다. 실물 device switching 측정이 아니며 ‘전류만으로’도 아니다. 별도로 spin angle에 따른 band topology를 계산한다. 180°(time reversal)는 C 부호를 반전하고, 120°(sublattice permutation)는 C를 보존한다. 자기 order와 SOC가 결합한 topology임을 보여주는 관계로 쓸 수 있다.

## 7. 기존 글과 차이, 원고에서 살릴 관계

- `2026-10-01_condensed-matter-topology-learning-thermal-computing/reports/content_ko.html`: 적층 FQH의 tunneling/interlayer interaction과 foliated/non-foliated order·애니온 통계를 다뤘다. 이번 글의 non-moiré **단층 자성 초격자→SOC→Chern geometry→같은 1/3 filling의 FCI/CDW 경쟁**은 그 글의 설명을 반복하지 않는다. FCI를 Fibonacci 비가환 애니온이나 topological quantum computation 구현으로 연결하지 않는다.
- `2026-10-06_quantum-quasiparticles-and-structured-computation/reports/review_ko.md`: BSE 유효모형·상태준비·총비용과 ‘모형/수치/장치 오차 구분’의 총론이다. 이번 새 기여는 그 문구의 반복이 아니라 **같은 C와 flat-band approximation에서도 투영 상호작용의 form factor 때문에 상이 갈리는 실제 비교**다.
- 중심 질문 제안: “에너지 분산을 없앴는데도 왜 전자는 서로 다른 질서를 고르는가?” W는 eigenvalue, Berry curvature·metric은 eigenvector의 k-dependence이며 투영 상호작용에 후자가 남는다. 이 물리 관계를 이해한 뒤 PES1088/168을 읽게 한다.
- 강한 반례: **flat+C≠0 ⇒ FCI**는 성립하지 않는다. 세 C=−1 밴드의 flat-band-limit ED에서 2nd CB는 CDW다. 더 작은 δB 하나만으로도 phase를 정하지 못한다.
- 향후 계산 조건: 실제 ε(k) 복원, substrate screening/비국소 interaction 변화, band mixing, 더 큰 cluster·twists, magnetic order 유지와 disorder를 조사한다. 이 항목을 원논문이 이미 해결했다고 쓰지 않는다.

## 8. 원자료 재현성의 미해결 항목

Zenodo `Table2.txt`는 표 숫자 텍스트가 아니라 18-orbital Wannier HR 형식이다. 이를 직접 Fourier 합산한 시범 대조는 reported Table 2의 W와 일치하지 않았다. `Fig3_1.txt`의 경로 band energy에서도 표와 모든 폭·gap이 곧바로 일치하지 않는다. mapping·parameter·후처리 조건을 아직 확정하지 못했으므로 이것을 논문 오류 또는 성공적 band 재현으로 보고하지 않는다. 현재 재구성 그림에는 **저널 Table 2의 reported 수치**와 **검산한 PES counting**을 쓰고 원자료 band 재현 주장은 보류한다. 실제 데이터 파일을 읽지 않은 추정 그림을 계산 재현으로 표시하지 않는다.
