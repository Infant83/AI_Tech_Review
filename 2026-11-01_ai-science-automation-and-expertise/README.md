# 양자와 재료 연구의 AI 자동화와 과학적 판단

2026-11-01 · AI Tech Review Letters · AI for Science

양자 시뮬레이션 에이전트와 전자구조 예측 신경망의 실제 과제를 설명하고, 질문·계산 조건·학습 목표·재현 기준에 전문성이 사용되는 방식을 다룬다. 에이전트의 소프트웨어 운영, 학습 대리모형, 설정 평가, 주장 재현과 연구 품질 집계를 서로 다른 성과로 읽는다. 한국어 정본과 영어 전문을 제공한다.

## 읽기와 상태

- 한국어: [원고](reports/review_ko.md), [웹](dist/index.html), [PDF](dist/review_ko.pdf)
- English: [Manuscript](reports/review_en.md), [Article](dist/en/index.html), [PDF](dist/en/review_en.pdf)
- [표지 기획](cover-art-brief.md), [설명 설계](review-explanation-brief.md), [표지 프롬프트](artifacts/hero-prompt.txt)
- 상태: 한영 원고·독립 과학·설명 감수와 HTML/PDF 출력 검수를 완료했다. 한국어9쪽·영어11쪽의 전 페이지, 모바일390px, 출처·글꼴·링크를 확인했으며 공개 페이지와 PDF·그림·표지의 실제 HTTPS 배포 검증도 완료했다.
- 공개 주소: https://infant83.io/AI_Tech_Review/reviews/2026-11-01_ai-science-automation-and-expertise/
- English: https://infant83.io/AI_Tech_Review/reviews/2026-11-01_ai-science-automation-and-expertise/en/

## 근거와 작업 범위

El Agente Cuántico의 arXiv v3 PDF와 Borealis V6 일부 공개 산출물, AutoMat v2 PDF, FermiScope v1 PDF·HTML·표, INCARBench v2, JCCM의 공개 방법과 집계 및 2024년 인간–AI 메타분석·Perspective를 대조했다. JCCM의 제한된 코멘터리 PDF 전문은 열람하지 않았다. 기술적 수치의 근거와 실제 인용 판본을 구별했다.

El Agente의 abstract 메타데이터·HTML·PDF에는 저자 목록·날짜 차이가 있어 기술 검토에는 2026-11-01에 확보한 80쪽 v3 PDF를 사용했다. 저널 최종판 전문과 같다고 가정하지 않는다. 논문의 관측량·초기분포 실패 설명과 공개 실행 폴더가 일관되게 대응함을 확인하지 못했으므로, 실패 사례는 논문 보고로 귀속한다. 공개 코드를 실행해 재현했다는 주장을 하지 않는다.

FermiScope의 Table 1·7·12는 PDF와 HTML을 대조했다. 50개 분자의 SCF 반복·총시간 비교가 존재하며, 누적 LDOS만의 추가 속도 향상으로 확대하지 않는다. INCARBench는 표준화한 참조 설정을 평가하고, 실제 VASP 물성·수렴을 검증한 연구와 구별한다. JCCM의 88%는 AI 평가자의 문제 지적 비율이며 사람의 확정 오류율이 아니다. 동일 분야 표본·대조군과 전체 표본을 섞지 않는다.

## 독립 검토와 실제 역할

- root: 공개 1차 출처 종합, 한국어 집필, 표지 기획·생성, 편집과 출판 통합.
- cuantico_source: El Agente·AutoMat 판본·수치·공개 산출물 대조와 한국어 원고의 독립 과학·설명·서지 검토.
- dqb_fermiscope: FermiScope·INCARBench PDF·표와 교육 모형의 독립 검산, 해당 원고·도식 감수.
- journal_dataset: JCCM 데이터·대조군과 메타분석·Perspective의 범위 검토, 영어 전문 번역과 한영 주장·참고문헌 대응 검사.
- agent_standards: 원본 한영 PC·모바일 SVG, 데이터 재도식, 글꼴·HTML/PDF 조판과 출력 검사.

작성 시스템은 OpenAI Codex이고 정확한 작성 모델 식별자는 미보존이다. 사용자의 주제·분야 맥락·비판적 AI 활용·전문성에 대한 편집 방향을 반영했다. 문장 단위 사람 승인·독자 이해도 평가는 수행하지 않았다. 출력 검사를 사람의 이해도 평가로 표시하지 않는다.

## 세 도식과 재현 범위

1. `h2_energy`: Borealis V6의 CC0 원본 CSV 19점을 재도식했다. 보고 오차 열의 mHa를 μHa로 변환했다. 반올림된 에너지끼리 뺀 값이 아니다. VQE 재실행·실제 QPU 결과가 아니다.
2. `density_gap`: 같은 정규직교 기저와 반대 스핀 전자 2개에서 비점유 준위를 바꾼 교육 모형이다. 독립 SCF 해나 Hohenberg–Kohn 반례가 아니다. 밀도 비교의 blind spot을 설명하며 평균 행렬 오차와 gap 오차의 역전은 논문의 별도 표로 뒷받침한다.
3. `referee_controls`: 공개된 동일 분야 AI 표본 130편과 일반 대조군 50편의 비율·95% bootstrap 구간을 다시 그렸다. 원 AI 심사를 재실행하거나 개별 논문을 재판정하지 않았다.

도식은 각 언어의 PC·모바일 판본으로 작성했고 출처·가공값·검사를 [제작 코드](artifacts/build_figures.py)와 [그림 출처](artifacts/data/figure-provenance.json)에 남겼다. 표지는 내장 image_gen의 원본 개념 그림이다. 프리즘은 정보의 구분과 관찰의 선택을 비유하며, 실제 LDOS 측정이나 장치가 아니다. 새 영상은 제작하지 않았다.

## 다시 만들기

1. `python3 artifacts/build_figures.py`로 원본 한영 SVG를 만든다.
2. NanumGothic Regular·Bold와 Noto Sans 보완 글꼴의 OFL 원본을 사용해 `python3 artifacts/build_fonts.py --regular FONT_REGULAR --bold FONT_BOLD`를 실행한다.
3. 설치된 Node 모듈의 경로를 `REVIEW_NODE_MODULES` 등 builder의 의존성 경로에 제공하고 `node artifacts/build_review.mjs`를 실행한다. `marked`·`mathjax-full`이 필요하다.
4. PDF 새 제작·편집의 적용 가능한 도구 계약을 따른 뒤 `python3 artifacts/build_pdf.py --node NODE_BINARY --modules NODE_MODULES`로 Chrome·Playwright 출력을 만든다.

원 논문 PDF·수집 원문·개인 메일·QA 화면과 상세 감사는 `notes/`·`tmp/`에만 보존하고 Git과 공개 배포에서 제외한다. 웹 배포는 dist의 최종 HTML·CSS·표지·명시된 도식·PDF만 허용한다. 중앙 등록은 scripts/publish_public_site.py와 scripts/hub_summaries_en.json으로 관리한다.

## 출판 검증

공개 사이트 검사 오류0, 관련87개 회귀검사 통과. 기존 리뷰1469개 파일·50개 리뷰 기록·96개 아카이브 기록과 기존 독자용 기사 수정 이력을 보존했다. 등록 후51개 리뷰·98개 PDF이며, 각 언어 PDF의 제작본·원본 아카이브·공개 기사·공개 아카이브4사본이 같은 SHA256이다. 정확한 값과 출력 범위는 [제작 manifest](figure-manifest.json)에 기록한다. [Pages배포](https://github.com/Infant83/AI_Tech_Review/actions/runs/41263176124)가 성공했고 실제32개 URL을 확인했다. 바이너리 자산은 모두 정확히 일치했고,8개HTML은 식별한 Cloudflare 분석 스크립트 삽입·기존 공개 연락 링크 보호만 제외하면 일치했다. 한영 기존 canonical 주소도 실제 서비스 도메인으로 정상 연결된다.

실제 서비스의 한영1440/390px 화면·도식·공개 정보와 KO→EN→KO 전환도 확인했다. 초기 공용 갱신 처리가 끝난 뒤 글꼴과 이미지를 다시 확인했다. 본문·자산 오류0이며, 익명 구독 조회401은 기존 기사에서도 같은 동작이었다. 읽기전용 QA는 통계 POST를 차단했고 구독·반응·메시지를 작성하지 않았다.
