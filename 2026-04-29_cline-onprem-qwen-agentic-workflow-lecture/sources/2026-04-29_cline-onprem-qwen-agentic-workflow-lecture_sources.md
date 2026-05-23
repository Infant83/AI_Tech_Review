# Cline 온프레미스 Qwen Agentic Workflow 강연 - Source Note

작성일: 2026-04-29  
패키지: `2026-04-29_cline-onprem-qwen-agentic-workflow-lecture`

## 1. 입력 자료 상태

### 사용자 제공 목표

- 강연 주제: `VS Code 확장 Cline을 활용한 개인화 Agentic Workflow 구축과 일상 업무 자동화`
- 발표 시간: 90분
- 대상: 연구소 또는 기술 조직 구성원
- 핵심 메시지:
  - AI에게 업무를 통째로 맡기는 것이 아니라, 사람이 검토하고 운영할 수 있는 workflow로 재구성한다.
  - Cline을 단순 coding assistant가 아니라 개인 업무용 agentic workflow harness로 설명한다.
  - Markdown Rules, Global Rules, Local Rules, Skillset, Workflow, `AGENTS.md`가 agent 행동을 조직화하는 핵심 인터페이스다.
  - On-premise LLM은 security, governance, privacy, reproducibility 관점에서 설명한다.

### ChatGPT 대화 링크

- URL: https://chatgpt.com/c/69efe75e-320c-83a9-857d-e6de36879f4a
- 현재 상태: 공개 웹 접근에서는 로그인 화면만 확인되어 대화 본문을 직접 열람하지 못함.
- 처리 원칙:
  - 해당 링크의 심층 리서치 내용을 읽었다고 가정하지 않는다.
  - 사용자가 붙여넣는 원문 또는 로그인된 브라우저에서 확보한 텍스트만 내부 심층 리서치 근거로 사용한다.
  - 지금 생성하는 Skywork 입력 패키지는 `심층 리서치 원문 삽입 영역`을 포함한다.

## 2. 용어 정정 규칙

- `Cline`:
  - VS Code에서 동작하는 agent coding extension.
  - 발표에서는 coding assistant보다 넓은 의미의 personal workflow harness로 설명한다.
- `VS Code`:
  - 잘못 전사된 편집기 명칭은 모두 `VS Code`로 정정한다.
- `Qwen`:
  - 내부 발표에서는 `Qwen 계열 온프레미스 LLM`이라고 표현한다.
  - `Qwen-3.5`, 파라미터 수, context length, benchmark 수치는 심층 리서치 원문 또는 공식 출처에서 확인된 경우에만 단정한다.
- 금지:
  - 민감한 endpoint, credential, 내부 URL, 개인 식별 정보, 미공개 코드 경로를 포함하지 않는다.
  - 모델 성능, 보안성, 내부 운영 현황을 근거 없이 단정하지 않는다.

## 3. 확인된 외부 근거

### Intro hook: 대통령-하사비스 YouTube Shorts

- YouTube Shorts  
  https://youtube.com/shorts/69HKqLFis0Y
  - yt-dlp metadata:
    - id: `69HKqLFis0Y`
    - title: `알파고로 시작해 제미나이 얘기로 구글 딥마인드 CEO를 맞이하는 잼통`
    - uploader: `명쾌한시선`
    - upload date: `2026-04-27`
    - duration: 47 seconds
    - description includes: Google DeepMind CEO Demis Hassabis, AlphaGo, Gemini, `#이재명대통령`
  - archived files:
    - `sources/youtube_69HKqLFis0Y.metadata.json`
    - `sources/youtube_69HKqLFis0Y.ko-orig.vtt`
  - caption-based interpretation:
    - 대통령이 AlphaGo로 인한 한국 사회의 충격과 Gemini 사용 경험을 언급한다.
    - Gemini가 때때로 지시하지 않은 일을 하는 문제를 질문한다.
    - Hassabis는 foundation model이 instructions가 specific하지 않을 때 다른 일을 할 수 있다는 취지로 답한다.
  - caution:
    - 자동 자막이며 일부 영어 문장이 끊겨 있다.
    - 슬라이드에서는 장문의 직접 인용 대신 `specific enough한 instruction과 control surface가 왜 필요한가`라는 opening question으로 사용한다.

### Cline 공식 문서

- Cline customization overview  
  https://docs.cline.bot/customization/overview
  - Rules, Skills, Workflows, Hooks, `.clineignore`가 서로 다른 목적과 활성 조건을 가진 customization layer로 설명됨.
  - Rules는 항상 또는 조건부로 적용되는 행동 지침, Skills는 요청에 따라 로드되는 전문 지식, Workflows는 `/workflow.md`로 호출되는 단계형 자동화로 정리할 수 있음.
  - Global과 project-specific 저장 위치가 나뉘며, 프로젝트 저장소에 둔 설정은 팀 공유와 리뷰가 가능함.
  - 보안 관점에서 customization file도 실행 환경에 영향을 주므로 코드와 같은 수준으로 검토해야 한다는 경고가 있음.

- Cline workflows 문서  
  https://docs.cline.bot/customization/workflows
  - Workflow는 Markdown 파일이며 파일명이 slash command처럼 호출됨.
  - Workspace workflow는 `.clinerules/workflows/`에 둔다.
  - Global workflow는 사용자 시스템의 Cline Workflows 디렉터리에 둔다.
  - Workflow는 자연어 단계, Cline tool call, CLI command, MCP tool call을 조합할 수 있음.
  - 복잡한 프로세스는 독립 실행 가능한 workflow로 나누고 version control하라는 권고가 있음.

- Cline rules 문서  
  https://www.mintlify.com/cline/cline/customization/cline-rules
  - Rule은 지속적으로 적용되는 Markdown instruction이다.
  - `.clinerules/`, `.cursorrules`, `.windsurfrules`, `AGENTS.md`를 rule source로 인식한다.
  - Workspace rules는 `.clinerules/` 아래에 두고, Global rules는 `Documents/Cline/Rules` 등 OS별 위치에 둔다.
  - Header, bullet, example, 이유 설명이 Cline이 rule 범위를 이해하는 데 도움이 된다고 설명됨.
  - Conditional rules는 YAML frontmatter의 path 조건으로 특정 파일 범위에만 활성화할 수 있음.

- Cline GitHub repository  
  https://github.com/cline/cline
  - Cline은 VS Code 안에서 파일 구조, 소스 코드, regex search 등을 활용해 context를 확보하고, terminal command 실행, file edit, browser use, MCP 기반 tool 확장을 수행할 수 있는 autonomous coding agent로 설명됨.

### Agent harness 및 governance 관련 외부 근거

- OpenAI Agents SDK 발표  
  https://openai.com/index/the-next-evolution-of-the-agents-sdk/
  - 2026-04-15 공개 글.
  - agent loop를 위한 harness, controlled workspace, explicit instructions, tools, memory, sandbox, MCP, skills, `AGENTS.md`, shell, apply patch 같은 primitive가 강조됨.
  - 발표에서는 이를 `harness engineering`과 `agent operating layer` 트렌드의 외부 참고 근거로 사용할 수 있음.

- Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems  
  https://arxiv.org/abs/2604.14228  
  https://github.com/VILA-Lab/Dive-into-Claude-Code
  - arXiv abstract는 Claude Code가 shell command 실행, file edit, external service call을 수행하는 agentic coding tool이라고 설명한다.
  - 논문은 공개 TypeScript source code 분석을 통해 Claude Code architecture를 설명한다.
  - core loop는 model을 호출하고 tool을 실행하고 반복하는 simple while-loop라고 설명한다.
  - 대부분의 code는 permission system, context compaction, extensibility, subagent delegation, session storage 같은 loop 주변 system에 있다고 설명한다.
  - GitHub repository README는 `98.4% infrastructure, 1.6% AI`라는 요약 수치를 제시한다.
  - caution:
    - 소셜 미디어에서는 `leaked / reverse-engineered`로 유통되지만, 발표 자료에는 `공개 TypeScript source code 분석 기반 연구`라고 중립적으로 표현한다.
    - `98.4%`는 Claude Code codebase 분석 수치이며 Cline이나 모든 agent system에 직접 일반화하지 않는다.

- LinkedIn discussion: Eric Vyacheslav post  
  https://www.linkedin.com/posts/eric-vyacheslav-156273169_researchers-reverse-engineered-claude-code-share-7452612489550258176-53w1
  - 공개 HTML에서 `Claude Code Reversal Reveals 98.4% Infrastructure`라는 제목과 98.4% infrastructure framing을 확인.
  - comment에 arXiv:2604.14228 링크가 포함됨.
  - 발표에서는 LinkedIn을 primary evidence로 쓰지 않고, 위 arXiv/GitHub source로 claim을 anchor한다.

### AI-assisted mathematics 사례

- Erdős Problem #1196 discussion thread  
  https://www.erdosproblems.com/forum/thread/1196
  - 문제 페이지/토론 thread에서 `Additional thanks to: Liam Price`가 확인됨.
  - Liam Price가 2026-04-16에 `the link to the 5.4 Pro chat that solved the problem`을 공유.
  - Terence Tao가 해당 proof process와 follow-up runs, reasoning opacity, Markov-chain/von Mangoldt idea의 성격을 논의.
  - Math, Inc. formalization 관련 comment도 확인됨.

- Scientific American article  
  https://www.scientificamerican.com/article/amateur-armed-with-chatgpt-vibe-maths-a-60-year-old-problem/
  - 2026-04-24 기사.
  - Liam Price, ChatGPT Pro, 60-year-old Erdős problem, primitive sets 관련 보도.
  - Terence Tao는 이 사례가 이전 `Erdős problem` hype와 다르며, 사람들이 처음에 잘못된 방향으로 들어간 것과 관련된 `mental block`의 가능성을 언급.
  - Jared Duker Lichtman의 primitive sets 설명과 2022년 관련 proof 맥락도 포함.

- FutureGenNews summary  
  https://futuregennews.com/gpt-5-4-pro-credited-with-solving-erdos-primitive-sets-problem-after-prompt-by-liam-price
  - Accessible primary materials는 attribution과 formalization 상태를 확인하지만, viral framing 전체를 독립적으로 입증하지는 못한다고 caution을 명시.
  - 발표에서는 이 caution을 그대로 반영해 `AI가 난제를 단독으로 해결했다`가 아니라 `AI-assisted discovery가 고급 연구에서도 의미 있는 신호를 보이기 시작했다`로 표현한다.

### Qwen 관련 근거

- Alibaba Cloud Community: Qwen3-Coder-Next  
  https://www.alibabacloud.com/blog/602864
  - 2026-02-05 글.
  - Qwen3-Coder-Next를 coding agents와 local development에 맞춘 open-weight model로 설명.
  - agentic training, executable task synthesis, environment interaction, reinforcement learning, tool usage, failure recovery가 강조됨.

- arXiv: Qwen3-Coder-Next Technical Report  
  https://arxiv.org/abs/2603.00729
  - Qwen3-Coder-Next는 80B total parameter, 3B active parameter로 설명됨.
  - coding agents를 위한 open-weight model이며, executable environment feedback을 포함한 agentic training을 수행했다고 설명됨.
  - 이 수치는 `Qwen3-Coder-Next`에 대한 것이며, 내부 발표에서 `Qwen-3.5` 또는 다른 내부 모델명에 그대로 대입하면 안 된다.

## 4. 강연에서 사용할 claim status

| Claim | 상태 | 발표 처리 |
|---|---:|---|
| YouTube Shorts에는 AlphaGo, Gemini, Google DeepMind CEO Hassabis 관련 대통령 환담이 나온다 | confirmed | metadata와 caption 기반으로 intro hook 사용 |
| Hassabis가 `specific enough` instruction/control의 필요성을 정확한 문구로 말했다 | caution | 자동 자막 기반이므로 직접 인용 대신 취지로만 사용 |
| Claude Code 분석에서 `98.4% infrastructure, 1.6% AI`라는 framing이 제시된다 | confirmed | VILA-Lab GitHub/arXiv 기반으로 사용 |
| `98.4%` 수치가 모든 agent system에 그대로 적용된다 | refuted as absolute | Claude Code 사례로만 소개하고 일반 원리로는 `harness 비중이 크다`고 해석 |
| Erdős #1196 사례는 AI-assisted discovery가 연구 수준 문제에서도 의미 있는 신호를 보인다는 근거다 | confirmed with caution | Erdős thread, Scientific American, caution article 함께 사용 |
| AI가 아무 human review 없이 누구도 못 푼 난제를 완전히 독립적으로 해결했다 | unconfirmed / caution | Price prompt, expert discussion, formalization, refinement가 결합된 사례로 설명 |
| Cline은 VS Code 안에서 파일 읽기, 수정, terminal command, browser, MCP tool 확장을 활용할 수 있다 | confirmed | Cline 공식 repo와 문서 근거로 설명 |
| Cline Rules, Skills, Workflows, Hooks, `.clineignore`는 서로 다른 customization layer다 | confirmed | 공식 문서 기반으로 표와 계층 구조에 반영 |
| `AGENTS.md`는 Cline에서 rule source로 인식될 수 있다 | confirmed | Cline rules 문서 기반으로 반영 |
| 최근 agent system은 model 자체보다 harness, tools, memory, sandbox, instructions 쪽으로 중요성이 이동하고 있다 | confirmed with interpretation | OpenAI Agents SDK 글과 Cline 문서를 결합한 해석으로 표시 |
| 내부 연구소의 Qwen 모델명이 `Qwen-3.5`이고 특정 파라미터 수를 가진다 | unconfirmed | 사용자가 제공할 심층 리서치 원문 확인 전까지 placeholder 유지 |
| On-premise LLM이 항상 cloud LLM보다 안전하다 | refuted as absolute | governance 설계 없이는 안전을 단정할 수 없다고 설명 |

## 5. Skywork 업로드 권장 파일

- `skywork_inputs/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_source_pack.md`
- `skywork_inputs/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_skywork_prompt_v1.md`
- `skywork_inputs/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_visual_asset_prompts.md`
- `reports/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_blueprint.md`
- 기본 템플릿: `C:\Users\angpa\.codex\skills\skywork-ppt-workflow\assets\LGD_Template.pptx`
