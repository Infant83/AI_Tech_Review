# 통합 HTML과 PDF 재생성

루트의 학습 문서 다섯 개와 `sessions/` 네 파일을 순서대로 묶어 `dist/index.html`과 `output/pdf/classiq-talk-series-notes-ko.pdf`를 만든다. `dist/notes.pdf`는 읽기용 사본이다. 원영상·자막·전사·QA 파일은 복사하지 않는다. 파일 목록을 고정해 최종 글·승인한 그림·스타일·글꼴·라이선스만 읽기용 폴더에 넣는다.

`build_fonts.py`는 제공된 OFL 한국어 글꼴을 문서에 필요한 문자만 포함한 WOFF2로 만들고 family 이름을 QML Archive Sans로 바꾼다. 이전 렉처 시리즈의 조판 체계를 재사용했으며 원본 글꼴의 라이선스는 `font-OFL.txt`에 보존했다. 글꼴 원본 경로는 출력물에 남기지 않는다.

필요한 Python 패키지는 fontTools·Brotli와 도식 제작용 Matplotlib·NumPy, Node 패키지는 marked·mathjax-full·playwright다. Node의 모듈 위치를 `REVIEW_NODE_MODULES`에 운영체제 경로 구분자로 연결한다. Google Chrome이 설치돼 있어야 한다. 아래 명령은 시리즈 루트에서 실행한다.

도식은 설치된 Noto Sans KR 글꼴을 사용한다. 글꼴 파일이 기본 사용자 글꼴 폴더에 없으면 `CLASSIQ_FIGURE_FONT_REGULAR`·`CLASSIQ_FIGURE_FONT_BOLD` 환경변수로 지정한다.

```sh
python artifacts/build_fonts.py --regular FONT_REGULAR.ttf --bold FONT_BOLD.ttf
python artifacts/verify_examples.py
python artifacts/build_concept_figures.py
python artifacts/merge_figures.py
node artifacts/build_notes.mjs
node artifacts/print_notes.mjs
```

`FONT_REGULAR.ttf`·`FONT_BOLD.ttf`를 OFL 글꼴 원본으로 바꾼다. 재생성 때도 글꼴과 본문을 함께 갱신한다. MathJax가 수식을 SVG로 렌더하며, 미해결 수식과 허용하지 않은 로컬 링크를 만나면 생성을 중단한다.

`figures/concepts/manifest.json`과 두 화면 발췌 manifest를 `merge_figures.py`로 합쳐 최종 허용 목록 `figures/manifest.json`을 만든다. 발표 발췌 PNG는 출처 시각과 크롭 영역이 확정된 편집 자산이다. SVG와 PNG를 임의로 폴더 전체에서 복사하지 않고, 실제 본문에서 사용하는 최종 목록만 복사한다. 캡션과 확대 링크는 본문에서 생성한다.

`print_notes.mjs`는 데스크톱 1440px와 모바일 390px에서 본문 가로 넘침, 글꼴 로드, 수식 오류, 깨진 내부 링크와 중복 ID, 모든 그림의 로드·대체 텍스트·캡션·잘림을 검사한 다음 A4 PDF를 만든다. 그림별 확대 검수 화면도 남긴다. PDF에는 로컬 서버를 가리키는 다운로드 링크를 넣지 않는다. `tmp/pdfs/`의 화면·검사 결과는 읽기용 폴더에서 제외한다.

최종 PDF는 Poppler로 모든 페이지를 렌더해 접촉시트와 대표 확대 화면으로 확인한다. pypdf로 metadata·첨부·URI와 본문 누락을 검사한다. 독립 수학 검토와 원영상 내용 확인은 출력 레이아웃 검사와 별개이며, 해당 범위는 `sources.md`에 기록한다.
