# OMat24 데이터 중복성과 학습 집합 압축

2026년 10월 19일 발행하는 한영 AI Tech Review 패키지다. 한국어를 기본 언어로 제공하며, 두 언어의 완전한 리뷰 PDF를 문서 아카이브에도 등록한다. 검토 대상은 Moerman·Poltavsky·Charkin-Gorbulin·Tkatchenko의 [arXiv:2610.14392v1](https://arxiv.org/abs/2610.14392v1)이다.

- [한국어 리뷰](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-18_materials-dataset-redundancy/)
- [English edition](https://infant83.github.io/AI_Tech_Review/reviews/2026-10-18_materials-dataset-redundancy/en/)
- [문서 아카이브](https://infant83.github.io/AI_Tech_Review/archive/)

## 패키지 구성

- `reports/review_ko.md`, `reports/review_en.md`: 본문 원고.
- `dist/index.html`, `dist/review_ko.pdf`: 한국어 HTML과 5쪽 PDF.
- `dist/en/index.html`, `dist/en/review_en.pdf`: 영어 HTML과 6쪽 PDF.
- `dist/review_ko.md`, `dist/en/review_en.md`: 작성·검증 공시를 포함한 Markdown 배포본.
- `artifacts/hero.webp`: 내장 imagegen으로 생성한 개념 표지. 실제 원자 구조나 정량 결과가 아니다.
- `artifacts/force_mae_ko.svg`, `artifacts/force_mae_en.svg`: 저자 공개 CSV의 벌크 힘 성분 MAE를 재도식화한 결정론적 도표.
- `figure-manifest.json`: 표지의 전체 최종 프롬프트·생성 방식·저장 경로와 도표의 원자료·수치·해석 범위.
- `artifacts/build_*.py`, `artifacts/build_review.mjs`: 도표·폰트·한영 HTML/PDF 제작 코드.
- `artifacts/font-OFL.txt`, `artifacts/font-license.txt`: 원 폰트와 파생 subset의 라이선스 기록.

원문 수집물과 내부 조사·출력 검사 기록은 공개 배포에 포함하지 않는다. 사이트에는 최종 HTML, PDF, 스타일, 개념 표지와 해당 언어의 도표 등 실제 참조 자산만 게시한다.

## 재빌드

Node.js의 `marked`, `playwright`와 Chrome, Python의 matplotlib·fontTools·brotli가 필요하다. 폰트 입력은 OFL 라이선스의 Nanum Gothic Regular/Bold처럼 한국어를 지원하는 서체를 사용한다. 사용자 환경의 런타임과 의존성 위치는 명령 인자나 `CODEX_PRIMARY_RUNTIME_NODE_MODULES`로 전달한다.

```sh
python artifacts/build_figures.py --font /path/to/NanumGothic-Regular.ttf
python artifacts/build_fonts.py --regular /path/to/NanumGothic-Regular.ttf --bold /path/to/NanumGothic-Bold.ttf
node artifacts/build_review.mjs --public-base=https://infant83.github.io/AI_Tech_Review/reviews/2026-10-18_materials-dataset-redundancy/
python artifacts/build_pdf.py --node /path/to/node --modules /path/to/node_modules --qa-dir tmp/qa
```

도표 코드는 [공식 코드 고정 commit](https://github.com/em819/omat24-chemenv-subset/tree/723696de2c26584b8a907ef900690c0caf3c7b68)의 공개 집계값을 사용한다. 모델 재학습·DFT·MD를 재실행하지 않는다. 빌더는 공개 게시·아카이브 등록·Git 작업을 수행하지 않는다.

## 편집과 검증

책임 편집자는 김현중 / Hyun-Jung Kim이며 AI 보조는 OpenAI Codex다. 실제 기록된 역할은 `root`의 자료 대조·CSV 산술·한국어 집필·표지·게시 통합, `identify_paper`의 독립 식별·선행연구·영어판, `critical_audit`의 수치·방법론 감사, `publication_build`의 도표·조판·폰트·HTML/PDF와 출력 검사다. 정확한 작성 모델 식별자는 미보존이며, 발행 요청을 문장별 사람 승인으로 간주하지 않는다.

원자 수와 구조 수의 분모, 힘 성분 MAE와 벡터 오차, MD 평균 진행률과 실행 완료율을 구분했다. 공개 결과 CSV의 산술, 원문·SI·한영 본문과 도표를 대조하고 11쪽 PDF 전체 렌더링, 모바일 폭, 링크·메타데이터·자산 및 공개 범위를 확인했다. 작성 기준은 [AI Tech Review Editorial Harness 2026.08](https://infant83.github.io/AI_Tech_Review/methods/)이다.
