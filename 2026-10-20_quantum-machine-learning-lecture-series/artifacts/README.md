# HTML·PDF 재생성

이 폴더의 스크립트는 편집 가능한 Markdown 정본에서 한 페이지 HTML과 통합 A4 PDF를 만든다. 작업 위치는 시리즈 루트다. 원문·실습 실행 결과를 갱신한 다음 글꼴 → 교육용 그래프 → HTML → PDF 순으로 실행한다. `dist/`는 재생성 때 allowlist로 다시 만들며 개인 환경의 경로·QA 이미지·조사 메모를 복사하지 않는다.

## 설치 기록

실제 조판에 사용한 Node는 24.19.0, marked 17.0.5, mathjax-full 3.2.2, Playwright 1.62.1, Google Chrome 155.0.8059.85다. 다음은 프로젝트 전용 설치 예시다. npm과 Google Chrome이 설치되어 있어야 한다.

```sh
npm install --prefix .build/node --no-save marked@17.0.5 mathjax-full@3.2.2 playwright@1.62.1
export REVIEW_NODE_MODULES="$(pwd)/.build/node/node_modules"
```

이미 설치된 모듈을 쓰려면 `REVIEW_NODE_MODULES`에 해당 `node_modules` 디렉터리를 지정한다. 여러 경로는 운영체제의 경로 구분자(macOS/Linux `:`, Windows `;`)로 연결한다. 각 패키지를 서로 다른 경로에 설치해도 된다. Chrome은 기본 `channel: chrome`으로 선택하며 별도 실행 파일을 쓰려면 `REVIEW_CHROME`을 지정한다.

Python 패키지의 실제 사용 버전은 fontTools 4.58.4, Brotli 1.1.0(글꼴 subset), NumPy 2.3.5, Matplotlib 3.10.7(그래프), pypdf 6.10.0(검사), Pillow 11.2.1(접촉시트)이다. 글꼴 작업은 Python 3.9.6에서, 그래프와 PDF 검사는 Python 3.12.14에서 수행했다. 하나의 Python 3.12 가상환경에 다음 패키지를 설치해 사용할 수도 있다. 이 통합 설치 조합 자체는 별도 실행하지 않았으므로 기록된 각 도구 버전과 실행환경을 구별한다.

```sh
python3.12 -m venv .build/python
. .build/python/bin/activate
python -m pip install fonttools==4.58.4 Brotli==1.1.0 numpy==2.3.5 matplotlib==3.10.7 pypdf==6.10.0 Pillow==11.2.1
```

## 생성 명령

글꼴 원본 Regular·Bold TTF는 별도로 준비한다. 배포된 Nanum Gothic의 OFL은 `font-OFL.txt`에 보존했다. `build_fonts.py`는 출력 font의 family·full·PostScript 이름을 **QML Archive Sans**로 바꾼 뒤 정본과 UI에 필요한 글리프만 WOFF2로 저장한다. 원본 font 경로는 출력 font에 기록하지 않는다.

```sh
python artifacts/build_fonts.py --regular FONT_REGULAR.ttf --bold FONT_BOLD.ttf
python artifacts/build_figures.py
node artifacts/build_notes.mjs
node artifacts/print_notes.mjs
```

font 옵션 대신 `QML_FONT_REGULAR`, `QML_FONT_BOLD` 환경변수도 사용할 수 있다. `FONT_REGULAR.ttf`, `FONT_BOLD.ttf`는 준비한 파일 경로로 바꾼다. 첫 PDF 제작 때 적용한 artifact-operation marker는 제작 세션용이며 이 일반 재생성 명령에 중복해서 넣지 않았다.

HTML 출력은 `dist/index.html`, PDF 정본은 `output/pdf/quantum-machine-learning-lecture-notes-ko.pdf`, 배포 사본은 `dist/notes.pdf`다. MathJax는 `\(...\)`, `$$...$$`, `\[...\]`를 SVG로 조판하며 코드 블록·inline code의 수식 문자열은 바꾸지 않는다. Markdown 문서 링크는 내부 anchor로 바꾸고 실습 코드·결과 8개와 그래프 3개·출처 manifest·subset 글꼴·OFL만 명시적으로 배포한다.

2.0판은 수학 준비편·용어집·워크북을 포함한 정본 27개를 순서대로 묶는다. 용어집의 144항목에는 안정적인 anchor를 붙이고 브라우저에서 한국어·영문·약어 검색을 제공한다. 검색 상태는 인쇄 내용에 영향을 주지 않는다.

`print_notes.mjs`는 1440px·390px에서 가로 넘침, 수식 오류, 깨진 anchor·중복 ID, 글꼴과 세 그림의 load·clipping을 확인하고, 144항목 검색의 단일 결과·결과 없음·초기화도 검증한다. 그 뒤 태그와 목차가 있는 PDF를 만든다. QA 화면과 결과는 `tmp/pdfs/`에만 저장한다. PDF는 본문 9.6pt, A4, 쪽번호 footer, 문서별 새 페이지이며 참고문헌은 8.2pt로 조판한다.

## PDF 최종 검사

Poppler의 `pdftoppm`·`pdfinfo`로 페이지를 렌더하고 문서 정보를 확인한다.

```sh
pdftoppm -r 80 -png output/pdf/quantum-machine-learning-lecture-notes-ko.pdf tmp/pdfs/page
pdfinfo output/pdf/quantum-machine-learning-lecture-notes-ko.pdf
```

모든 페이지 PNG를 접촉시트로 검토하고 대표 수식·표·용어 페이지는 확대 검토한다. pypdf로 본문 누락, metadata, attachment와 링크 URI를 확인하고 내부 경로·로컬 서버 URI가 없음을 검사한다. `tmp/pdfs/`는 공개 배포물에 포함하지 않는다. 논문 도표나 물리 장치의 측정값을 생성한 것으로 표시하지 않는다.
