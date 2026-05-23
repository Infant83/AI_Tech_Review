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
