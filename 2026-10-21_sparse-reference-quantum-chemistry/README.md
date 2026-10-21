# 희소 기준상태와 혼합 추정량: 대학원 세미나 리뷰

근거 기준일: 2026-10-21. Lenihan et al., arXiv:2610.26689v1을 중심으로 독립 집필한 90분 세미나형 AI Tech Review다. 원 연구의 공식 수업이나 강의 녹취가 아니다.

- 한국어 정본: [세미나 원고](reports/2026-10-21_sparse-reference-quantum-chemistry_final_review.md)
- 전체 영어판: [English manuscript](reports/2026-10-21_sparse-reference-quantum-chemistry_final_review_en.md)
- 공개 웹판: `dist/index.html`, `dist/en/index.html`
- PDF: `dist/review.pdf`, `dist/en/review-en.pdf`
- 공개 수식·교육 그림·2준위 실습: `artifacts/`
- 표지 기획·검수: [cover-art-brief.md](cover-art-brief.md), [그림 제작 기록](figure-manifest.json)

전자구조의 실제 질문에서 시작해 투영·잔차 항등식, 바닥상태 부호 조건, compute–uncompute 읽기, 두 준위 계산과 두 반례, 근사 상태의 오차 곱, 잔차 절단 bound, 유한 표본 분산과 최적 배분을 유도한다. 실제 Helios 결과는 이상적 (6,6) 약 400샷 추정과 (10,10) 구조당 10,000 제출샷을 구별하고, 후선택·정밀도·중심값 편향을 대조한다. 문제와 해설 5개, 조작 가능한 교육 실습을 포함한다. SVD-THC는 별도 논리 자원의 비교 사례다.

수치 교육 계산은 직접 검산했으며 실제 분자 전자구조·장치 회로·QPU·원 논문 학습을 독립 재현하지 않았다. 상호작용 실습의 θ=30°, Δ=100 mHa, accepted shots=10,000은 리뷰의 합성 기본값이며 논문 parameter나 데이터가 아니다. 원 논문 결과와 리뷰 계산·후속 응용 제안을 구별한다.

## 재생성

`artifacts/build_figures.py`는 NumPy·Matplotlib과 공개 라이선스 한영 글꼴로 도표를 만들고 독립 행렬·미분·배분 계산을 검사한다. `artifacts/build_fonts.py`는 `--regular`·`--bold`로 글꼴을 지정해 WOFF2 subset을 만든다. 글꼴 라이선스는 `artifacts/font-license.txt`와 `artifacts/font-OFL.txt`에 보존한다.

`artifacts/build_review.mjs`는 `marked`와 `mathjax-full`로 한영 원고를 렌더링한다. 설치된 의존성은 `REVIEW_NODE_MODULES` 또는 `CODEX_PRIMARY_RUNTIME_NODE_MODULES`로 지정한다. 수식은 로컬 SVG로 만들어 네트워크 없이 표시하고, 한영 그림과 최종 표지·실습 JS만 명시적으로 복사한다.

`artifacts/build_pdf.py --node NODE --modules MODULES`는 로컬 HTML을 완전한 한영 PDF로 출력한다. PDF의 수학·표·그림과 전체 페이지를 렌더링해 확인한다. `--language ko` 또는 `--language en`으로 한 언어만 다시 출력할 수 있다. QA는 `tmp/pdfs/` 아래에 두며 커밋·사이트 배포에서 제외한다.

`scripts/publish_public_site.py --review 2026-10-21_sparse-reference-quantum-chemistry`로 기존 리뷰를 보존하면서 이 리뷰와 허브를 생성한다. 원 논문 수집 자료·내부 조사 노트·QA 화면은 공개 리뷰 자산으로 복사하지 않는다. 개인 메일과 수집 식별자는 이 주제 묶음에 보관하지 않는다.
