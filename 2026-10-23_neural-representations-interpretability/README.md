# 신경망을 이해한다는 것: 의미를 읽고 원인을 시험하는 과학

2026-10-23 심층 개편판. 초기 기사 검토를 독립 AI Tech Review로 발전시킨 교양과학 글이다. 뉴런·특징·회로에서 출발해 모델 수정과 추적, 안전 감사, 독립 검증과 신뢰의 조건으로 이어진다.

- 한국어 정본: [reports/review.md](reports/review.md)
- 전체 영어판: [reports/review_en.md](reports/review_en.md)
- 읽기용 웹: [dist/index.html](dist/index.html), [dist/en/index.html](dist/en/index.html)
- 한영 PDF: [한국어](dist/review.pdf), [English](dist/en/review-en.pdf)
- 설명 기획과 독자·주장·그림의 연결: [review-explanation-brief.md](review-explanation-brief.md)
- 표지·도식 제작 기록: [cover-art-brief.md](cover-art-brief.md), [figure-manifest.json](figure-manifest.json)

댈러스–텍사스–오스틴 계산의 특징군 개입을 먼저 설명하고, 입력을 바꾸는 일과 내부 계산에 개입하는 일의 차이를 보여 준다. 다의성·중첩·재귀적 일반화·SAE를 구별한 뒤 원래 뉴런의 문법 회로 실험과 Goodfire–Gao 논쟁을 잇는다. 후반부는 금문교 특징 조절, 페르소나 벡터의 개입과 실패한 규제, AuditBench v4를 바탕으로 ‘설명을 찾은 다음 어떻게 고치고 다시 점검할 것인가’를 묻는다. 접근권과 수정 목표에 관한 논의는 리뷰의 전망으로 명시한다.

실제 모델 학습·SAE/CLT·개입·감사 실험을 독립 재현하지 않았다. 원 논문·고정 공식 코드·평가 조건을 대조했으며 보고 결과, 리뷰 해석, 후속 제안을 구별한다. 구독이 필요한 MIT 테크놀로지 리뷰 인터뷰 전문은 접근하지 않았다. 최초 8쪽판은 내부 제작 기록으로 보존하며 공개 아카이브에 중복 등록하지 않는다.

## 재생성

주제 폴더에서 `python3 artifacts/build_figures.py`가 초기 개념 도식을, `python3 artifacts/build_deep_figures.py`가 새 도시 개입·연구에서 개발로 이어지는 도식을 만든다. 정식 본문에는 유지한 표현 개념 도식 1종과 새 도식 2종만 사용한다.

`python3 artifacts/build_fonts.py --regular FONT --bold FONT`가 원고·UI·SVG의 문자를 모아 공개 라이선스 글꼴 subset을 생성한다. `artifacts/font-OFL.txt`와 `artifacts/font-license.txt`에 라이선스를 보존한다. `REVIEW_NODE_MODULES`를 설치된 Node dependency 디렉터리로 지정한 뒤 Node로 `artifacts/build_review.mjs`를 실행한다. `marked`를 사용하며 TeX가 있을 때만 `mathjax-full`을 사용한다.

`artifacts/build_pdf.py --node NODE --modules MODULES`는 로컬 HTML에서 한영 PDF를 출력한다. Playwright와 Chrome이 필요하다. 모든 페이지를 렌더링해 확인하고 웹의 모바일 화면·자산·메타데이터도 별도로 검사한다. SVG 원본 확대 링크는 화면에서 제공하고 PDF에는 내부 file URL이 남지 않도록 처리한다.

## 배포 범위

정식 리뷰는 `scripts/publish_public_site.py`의 등록부에서 관리하고, 최종 검수한 한영 PDF를 `archive/manifest.json`에 등록한다. 중앙 게시기는 로컬 정적 사이트를 만든다. 로컬 생성만으로 외부 사이트 게시 완료를 뜻하지 않으며 Git commit·push와 실제 live URL 확인은 수행한 경우에만 별도로 기록한다.

최종 `dist/`에는 해당 언어의 HTML·CSS·표지·설명 SVG·PDF만 포함한다. 원문 수집 파일·조사 노트·QA PNG·로컬 절대경로는 배포하지 않는다. `notes/`와 `tmp/`는 내부 기록이며 `.gitignore`와 사이트의 자산 허용목록으로 배포에서 제외한다. 초기 8쪽판과 보관용 `hero-original.png`는 공개 리뷰 자산으로 복사하지 않는다.

## 작성과 검토

책임 편집자는 김현중이다. OpenAI Codex가 조사·한영 집필·시각자료·출력 제작을 보조했다. 별도 역할이 과학·수치·주장 범위, 읽기 흐름과 전망, 한영 대응, 실제 출력물을 검토했다. 사람의 주제 채택·문체 방향은 반영했지만 전체 원고의 문장별 사람 감수나 이해도 평가는 수행하지 않았다. 하네스와 역할·검증 범위는 한영 본문 하단에 공개한다.

## 최종 검수와 로컬 등록

심층판은 한국어 12쪽·영어 14쪽이다. 최종 26쪽을 렌더링하고 본문·도식·4행 표·참고문헌·작성 공개를 확인했다. 한영 제목·메타데이터·글꼴·자산 참조가 일치하고 390px 모바일 가로 넘침·깨진 이미지·페이지 오류는 0이다. PDF 첨부·내부 file URI·내부 경로·대체문자도 발견되지 않았다.

한영 PDF를 정식 리뷰 목록과 PDF 아카이브의 로컬 사이트에 등록했다. 주제 원본·아카이브·사이트 리뷰·사이트 아카이브의 네 사본은 언어별로 바이트가 같다. 기존 문서 등록 정보를 보존했고, 관련 기존 검사 51개와 사이트 검증을 통과했다. 원고·코드·도식과 명시한 자산만 배포하며 내부 초기판·수집 원문·노트·QA는 제외한다. Git commit·push·외부 사이트 업로드와 live URL 검증은 실행하지 않았다.
