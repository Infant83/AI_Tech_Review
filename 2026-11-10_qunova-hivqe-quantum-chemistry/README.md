# 큐노바 HI-VQE와 양자화학의 계산 분업

근거 기준일: 2026-11-10. 한영 원고·표지·기술 도식·웹·PDF를 제작하고 과학·번역·화면·PDF 검수를 마쳤다.

- 원고: [한국어](reports/review_ko.md) · [English](reports/review_en.md)
- 출판 원본: [한국어 HTML](dist/index.html) · [English HTML](dist/en/index.html)
- PDF: [한국어](dist/review_ko.pdf) · [English](dist/en/review_en.pdf)
- 설명 기획·검토: [review-explanation-brief.md](review-explanation-brief.md)
- 표지 기획·출처·검수: [cover-art-brief.md](cover-art-brief.md)
- 독립 설명 계산: [verify_examples.py](artifacts/verify_examples.py) · [수치](artifacts/example-results.json)
- 기술 도식: [계산 분업](artifacts/handover_workflow_ko.svg) · [부분공간과 에너지](artifacts/support_and_energy_ko.svg)
- 과학·시각 검수: [science-publication-audit.json](artifacts/science-publication-audit.json)

편집부(AEDAUT)는 큐노바의 원리·논문 판본·공개 성능과 양자 이점 조건, 비교 기업의 접근을 조사하고 한영 원고와 시각자료를 준비했다. 운영팀(ADOPT)의 기존 등록·연속성·아티팩트 검증 경로를 사용한다. 실제 공개 상태는 해당 출판 요청과 GitHub Pages 배포 기록으로 확인한다.

계산 재생성에는 Python과 `artifacts/requirements-examples.txt`의 NumPy·Matplotlib가 필요하다. `python artifacts/verify_examples.py`는 두 자리 Hubbard 행렬을 직접 만들고 해석해와 대조한 뒤 결과 JSON·SVG를 만든다. QPU 실행·회사 알고리즘 재현·속도 비교는 수행하지 않는다.

웹 생성에는 Node.js와 `marked`·`mathjax-full`, 글꼴 생성에는 `artifacts/requirements-build.txt`의 Python 도구가, PDF에는 Playwright와 Chrome이 필요하다. `build_fonts.py`는 환경변수로 제공한 허용 글꼴 원본에서 subset을 만들고, `build_review.mjs`는 한영 Markdown을 출판 HTML로 변환한다. `build_pdf.py --help`에서 문서 렌더링·비공개 QA 출력 옵션을 확인할 수 있다. 전체 글꼴 원본과 QA 화면은 공개 배포에 포함하지 않는다.
