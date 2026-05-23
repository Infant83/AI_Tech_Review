# Skywork Source Pack

프로젝트명: Cline 온프레미스 Qwen Agentic Workflow 강연  
작성일: 2026-04-29  
언어: 한국어, 주요 기술 용어는 영어 병기  
목표 산출물: 90분 기술 강의용 PowerPoint deck, speaker notes 포함

## 1. 강연 목표

이 강연은 Cline을 단순한 AI coding assistant로 소개하지 않는다. 연구소 또는 기술 조직 구성원이 일상 업무를 `Agentic Workflow`로 재구성하고, VS Code 안에서 Cline을 개인 workflow harness로 운영하는 방법을 설명한다.

강연의 마지막 메시지는 다음 문장으로 수렴해야 한다.

> AI를 잘 쓰는 것보다 중요한 것은, AI가 참조할 수 있는 나의 업무 맥락과 절차를 구조화하는 것이다.

## 2. 발표 대상

- 연구소 또는 기술 조직 구성원
- LLM, VS Code, Git, DevOps, MLOps에 어느 정도 익숙한 청중
- Cline, Markdown Rules, Skills, Workflow, `AGENTS.md` 기반 agent harness에는 익숙하지 않은 청중
- 내부 업무 자동화, 연구 노트, 보고서 작성, project tracking, Git workflow 개선에 관심 있는 사용자

## 3. 반드시 지킬 용어

- `Cline`: VS Code 확장 기반 agent coding extension. 발표에서는 personal workflow harness로 확장해서 설명한다.
- `VS Code`: 잘못 전사된 표현은 모두 VS Code로 정정한다.
- `On-premise LLM`: 내부 연구소 환경 또는 조직 내부에서 운영되는 LLM. 구체 endpoint는 쓰지 않는다.
- `Qwen 계열 모델`: 내부 심층 리서치에서 확인된 정확한 모델명만 단정한다.
- `Markdown Rules`, `Global Rules`, `Local Rules`, `Skillset`, `Workflow`, `Human-in-the-loop`, `Tool Calling`, `Governance`, `DevOps`, `Git Workflow`, `Obsidian`, `OpenProject`는 영어 병기를 유지한다.

금지:

- `Cline`을 다른 표현으로 바꾸지 않는다.
- 내부 URL, credential, token, endpoint, 개인 정보, 미공개 코드 경로를 포함하지 않는다.
- 확인되지 않은 Qwen 모델명, 파라미터 수, benchmark 수치를 단정하지 않는다.

## 4. 확인된 외부 근거 anchor

### 4.0 Opening hook: `specific enough`하지 않은 AI 활용의 문제

출처:

- YouTube Shorts: https://youtube.com/shorts/69HKqLFis0Y
- Archived metadata: `sources/youtube_69HKqLFis0Y.metadata.json`
- Archived auto-caption: `sources/youtube_69HKqLFis0Y.ko-orig.vtt`

확인된 내용:

- 2026-04-27 업로드된 47초 Shorts.
- 제목은 AlphaGo와 Gemini를 언급하며 Google DeepMind CEO Demis Hassabis를 맞이하는 장면으로 설명한다.
- 자동 자막에는 대통령이 AlphaGo로 인한 한국 사회의 충격과 Gemini 사용 경험을 언급한 뒤, Gemini가 때때로 지시하지 않은 일을 하는 문제를 질문하는 흐름이 나온다.
- Hassabis의 답변은 foundation model이 instruction이 specific하지 않을 때 다른 일을 할 수 있다는 취지로 이어진다.

슬라이드 처리:

- 이 영상은 opening anecdote로만 사용한다.
- 자동 자막이 불완전하므로 장문 직접 인용은 피한다.
- 핵심 질문은 다음처럼 정리한다.

> AI가 유용하다는 것은 이미 안다. 문제는 instruction, control, audit이 specific enough하지 않을 때 무엇이 벌어지는가다.

이 질문에서 오늘 강연의 주제로 연결한다.

- `specific enough`한 지시는 단순히 prompt를 길게 쓰는 것이 아니다.
- 어떤 파일을 읽을 수 있는지, 어떤 tool을 쓸 수 있는지, 어디서 멈춰야 하는지, 무엇을 기록해야 하는지까지 정하는 것이다.
- 이 구조가 개인 업무에서는 Cline의 Markdown Rules, Global Rules, Local Rules, Skillset, Workflow, `AGENTS.md`, working notes로 구현된다.

### 4.1 Cline customization layer

출처: https://docs.cline.bot/customization/overview

Cline 공식 문서는 customization layer를 다음처럼 구분한다.

| Layer | 역할 | 활성 방식 | 강연에서의 해석 |
|---|---|---|---|
| Rules | Cline 행동을 정의 | 항상 또는 조건부 | coding style, 보안 원칙, 보고서 형식, project constraint |
| Skills | 전문 지식 로드 | 요청이 맞을 때 | 특정 업무나 도메인에 필요한 procedure pack |
| Workflows | 단계형 자동화 | `/workflow.md` 호출 | daily report, release, email checkup, Git workflow |
| Hooks | 특정 순간의 custom logic | 이벤트 기반 | 검증, 차단, 알림, 정책 enforcement |
| `.clineignore` | 접근 제외 | 항상 | 큰 파일, 민감 파일, build artifact 제외 |

공식 문서의 중요한 해석:

- Customization은 Cline을 일반 assistant에서 codebase, team convention, workflow에 맞는 assistant로 바꾼다.
- Project-specific customization은 version control과 review가 가능하므로 팀 운영에 적합하다.
- Global customization은 개인 선호와 반복 업무에 적합하다.
- Customization file은 Cline이 command 실행과 file edit에 영향을 주므로 코드와 같은 수준으로 검토해야 한다.

### 4.2 Cline Workflows

출처: https://docs.cline.bot/customization/workflows

- Workflow는 Markdown 파일이다.
- 파일명은 slash command로 호출된다.
- Workspace workflow는 `.clinerules/workflows/`에 둔다.
- Workflow는 natural language instruction, specific tool call, CLI command, MCP tool call을 조합할 수 있다.
- 복잡한 업무는 여러 workflow로 나누고 version control한다.

강연 적용:

- `daily-checkup.md`: 이메일, 일정, blocker를 요약한다.
- `daily-report.md`: 오늘 한 일, 진행 중인 일, blocker, 내일 계획을 정리한다.
- `git-update.md`: repository status, diff summary, commit message, issue update를 연결한다.
- `openproject-sync.md`: 작업 결과를 project tracking system에 남긴다.

### 4.3 Cline Rules and AGENTS.md

출처: https://www.mintlify.com/cline/cline/customization/cline-rules

- Cline은 `.clinerules/`, `.cursorrules`, `.windsurfrules`, `AGENTS.md`를 rule source로 인식한다.
- Workspace rules는 project root의 `.clinerules/` 아래에 둔다.
- Global rules는 OS별 Cline Rules 디렉터리에 둔다.
- Rule은 scannable하고 specific해야 한다.
- Header, bullet, example, 이유 설명이 Cline의 해석을 돕는다.
- Conditional rules는 path 조건으로 특정 파일군에만 활성화할 수 있다.

강연 적용:

- Global Rules: 말투, 보안 기본 원칙, 공통 보고 스타일, 승인 없이 하지 말아야 할 행동.
- Local Rules: repository별 build/test 절차, commit convention, 연구노트 템플릿, project-specific 금지사항.
- `AGENTS.md`: Cline뿐 아니라 다른 agent tool도 읽을 수 있는 cross-tool instruction surface로 설명한다.

### 4.4 Cline tool-using agent 기능

출처: https://github.com/cline/cline

- Cline은 VS Code 안에서 file structure와 source code context를 읽고 작업한다.
- terminal command를 실행하고 결과를 확인할 수 있다.
- file edit를 diff 형태로 제시하고 사용자가 검토할 수 있다.
- browser, MCP 기반 custom tool 확장을 활용할 수 있다.

강연 적용:

- Cline은 chat output을 생성하는 도구가 아니라, workspace 내부 자료와 command 결과를 읽고 다음 행동으로 이어가는 agent interface다.
- 하지만 command 실행과 file edit가 가능하므로 permission, review, rule boundary가 필요하다.

### 4.5 Harness engineering trend

출처: https://openai.com/index/the-next-evolution-of-the-agents-sdk/

- OpenAI는 2026-04-15 Agents SDK 관련 글에서 agent loop를 위한 harness, controlled workspace, explicit instructions, tools, memory, sandbox, MCP, skills, `AGENTS.md`, shell, apply patch 등을 agent system primitive로 설명한다.

강연 적용:

- 최근 트렌드는 더 큰 모델을 고르는 문제에서 끝나지 않는다.
- agent가 어떤 파일을 읽고, 어떤 tool을 쓰고, 어떤 rule을 따르고, 어떤 memory를 남기는지를 설계하는 `harness engineering`이 중요해지고 있다.
- Governance는 법무/보안 부서의 문서가 아니라 agent가 실제로 실행할 수 있는 boundary로 내려와야 한다.

### 4.5A Claude Code reverse-engineering / harness-dominant architecture

출처:

- https://arxiv.org/abs/2604.14228
- https://github.com/VILA-Lab/Dive-into-Claude-Code
- https://www.linkedin.com/posts/eric-vyacheslav-156273169_researchers-reverse-engineered-claude-code-share-7452612489550258176-53w1

확인된 내용:

- arXiv paper `Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems`는 2026-04-14 제출된 tech report다.
- 논문은 Claude Code의 공개 TypeScript source code를 분석해 agent architecture를 설명한다.
- abstract 기준 Claude Code의 core는 model을 호출하고, tool을 실행하고, 반복하는 simple while-loop다.
- loop 주변에는 permission system, seven modes, ML-based classifier, five-layer context compaction, four extensibility mechanisms, subagent delegation, append-oriented session storage가 있다.
- GitHub README는 이 분석을 `98.4% infrastructure, 1.6% AI`로 요약한다.
- LinkedIn 글은 같은 framing을 대중적으로 확산시킨 signal로 사용하되, 수치 근거는 arXiv/GitHub에 둔다.

강연 적용:

- `specific enough`는 감으로 정하는 수준이 아니다.
- production-grade agent는 prompt가 아니라 permission, context, tool routing, recovery, memory, audit이 함께 구성된 harness다.
- 이 사례는 Cline 강연에서 `rules / skills / workflows / AGENTS.md`가 부가 장식이 아니라 agent 성능과 안전성의 핵심 운영층임을 설명하는 bridge가 된다.

주의:

- `98.4%`는 Claude Code codebase 분석 수치다.
- 모든 agent system, Cline, 또는 내부 Cline workflow에 그대로 적용하면 안 된다.
- 소셜에서는 `leaked`라고 표현되지만, 슬라이드에는 `공개 TypeScript source code 분석 기반 연구`라고 쓴다.

### 4.5B AI-assisted mathematics: 가능성의 반대편

출처:

- https://www.erdosproblems.com/forum/thread/1196
- https://www.scientificamerican.com/article/amateur-armed-with-chatgpt-vibe-maths-a-60-year-old-problem/
- https://futuregennews.com/gpt-5-4-pro-credited-with-solving-erdos-primitive-sets-problem-after-prompt-by-liam-price

확인된 내용:

- Erdős Problem #1196 discussion thread에는 Liam Price에 대한 additional thanks와 GPT-5.4 Pro chat link 언급이 있다.
- Terence Tao, Jared Duker Lichtman 등 수학자들의 논의가 thread에 남아 있다.
- Scientific American은 Liam Price가 ChatGPT Pro를 이용해 primitive sets 관련 60년 된 Erdős problem 해결에 기여한 사례를 보도했다.
- 같은 보도에서 Terence Tao는 이 사례가 단순한 literature search 사례와 다르며, 사람들이 처음에 잘못된 방향으로 들어간 `mental block`과 관련될 수 있다고 설명한다.
- FutureGenNews는 public primary materials가 attribution과 formalization 상태를 뒷받침하지만, viral framing 전체를 독립적으로 입증하지는 못한다고 주의한다.

강연 적용:

- 이 사례는 agentic AI의 가능성을 보여주는 opening counterweight다.
- 단, `AI가 혼자서 완전히 해결했다`가 아니라 `human prompt, AI exploration, expert verification, formalization/refinement가 결합된 AI-assisted discovery`로 설명한다.
- 메시지:
  - 충분히 잘 구조화된 interaction은 미지의 영역을 탐색하게 해준다.
  - 그래서 더더욱 control, audit, provenance, human review가 필요하다.

### 4.6 Qwen and on-premise coding agent model

출처:

- https://www.alibabacloud.com/blog/602864
- https://arxiv.org/abs/2603.00729

확인된 claim:

- Qwen3-Coder-Next는 coding agents와 local development에 맞춘 open-weight model로 소개된다.
- 기술 보고서 기준 Qwen3-Coder-Next는 80B total parameter, 3B active parameter 모델이다.
- executable environments, agentic training, tool usage, failure recovery가 강조된다.

주의:

- 이 수치는 Qwen3-Coder-Next에 대한 것이다.
- 내부 발표의 `Qwen-3.5` 또는 내부 모델명, 파라미터 수는 심층 리서치 원문과 내부 운영 자료에서 확인된 경우에만 사용한다.
- 확인 전에는 `Qwen 계열 온프레미스 LLM`이라고 표현한다.

## 5. 심층 리서치 원문 삽입 영역

아래 영역에 ChatGPT 링크에서 확보한 심층 리서치 결과를 붙여넣어 최종 Skywork 실행 전에 보강한다.

```md
<<심층 리서치 결과 원문을 여기에 삽입>>
```

## 6. 강연 내러티브

1. 사람은 매일 같은 종류의 업무를 반복하지만, 그 업무의 맥락은 계속 바뀐다.
2. 대통령-하사비스 대화는 `AI가 강력해질수록 instruction과 audit이 구체적이어야 한다`는 질문을 던진다.
3. Claude Code 분석은 agent의 차별점이 model call 자체보다 surrounding harness에 있음을 보여준다.
4. Erdős #1196 사례는 잘 쓰인 AI가 연구 수준 문제에서도 새로운 경로를 제안할 수 있음을 보여준다.
5. 따라서 문제는 `AI를 쓸 것인가`가 아니라 `얼마나 specific enough한 harness로 쓸 것인가`다.
6. Agentic Workflow는 작업 절차, tool, rule, memory, human review를 하나의 반복 가능한 운영 구조로 만든다.
7. Cline은 VS Code 안에서 이 구조를 개인 업무에 적용할 수 있는 실용적인 harness가 될 수 있다.
8. On-premise LLM은 내부 자료를 다룰 때 중요한 선택지지만, 그것만으로 governance가 완성되지는 않는다.
9. Global Rules, Local Rules, Skillset, Workflow, `AGENTS.md`를 설계해야 agent가 일관되게 행동한다.
10. Agent output은 결과물로 끝나지 않고 다음 작업의 input, working note, project memory가 된다.

## 7. 필수 데모 시나리오

### Demo 1. Email summarization / daily checkup

- 아침에 확인할 이메일을 요약한다.
- action item, deadline, reply-needed item으로 분류한다.
- 결과를 daily note로 전환한다.
- 사람이 민감한 답장, 대외 발송, 일정 확정을 검토한다.

### Demo 2. Daily report preparation

- 오늘 한 일, 진행 중인 일, blocking issue, tomorrow plan을 정리한다.
- Obsidian memo 또는 Markdown report로 저장한다.
- Cline이 이전 working notes를 참조해 초안을 만들고, 사람이 표현과 민감 정보를 정리한다.

### Demo 3. Git / DevOps workflow

- repository status를 확인한다.
- 변경 사항을 요약한다.
- commit message를 작성한다.
- branch, merge request, issue tracking, OpenProject 업데이트와 연결한다.
- 승인 없는 push, merge, destructive command는 금지 boundary로 둔다.

## 8. 시각 스타일 요구

- 전문적이되 딱딱하지 않게.
- 기술 세미나용 corporate template과 hand-crafted workflow notebook 느낌을 결합한다.
- 친근한 spot illustration을 중간중간 사용하되, 각 슬라이드를 그림으로 채우지 않는다.
- 반복 모티프:
  - VS Code workspace
  - Cline as workflow harness
  - Markdown pages and rules
  - On-premise LLM server
  - human review checkpoint
  - notes to memory to next task loop
- 피할 것:
  - 과한 SF 로봇 이미지
  - 마케팅용 추상 gradient
  - 의미 없는 장식 아이콘
  - 회사 내부 시스템처럼 보이는 구체 UI mock
  - 이미지 안에 깨지는 텍스트
