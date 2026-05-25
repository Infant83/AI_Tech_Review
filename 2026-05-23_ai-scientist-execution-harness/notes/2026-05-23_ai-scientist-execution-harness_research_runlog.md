# AI 과학자 실행 하네스 리뷰 runlog

## 2026-05-23

### 패키지 생성

- Root topic folder: `2026-05-23_ai-scientist-execution-harness/`
- 생성 목적: `daily_research_review/2026-05-23_ai-for-science-review-strategy/`에서 정리한 intake를 본 리뷰 작성 공간으로 승격

### 생성 폴더

- `sources/`
- `notes/`
- `reports/`
- `artifacts/final_review/figures/`
- `skywork_inputs/`
- `skywork_exports/`

### 초기 파일

- `sources/2026-05-23_ai-scientist-execution-harness_intake_bridge.md`
- `notes/2026-05-23_ai-scientist-execution-harness_review_flow.md`
- `notes/2026-05-23_ai-scientist-execution-harness_research_runlog.md`
- `reports/2026-05-23_ai-scientist-execution-harness_final_review.md`
- `skywork_inputs/2026-05-23_ai-scientist-execution-harness_skywork_prompt_v1.md`

### 가져온 그림

- `artifacts/final_review/figures/ai_scientist_validation_loop.svg`
- `artifacts/final_review/figures/ai_scientist_harness_example.svg`
- `artifacts/final_review/figures/ai_scientist_hero.svg`
- `artifacts/final_review/figures/ai_scientist_guardrail_matrix.svg`

### final_review 작성 및 검증

- 작성 파일: `reports/2026-05-23_ai-scientist-execution-harness_final_review.md`
- HTML companion: `reports/2026-05-23_ai-scientist-execution-harness_final_review.html`
- 포함 그림:
  - hero: `ai_scientist_hero.svg`
  - validation loop: `ai_scientist_validation_loop.svg`
  - harness example: `ai_scientist_harness_example.svg`
  - guardrail matrix: `ai_scientist_guardrail_matrix.svg`
- 포함 실전 예시:
  - `problem_card.yaml`
  - `prompts/hypothesis_generation.md`
  - `hypothesis_candidates.json`
  - `score_hypotheses.py`
  - Gemini CLI / Claude Code headless-style command examples
- 문체/그림 audit:
  - command: `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: `finding_count: 0`, `figure_count: 4`, `figure_density: ok`
- HTML 렌더링:
  - command: `python scripts\markdown_to_html.py --mode final-review .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: rendered successfully
- 로컬 이미지 참조 확인:
  - image count: 4
  - all referenced SVG assets exist under `artifacts/final_review/figures/`
- Playwright browser check:
  - command: `npx playwright screenshot --full-page file:///.../reports/2026-05-23_ai-scientist-execution-harness_final_review.html %TEMP%\ai_scientist_final_review_playwright.png`
  - result: screenshot captured in temp folder; hero, side table of contents, figures, code blocks, and references rendered normally

### 남은 후속 작업

1. 사용자가 배포를 원하면 `dist/`와 `dist.zip` 생성
2. 필요 시 Obsidian mirror 및 OpenProject sync
3. Skywork deck 생성 단계로 승격 가능

### 도입/문체/시각 자료 재작업

- 사용자 피드백 반영:
  - 에르되시 문제 #1196의 배경 설명이 부족했던 도입부를 전면 재작성
  - `Bixonimania` 사례를 초반 경고에서 중반부 자연스러운 우려 질문으로 이동
  - `사례로 읽는 편이 안전합니다`, `짚었습니다`, `보여줍니다`, `하자는 뜻은 아닙니다` 계열의 독자 해석 강제 문체 제거
  - `하네스`, `감사`, `인간의 판단` 같은 반복 주제어의 노출을 줄이고 `작업대`, `작업 폴더`, `실행 루프` 중심으로 분산
- 추가 품질 기준 파일:
  - `GOAL.md`
- 생성/채택한 imagegen 이미지:
  - `artifacts/final_review/figures/imagegen/ai_scientist_erdos_blackboard.png`
  - `artifacts/final_review/figures/imagegen/ai_scientist_coscientist_lab.png`
  - `artifacts/final_review/figures/imagegen/ai_scientist_guarded_library.png`
  - manifest: `artifacts/final_review/figures/imagegen/IMAGEGEN_MANIFEST.md`
- 추가 SVG:
  - `artifacts/final_review/figures/ai_scientist_erdos_1196_explainer.svg`
- 재작성 후 audit:
  - command: `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: `finding_count: 0`, `figure_count: 7`, `figure_density: ok`
- HTML 재렌더링:
  - command: `python scripts\markdown_to_html.py --mode final-review .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: rendered successfully
- 로컬 이미지 참조 확인:
  - image count: 7
  - all referenced PNG/SVG assets exist
- Playwright browser check:
  - command: `npx playwright screenshot --full-page file:///.../reports/2026-05-23_ai-scientist-execution-harness_final_review.html %TEMP%\ai_scientist_final_review_revised_playwright.png`
  - result: hero image, section figures, side TOC, code blocks, and references rendered normally

### 작성 정보 / References / provenance 보강

- Gmail 확인:
  - query: `in:anywhere subject:"ai for sci" -in:trash -in:spam`
  - result: 2026-05-22 16:52 KST, subject `ai for sci`
  - body: Sergei Kalinin LinkedIn 공유 링크 1건
  - 적용: 메일은 주제 탐색 신호로만 기록하고, 본문 claim은 외부 검증 자료로 재확인
- 추가 리서치:
  - Nature, `Towards end-to-end automation of AI research`, 2026-03-25
  - 본문 `수학에서 과학으로` 섹션에 The AI Scientist 문단 추가
  - References에 The AI Scientist와 직접 검증 항목 추가
- 작성 정보 보강:
  - `작성자`, `작성 보조 및 퇴고`, `최초 작성일`, `최종 수정`, `작성 형식`, `발행 라벨`
  - `주제 탐색 참고자료`, `주요 검증 참고자료`
  - 이전 리뷰 참고: `2026-05-09_ai-updates-weekly_final_review.md`, `2026-05-07_tabpfn-oled-manufacturing-foundation-model_final_review.md`
- References 구조 변경:
  - `직접 검증 참고자료`
  - `처음 참고한 자료`
  - `문체와 시각자료 참고`
- Figure provenance:
  - created `artifacts/final_review/figures/FIGURE_MANIFEST.md`
  - linked existing `artifacts/final_review/figures/imagegen/IMAGEGEN_MANIFEST.md`
  - additional figure was not added; current article uses 7 figures and the new provenance/reference sections do not need another visual in the body
- 문체/그림 audit:
  - phrase scan: no matches for the main watchlist after replacing `좋은 보조선`
  - command: `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: `finding_count: 0`, `figure_count: 7`, `figure_density: ok`
- HTML 재렌더링:
  - command: `python scripts\markdown_to_html.py --mode final-review .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: rendered successfully
- 로컬 이미지 참조 확인:
  - image count: 7
  - all referenced PNG/SVG assets exist
- 로컬 문서 링크 확인:
  - local href count: 15
  - missing count: 0
- Playwright browser check:
  - command: `npx playwright screenshot --full-page file:///.../reports/2026-05-23_ai-scientist-execution-harness_final_review.html %TEMP%\ai_scientist_final_review_provenance_pass_playwright.png`
  - result: hero, figures, code blocks, 작성 정보, 계층형 References, side TOC rendered normally

## 2026-05-25

### 섹션 단위 퇴고

- 대상 파일: `reports/2026-05-23_ai-scientist-execution-harness_final_review.md`
- 퇴고 방식: 문단 단위가 아니라 섹션 단위로 도입부, 수학에서 과학으로, 국가/기업 전환, 실행 전략, 결말을 순차 수정
- 수정 방향:
  - 도입부의 기사 전달 톤을 줄이고 Liam Price와 에르되시 #1196 장면에서 바로 수학적 질문으로 들어가도록 조정
  - `수학에서 과학으로` 섹션의 사례 나열을 연구 업무 단위 변화라는 한 축으로 정리
  - 국가/기업 신호가 회사 문제로 내려오는 연결을 강화
  - 실행 하네스 설명에서 추상 은유보다 문제 카드, 자료, 평가 함수, 의사결정 로그가 보이도록 수정
  - 결말의 슬로건성 비유를 낮추고 작은 작업대와 기록 중심의 준비로 마무리
- 문체/그림 audit:
  - command: `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: `finding_count: 0`, `figure_count: 7`, `figure_density: ok`
- HTML 재렌더링:
  - command: `python scripts\markdown_to_html.py --mode final-review .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: rendered successfully
- 배포용 dist 갱신:
  - command: `python scripts\html_to_dist.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.html --dist .\2026-05-23_ai-scientist-execution-harness\dist --zip --zip-path .\2026-05-23_ai-scientist-execution-harness\dist.zip`
  - result: `[local-ref-check] ok`
  - package path: `2026-05-23_ai-scientist-execution-harness\dist`
  - zip path: `2026-05-23_ai-scientist-execution-harness\dist.zip`
- 배포본 렌더링 확인:
  - command: `npx playwright screenshot --full-page http://127.0.0.1:8793/index.html %TEMP%\ai_scientist_dist_section_polish_20260525.png`
  - result: screenshot captured, `5308634` bytes
- Obsidian mirror:
  - mirror root: `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-23_ai-scientist-execution-harness`
  - copied: report markdown, report HTML, research runlog, final review figures

### 제목 확정 후 HTML/dist 재배포

- 대상 파일: `reports/2026-05-23_ai-scientist-execution-harness_final_review.md`
- 확정 제목: `AI 과학자, 시작의 끝에서: The End of the Beginning for AI Scientists`
- 확정 부제: `에르되시 문제 #1196에서 연구 실행 하네스까지, 우리가 이미 기대기 시작한 AI 과학자를 어떻게 준비할 것인가`
- 문체/그림 audit:
  - command: `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: `finding_count: 0`, `figure_count: 7`, `figure_density: ok`
- HTML 재렌더링:
  - command: `python scripts\markdown_to_html.py --mode final-review .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - result: rendered successfully
  - html path: `2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.html`
  - html size: `76055` bytes
- 배포용 dist 갱신:
  - command: `python scripts\html_to_dist.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.html --dist .\2026-05-23_ai-scientist-execution-harness\dist --zip --zip-path .\2026-05-23_ai-scientist-execution-harness\dist.zip`
  - result: `[local-ref-check] ok`
  - package path: `2026-05-23_ai-scientist-execution-harness\dist`
  - index path: `2026-05-23_ai-scientist-execution-harness\dist\index.html`
  - index size: `74847` bytes
  - zip path: `2026-05-23_ai-scientist-execution-harness\dist.zip`
  - zip size: `10313814` bytes
- 배포본 브라우저 검증:
  - local preview URL: `http://127.0.0.1:8765/index.html`
  - server pid: `38568`
  - HTTP status: `200`
  - Playwright desktop check: title and H1 matched the finalized title; `figureCount: 7`, `imageCount: 7`, `brokenImages: []`
  - Playwright local href check: unique local hrefs `15`, failed links `0`
  - Playwright mobile check: viewport width `375`, horizontal overflow `false`, figures contained within page width
  - verification screenshots were captured through Playwright MCP for desktop and mobile viewport checks and were not added to `dist`
- Obsidian mirror sync:
  - mirror root: `C:\Users\angpa\Obsidian_Vault\AI_Tech_Review\2026-05-23_ai-scientist-execution-harness`
  - copied: final review markdown, final review HTML, research runlog, `dist.zip`, final review figures
  - copied top-level figure items: `7`

### AI Tech Review Letters 사이트 갱신

- 수정 범위:
  - `reports/2026-05-23_ai-scientist-execution-harness_final_review.md`
  - `scripts/publish_public_site.py`
  - `site/index.html`
  - `site/manifest.json`
  - `site/reviews/2026-05-23_ai-scientist-execution-harness/index.html`
- 원고 frontmatter:
  - `issue date: 2026-05-23` 추가로 상단 발행 라벨을 `AI Tech Review Letters: Week 21 (2026-05-23)`로 고정
  - `author: "김현중"`으로 변경해 `AI Governance 팀` 표기 제거
- 사이트 카드:
  - title: `AI 과학자, 시작의 끝에서: The End of the Beginning for AI Scientists`
  - subtitle: `에르되시 문제 #1196에서 연구 실행 하네스까지, 우리가 이미 기대기 시작한 AI 과학자를 어떻게 준비할 것인가`
  - updated: `2026-05-25`
  - tags: `AI for Science`, `AI Scientist`, `AI Co-Scientist`, `Research Harness`
- 투명성 고지:
  - 작성자 표기에서 `AI Governance 팀` 제거
  - 작성자 링크에 `GitHub` 추가: `https://github.com/Infant83`
  - 책임 문구를 `이 허브의 게시물은 AI 보조 생성 및 퇴고 과정을 거친 콘텐츠입니다.`로 축약
- 재생성 명령:
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - `python scripts\html_to_dist.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.html --dist .\2026-05-23_ai-scientist-execution-harness\dist --zip --zip-path .\2026-05-23_ai-scientist-execution-harness\dist.zip`
  - `python scripts\publish_public_site.py`
- 검증 결과:
  - `html_to_dist.py`: `[local-ref-check] ok`
  - `publish_public_site.py`: `[public-site-check] ok`, `reviews=4`
  - 문체/그림 audit: `finding_count: 0`, `figure_count: 7`, `figure_density: ok`
  - Playwright site home check: latest title/subtitle matched, `hasAiGovernanceTeam: false`, `hasOldResponsibility: false`, `hasNewNotice: true`
  - site preview URL: `http://127.0.0.1:8766/index.html`
  - site preview server pid: `36996`

### 최종 제목 단순화

- 최종 제목: `AI 과학자, 시작의 끝에서`
- 처리 내용:
  - 원고 frontmatter `title`과 본문 H1에서 영문 병기 제거
  - `The End of the Beginning for AI Scientists`는 alias와 참고자료 맥락에만 유지
  - `scripts/publish_public_site.py`의 AI Tech Review Letters 카드 제목도 동일하게 변경
- 재생성 명령:
  - `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - `python scripts\markdown_to_html.py --mode final-review .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.md`
  - `python scripts\html_to_dist.py .\2026-05-23_ai-scientist-execution-harness\reports\2026-05-23_ai-scientist-execution-harness_final_review.html --dist .\2026-05-23_ai-scientist-execution-harness\dist --zip --zip-path .\2026-05-23_ai-scientist-execution-harness\dist.zip`
  - `python scripts\publish_public_site.py`
- 검증 결과:
  - 문체/그림 audit: `finding_count: 0`, `figure_count: 7`, `figure_density: ok`
  - `html_to_dist.py`: `[local-ref-check] ok`
  - `publish_public_site.py`: `[public-site-check] ok`, `reviews=4`
  - `site/index.html`, `site/reviews/2026-05-23_ai-scientist-execution-harness/index.html`, `site/manifest.json`에서 제목 `AI 과학자, 시작의 끝에서` 확인

### 배포본 이메일 발송

- 발송 일시: 2026-05-25
- 수신자: `hyun-jung.kim@lgdisplay.com`
- 제목: `AI Tech Review Letters 배포본 - AI 과학자, 시작의 끝에서`
- 첨부: `2026-05-23_ai-scientist-execution-harness\dist.zip`
- Gmail message id: `19e5f07b84a538f5`
- Gmail thread id: `19e5f07b84a538f5`
- 결과: `SENT`
