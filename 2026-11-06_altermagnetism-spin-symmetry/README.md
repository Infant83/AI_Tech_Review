# Altermagnetism과 계산재료과학

2026-11-06 작성한 한영 AI Tech Review. 수정한 수채화 표지와 한영 본문·PDF를 공개 허브와 아카이브에 함께 등록한다. 공개 주소는 https://infant83.io/AI_Tech_Review/reviews/2026-11-06_altermagnetism-spin-symmetry/ 이다.

- [한국어 읽기](dist/index.html), [한국어 PDF](dist/review_ko.pdf)
- [English article](dist/en/index.html), [English PDF](dist/en/review_en.pdf)
- 번호 인용·참고문헌을 갖춘 원고: `reports/review_ko.md`, `reports/review_en.md`
- 편집 가능한 집필 원본: `artifacts/manuscripts/`. `[@key]` 인용을 `export_manuscripts.py`로 번호화한다.
- 선행 연구·실험·서지: `artifacts/reference-sources.json`, `artifacts/reference-manifest.json`
- 표지 기획·전체 프롬프트: `cover-art-brief-v2.md`, `artifacts/cover-spec-v2.json`
- 설명 기획: `review-explanation-brief.md`. 제작·검토 범위: `notes/editorial-review.md`.

반자성·반강자성의 구별, 스핀군과 운동량별 비상대론적 분리, d/g-wave, MnTe·CrSb의 전자·마그논 관측, RuO₂의 시료별 논쟁, DFT·상관·SOC·Wannier 수송과 스핀 소자를 연결한다. 2026년 10월 스핀 주입·편극 마그논 결과를 포함하며 해당 측정 조건을 보존했다. 기존 평탄 Chern 밴드 글의 비공선 자기질서·SOC 메커니즘과 구별되는 새 리뷰다.

`build_figures.py`는 2차원 유효 모형과 두 부분격자 확장의 수치·대칭 검산을 실행하고 한영 화면·모바일·인쇄용 SVG를 만든다. `model-results.json`에 격자·온도 broadening·점유수·회전·절점·고유값 검사를 보존한다. 원 재료의 DFT·DMFT·실험을 재현한 작업은 아니다. 현재 표지는 검증한 CrSb 배위와 g-wave 부호 모형을 참고한 내장 image_gen 수채화 개념 그림이다. 미술·물리·시각 서사 전문 역할의 검토 후 B안을 선택했고, 한영 본문과 PDF에 반영했다.

빌드에 Python의 NumPy·Matplotlib·FontTools·Brotli·pypdf·Pillow와 Node.js의 marked·mathjax-full 3.2.2·Playwright/Chrome이 필요하다. NanumGothic Regular/Bold를 설치하거나 폰트 빌더에 경로를 전달한다. Noto Sans·Noto Sans Math의 라이선스가 있는 보완 글꼴을 제작 자산에 보존했다. 생성한 글꼴 부분집합은 이름을 변경하고 전체 OFL을 유지한다.

1. `python3 artifacts/export_manuscripts.py`
2. `python3 artifacts/build_figures.py`
3. `python3 artifacts/build_fonts.py --regular /path/to/NanumGothic-Regular.ttf --bold /path/to/NanumGothic-Bold.ttf`
4. `REVIEW_NODE_MODULES=/path/to/node_modules node artifacts/build_review.mjs --public-base=https://infant83.io/AI_Tech_Review/reviews/2026-11-06_altermagnetism-spin-symmetry/`
5. `python3 artifacts/build_pdf.py --node /path/to/node --modules /path/to/node_modules`
6. `python3 artifacts/check_output.py --public-base=https://infant83.io/AI_Tech_Review/reviews/2026-11-06_altermagnetism-spin-symmetry/`

위 명령은 주제 폴더 기준이다. PDF 새 제작 작업에는 활성 PDF 스킬의 operation marker를 먼저 실행한다. `build_review.mjs`는 기본적으로 로컬 언어 전환·인용 링크를 만든다. 공개 빌드에는 위의 `--public-base`를 전달해 canonical·hreflang·OG 이미지와 인용·언어 전환 주소를 생성한다. PDF에는 공개 외부 링크를 남기고 로컬 호스트 경로를 포함하는 링크 주석을 제거한다.

`dist/`에는 최종 한영 HTML·CSS·PDF·표지·참조 SVG만 들어간다. 조사 메모·원문·QA 화면·임시 의존성은 배포하지 않는다. 사용자의 수정본 업데이트 지시에 따라 이 글만 사이트 등록·게시 대상으로 삼는다. 예약 작업은 변경하지 않는다. 기존 리뷰 54편의 공개 파일 1,707개·PDF 115개와 기존 독자 갱신 기록 131개를 보존했다. 한영 PDF는 각각 원본 dist·공개 기사·아카이브 원본·공개 아카이브 네 사본의 해시가 일치한다. 허브·공개 정보·아카이브·독자 갱신 관련 기존 검사 92건과 공개 산출물 2,234개 검증을 통과했다. 신규 허브 소개는 스핀 밴드 분리가 유용한 전류로 이어지는 데 필요한 자기질서·도메인·접점을 함께 설명하도록 독립 감수했다. 실제 배포 확인 기록은 게시 작업의 출력으로 별도 보존한다.
