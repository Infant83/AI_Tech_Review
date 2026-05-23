# Skywork Prompt v1

아래 프롬프트를 Skywork에 붙여넣고, 다음 파일을 함께 업로드한다.

- `C:\Users\angpa\.codex\skills\skywork-ppt-workflow\assets\LGD_Template.pptx`
- `skywork_inputs/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_source_pack.md`
- `skywork_inputs/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_visual_asset_prompts.md`
- `reports/2026-04-29_cline-onprem-qwen-agentic-workflow-lecture_blueprint.md`

---

업로드된 자료와 `LGD_Template.pptx`를 기반으로 한국어 PowerPoint deck을 생성해 주세요.

## 1. 프로젝트

프로젝트명: Cline과 온프레미스 Qwen으로 구축하는 일상 업무용 Agentic Workflow 강연안  
강의 제목: VS Code 확장 Cline을 활용한 개인화 Agentic Workflow 구축과 일상 업무 자동화  
발표 시간: 90분  
권장 분량: 총 35장 이내. 기본 구성은 31장 main slides + 4장 appendix slides.  
비율: 16:9  
템플릿: 업로드된 `LGD_Template.pptx`를 기본 템플릿으로 사용.

## 2. 청중

- 연구소 또는 기술 조직의 동료
- LLM, VS Code, Git, DevOps, MLOps에 관심은 있지만 Cline과 agentic workflow에는 익숙하지 않은 청중
- 일부는 LLM과 VS Code는 익숙하지만, Markdown Rules, Skillset, Workflow, `AGENTS.md`를 이용한 personal workflow harness 개념에는 익숙하지 않음

## 3. Deck의 목적

이 deck은 단순한 도구 소개나 제품 홍보가 아닙니다. 다음을 설명하는 90분 기술 강의자료여야 합니다.

1. Agentic Workflow가 무엇인지 명확히 설명한다.
2. Cline이 VS Code 안에서 단순 coding assistant를 넘어 personal workflow harness로 활용될 수 있음을 보여준다.
3. On-premise LLM을 governance, security, privacy, reproducibility 관점에서 설명한다.
4. Global Rules와 Local Rules, Markdown Rules, `AGENTS.md`, Skills, Workflows를 통해 Cline의 행동 방식과 업무 절차를 어떻게 정의하는지 설명한다.
5. Human-readable이면서 AI-readable한 working notes, rules, workflow documents의 중요성을 강조한다.
6. Email checkup, daily report preparation, Git workflow, OpenProject, Obsidian memo 같은 daily office workflow에 Cline을 연결하는 예시를 제시한다.
7. Agent output이 다음 작업의 input, 작업 이력, 업무 맥락, 지식 축적이 되는 순환 구조를 설명한다.
8. 마지막 메시지는 다음 문장으로 수렴한다.

> AI를 잘 쓰는 것보다 중요한 것은, AI가 참조할 수 있는 나의 업무 맥락과 절차를 잘 구조화하는 것이다.

## 4. 반드시 지킬 용어와 정정 규칙

- `Cline`은 VS Code에서 동작하는 agent coding extension이다.
- `Cline`은 단순한 vibe coding 도구가 아니라 개인화 workflow, skillset, rule, Markdown 기반 작업 지침을 통해 일상 업무를 보조하는 agentic workflow harness로 설명한다.
- `VS Code` 표현을 정확히 사용한다.
- `Qwen-3.5`, `Qwen3-Coder-Next`, 기타 Qwen 모델명과 파라미터 수는 업로드된 source pack에서 확인된 경우에만 단정한다.
- 내부 모델이 정확히 확인되지 않으면 `Qwen 계열 온프레미스 LLM`이라고 표현한다.
- 내부 endpoint, credential, 내부 URL, 개인 정보, 미공개 코드 경로를 포함하지 않는다. 필요한 경우 `<INTERNAL_LLM_ENDPOINT>`, `<PROJECT_ID>`, `<USER_NAME>` 같은 placeholder로 표현한다.

## 5. 소스 우선순위

1. 업로드된 source pack과 blueprint.
2. 업로드된 심층 리서치 원문이 있으면 그 내용을 가장 우선한다.
3. Cline 공식 문서와 Cline GitHub repository.
4. OpenAI Agents SDK 글은 harness engineering trend 설명용 외부 anchor로만 사용한다.
5. Alibaba Cloud Qwen3-Coder-Next 글과 arXiv technical report는 Qwen 계열 coding agent trend anchor로만 사용한다.

주의:

- source pack에 없는 기술적 사실을 임의로 추가하지 말라.
- 특히 Qwen 모델명, parameter count, context length, benchmark 수치는 검증된 경우에만 사용하라.
- 불확실한 내용은 `내부 자료 확인 필요`, `확인된 범위에서는`, `이 강연에서는 placeholder로 둔다`처럼 제한적으로 표현하라.

## 6. 전체 내러티브

Deck의 서사는 다음 흐름을 따라야 한다.

1. 대통령과 Demis Hassabis의 짧은 대화를 opening hook으로 사용한다.
2. AlphaGo와 Gemini의 성능은 이미 충분히 인상적이다. 질문은 Gemini 같은 foundation model이 때때로 지시하지 않은 일을 할 수 있을 때, 어떤 control과 audit이 필요한가다.
3. Hassabis 답변의 취지는 instruction이 specific하지 않을 때 모델이 다른 일을 할 수 있다는 점으로 연결한다. 자동 자막 기반이므로 장문 직접 인용은 피하고, `specific enough`라는 질문으로 재구성한다.
4. `Specific enough`는 prompt를 길게 쓰는 것이 아니다. 어떤 파일을 읽고, 어떤 tool을 쓰고, 어디서 멈추고, 어떤 evidence를 남기는지까지 정하는 것이다.
5. Claude Code 분석은 production agent에서 model call보다 surrounding infrastructure가 훨씬 크다는 신호를 준다. `98.4% infrastructure, 1.6% AI`는 Claude Code 사례 수치로만 사용하고, universal law로 일반화하지 않는다.
6. Erdős #1196 사례는 AI-assisted discovery가 고급 연구에서도 의미 있는 가능성을 보인다는 반대편 사례다. 단, prompt, model exploration, expert verification, formalization/refinement가 결합된 사례로 설명한다.
7. 따라서 문제는 `AI를 쓸 것인가`가 아니라 `얼마나 specific enough한 harness로 쓸 것인가`다.
8. 우리는 매일 이메일, 보고서, Git, project tracking, 연구 노트 사이를 오가며 context switching을 반복한다.
9. Agentic Workflow는 context, tools, rules, memory, human review를 하나의 반복 가능한 운영 구조로 묶는다.
10. Cline은 VS Code 안에서 이 구조를 개인 업무에 적용할 수 있는 실용적인 harness가 될 수 있다.
11. On-premise LLM은 내부 자료를 다룰 때 중요한 선택지지만, 그 자체가 governance를 완성하지는 않는다.
12. Global Rules, Local Rules, Skillset, Workflow, `AGENTS.md`, working notes를 설계해야 agent가 일관되게 행동한다.
13. Agent output은 결과물로 끝나지 않고 다음 task의 input, working note, project memory가 된다.
14. 결국 중요한 것은 모델을 잘 고르는 일보다, 모델이 읽고 따를 수 있는 업무 운영체계를 만드는 일이다.

## 7. Section 구성과 시간

### Section 1. Opening & Motivation - 10분

Slides 1-4.

- YouTube Shorts의 대통령-하사비스 대화로 시작한다.
- 질문: instruction과 audit이 `specific enough`하지 않을 때 agent는 어디로 drift하는가?
- Claude Code 98.4% infrastructure 사례로 harness engineering의 필요성을 보여준다.
- Erdős #1196 AI-assisted discovery 사례로 가능성을 보여주되, expert verification과 formalization을 함께 강조한다.
- 핵심 메시지: 업무를 AI에게 맡기는 것이 아니라, AI와 사람이 함께 관리할 수 있는 workflow로 재구성한다.

### Section 2. System Overview: VS Code, Cline, On-premise LLM - 15분

Slides 5-10.

- VS Code 중심 작업 환경.
- Cline의 역할: coding agent, tool-using agent, workflow assistant, personal workflow harness.
- 연구소 On-premise LLM과의 연결.
- Qwen 계열 내부 LLM 소개는 확인된 범위에서만 설명.
- On-premise 환경의 장점과 한계: security, data governance, internal knowledge protection, compliance, latency, availability, 운영 책임.
- 외부 cloud LLM과 On-premise LLM governance 비교.

### Section 3. From Prompting to Workflow Engineering - 15분

Slides 11-15.

- prompt engineering과 workflow engineering의 차이.
- Human-readable + AI-readable Markdown 문서의 중요성.
- 업무 맥락을 Cline이 참조할 수 있는 형태로 작성하는 이유.
- Rules, Skills, Workflows, working notes의 역할.
- 최근 trend: harness engineering, agent operating layer, governance by executable boundary.

### Section 4. Global and Local Markdown Rules for Cline - 20분

Slides 16-22.

- Global Rules: 기본 말투, 보안 규칙, 일반 코딩 스타일, 업무 원칙.
- Local/project-specific Rules: repository, 연구 프로젝트, 보고서 양식, DevOps workflow.
- `AGENTS.md`: cross-tool instruction surface.
- Skillset: 필요할 때 로드되는 전문 절차.
- Workflow: 순서와 중단 조건이 있는 반복 업무.
- 예시: Git commit convention, daily report format, Python/Fortran convention, 연구노트 정리, 금지 정보.

### Section 5. Demonstration Scenarios - 20분

Slides 23-26.

Demo 1. Email summarization / daily checkup

- 아침 이메일 요약.
- action item, deadline, reply-needed item 분류.
- daily note 전환.

Demo 2. Daily report preparation

- 오늘 한 일, 진행 중인 일, blocker, tomorrow plan.
- Obsidian memo 또는 Markdown report 저장.
- 이전 working notes 참조.

Demo 3. Git / DevOps workflow

- repository 상태 확인.
- 변경 사항 요약.
- commit message 작성.
- branch, merge request, issue tracking, OpenProject 연결.
- push/merge는 human approval.

### Section 6. Interactive Feedback Loop - 10분

Slides 27-29.

- Agent output이 다음 task의 input이 되는 구조.
- 작업 결과 -> working note -> project memory -> next action.
- Human-in-the-loop.
- 실패하거나 부정확한 output을 rule/workflow 개선으로 되돌리는 방법.

### Section 7. Governance, Boundaries, and Risk Management - 5분

Slide 30.

- On-premise LLM을 쓰더라도 필요한 보안 원칙.
- 내부 정보, 개인 정보, 연구 데이터, 미공개 코드 취급.
- Cline rules에 금지 사항 명시.
- tool use 권한 관리.
- 사람이 최종 책임자.

### Section 8. Conclusion & Q&A - 5분

Slide 31.

- 핵심 메시지 요약.
- Cline은 personal workflow harness로 확장 가능.
- Markdown skillset과 workflow는 AI와 사람이 공유하는 업무 운영체계.
- Q&A 유도.

### Appendix - 4장

Slides 32-35.

- 예시 Global Rule.
- 예시 project-specific Local Rule.
- 예시 daily report template.
- 예시 Git workflow instruction.

## 8. Slide-by-slide 생성 지침

업로드된 blueprint의 35장 구성을 따른다. 각 slide에는 반드시 다음을 포함한다.

1. slide title
2. 핵심 bullet 3-5개
3. speaker notes
4. visual suggestion 또는 실제 diagram

Speaker notes는 실제 발표자가 읽거나 참고할 수 있을 정도로 자세하게 작성한다. 단, slide 본문은 과도하게 길게 쓰지 않는다.

각 slide의 speaker notes는 다음 구조를 권장한다.

- 첫 문장: 이 slide에서 전달할 핵심.
- 중간: 발표자가 설명할 예시와 주의점.
- 마지막: 다음 slide로 넘어가는 bridge.

## 9. 필수 시각 자료

다음 7개는 deck 안에 반드시 포함한다.

1. 전체 시스템 아키텍처:
   - User -> VS Code -> Cline -> On-premise LLM -> Tools / Files / Git / Notes
2. Global Rules와 Local Rules의 계층 구조:
   - Global Rules, Local Rules, `AGENTS.md`, `.clinerules/`, `.clinerules/workflows/`, `.cline/skills/`
3. Human-readable / AI-readable Markdown workflow 문서 개념도:
   - 사람의 working note와 Cline context가 같은 Markdown 문서를 공유
4. Daily office workflow loop:
   - Email -> Summary -> Daily Note -> Report -> Git/Project Update -> Next Task
5. Human-in-the-loop feedback cycle:
   - Request -> Agent action -> Human review -> Refined instruction -> Saved workflow
6. 외부 cloud LLM과 On-premise LLM governance 비교표:
   - data path, access control, audit, latency, availability, cost, operational responsibility
7. Prompting과 Workflow Engineering의 차이 비교표:
   - one-shot instruction vs reusable operating structure

추가 opening 시각 자료:

8. `Specific enough?` opening bridge:
   - 대통령-과학자 대화를 직접 초상화처럼 재현하지 말고, `AI capability -> ambiguous instruction -> control/audit question -> harness engineering` 흐름으로 표현한다.
9. Claude Code harness iceberg:
   - visible model reasoning과 surrounding infrastructure를 대비한다.
   - `98.4%`는 Claude Code case study로만 표시하고 universal law처럼 표현하지 않는다.
10. AI-assisted discovery path:
   - problem -> AI exploration -> expert review -> formalization -> reusable method.
   - Erdős #1196 사례는 `human-AI collaboration`으로 표현한다.

## 10. 시각 스타일 지침

이 deck은 기술 세미나 자료이지만, 딱딱한 표만 반복하지 말고 강연자가 신경 써서 준비한 느낌이 나야 한다.

기본 스타일:

- LGD_Template의 corporate white-grid rhythm을 유지한다.
- 정보 밀도는 충분히 유지한다.
- section 전환과 핵심 개념에는 친근한 spot illustration을 넣는다.
- diagram과 table은 깔끔하고 설명 기능이 있어야 한다.
- 작은 dark green annotation text를 사용해 용어 설명, caveat, source note를 붙일 수 있다.
- reference는 하단 또는 관련 블록 근처에 작은 dark gray text로 명시한다.

이미지 사용 방식:

- 전 slide를 이미지로 채우지 않는다.
- 이미지가 slide 본문을 대체하지 않게 한다.
- 4-8개의 반복 가능한 visual motif를 deck 전체에 연결성 있게 사용한다.
- 이미지 안에 readable text를 넣지 않는다.
- 생성형 이미지가 필요한 경우 업로드된 `visual_asset_prompts`를 사용한다.

반복 모티프:

- VS Code workspace
- Cline as workflow harness
- Markdown rule cards
- On-premise LLM server and governance gate
- human review checkpoint
- working note to memory loop

피해야 할 것:

- 과한 SF 로봇 이미지.
- 마케팅 슬로건형 hero slide.
- 의미 없는 gradient blob.
- 유치한 캐릭터.
- 내부 회사 시스템처럼 보이는 구체 UI.
- 이미지 안의 깨진 텍스트.

## 11. 도식 스타일 제안

다음 slide pattern을 섞어 사용한다.

- Architecture diagram
- Annotated workflow
- Before/after comparison
- Governance comparison table
- Layered hierarchy
- Process + failure point + control action
- Demo flow storyboard
- Source status table

## 12. 발표 톤

- 전문적이고 기술 세미나에 적합하게.
- 너무 마케팅스럽지 않게.
- tool promotion보다 methodology 중심.
- 한국어 문장은 짧고 구체적으로.
- "핵심은", "중요한 것은" 같은 상투적 강조 표현을 남발하지 않는다.
- 주장, 근거, 제한 사항을 분리한다.
- 확인되지 않은 내용은 단정하지 않는다.

## 13. Output requirements

PowerPoint deck에는 다음이 포함되어야 한다.

- 31장 main slides + 4장 appendix slides, 총 35장 이내.
- 모든 slide에 speaker notes.
- 각 section별 예상 시간 표시.
- 마지막 main section에 전체 강의 요약 slide와 Q&A 유도 slide.
- Appendix:
  - 예시 Markdown Global Rule
  - 예시 project-specific Local Rule
  - 예시 Daily Report Template
  - 예시 Git Workflow Instruction

Deck 생성 후 self-check:

- `Cline` 용어가 일관되게 쓰였는가.
- Qwen 모델 수치가 검증된 범위 밖으로 확장되지 않았는가.
- 내부 민감 정보가 placeholder 처리되었는가.
- 그림이 장식이 아니라 설명을 돕는가.
- slide 본문이 너무 길지 않고 speaker notes에 설명이 들어갔는가.
- 90분 발표 흐름이 자연스러운가.
