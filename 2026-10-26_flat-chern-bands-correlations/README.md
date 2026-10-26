# 평탄한 Chern 밴드의 상관 상태

2026-10-26 정식 발행 패키지. 한국어를 canonical로 하고 영어 전문을 함께 제공한다.

- [한국어 기사](https://infant83.io/AI_Tech_Review/reviews/2026-10-26_flat-chern-bands-correlations/)
- [English article](https://infant83.io/AI_Tech_Review/reviews/2026-10-26_flat-chern-bands-correlations/en/)
- 원고: `reports/review_ko.md`, `reports/review_en.md`
- PDF: `dist/review_ko.pdf`, `dist/en/review_en.pdf`
- 과학·설명 기획과 계산: [기존 주제 폴더](../2026-10-26_flat-bands-and-targeted-dynamics/)

재료 논문의 DFT·다체 ED와 리뷰의 두 밴드 교육 계산, 공개 PES 원자료 재계수를 구분한다. 재료 계산·QPU·실험을 독립 재현했다고 주장하지 않는다. 실제 밴드폭과 분산을 없앤 ED를 구분하고, VB의 전 플럭스 global gap 제한을 보존했다.

`artifacts/build_figures.py`는 원 교육 그림과 검산 결과에서 한영 PC·모바일 SVG 8개를 재생성한다. 원 좌표·계수·팔레트를 유지하며, 임시 재생성 결과는 최종 SVG와 바이트 단위로 대조했다. 표지는 내장 image_gen으로 제작한 개념 그림이다. 프롬프트·캡션·alt·SHA256은 `artifacts/cover-spec.json`, 기획과 축소·흑백 검수는 `cover-art-brief.md`, 최종 그림 기록은 `figure-manifest.json`에 있다.

빌드 순서는 `artifacts/build_fonts.py` → `artifacts/build_review.mjs` → `artifacts/build_pdf.py`다. 글꼴 경로는 `--regular`·`--bold`, Node 의존성은 `REVIEW_NODE_MODULES`·`CODEX_PRIMARY_RUNTIME_NODE_MODULES`, PDF 런타임은 `--node`·`--modules`로 전달한다. 글꼴은 NanumGothic Regular/Bold의 OFL 허용 부분집합이며 이름을 변경하고 전체 라이선스를 보존했다. Node는 marked·mathjax-full 3.2.2·Playwright와 Chrome, Python은 fontTools·brotli가 필요하다.

원고의 picture 요소는 빌더가 명시적인 PC·모바일 img로 바꿔 기존 게시기의 자산 allowlist에 포함한다. 640px 이하 화면은 세로 그림을, PDF는 PC 그림을 사용한다. 표지 전체를 표시하고 수식은 내용 기반 이름의 SVG로 조판한다. `dist/`는 최종 HTML·CSS·PDF·표지·참조 SVG만 포함한다. 원문·원자료·수집 경위·내부 감수 메모·QA 화면은 사이트에 배포하지 않는다.

원고·데이터 검토 역할은 기존 기록을 유지한다. `publish_flatband_text`는 한영 게재 원고·반응형 그림·APS 참고문헌, `publication_pipeline_audit`는 독립 한영 주장·표지·전체 PDF 출력 감수, `root`는 계산 검산·조판·배포 통합을 담당했다. 정확한 작성 모델 식별자는 미보존이다. 사람의 발행 요청과 문장별 승인·독자 이해도 실험을 구분한다. 서지 확인 자료와 번호 대응은 `artifacts/reference-manifest.json`에 보존한다.
