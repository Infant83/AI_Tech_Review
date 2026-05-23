# Skywork Prompt v2 Compact

업로드된 `LGD_Template.pptx`, source pack, visual asset prompts, blueprint를 기반으로 한국어 PowerPoint deck을 생성하라.

## Deck

- 제목: `From Prompt to Workflow: VS Code + Cline + On-premise LLM을 활용한 일상 업무 자동화`
- 강연 주제: `VS Code 확장 Cline을 활용한 개인화 Agentic Workflow 구축과 일상 업무 자동화`
- 발표 시간: 90분
- 권장 분량: 31 main slides + 4 appendix slides, 총 35장 이내
- 템플릿: 업로드된 `LGD_Template.pptx`
- 톤: 기술 세미나, 내부 교육, 실무 방법론 중심. 제품 홍보처럼 쓰지 말 것.

## Core Message

이 강연의 결론은 다음 문장으로 수렴해야 한다.

> AI를 잘 쓰는 것보다 중요한 것은, AI가 참조할 수 있는 나의 업무 맥락과 절차를 잘 구조화하는 것이다.

Cline은 단순 coding assistant가 아니라 VS Code 안에서 개인의 `rules + skills + workflows + working notes + human review`를 실행 가능한 agentic workflow harness로 묶는 도구로 설명한다.

## Opening Hook

인트로는 다음 흐름으로 강하게 시작한다.

1. 대통령과 Google DeepMind CEO Demis Hassabis의 YouTube Shorts 대화를 opening hook으로 사용한다.
2. AlphaGo와 Gemini의 성능은 이미 인상적이다. 하지만 Gemini 같은 foundation model이 때때로 지시하지 않은 일을 할 수 있다는 질문에서 출발한다.
3. 자동 자막 기반이므로 직접 인용은 피하고, `instruction과 audit이 specific enough하지 않을 때 agent는 어디로 drift하는가?`라는 질문으로 재구성한다.
4. Claude Code 분석의 `98.4% infrastructure, 1.6% AI` framing을 harness engineering의 필요성으로 연결한다. 단, 이 수치는 Claude Code case study로만 표시하고 universal law처럼 쓰지 말라.
5. Erdős #1196 AI-assisted discovery 사례를 가능성의 반대편으로 제시한다. 단, `AI가 혼자 난제를 풀었다`가 아니라 `human prompt + model exploration + expert verification + formalization/refinement`가 결합된 사례로 설명한다.
6. 결론: 강력한 AI일수록 control, audit, provenance, human review가 필요하다.

## Must Cover

- Agentic Workflow의 의미
- Chat 사용과 Agentic Workflow의 차이
- VS Code 중심 작업 환경
- Cline의 역할: coding agent, tool-using agent, workflow assistant, personal workflow harness
- On-premise LLM을 쓰는 이유: governance, security, privacy, reproducibility
- Cloud LLM vs On-premise LLM 비교
- Prompt Engineering에서 Workflow Engineering으로 이동
- Markdown Rules의 의미
- Global Rules와 Local Rules의 계층 구조
- `AGENTS.md`의 의미: agent instruction surface, human-readable contract
- Skillset: 필요할 때 로드되는 전문 절차
- Workflow: 순서와 중단 조건이 있는 반복 업무
- Working notes: output을 다음 task의 input으로 만드는 memory layer
- Demo 1: Email summarization / daily checkup
- Demo 2: Daily report preparation
- Demo 3: Git / DevOps / OpenProject / Obsidian workflow
- Human-in-the-loop feedback cycle
- Governance, boundaries, risk management
- 결론과 Q&A

## Required Visuals

다음 도식을 반드시 포함한다.

1. User -> VS Code -> Cline -> On-premise LLM -> Tools / Files / Git / Notes
2. Global Rules / Local Rules / `AGENTS.md` / Skills / Workflows 계층 구조
3. Human-readable + AI-readable Markdown workflow 문서 개념도
4. Daily office workflow loop: Email -> Summary -> Daily Note -> Report -> Git/Project Update -> Next Task
5. Human-in-the-loop feedback cycle: Request -> Agent action -> Human review -> Refined instruction -> Saved workflow
6. Cloud LLM vs On-premise LLM governance 비교표
7. Prompting vs Workflow Engineering 비교표
8. Claude Code harness iceberg: visible model call vs large surrounding infrastructure
9. AI-assisted discovery path: problem -> AI exploration -> expert review -> formalization -> reusable method

## Visual Style

- LGD template rhythm을 유지한다.
- 정보 밀도는 high로 유지한다.
- 딱딱한 표만 반복하지 말고, 친근한 spot illustration과 diagram을 섞는다.
- visual asset prompts 파일의 스타일을 반영한다.
- 이미지가 slide 본문을 대체하지 않게 한다.
- 이미지 안에 readable text를 넣지 않는다.
- real-person likeness, 정치 이미지, 국기, 회사 내부 UI, credential, internal endpoint를 넣지 않는다.
- small dark-green inline annotation은 용어 설명과 caveat에만 사용한다.
- source/reference는 작고 dark-gray로 표시한다.

## Source and Fact Policy

- 업로드된 source pack과 blueprint를 최우선으로 사용한다.
- Cline, Claude Code, Qwen, Erdős 사례는 source pack의 claim status를 따른다.
- Qwen 모델명, parameter count, context length는 source pack에서 확인된 경우에만 단정한다.
- 내부 LLM endpoint, credential, 내부 URL, 개인 정보는 절대 넣지 않는다.
- 불확실한 내용은 `확인된 범위에서는`, `내부 자료 확인 필요`, `사례 기반 시사점`처럼 낮춰 표현한다.

## Slide Requirements

각 slide는 다음을 포함한다.

- slide title
- bullet 3-5개
- 충분한 speaker notes
- diagram/table/visual suggestion 또는 실제 visual

Speaker notes는 발표자가 실제로 읽거나 참고할 수 있을 정도로 자세하게 작성한다. Slide 본문은 과도하게 길게 쓰지 않는다.

## Appendix

마지막에 appendix 4장을 포함한다.

- 예시 Markdown Global Rule
- 예시 project-specific Local Rule
- 예시 Daily Report Template
- 예시 Git Workflow Instruction

이 기준으로 전체 deck을 생성하라.

