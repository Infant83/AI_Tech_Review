# 원논문 결과 그림 선별과 재사용 조건 대조

2026-11-27 · 편집부(AEDAUT) 원문·시각·권리 조건 조사 · figure_source_audit

## 선택과 실제 확인 범위

현재 리뷰의 검산한 조화 모형 뒤에 실제 결과를 놓아, 곡률의 차이가 실제 MLIP의 진동 예측과 상 복원에 어떻게 나타나는지 보여 준다. Deng 등의 원 Fig. 4 전체를 리뷰 그림 3, Grandel 등의 원 Fig. 4 전체를 리뷰 그림 4로 채택한다. 리뷰 자체의 일반화 워크플로는 그림 5로 이어진다. 두 그림은 저자 보고 계산 결과이며 ATRL의 신규 MLIP·DFT 재현 결과로 표시하지 않는다.

출판사의 정식 article 페이지와 figure 페이지의 실제 HTML, 출판사 미디어 서버의 full PNG를 직접 확보했다. Grandel은 PMC 보존 전문에서도 캡션·전후 결과·Methods와 권리 조항을 대조했다. 두 PNG를 실제 이미지로 열어 색상·범례·축·패널·구조와 원문 설명의 대응을 확인했다. 이번 과정에서는 원본 그림의 자르기·재색칠·텍스트 덮기·패널 재배열·데이터 추출을 하지 않았다. 화면 표시 크기만 조절한다. 원본에 없는 데이터 점·오차막대·곡선을 보간하거나 생성하지 않는다.

## 재사용 근거

두 정식 논문의 권리 표시는 각각 © The Author(s) 2025 및 © The Author(s) 2026, **Creative Commons Attribution 4.0 International (CC BY 4.0)**다. 본문 라이선스는 출처·저자 표시, 라이선스 링크, 변경 사항 표시를 요구한다. 이미지와 제삼자 자료에도 같은 라이선스를 적용하되 별도 credit line이 있으면 그 조건을 따르도록 명시한다. 선택한 두 Fig. 4와 각각의 캡션에는 별도 제삼자 크레딧이나 라이선스 제외 표시가 없었다.

- Deng 정식 권리·본문: <https://www.nature.com/articles/s41524-024-01500-6>
- Deng 원 그림·캡션: <https://www.nature.com/articles/s41524-024-01500-6/figures/4>
- Grandel 정식 권리·본문: <https://www.nature.com/articles/s41524-026-02338-w>
- Grandel 원 그림·캡션: <https://www.nature.com/articles/s41524-026-02338-w/figures/4>
- Grandel 보존 전문의 권리 대조: <https://pmc.ncbi.nlm.nih.gov/articles/PMC13713550/>
- 라이선스: <https://creativecommons.org/licenses/by/4.0/>

다운로드한 이미지·정식 DOI·패널 번호·권리·변경 여부·확인일·체크섬은 `../artifacts/source-figures/manifest.json`에 기록했다. 전체 조사 HTML은 공개 산출물에 넣지 않고 `output/foundation-source-figures-20261127/`에 임시 조사 증거로 두었다. 공개 열람 가능성만으로 재사용 조건을 추정한 것이 아니다.

## 리뷰 그림 3 — 연화가 실제 진동 스펙트럼에 남는 모습

원 출처: B. Deng et al., *Systematic softening in universal machine learning interatomic potentials*, npj Comput. Mater. **11**, 9 (2025), DOI [10.1038/s41524-024-01500-6](https://doi.org/10.1038/s41524-024-01500-6), **원 Fig. 4 전체**.

원본: `../artifacts/source-figures/deng-2025-fig4.png`, 1451×527px, 152,186 bytes.
SHA-256: `45372858dc3186495d10d113f4e56ea4ba4e066e6ad0f68558bf4501f32518fc`.

다운로드: <https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41524-024-01500-6/MediaObjects/41524_2024_1500_Fig4_HTML.png>

### 읽는 순서와 주장에 기여하는 내용

- 패널 (a)의 세로축은 진동수 THz, 가로축은 결정에서 진동의 공간적 반복을 구별하는 파수 경로다. 오른쪽의 좁은 축은 진동 상태밀도(DOS)다. CsF(mp-1784)의 빨간 실선이 DFT, 초록 MACE·파란 M3GNet·주황 CHGNet 선이 MLIP다. 특히 높은 진동수 가지의 낮아진 위치가 작은 모형에서 설명한 곡률 차이를 실제 계산과 잇는다. 여기서 실제 이온 결정의 광학 진동을 언급할 수 있으나, 네 동일 원자 사슬의 교대 모드를 광학 모드라고 바꾸지는 않는다.
- 패널 (b)는 비자성·U 보정 없는 229재료 각각의 최대 진동수 비 `max(ω_uMLIP)/max(ω_DFT)` 분포다. 기준 1보다 낮은 재료 비율이 M3GNet 97.4%, CHGNet 90.8%, MACE 93.9%로 원본에 인쇄되어 있다. 이 백분율은 **그 재료 집합에서 최대 진동수를 과소 예측한 비율**이며 진동수의 평균 감소량이나 정확도 점수로 읽으면 안 된다.
- 참조는 PhononDB의 PBEsol 자료, 비해석 보정(NAC) 제외다. 실제 극성 결정에서는 긴 파장 진동과 장거리 전기장의 결합을 어떻게 넣을지 따로 정해야 한다. 이 논문의 세 모델·당시 판본에서 관찰한 결과로 한정한다.

### 본문 통합 제안

기존 Deng 설명 문단을 둘로 나누고, 첫 문단에서 그림 3(a)의 CsF와 그림 3(b)의 1 기준선을 읽도록 안내한 뒤 원본을 배치한다. 다음 문단에 PBEsol·비자성·U 미적용·NAC 제외 조건과 다음 검증의 선택을 둔다. 이렇게 하면 교육 계산→실제 스펙트럼→여러 재료에서의 경향→조건을 맞춘 후속 검증이 이어진다.

### 캡션 제안

국문: **그림 3. 실제 결정에서 나타난 진동수 연화.** (a) CsF의 진동 분산과 상태밀도, (b) 229재료에서 MLIP와 DFT의 최대 진동수 비. 분포의 1 아래는 최대 진동수의 과소 예측을 뜻한다. M3GNet·CHGNet·MACE-MP-0와 PBEsol 기준을 비교했으며 비해석 보정은 제외했다. Deng 등[4]의 Fig. 4 전체 재수록. © The Author(s) 2025, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 표시 크기만 조정했으며 내용은 변경하지 않았다.

EN: **Figure 3. Phonon softening in actual crystals.** (a) Phonon dispersion and density of states of CsF. (b) The ratio of MLIP to DFT maximum phonon frequencies across 229 materials; values below one indicate underprediction. M3GNet, CHGNet and MACE-MP-0 are compared with the PBEsol reference, without non-analytical corrections. Reproduced in full from Fig. 4 of Deng et al. [4]. © The Author(s) 2025, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Display size adjusted; content unchanged.

## 리뷰 그림 4 — 같은 불안정 모드를 잡은 뒤 갈라지는 최종 상

원 출처: J. Grandel, P. Benner, and J. George, *Targeted fine-tuning of machine-learning interatomic potentials for phonons and phase transitions*, npj Comput. Mater. **12**, 354 (2026), DOI [10.1038/s41524-026-02338-w](https://doi.org/10.1038/s41524-026-02338-w), **원 Fig. 4 전체**.

원본: `../artifacts/source-figures/grandel-2026-fig4.png`, 1450×1261px, 1,415,272 bytes.
SHA-256: `301dc42b7a23346b576212bc75ec2c558b4783edd73fa648e735184fd6222e2d`.

다운로드: <https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41524-026-02338-w/MediaObjects/41524_2026_2338_Fig4_HTML.png>

### 읽는 순서와 주장에 기여하는 내용

- (a) K₃Sb의 M–K–Γ 구간에서 검은 DFT 곡선의 K점 아래로 내려가는 가지를 먼저 읽는다. 이 그림의 음수 표시는 불안정성의 허수 진동수를 관례에 따라 표시한 것이다. 초록 multihead와 하늘색 L²-TSP는 이 불안정성을 포착한다. 기반 MP-0b3·처음부터 학습·transfer는 이 K점 불안정성을 놓친다.
- (b) 원자의 집단 변위에 따른 에너지 차이를 읽는다. 두 미세조정 방법 모두 이중 우물을 만들지만, DFT에 비해 두 최소점이 안쪽으로 이동하고 깊이도 다르다. L²-TSP가 깊이를 과대, multihead가 크게 과소 예측한다. 따라서 이 그림으로 L²-TSP가 **변위 경로 전체의 에너지를 정확하게 재현했다**고 쓰면 안 된다.
- **기호 혼동 주의:** 원본 (b)의 `Q [amu^(1/2) Å]`는 질량가중 정규 좌표다. 리뷰 교육 예제의 `q [Å]` 또는 일반화힘 `Q`와 다른 기호 관례다. 캡션 또는 바로 앞 본문에서 원 그림이 쓰는 Q를 명시적으로 풀어야 한다. 원본 그림의 축을 임의 변경하지 않는다.
- (c) 검은 DFT·초록 multihead·하늘색 L²-TSP의 이완 경로를 비교한다. 원 안 숫자 8·24는 원시 단위격자의 원자 수다. DFT와 L²-TSP는 P6₃cm에, multihead는 R−3에 도달한다. 오른쪽은 초기 P6₃/mmc와 P6₃cm 구조다. 구조 그림은 실제 원논문 결과를 구체화하며 장식용 결정 모형이 아니다.
- 연구 전체는 재료마다 열 개 구조를 사용해 미세조정한 53재료 비교이며, 상 복원 검사는 9개 불안정 재료에서 DFT 가능한 26/41 파수점으로 제한된다. K₃Sb는 그중 대표 사례다. 53재료 모두에서 같은 상 결과가 나왔다고 확대하지 않는다.

### 본문 통합 제안

기존 K₃Sb 문단의 (i) K점 불안정성과 (ii) 최종 상 설명 사이에 (b)의 두 우물 깊이 차이를 한 문장으로 연결한다. 본문에서 (a)→(b)→(c)를 안내하고 원 그림을 배치한다. 이어 F1 변화와 상 복원 검사의 범위를 설명한다. 이 순서는 평균 진동 오차·불안정 모드·경로 에너지·최종 상이 서로 다른 검증임을 실제 한 물질로 보여 준다.

### 캡션 제안

국문: **그림 4. K₃Sb에서 진동의 불안정성을 포착한 뒤에도 갈라지는 구조 예측.** (a) DFT(검정)와 다섯 모델의 진동 분산, (b) K점 불안정 모드를 따른 이중 우물 에너지, (c) 이완 후의 상과 상대 에너지. (b)의 Q는 질량가중 정규 좌표이고 (c)의 원 안 숫자는 원시 단위격자의 원자 수다. L²-TSP와 multihead는 모두 불안정 모드를 잡지만, 최종 상은 각각 P6₃cm와 R−3다. Grandel 등[5]의 Fig. 4 전체 재수록. © The Author(s) 2026, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 표시 크기만 조정했으며 내용은 변경하지 않았다.

EN: **Figure 4. Capturing an instability can lead to different relaxed phases in K₃Sb.** (a) DFT (black) and five ML phonon spectra. (b) The double-well energy along the unstable K mode. (c) Relaxed phases and their relative energies. Q in (b) is a mass-weighted normal coordinate; the circles in (c) give atom counts in primitive cells. L²-TSP and multihead both capture the instability, but relax to P6₃cm and R−3, respectively. Reproduced in full from Fig. 4 of Grandel et al. [5]. © The Author(s) 2026, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Display size adjusted; content unchanged.

## 제작상의 권고

두 결과 그림의 원래 색상과 글자·축·범례를 보존하고, 리뷰 바깥 프레임·여백·캡션만 본문 톤에 맞춘다. 원본의 DFT 색은 Deng에서 빨강, Grandel에서 검정이므로 같은 의미를 강제로 같은 색으로 통일하지 않는다. 작은 화면에서는 전체 그림을 축소해 버리기보다 원본 열기/확대 경로를 제공하고 캡션의 패널 안내가 이어지게 한다. Grandel 전체 그림은 높이가 있어 PDF에서 최소 유효 글자 크기와 캡션 결속을 실제 출력으로 확인해야 한다.

## 한영 본문에 통합한 뒤의 독립 감수

통합 담당자가 편집한 `reports/review_ko.md`와 `reports/review_en.md`의 새 그림 3·4 해설·캡션·alt를 다시 읽고, 실제 원본 PNG와 위 공개 전문의 패널 설명·주변 결과·Methods에 대조했다. 이번 감수자는 이 통합 문장을 작성하지 않았다. 원고만 감수했으며 최종 브라우저·PDF 조판 확인은 별도 제작 감수 범위다.

핵심 대조는 통과했다. 229재료와 세 백분율은 최대 진동수를 낮게 예측한 **재료의 비율**로 정확하게 해석됐으며, PBEsol·비자성·U 미적용·NAC 제외 조건이 남아 있다. CsF의 파수 경로·진동수와 높은 M3GNet 가지의 차이를 읽도록 안내한다. 그림 2의 교육 계산에서 그림 3의 실제 결과로 이어지는 문단의 목적이 드러난다.

K₃Sb 설명은 0 아래에 그린 값이 허수 진동수의 불안정성 표시라는 점, 원본 Q의 질량가중 변위 단위, 리뷰 q·일반화힘 Q와의 기호 차이를 분명히 한다. L²-TSP의 우물 깊이 과대 예측과 multihead의 과소 예측을 모두 보존하고, 최종 P6₃cm·R−3 상의 차이를 별도 검증으로 설명한다. 패널 (b)의 meV와 (c)의 meV/atom, 원 안 숫자의 원자 수 설명도 원본과 같다. 최종 상의 복원을 변위 경로 전체의 정확성으로 확대하지 않았다.

그림 3·4의 번호는 각각 원논문 결과에, 워크플로 관련 설명은 그림 5에 대응한다. 본문에서 이전 워크플로를 그림 3으로 부르는 잔여 문장은 없었다. 캡션의 원 Fig. 4 링크·본문 참고문헌 [4]/[5]·연도·권리 표시·CC BY 4.0 링크·원그림 무수정 재수록 표시는 대응한다.

통합 담당자에게 작은 표현 보완 두 건을 전달했다. 국문 원자 수 설명의 ‘기본 단위격자’를 원문의 primitive unit cell에 해당하는 ‘원시 단위격자’로 맞추고, 영문 그림 3의 모델 선 설명에는 MACE의 점 모양까지 포함해 dashed and dotted라고 쓰면 더 정확하다. 핵심 결과의 오류나 독자를 다른 물리적 주장으로 이끄는 문제는 발견하지 않았다. 이 두 항목의 실제 적용 여부는 통합 담당자가 이후 원고에서 확인한다.
