# Cline 온프레미스 Qwen Agentic Workflow 강연 Blueprint

작성일: 2026-04-29  
목표: 90분 기술 강의용 Skywork deck 설계  
권장 슬라이드 수: 31 main slides + 4 appendix slides = 총 35장

## Summary

- Cline은 VS Code 안에서 개인 업무 절차를 실행 가능한 agentic workflow로 묶는 harness로 설명한다.
- 강연의 중심은 모델 성능 비교가 아니라 `rules + skills + workflows + working notes + human review`의 운영 구조다.
- On-premise LLM은 민감 정보 보호에 유리한 선택지일 수 있으나, governance와 tool boundary가 함께 설계되어야 한다.
- Introduction은 대통령-하사비스 대화의 `specific enough` 문제 제기에서 시작해 Claude Code 98.4% infrastructure 분석과 Erdős #1196 AI-assisted discovery 사례로 연결한다.
- 시각 스타일은 기술 세미나용 corporate deck에 친근한 spot illustration과 workflow diagram을 섞는다.

## Section Plan

| Section | 시간 | 슬라이드 | 역할 |
|---|---:|---:|---|
| 1. Opening & Motivation | 10분 | 1-4 | 왜 지금 Agentic Workflow인가 |
| 2. System Overview | 15분 | 5-10 | VS Code, Cline, On-premise LLM 구조 |
| 3. From Prompting to Workflow Engineering | 15분 | 11-15 | prompt에서 workflow 설계로 이동 |
| 4. Global and Local Markdown Rules | 20분 | 16-22 | Rules, Skills, Workflows, AGENTS.md 의미 |
| 5. Demonstration Scenarios | 20분 | 23-26 | Email, daily report, Git/DevOps 데모 |
| 6. Interactive Feedback Loop | 10분 | 27-29 | output이 다음 input이 되는 구조 |
| 7. Governance and Boundaries | 5분 | 30 | 보안, 권한, 책임 경계 |
| 8. Conclusion & Q&A | 5분 | 31 | 요약 및 Q&A |
| Appendix | 필요 시 | 32-35 | 예시 rule, workflow, template |

## Slide-by-slide Blueprint

### 1. Title - 개인화 Agentic Workflow 강연

Bullets:

- VS Code + Cline + On-premise LLM
- Markdown Rules와 Skillset으로 구성하는 업무 자동화
- daily office workflow를 agentic loop로 바꾸는 방법

Speaker note:

- 오늘 강연은 Cline 사용법 소개가 아니다. 개인의 반복 업무를 Cline이 참조하고 실행할 수 있는 구조로 만드는 방법을 다룬다.
- 업무를 AI에게 넘기는 것이 아니라, AI와 사람이 같이 운영할 수 있는 절차로 재구성하는 관점이다.

Visual:

- Asset 1 `Agentic Workflow Desk`를 title 보조 이미지로 사용.

### 2. 오늘의 결론을 먼저 말하면

Bullets:

- AI는 이미 충분히 강력하다.
- 문제는 instruction과 control이 `specific enough`한가다.
- 좋은 prompt보다 오래 남는 것은 좋은 workflow다.
- 자동화보다 중요한 것은 검토 가능한 자동화다.

Speaker note:

- 대통령과 Google DeepMind CEO Demis Hassabis의 짧은 대화를 opening hook으로 사용한다. AlphaGo와 Gemini의 높은 성능을 인정하면서도, Gemini가 때때로 지시하지 않은 일을 하는 문제를 묻는 장면이다.
- 자동 자막이 완벽하지 않으므로 장문 인용으로 처리하지 않는다. 이 장면에서 가져올 질문은 단순하다. AI가 강력할수록 instruction, control, audit이 얼마나 구체적이어야 하는가.
- 오늘의 중심 문장은 "AI가 참조할 수 있는 업무 운영체계를 만든다"이다. Cline의 rules, skills, workflows, `AGENTS.md`는 그 운영체계의 구체적인 파일 표면이다.

Visual:

- 대통령-과학자 대화를 직접 재현하지 말고, `question bubble -> control surface -> workflow harness`로 이어지는 친근한 editorial illustration.

### 3. Specific enough란 얼마나 구체적인가

Bullets:

- Claude Code 분석: `1.6% AI / 98.4% infrastructure`
- permission, context, compaction, tools, recovery가 agent를 움직임
- core loop는 단순하지만 주변 harness가 복잡함
- Cline에서도 rules와 workflow가 부가 기능이 아니라 운영층

Speaker note:

- `specific enough`를 감으로 말하면 추상적이다. 최근 Claude Code source-level 분석은 이 질문에 꽤 강한 힌트를 준다.
- 연구진은 Claude Code의 공개 TypeScript source code를 분석했고, GitHub README는 98.4%가 deterministic infrastructure, 1.6%가 AI decision logic이라는 framing을 제시한다. 이 수치를 모든 agent에 일반화하면 안 되지만, agent 제품의 실체가 model call 주변의 permission, context, tool routing, recovery logic에 있다는 점은 강한 시사점이다.
- Cline 강연에서도 같은 구조를 개인 업무 규모로 낮춰 설명한다. Global Rules, Local Rules, Skillset, Workflow, `AGENTS.md`, working notes가 바로 작은 규모의 harness다.

Visual:

- Iceberg 또는 layered stack: visible model response 1.6%, beneath surface harness 98.4%. 하단에 `Claude Code case, not universal law` 작은 annotation.

### 4. 가능성의 반대편: AI-assisted discovery

Bullets:

- Erdős #1196: AI-assisted mathematical discovery 사례
- prompt, model exploration, expert verification, formalization이 결합
- 강력한 AI일수록 provenance와 audit이 중요
- 오늘의 질문: 이 힘을 daily office workflow에 안전하게 연결하는 법

Speaker note:

- 인트로는 공포나 통제만으로 끝내면 안 된다. AI는 실제로 새로운 경로를 제안할 수 있다.
- Erdős Problem #1196 사례는 Liam Price, GPT-5.4 Pro, Terence Tao와 Jared Duker Lichtman의 논의, formalization/refinement가 결합된 사례로 설명한다. `AI가 혼자 난제를 풀었다`고 과장하지 않는다.
- 이 사례가 보여주는 것은 가능성이다. 동시에 그 가능성은 human review, proof audit, provenance가 붙을 때 신뢰 가능한 결과가 된다.
- 이제 이 질문을 연구소의 일상 업무로 가져온다. 이메일, 보고서, Git, Obsidian, OpenProject도 작지만 같은 구조를 가진다.

Visual:

- Math discovery path: problem -> AI exploration -> expert review -> formalization -> new method. 오른쪽 하단에 `power requires audit` annotation.

### 5. System Overview

Bullets:

- User -> VS Code -> Cline -> On-premise LLM
- Tools: files, terminal, Git, browser, MCP
- Notes: Markdown, Obsidian, project docs
- Review: 사람이 승인하고 수정하는 checkpoint

Speaker note:

- Cline은 VS Code 안에서 작업 공간과 연결된다. 모델은 reasoning을 담당하지만, 실제 업무성은 files, terminal, Git, notes 같은 주변 시스템과 연결될 때 생긴다.

Visual:

- 필수 아키텍처 다이어그램: User -> VS Code -> Cline -> On-premise LLM -> Tools / Files / Git / Notes.

### 6. Cline의 역할을 다시 정의하기

Bullets:

- coding assistant
- tool-using agent
- workflow assistant
- personal workflow harness

Speaker note:

- Cline은 코드를 작성하는 도구로 시작하지만, rule과 workflow를 구성하면 daily work assistant가 된다.
- 중요한 것은 Cline이 내 업무 스타일을 추측하게 두는 것이 아니라, 읽을 수 있는 지침으로 제공하는 것이다.

Visual:

- 같은 Cline이 네 역할로 확장되는 radial diagram.

### 7. Cline이 실제로 다루는 작업 표면

Bullets:

- file structure와 source code context
- terminal command 결과
- browser 및 web tool
- MCP 기반 custom tool
- diff 기반 file edit와 human review

Speaker note:

- 공식 repository 설명 기준 Cline은 파일, terminal, browser, MCP와 연결된다. 이것은 강력하지만 통제가 필요하다는 뜻이기도 하다.

Visual:

- Workspace map: files, terminal, browser, tools.

### 8. 왜 On-premise LLM인가

Bullets:

- 내부 자료와 연구 데이터 보호
- governance와 audit 요구
- 재현 가능한 운영 환경
- 외부 SaaS 의존도 조절
- 단, on-premise만으로 안전이 완성되지는 않음

Speaker note:

- 온프레미스 환경은 내부 데이터 처리 관점에서 유리한 선택지다. 그러나 모델이 내부에 있다고 해서 자동으로 안전한 workflow가 되는 것은 아니다.
- 어떤 파일을 읽을 수 있는지, 어떤 명령을 실행할 수 있는지, 무엇을 저장하는지까지 설계해야 한다.

Visual:

- Asset 3 `On-premise Governance Bridge`.

### 9. Qwen 계열 모델을 말할 때의 주의점

Bullets:

- 내부 모델명과 파라미터 수는 확인된 자료 기준으로만 표현
- Qwen3-Coder-Next 외부 자료는 agentic coding trend anchor로 사용
- local development와 coding agent 최적화 흐름은 발표 맥락과 연결 가능
- 내부 endpoint와 운영 정보는 placeholder 처리

Speaker note:

- Qwen 관련 설명은 정확성이 중요하다. 외부 자료에서 확인한 수치가 내부 모델을 의미하지 않는다.
- 내부 심층 리서치 원문이 확보되면 모델명을 확정하고, 지금 단계에서는 Qwen 계열 온프레미스 LLM이라고 표현한다.

Visual:

- `confirmed / caution / placeholder` 세 칸으로 나누는 fact status table.

### 10. Cloud LLM vs On-premise LLM Governance 비교

Bullets:

- 데이터 이동 경로
- 접근 제어와 audit
- 모델/인프라 운영 책임
- latency와 availability
- 비용과 확장성 trade-off

Speaker note:

- 어느 쪽이 절대적으로 좋다고 말하기보다, governance surface가 어디에 있는지 비교한다.
- 온프레미스는 데이터 통제에 강점이 있지만, 운영 책임이 내부로 들어온다.

Visual:

- 필수 governance comparison table.

### 11. Prompt Engineering에서 Workflow Engineering으로

Bullets:

- Prompt: 한 번의 요청을 잘 쓰는 기술
- Workflow: 반복 가능한 작업 절차를 설계하는 기술
- Harness: model, tools, rules, memory를 묶는 실행 구조
- 좋은 workflow는 다음 작업에 재사용됨

Speaker note:

- prompt만 잘 써서는 매번 새로 시작한다. workflow는 작업 절차 자체를 asset으로 만든다.
- 최근 agent trend도 이 방향으로 이동하고 있다. 모델 표면보다 harness interface가 중요해진다.

Visual:

- 필수 Prompting vs Workflow Engineering 비교표.

### 12. Human-readable + AI-readable Markdown

Bullets:

- 사람은 읽고 고칠 수 있어야 함
- Cline은 그대로 context로 읽을 수 있어야 함
- rule, workflow, note, template이 같은 문법을 공유
- Markdown은 업무 절차를 지식 자산으로 남김

Speaker note:

- Markdown은 단순 문서 형식이 아니다. 사람과 agent가 같이 읽는 업무 interface가 된다.
- 문서가 사람이 읽기 어려우면 유지되지 않고, agent가 읽기 어려우면 실행되지 않는다.

Visual:

- Asset 2 `Rules, Skillset, Workflow Hierarchy`.

### 13. Working Notes가 중요한 이유

Bullets:

- agent output을 작업 이력으로 남김
- 다음 보고서와 회의 준비의 source가 됨
- context switching 비용 감소
- 개인 업무 기억을 project memory로 전환

Speaker note:

- Cline이 잘 동작하려면 과거 작업 맥락이 필요하다. 그 맥락은 chat history에만 있으면 약하다.
- Markdown working note로 남겨야 다음 작업에서 다시 참조할 수 있다.

Visual:

- Notes -> Memory -> Next Task loop.

### 14. Agentic Workflow의 기본 구성요소

Bullets:

- Instruction: 무엇을 우선할 것인가
- Context: 어떤 자료를 볼 것인가
- Tool: 어떤 행동을 할 수 있는가
- Boundary: 어디서 멈출 것인가
- Memory: 무엇을 남길 것인가

Speaker note:

- 이 다섯 가지가 없으면 agent는 좋은 답변은 할 수 있어도 안정적인 업무 수행자는 되기 어렵다.

Visual:

- Five-part harness diagram.

### 15. Harness Engineering 트렌드

Bullets:

- model selection을 넘어 agent operating layer로 이동
- MCP, Skills, `AGENTS.md`, sandbox, tool permission
- 업무별 domain logic이 경쟁력이 됨
- 조직에서는 governance와 실행성을 동시에 봐야 함

Speaker note:

- 최근 흐름은 "더 똑똑한 모델"만의 문제가 아니다. agent가 어떤 환경에서 어떤 권한으로 움직이는지가 중요해진다.
- 개인 업무에서도 같은 원리가 적용된다.

Visual:

- Asset 7 `Harness Engineering Trend`.

### 16. Global Rules란 무엇인가

Bullets:

- 모든 project에 적용되는 개인 기본 원칙
- 말투, 보고 형식, 보안 기본선
- 승인 없이 하지 말아야 할 작업
- 반복 업무의 기본 처리 방식

Speaker note:

- Global Rules는 내 일하는 방식의 기본값이다. 예를 들어 "민감 정보는 generic placeholder로 바꿔라", "destructive command 전에는 반드시 확인하라" 같은 원칙이다.

Visual:

- Personal baseline layer diagram.

### 17. Local Rules란 무엇인가

Bullets:

- 특정 repository 또는 project에 붙는 규칙
- build/test/deploy 절차
- commit convention과 branch 전략
- 연구노트, 보고서, data path 규칙
- Global Rules와 충돌하면 local context를 우선

Speaker note:

- Local Rules는 project-specific context다. 같은 Git workflow라도 프로젝트마다 test command, report format, 금지 경로가 다르다.

Visual:

- 필수 Global vs Local hierarchy diagram.

### 18. `AGENTS.md`의 의미

Bullets:

- repository에 함께 남는 agent instruction surface
- cross-tool compatibility를 고려한 지침 파일
- 사람이 리뷰할 수 있는 업무 계약서
- project onboarding 문서로도 활용 가능

Speaker note:

- `AGENTS.md`는 agent에게만 주는 비밀 prompt가 아니다. 프로젝트에서 agent가 어떻게 행동해야 하는지를 사람이 함께 검토할 수 있는 문서다.

Visual:

- Repository root with AGENTS.md, .clinerules, workflows.

### 19. Skillset은 언제 필요한가

Bullets:

- 항상 로드하기에는 긴 전문 절차
- 특정 업무에서만 필요한 domain knowledge
- 분석, 문서화, 배포, 보안 검토 같은 역할별 절차
- 재사용 가능한 업무 능력 단위

Speaker note:

- Skillset은 모든 상황에 넣는 지침이 아니다. 필요할 때 로드되는 전문 절차다.
- 예를 들어 "OpenProject 업데이트", "Obsidian 회의록 정리", "Git release note 작성"은 skill로 분리하기 좋다.

Visual:

- Skill cards activated on demand.

### 20. Workflow는 언제 필요한가

Bullets:

- 반복되는 multi-step process
- 순서와 중단 조건이 중요한 업무
- tool call과 human checkpoint가 섞인 작업
- slash command로 호출 가능한 절차

Speaker note:

- workflow는 "매번 설명하기 싫은 절차"를 파일로 만든 것이다.
- daily report, release prep, issue sync, paper review intake 같은 업무가 여기에 맞다.

Visual:

- Workflow checklist with stop gates.

### 21. Rule, Skill, Workflow를 나누는 기준

Bullets:

- Rule: 항상 지켜야 하는 방식
- Skill: 필요할 때 꺼내 쓰는 전문성
- Workflow: 순서대로 실행할 절차
- Note: 결과와 맥락을 남기는 기록

Speaker note:

- 이 구분이 흐려지면 모든 지침이 한 파일에 쌓인다. 그러면 사람이 유지하기도 어렵고 agent도 필요한 맥락을 놓친다.

Visual:

- 2x2 decision table.

### 22. 예시: 내 업무용 Cline harness 구성

Bullets:

- Global Rules: 보안, 말투, 보고 기본값
- Local Rules: project별 build/test/report 규칙
- Workflows: daily checkup, daily report, Git update
- Skills: Obsidian, OpenProject, research memo
- Notes: 작업 결과와 다음 action 저장

Speaker note:

- 여기서부터는 개념이 아니라 운영 구조를 본다. Cline을 매번 설득하는 대신, Cline이 읽을 수 있는 업무 환경을 만든다.

Visual:

- Personal harness stack diagram.

### 23. Demo 1 - Email summarization / daily checkup

Bullets:

- 오늘 확인할 email과 일정 확인
- action item, deadline, reply-needed 분류
- 민감한 reply는 사람이 검토
- 결과를 daily note로 저장

Speaker note:

- 이메일 요약은 단순 요약으로 끝나면 가치가 작다. action item과 다음 작업으로 연결되어야 한다.
- Cline이 할 일은 요약 초안과 분류이고, 사람이 할 일은 외부 발송과 민감 판단이다.

Visual:

- Email -> Summary -> Daily Note mini flow.

### 24. Demo 2 - Daily report preparation

Bullets:

- 오늘 한 일
- 진행 중인 일
- blocker
- tomorrow plan
- Obsidian 또는 Markdown report 저장

Speaker note:

- daily report는 하루가 끝날 때 새로 쓰는 문서가 아니라, 하루 동안 쌓인 working note를 재구성하는 결과물이어야 한다.

Visual:

- Daily Note -> Report template transformation.

### 25. Demo 3 - Git / DevOps workflow

Bullets:

- repository status 확인
- diff summary 생성
- commit message 초안 작성
- issue 또는 OpenProject update 연결
- push/merge는 human approval

Speaker note:

- Git workflow는 Cline이 강력하게 도와줄 수 있지만 위험도도 있다. 그래서 command boundary와 approval rule이 필요하다.

Visual:

- Git status -> diff -> commit message -> project update flow.

### 26. Daily office workflow loop

Bullets:

- Email -> Summary
- Summary -> Daily Note
- Daily Note -> Report
- Report -> Git/Project Update
- Update -> Next Task

Speaker note:

- 세 데모를 따로 보면 작은 자동화처럼 보인다. 묶어서 보면 업무 루프가 된다.
- 이 루프가 반복될수록 agent가 참조할 context가 늘어난다.

Visual:

- 필수 Daily office workflow loop diagram 또는 Asset 6.

### 27. Agent output은 끝이 아니라 input이다

Bullets:

- 요약은 다음 회의 준비의 source
- report는 project tracking의 source
- Git summary는 release note의 source
- working note는 다음 Cline task의 context

Speaker note:

- AI output을 복사해서 버리면 축적이 없다. Markdown으로 저장하고 다음 workflow가 읽게 해야 한다.

Visual:

- Output -> Note -> Memory -> Next action loop.

### 28. Human-in-the-loop feedback cycle

Bullets:

- Request
- Agent action
- Human review
- Refined instruction
- Saved workflow

Speaker note:

- 사람이 매번 agent를 통제한다는 뜻이 아니다. 사람이 경계를 정하고, 잘못된 결과를 rule이나 workflow 개선으로 되돌린다는 뜻이다.

Visual:

- 필수 Human-in-the-loop feedback cycle 또는 Asset 4.

### 29. 실패한 output을 어떻게 자산으로 바꾸는가

Bullets:

- 왜 실패했는지 기록
- rule로 바꿀지 workflow로 바꿀지 결정
- 예외와 중단 조건을 추가
- 다음 실행에서 재검증

Speaker note:

- 실패한 agent output은 낭비가 아니다. 반복되는 실패는 지침이 부족하다는 신호다.

Visual:

- Failure -> Diagnosis -> Rule update -> Re-run.

### 30. Governance, Boundaries, Risk Management

Bullets:

- On-premise LLM도 무제한 접근을 의미하지 않음
- 민감 파일과 개인정보는 접근 제외
- destructive command와 외부 전송은 승인 필요
- 사람은 최종 책임자

Speaker note:

- 내부 모델을 쓴다고 보안 문제가 사라지지 않는다. agent에게 어떤 권한을 줄지, 어디서 멈출지를 문서와 도구 수준에서 설계해야 한다.

Visual:

- Permission gate diagram.

### 31. Conclusion & Q&A

Bullets:

- Cline은 personal workflow harness로 확장 가능
- Markdown Rules와 Skillset은 사람과 AI가 공유하는 업무 운영체계
- 좋은 자동화는 검토 가능하고 반복 가능해야 함
- 질문: 내 업무에서 가장 먼저 workflow로 만들 수 있는 것은 무엇인가

Speaker note:

- 마지막으로 도구보다 구조를 강조한다. 오늘 이후 바로 할 수 있는 일은 거창한 agent를 만드는 것이 아니라, 내 업무의 첫 workflow와 첫 rule을 쓰는 것이다.

Visual:

- Asset 8 closing operating system metaphor.

## Appendix Slides

### 32. Appendix - Example Global Rule

Content:

- 보안 기본 원칙
- 대외 발송 금지
- 민감 정보 placeholder 처리
- destructive command approval

Visual:

- Markdown snippet style.

### 33. Appendix - Example Local Rule

Content:

- project 목적
- build/test command
- report format
- forbidden paths
- commit convention

Visual:

- Repository-specific rule file example.

### 34. Appendix - Example Daily Report Template

Content:

- Done
- In progress
- Blockers
- Tomorrow
- Links / Evidence

Visual:

- Obsidian note template.

### 35. Appendix - Example Git Workflow Instruction

Content:

- Check status
- Summarize diff
- Propose commit message
- Ask before commit
- Link issue or OpenProject item

Visual:

- Workflow Markdown file with approval gate.
