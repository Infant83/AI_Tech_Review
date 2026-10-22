# AI_Tech_Review

기술 리뷰 패키지, 심층 리서치 메모, 슬라이드 산출물을 함께 관리하는 워크스페이스다.

## 저장소 구성
- 루트 주제 패키지는 `YYYY-MM-DD_<topic-slug>` 형식으로 관리한다.
- 일별 인테이크와 대화 메모는 `daily_research_review/` 아래에 누적한다.
- 리서치 리포트, 슬라이드 입력/산출물, 보조 소스는 주제 폴더 안에 함께 보관한다.
- 공개 PDF 문서는 `archive/manifest.json`에 등록하며, [아카이브 운영 안내](archive/README.md)에 따라 추가한다.

## 리뷰·렉처·브리핑과 자료 보관

[리뷰허브](https://infant83.github.io/AI_Tech_Review/)에서 심층 리뷰를 읽고, [렉처 노트](https://infant83.github.io/AI_Tech_Review/lectures/)에서 주제별 학습을 시작한다. [브리핑](https://infant83.github.io/AI_Tech_Review/briefings/)에서는 Daily Quantum Review(Daily Quantum Brief)와 주간 브리핑의 주제를 월별 달력과 게시판 목록으로 확인하고 PDF를 읽는다. 주요 메뉴는 리뷰허브 → 렉처 노트 → 브리핑 순서이며, [전체 자료 아카이브](https://infant83.github.io/AI_Tech_Review/archive/)는 전체 공개 PDF 보관본을 날짜·주제·분류로 찾는 보조 영역이다.

브리핑 달력은 공개 등록부의 `daily-quantum`·`weekly-review` 자료를 발행일 기준으로 표시한다. 메일 수신 시간이나 개인 메일 원문은 공개하지 않으며, 문서가 없는 날짜는 등록된 공개 브리핑이 없는 날을 뜻한다.

PDF를 등록한 뒤 `python3 scripts/publish_public_site.py --hub-only`를 실행하면 기존 리뷰 파일을 다시 생성하지 않고 허브·렉처 목록·브리핑·아카이브를 갱신한다. 기존 허브에 공개 조회수·분석 설정이 있으면 새 컴퓨터에서도 이를 보존하며, 명시한 환경변수가 있으면 그 설정을 우선한다. `site/manifest.json`은 심층 리뷰 목록, `site/archive-manifest.json`은 문서 목록이다.

2026-10-20에는 CMU 17-620 공개 실라버스에서 출발한 [퀀텀 머신러닝 독립 렉처 시리즈](2026-10-20_quantum-machine-learning-lecture-series/README.md)를 작성했다. [테크리뷰의 렉처 노트 항목](https://infant83.github.io/AI_Tech_Review/lectures/)에서 [웹 학습 노트](https://infant83.github.io/AI_Tech_Review/lectures/quantum-machine-learning/)와 PDF를 읽을 수 있다. 147쪽 2.0판은 80분 한국어 강의 18개·문제와 완전 풀이 72개·수학 준비편·한영 용어 144항목·14주 자율학습 안내·실행 실습 5개·프로젝트 3개를 제공한다. 원강의 녹취나 공식 교재가 아니며, 2025–2026 연구의 가정과 실제 QPU·고전 모사·논리 자원 추정의 범위를 구분한다.

## 기본 흐름

2026-10-22에는 Classiq의 최근 Quantum Office Hours 세 회와 NVIDIA 공동 금융 웨비나 한 회를 [상세 학습 노트](2026-10-22_classiq-talk-series/README.md)로 정리했다. [렉처 노트 목록](https://infant83.github.io/AI_Tech_Review/lectures/)에서 [웹 노트](https://infant83.github.io/AI_Tech_Review/lectures/classiq-talk-series/)와 61쪽 PDF를 읽을 수 있다. 1.1판은 실제 질의응답·수학 보충 해설·용어집·복습 문제와 풀이에 발표 화면 13개와 독립 설명 도식 6개를 함께 제공한다. 발표자의 보고값과 계산 예제, CPU·GPU 모사와 실제 QPU 실행의 범위를 구별한 독립 학습 자료다.

새 리뷰의 표지는 [과학 표지 제작 원칙](COVER_ART_DIRECTION.md)에 따라 기획하고 [표지 기획 양식](templates/cover-art-brief.md)을 주제 폴더에 남긴다. 과학 분야·표현 유형·매체를 구분하고, 의미를 보존하는 관계·기사 고유성·최근 표지와의 다양성·작은 화면에서의 판독을 함께 확인한다.

비디오 abstract는 사용자 요청·발행 요건 또는 편집 판단에 따라 선택한다. [시범 제작 원칙](VIDEO_ABSTRACT_DIRECTION.md), [영상 브리프](templates/video-abstract-brief.md), [노터 비디오 abstract 제작 소스](2026-10-21_video-abstract-pilot/v4/README.md)를 참고한다. 생성형 비디오 API 없이 코드로 제작하며 렉처 노트 등에 기본으로 추가하지 않는다.

게시물·피규어·영상의 용어·설명 순서·메시지 전달은 [공통 설명 준칙](SCIENTIFIC_EXPLANATION_DIRECTION.md)을 따른다. [게시물 개편 양식](templates/review-explanation-brief.md)과 [노터 영상 브리프](2026-10-17_noether-symmetry-conservation/video-abstract-brief.md)에 문장·발화·그림의 연결을 구체화한다.

노터 v4는 생성한 개념 배경에 검증한 운동·수식·수치와 한영 합성 내레이션을 합성한다. 실제 발화에 맞춰 용어와 도식의 등장·변화·정지를 배치하며, 대표 사례를 게시물의 ‘대칭·보존법칙을 설계와 검증에 쓴다’는 논지로 연결한다. 짧은 abstract와 심화 설명의 범위를 구분한다.

1. 주제 또는 소스 팩을 받는다.
2. 소스와 노트를 워크스페이스 구조에 맞게 정리한다.
3. 심층 리서치를 수행하거나 보강한다.
4. memo / deepresearch 마크다운을 작성한다.
5. 필요하면 Skywork로 슬라이드를 생성한다.
6. 핵심 메모는 Obsidian에 미러링하고 주요 패키지는 OpenProject에 아카이브한다.

## 공개 허브 조회수 표시
- 공개 허브는 GitHub Pages의 정적 HTML 위에서 동작하고, 조회수 표시는 Cloudflare Worker와 D1을 붙인 작은 집계 API로 처리한다.
- `scripts/publish_public_site.py`가 `site/assets/public-metrics.js`, `site/assets/public-metrics.css`, `window.AI_TECH_REVIEW_METRICS` 설정을 허브와 리뷰 HTML에 삽입한다.
- 브라우저는 현재 경로를 `/AI_Tech_Review/` 또는 개별 리뷰 경로로 정규화한 뒤 Worker의 `/hit`에 1회 조회를 보낸다. 같은 탭 세션의 중복 집계는 `sessionStorage` 키로 줄인다.
- 읽은 시간은 개인정보가 아니라 페이지 활성 시간이다. JS가 화면이 보이고 브라우저 포커스가 있으며 최근 입력/스크롤이 있었던 시간만 모은다. 2분 이상 입력이 없으면 idle로 보고 멈추며, 한 페이지 탭 세션은 최대 45분까지만 누적한다.
- `/engagement` 전송은 기존처럼 15초 주기 또는 `visibilitychange`/`pagehide`/`blur` 시점에만 수행한다. 5초 미만의 짧은 활성 시간과 이미 보고한 스크롤 깊이는 다시 보내지 않아 Worker/D1 쓰기 비용을 늘리지 않는다.
- Worker 구현은 `.automation/cloudflare/ai-tech-review-public-metrics/src/worker.js`에 있다. 배포 이름은 `infant83-public-metrics`이고, D1의 `page_counts`, `daily_counts` 테이블에 경로별 `views`, `active_seconds`, `engagement_events`, `max_scroll_percent`만 저장한다.
- API는 `https://infant83.github.io`와 로컬 개발 origin만 CORS로 허용한다. `profile`, `ai-tech-review`, `ax-camp`, `gitlab-lectures`, `ml-math` site id로 parent/child 경로를 묶고, `/summary`는 페이지별 통계와 사이트별 합계를 함께 반환한다.
- 집계는 경로 단위 카운터만 저장한다. IP, User-Agent, 쿠키, 개인 식별자는 저장하지 않는다.
- Cloudflare Web Analytics 스크립트는 별도 트래픽 분석용이고, 화면에 보이는 `허브 조회`와 `평균 읽은 시간`은 위의 Worker/D1 집계값을 사용한다.

## 최근 Daily Review 스냅샷
_`daily_research_review/`의 최신 5개 항목에서 자동 생성._

### 2026-06-16 · 2026-06-16 Lev Selector Recent Updates
- 유형: `conversation memo`
- 소스: [`daily_research_review/2026-06-16_lev-selector-recent-updates.md`](daily_research_review/2026-06-16_lev-selector-recent-updates.md)
- 2026-06-16 기준 Lev Selector 채널의 최신 주간 AI 업데이트는 2026-06-12 공개된 [Exciting AI Updates Weekly - June 12, 2026](https://www.youtube.com/watch?v=zyE4uXQ5hS4)입니다.
- GitHub companion slide도 [2026-06-12-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-06-12-AI-Updates.pptx)가 최신 AI Updates 파일로 확인되었습니다.
- 이번 주 신호는 새 모델 이름보다 `agent memory`, `harness engineering`, `context compression`, `enterprise data platform 안의 agent`에 더 강하게 모입니다.

### 2026-05-23 · AI for Science 리뷰 전략
- 유형: `daily package`
- 소스: [`daily_research_review/2026-05-23_ai-for-science-review-strategy/reports/2026-05-23_ai-for-science-review-strategy_overview.md`](daily_research_review/2026-05-23_ai-for-science-review-strategy/reports/2026-05-23_ai-for-science-review-strategy_overview.md)
- Gmail에서 `subject:"ai for sci"`로 검색해 1건을 확인했습니다.
- 메일은 2026년 5월 22일 16:52:49 KST에 발송된 자기 전달/공유 메일이며, 본문에는 Sergei Kalinin의 LinkedIn 게시글 링크가 들어 있었습니다.
- LinkedIn 미리보기에는 `The end of the beginning for AI for Science`라는 글이 확인되었습니다. 게시글은 2026년 5월 Nature에 나온 Google/FutureHouse 계열 AI 과학 에이전트 논문들을 변곡점으로 보고, 다음 단계는 문헌·코드·시뮬레이션을 실제 실험 세계와 연결하는 일이라고 해석하는 취지였습니다.

### 2026-05-18 · 2026-05-18 Lev Selector Recent Updates
- 유형: `conversation memo`
- 소스: [`daily_research_review/2026-05-18_lev-selector-recent-updates.md`](daily_research_review/2026-05-18_lev-selector-recent-updates.md)
- 2026년 5월 18일 기준으로 Lev Selector 채널의 최신 주간 AI 업데이트는 2026년 5월 15일 공개된 [Exciting AI Updates Weekly - May 15, 2026](https://www.youtube.com/watch?v=5bgrHdi8mcE)입니다.
- GitHub 슬라이드 저장소에서도 최신 `AI Updates` 파일은 [2026-05-15-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-05-15-AI-Updates.pptx)로 확인했습니다.
- 이번 주 신호는 `chatbot`에서 `digital employee`, 즉 여러 도구를 오래 붙잡고 실행하는 개인/업무용 에이전트로 관심이 이동했다는 점입니다.

### 2026-05-01 · Nature Alert AI Digest Memo - 30 April 2026
- 유형: `daily package`
- 소스: [`daily_research_review/2026-05-01_nature-alert-ai-digest/reports/2026-05-01_nature-alert-ai-digest_memo.md`](daily_research_review/2026-05-01_nature-alert-ai-digest/reports/2026-05-01_nature-alert-ai-digest_memo.md)
- Gmail의 `Fwd: Nature alert for 30th April 2026`에서 Nature Volume 652 Issue 8112의 AI 관련 항목을 선별했다.
- 심층 확인에서는 Nature 원문, arXiv, bioRxiv/ChemRxiv DOI, OpenAlex metadata, 저자 공개 PDF를 대조했다.
- 생성형 AI 묶음의 중심은 warm LLM의 sycophancy, agentic grant writing, Agent4Science, AI와 수학, world models, AI compute governance다.

### 2026-04-24 · LGD OLED 투자와 Display Week 2026 OLED 신호
- 유형: `conversation memo`
- 소스: [`daily_research_review/2026-04-24_lgd-oled-investment-display-week-signals.md`](daily_research_review/2026-04-24_lgd-oled-investment-display-week-signals.md)
- `2026-04-23 GPT Pulse`에서 나온 `LGD OLED 인프라 투자`와 `SID 전 LGD/Fraunhofer 신호`를 하나의 심층 기술 리뷰 패키지로 승격했다.
- 새 패키지: `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\2026-04-24_lgd-oled-investment-display-week-signals`
- 핵심 결론은 `LGD 투자 = blue PHOLED 양산 확정`이 아니라, `2026-2028 OLED 기술 인프라 경쟁으로 읽어야 한다`는 것이다.

## README 갱신
```bash
python scripts/generate_readme.py
```

최근 항목 수를 늘리고 싶으면:
```bash
python scripts/generate_readme.py --limit 8
```
