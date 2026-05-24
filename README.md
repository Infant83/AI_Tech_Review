# AI_Tech_Review

기술 리뷰 패키지, 심층 리서치 메모, 슬라이드 산출물을 함께 관리하는 워크스페이스다.

## 저장소 구성
- 루트 주제 패키지는 `YYYY-MM-DD_<topic-slug>` 형식으로 관리한다.
- 일별 인테이크와 대화 메모는 `daily_research_review/` 아래에 누적한다.
- 리서치 리포트, 슬라이드 입력/산출물, 보조 소스는 주제 폴더 안에 함께 보관한다.

## 기본 흐름
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
- 읽은 시간은 개인정보가 아니라 페이지 활성 시간이다. JS가 화면이 보이는 동안의 시간을 모으고, 15초 주기 또는 `visibilitychange`/`pagehide` 시점에 `/engagement`로 보낸다. 5초 미만이고 스크롤 25% 미만인 짧은 흔적은 버린다.
- Worker 구현은 `.automation/cloudflare/ai-tech-review-public-metrics/src/worker.js`에 있다. 배포 이름은 `infant83-public-metrics`이고, D1의 `page_counts`, `daily_counts` 테이블에 경로별 `views`, `active_seconds`, `engagement_events`, `max_scroll_percent`만 저장한다.
- API는 `https://infant83.github.io`와 로컬 개발 origin만 CORS로 허용한다. `profile`, `ai-tech-review`, `ax-camp`, `gitlab-lectures`, `ml-math` site id로 parent/child 경로를 묶고, `/summary`는 페이지별 통계와 사이트별 합계를 함께 반환한다.
- 집계는 경로 단위 카운터만 저장한다. IP, User-Agent, 쿠키, 개인 식별자는 저장하지 않는다.
- Cloudflare Web Analytics 스크립트는 별도 트래픽 분석용이고, 화면에 보이는 `허브 조회`와 `평균 읽은 시간`은 위의 Worker/D1 집계값을 사용한다.

## 최근 Daily Review 스냅샷
_`daily_research_review/`의 최신 5개 항목에서 자동 생성._

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

### 2026-04-23 · 2026-04-23 GPT Pulse Overview
- 유형: `daily package`
- 소스: [`daily_research_review/2026-04-23_gpt-pulse-daily-review/reports/2026-04-23_gpt-pulse-daily-review_overview.md`](daily_research_review/2026-04-23_gpt-pulse-daily-review/reports/2026-04-23_gpt-pulse-daily-review_overview.md)
- 오늘 확인한 최신 Pulse 이슈는 `4월 23일` 표기본이었다.
- 전체 방향은 `교육/포용`, `MLOps/에이전트 거버넌스`, `중동 지정학 리스크`, `온디바이스 음성 실험`, `OLED/Display Week 신호`의 혼합형 피드였다.
- 후속 심층리서치 1순위는 `Agent observability and CI workload identity governance`다.

## README 갱신
```bash
python scripts/generate_readme.py
```

최근 항목 수를 늘리고 싶으면:
```bash
python scripts/generate_readme.py --limit 8
```

