# AI for Science 리뷰 전략 runlog

## 2026-05-23

### 메일 확인

- Gmail 검색어: `in:anywhere -in:spam -in:trash subject:"ai for sci"`
- 결과: 1건
- 메일 ID: `19e4eac64f467ae7`
- 메일 제목: `ai for sci`
- 메일 시각: 2026-05-22 16:52:49 KST
- 본문: Sergei Kalinin LinkedIn 공유 링크 1개
- 캡처 파일: `sources/2026-05-23_ai-for-science-review-strategy_email_capture.md`

### 웹 리서치

- 사용자 제공 Google/DeepMind/Google Research 링크 3개 확인
- Google Korea 2026-04-27 국가 AI 파트너십 발표 확인
- Google Korea 2026-05-19 Co-Scientist/Gemini for Science 발표 확인
- Nature 2026-05-19 AI Scientist 논문/뉴스/사설/비판 코멘트 클러스터 확인
- 한국 K-문샷 관련 정부/위원회/IRIS/정책 문서 검색 및 핵심 쟁점 정리

### 작성 파일

- `sources/2026-05-23_ai-for-science-review-strategy_email_capture.md`
- `notes/2026-05-23_ai-for-science-review-strategy_sources.md`
- `notes/2026-05-23_ai-for-science-review-strategy_deepresearch_prompt.md`
- `reports/2026-05-23_ai-for-science-review-strategy_overview.md`
- `reports/2026-05-23_ai-for-science-review-strategy_overview.html`
- `reports/2026-05-23_ai-for-science-review-strategy_review_plan_v2.md`
- `artifacts/figures/ai_scientist_validation_loop.svg`
- `artifacts/figures/ai_scientist_harness_example.svg`

### 렌더링 및 인덱스

- HTML 생성 명령: `python scripts\markdown_to_html.py --mode auto daily_research_review\2026-05-23_ai-for-science-review-strategy\reports\2026-05-23_ai-for-science-review-strategy_overview.md`
- HTML 생성 결과: 성공
- 문체 감사 명령: `python C:\Users\angpa\.codex\skills\ai-tech-review-editorial-harness\scripts\audit_review_text.py daily_research_review\2026-05-23_ai-for-science-review-strategy\reports\2026-05-23_ai-for-science-review-strategy_overview.md`
- 문체 감사 결과: finding_count 0. 단, 전략 문서 단계라 figure_density는 추후 final_review에서 보강 필요.
- README 갱신 명령: `python scripts\generate_readme.py`
- README 갱신 결과: `README.md`와 `daily_research_review/README.md`에 2026-05-23 AI for Science 리뷰 전략 항목 반영

### 방향 보강

- 사용자 후속 요청에 따라 리뷰 초점을 `AI 과학자가 어디까지 동료가 될 수 있는가`에서 `AI 과학자를 회사 문제 해결의 실행 파트너로 쓰는 법`으로 확장.
- Nature 논문 클러스터는 중심 근거로 유지하고, 정부 협력/K-문샷은 필요성과 방향성의 배경으로 배치.
- 실행 환경은 온프레미스 `Cline + Qwen/Ollama/LM Studio + MCP`와 서비스형 `Codex/Gemini CLI/Claude Code`로 나눠 정리.
- 회사형 검증 루프 그림 `artifacts/figures/ai_scientist_validation_loop.svg` 작성.
- 실제 하네스 실행 예시 그림 `artifacts/figures/ai_scientist_harness_example.svg` 작성.
- v2 HTML 생성 명령: `python scripts\markdown_to_html.py --mode auto daily_research_review\2026-05-23_ai-for-science-review-strategy\reports\2026-05-23_ai-for-science-review-strategy_review_plan_v2.md`
- v2 HTML 생성 결과: 성공
- v2 문체 감사 결과: finding_count 0. 단, 계획 문서 단계라 figure_density는 final_review에서 보강 필요.

### 도입부 보강

- 사용자 제안에 따라 수학 AI 뉴스와 Bixonimania 가짜 질병 사례를 도입부 전략에 반영.
- 추가 확인 출처:
  - `https://www.newsspace.kr/news/article.html?no=13494`
  - `https://www.quantamagazine.org/the-ai-revolution-in-math-has-arrived-20260413/`
  - `https://www.hani.co.kr/arti/science/science_general/1253718.html`
  - `https://www.nature.com/articles/d41586-026-01100-y`
- 뉴스스페이스 기사는 검증 완료 사실이 아니라 `AI 수학 연구 성과를 둘러싼 흥분과 검증 논쟁`의 장면으로만 쓰기로 함.
- Bixonimania 사례는 우려 섹션의 `가짜 지식의 인용망 확산` 항목으로 승격.
- 도입부 반영 후 v2 계획서 재렌더링 완료.
- 문체 재감사 결과: finding_count 0. Figure density는 계획 문서 단계라 final_review에서 보강 예정.

### 실행 시나리오 보강

- 사용자 요청에 따라 `첫 30일 실행안` 중심 구성을 제거.
- v2 계획서에 실제 사용 시나리오, 프롬프트 예시, 하네스 폴더 구조, MCP 설정 예시, `problem_card.yaml`, `hypothesis_candidates.json`, 결과 저장 구조를 추가.
- 기존 검증 루프 그림의 시간표식 문구를 제거하고 `ai_scientist_validation_loop.svg`로 이름을 정리.
- 신규 그림 `artifacts/figures/ai_scientist_harness_example.svg` 작성.
- v2 HTML 재렌더링 완료.
- v2 문체 재감사 결과: finding_count 0.
- `30일`, `2주`, `4주`, `8주` 표현이 v2 계획서, 심층 리서치 프롬프트, 소스 노트에 남아 있지 않음을 확인.
- `PoC` 표현도 v2 계획서, 심층 리서치 프롬프트, 소스 노트에서 제거. HTML에는 `ai_scientist_validation_loop.svg`, `ai_scientist_harness_example.svg` 두 그림 참조가 정상 반영됨.

### 본 리뷰 패키지 승격

- Root topic package 생성: `2026-05-23_ai-scientist-execution-harness/`
- 승격 목적: intake 전략을 실제 final review 작성 공간으로 전환
- 생성된 핵심 파일:
  - `sources/2026-05-23_ai-scientist-execution-harness_intake_bridge.md`
  - `notes/2026-05-23_ai-scientist-execution-harness_review_flow.md`
  - `reports/2026-05-23_ai-scientist-execution-harness_final_review.md`
  - `skywork_inputs/2026-05-23_ai-scientist-execution-harness_skywork_prompt_v1.md`

### 다음 작업 후보

1. 이 전략을 바탕으로 root topic package `2026-05-23_ai-for-science-national-collaboration/` 생성
2. `reports/*_memo.md`, `reports/*_deepresearch.md`, `reports/*_final_review.md` 작성
3. final review HTML, Skywork prompt packet, 슬라이드 생성
4. Obsidian mirror 및 OpenProject sync
