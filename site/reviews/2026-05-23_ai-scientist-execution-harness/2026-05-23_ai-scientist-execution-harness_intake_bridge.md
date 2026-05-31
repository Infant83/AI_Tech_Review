# AI 과학자 실행 하네스 리뷰: intake 연결 노트

## 패키지 목적

이 폴더는 `daily_research_review/2026-05-23_ai-for-science-review-strategy/`에서 발굴한 AI for Science 리뷰 방향을 본 리뷰 작성 공간으로 승격한 것입니다.

최종 리뷰는 `AI 과학자가 어디까지 동료가 될 수 있을까`라는 질문에서 출발하되, 결론은 회사의 실제 문제를 AI 과학자형 실행 하네스로 옮기는 방법에 둡니다. 독자가 얻어가야 할 것은 막연한 동향 요약이 아니라, 지금 쓸 수 있는 Cline, Qwen, Codex, Gemini CLI, Claude Code 등을 어떤 문제와 어떤 검증 구조에 붙일 수 있는지에 대한 실무 감각입니다.

## 원 intake 패키지

- Daily review package: `daily_research_review/2026-05-23_ai-for-science-review-strategy/`
- 전략 보고서: `daily_research_review/2026-05-23_ai-for-science-review-strategy/reports/2026-05-23_ai-for-science-review-strategy_review_plan_v2.md`
- 전략 HTML: `daily_research_review/2026-05-23_ai-for-science-review-strategy/reports/2026-05-23_ai-for-science-review-strategy_review_plan_v2.html`
- 심층 리서치 프롬프트: `daily_research_review/2026-05-23_ai-for-science-review-strategy/notes/2026-05-23_ai-for-science-review-strategy_deepresearch_prompt.md`
- 메일 캡처: `daily_research_review/2026-05-23_ai-for-science-review-strategy/sources/2026-05-23_ai-for-science-review-strategy_email_capture.md`

## 중심 출처

### 도입부 장면

- Quanta Magazine, `The AI Revolution in Math Has Arrived`, 2026-04-13  
  <https://www.quantamagazine.org/the-ai-revolution-in-math-has-arrived-20260413/>
- 뉴스스페이스, `[빅테크칼럼] AI, 인간 수학자의 '성역' 넘봤나... GPT-5.4의 '에르되시 난제' 해결 주장의 실체`, 2026-04-16  
  <https://www.newsspace.kr/news/article.html?no=13494>
- Nature News Feature, `Scientists invented a fake disease. AI told people it was real`, 2026-04-07  
  <https://www.nature.com/articles/d41586-026-01100-y>
- 한겨레, `가짜 질병 던졌더니 덥석 문 AI, 퍼나르고 학술지 인용까지`, 2026-04-11  
  <https://www.hani.co.kr/arti/science/science_general/1253718.html>

### Nature AI Scientist 클러스터

- Nature, `Accelerating scientific discovery with Co-Scientist`, 2026-05-19  
  <https://www.nature.com/articles/s41586-026-10644-y>
- Nature, `A multi-agent system for automating scientific discovery`, 2026-05-19  
  <https://www.nature.com/articles/s41586-026-10652-y>
- Nature, `An AI system to help scientists write expert-level empirical software`, 2026-05-19  
  <https://www.nature.com/articles/s41586-026-10658-6>
- Nature Editorial, `Why AI cannot do good science without humans`, 2026-05-19  
  <https://www.nature.com/articles/d41586-026-01551-3>
- Nature Comment, `The uncritical adoption of AI in science is alarming - we urgently need guard rails`, 2026-05-19  
  <https://www.nature.com/articles/d41586-026-01557-x>

### Google / 정부 / 실행 도구

- Google Korea, `구글 딥마인드와 과학기술정보통신부, 국가 AI 파트너십 발표`, 2026-04-27  
  <https://blog.google/intl/ko-kr/company-news/inside-google/announcing-our-partnership-with-the-republic-of-korea/>
- Google DeepMind, `AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms`, 2025-05-14  
  <https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/>
- Google Research, `Accelerating scientific breakthroughs with an AI co-scientist`, 2025-02-19  
  <https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/>
- Cline local models: <https://docs.cline.bot/running-models-locally/overview>
- Cline MCP: <https://docs.cline.bot/mcp/configuring-mcp-servers>
- Qwen3-Coder / Qwen Code: <https://qwenlm.github.io/blog/qwen3-coder/>
- OpenAI Codex: <https://openai.com/codex/>
- Codex agent loop: <https://openai.com/index/unrolling-the-codex-agent-loop/>
- Gemini CLI: <https://developers.google.com/gemini-code-assist/docs/gemini-cli>
- Gemini CLI headless mode: <https://google-gemini.github.io/gemini-cli/docs/cli/headless.html>
- Claude Code CLI reference: <https://code.claude.com/docs/en/cli-reference>

## 가져온 그림

- `artifacts/final_review/figures/ai_scientist_validation_loop.svg`
- `artifacts/final_review/figures/ai_scientist_harness_example.svg`

## 작성 시 유의점

- 뉴스스페이스의 GPT-5.4/에르되시 문제 보도는 검증 완료 사실이 아니라, AI 수학 연구 성과를 둘러싼 기대와 검증 논쟁을 여는 장면으로만 사용합니다.
- Bixonimania 사례는 우려 섹션의 핵심 사례로 둡니다.
- 시간표식 실행안은 쓰지 않습니다.
- 대신 실제 사용 가능한 하네스, 프롬프트, 파일시스템, 데이터 구조, 결과 저장 방식을 보여줍니다.
