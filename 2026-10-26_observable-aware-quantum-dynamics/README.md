# Observable-aware quantum dynamics

2026-10-26 AI Tech Review의 한영 기사 원고와 승인한 교육용 그림이다. 한국어를 canonical로 사용한다.

- [한국어 원고](reports/review_ko.md): 관측량과 항의 크기에 맞춘 양자 동역학 계산.
- [English manuscript](reports/review_en.md): Quantum dynamics tailored to observables and Hamiltonian scales.
- `figures/product_formula_comparison_{ko,en}.svg`: 상태 전파 오차·operator 2-norm 오차와 곱 공식의 차수 비교.
- `figures/observable_sampling_comparison_{ko,en}.svg`: 관측량별 교육용 표본분포의 편향 제곱·trajectory 분산 비교.
- `figures/flat_band_norm_counterexample_{ko,en}.svg`: 밴드폭 0이 작은 항 노름이나 교환자를 뜻하지 않는 대수적 반례.

그림은 앞서 만든 [정확 교육 계산](../2026-10-26_flat-bands-and-targeted-dynamics/artifacts/)의 SVG를 변경 없이 복사했다. 원 논문의 그림은 재사용하지 않는다. 수식은 HTML 제작 시 검증 가능한 SVG로 변환한다. 표지·배포용 HTML·PDF·게시 상태는 별도 제작·배포 기록을 따른다.

## 원고와 검증 범위

프리프린트 두 편의 원문·수식·수치 조건을 대조한 한국어 초안에서 정식 기사 문장을 정리하고 영어 전문을 작성했다. StateDRIFT의 관측량 편향·분산과 norm-aware 곱 공식의 전파 오차를 구분하며, Partial–Strang의 일반적 1차 차수와 α·분할 수의 교차 조건을 보존한다. 4.5–8배는 분자 상태 ℓ2 오차 감소, 11,201→983은 특정 BeH₂ 기준에서 예상한 두 큐비트 게이트 수라는 조건을 양 언어에 남긴다.

새 계산은 정확한 한 큐비트 교육 모형이다. 관측량 분포 탐색은 정확한 목표값을 아는 교육용 oracle이며 StateDRIFT allocator의 구현이나 전역 최적화 결과가 아니다. 원 논문의 분자 계산·QPU·장치 잡음·실제 회로 샷 비용은 재현하지 않았다. 분자·재료·장치 성능으로 수치를 확대하지 않는다.

기존 제작 역할 `dqb_today_algorithm_sources`는 원문·수식·교육 계산·도표를, `root`는 원고 통합과 SO(3) 독립 검산을 맡았다. 이번 `publish_dynamics_text`는 정식 한국어 문장과 영어 전문·기호·수치·그림 대응을 정리했다. 확인 가능한 정확한 작성 모델 식별자는 미보존이다. 편집 하네스는 AI Tech Review Editorial Harness 2026.08, 과학 설명 준칙 1.0이다. 사용자의 게재 요청과 문장별 사람 감수·독자 이해도 평가를 구분한다.

한영 원고 각각 H1 하나, 수식 블록 세 개, 본문 그림 세 개, 수치 표 두 개와 참고문헌 네 항목을 대조했다. 표 수치 10개·분자 비용 수치·독립 검산 오차·지역 그림 파일을 확인했으며, 원고의 임시 상태 표기·내부 절대경로·개인 메시지 metadata는 없다. 최종 HTML·PDF·모바일·공개 URL 검수는 게시 제작 단계의 기록으로 별도 남긴다.

## 모바일 그림

`artifacts/build_mobile_figures.py`는 데스크톱 그림의 420px 패널을 이동해 세로로 쌓는다. 데이터 곡선의 `points`, 막대의 너비·높이·색과 모든 단어·값은 자동 대조한다. 제목·축 라벨·주석은 줄바꿈·글자 크기·위치만 바꾸며, 600px 폭 SVG를 390px로 렌더링해 한영 여섯 그림 모두 확인했다. 긴 π 눈금은 그림 안쪽으로 정렬했다. 원고는 640px 이하에서 모바일 그림을 고르는 `<picture>`를 사용하며, PDF에는 데스크톱 그림을 사용한다. 실제 웹 페이지·PDF 출력 검수는 제작 단계에서 별도 확인한다.

## Publication package

- Korean: https://infant83.io/AI_Tech_Review/reviews/2026-10-26_observable-aware-quantum-dynamics/
- English: https://infant83.io/AI_Tech_Review/reviews/2026-10-26_observable-aware-quantum-dynamics/en/
- PDFs: dist/review_ko.pdf and dist/en/review_en.pdf.
- Build fonts, HTML and PDFs with artifacts/build_fonts.py, build_review.mjs and build_pdf.py. Font and runtime paths are explicit arguments/environment variables, never embedded host paths. The renamed OFL font subsets retain the full source license.
- The HTML builder converts picture to explicit desktop/mobile img sources for the existing publication allowlist. Screen widths up to640px use the stacked SVG; print uses the desktop SVG.
- APS citation metadata, primary sources and numbering are in artifacts/reference-manifest.json. NumPy developer credit and actual version2.0.2 are distinguished.
- Cover briefs, full prompt, bilingual captions/alts and final hashes are preserved in cover-art-brief.md, artifacts/cover-spec.json and figure-manifest.json. The built-in image_gen cover is conceptual; no data or hardware is depicted.
- publication_pipeline_audit independently checked bilingual claims, cover meaning and every PDF page. QA images and private source material are excluded from dist and site. Human line-by-line approval and comprehension testing were not performed.
