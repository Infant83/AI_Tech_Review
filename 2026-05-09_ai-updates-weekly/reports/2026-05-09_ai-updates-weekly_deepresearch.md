---
title: 2026-05-09 AI Updates Weekly Deep Research
date: 2026-05-09
type: report
aliases:
  - Lev Selector AI Updates Weekly Deep Research 2026-05-09
author: Codex
date created: 2026-05-09
date modified: 2026-05-09
topic: ai-updates-weekly
status: processed
tags:
  - deepresearch
  - ai
  - agents
  - harness-engineering
  - developer-tools
---

# 2026-05-09 AI Updates Weekly Deep Research

## Summary

Lev Selector의 `2026-05-08 AI Updates Weekly`는 표면적으로는 다양한 AI 뉴스 모음입니다. 하지만 검증 가능한 항목만 추리면, 이번 회차의 중심은 `agent operating layer`입니다. 모델이 아니라 모델을 실제 업무자로 만드는 하네스, 권한, 기억, 검증, 커넥터, 병합, 감사 표면이 경쟁의 앞쪽으로 이동하고 있습니다.

하네스는 모델 주변의 실행 구조입니다. 프롬프트, 도구 호출, 파일 읽기와 쓰기, shell 실행, connector 권한, memory, retry, evaluation, approval, 산출물 review를 묶어 모델이 실제 작업을 끝내도록 만드는 층입니다. 이번 회차의 강한 신호는 하네스가 더 이상 제품 내부 구현이 아니라, 별도의 연구 주제이자 제품 차별화 지점으로 올라왔다는 점입니다.

## 1. Anthropic은 기업용 에이전트를 regulated work surface로 밀고 있습니다

Anthropic 관련 항목은 이번 회차에서 가장 많이 등장합니다. 여기서 중요한 것은 개별 발표의 많고 적음이 아니라, 기업 업무에 들어가기 위한 조건이 비교적 선명하게 드러난다는 점입니다.

[Anthropic의 2026-05-05 금융 서비스 발표](https://www.anthropic.com/news/finance-agents)는 10개 ready-to-run agent template을 제시합니다. Pitch builder, KYC screener, month-end closer 같은 이름이 중요한 이유는, 이들이 단순한 chatbot use case가 아니라 승인, 감사, 데이터 권한, 산출물 형식을 필요로 하는 업무 단위이기 때문입니다. 같은 발표는 Microsoft Excel, PowerPoint, Word, Outlook과의 add-ins, 금융 데이터 connector, Moody's MCP app을 함께 언급합니다.

이건 `LLM이 답변을 잘한다`는 메시지가 아닙니다. 기업 데이터가 있는 곳, 문서가 만들어지는 곳, 승인과 감사가 필요한 곳에 에이전트를 심겠다는 메시지입니다.

[Anthropic의 SpaceX compute deal 발표](https://www.anthropic.com/news/higher-limits-spacex)는 다른 층의 신호입니다. Anthropic은 SpaceX Colossus 1 data center의 compute capacity 사용 계약을 통해 Claude Code rate limit을 늘리고 peak-hour reduction을 제거한다고 설명합니다. 이 발표는 제품 UX가 모델 품질만이 아니라 compute capacity에 직접 묶여 있다는 점을 보여줍니다.

[Claude Code Security 발표](https://www.anthropic.com/news/claude-code-security)는 보안 하네스의 방향을 보여줍니다. Claude가 codebase를 읽고 data flow를 추적하며 vulnerability를 찾고 patch를 제안하지만, 적용은 human approval을 거친다고 설명합니다. 즉, 자동화의 핵심은 "모든 것을 자동 적용"이 아니라, 탐지와 제안을 자동화하고 책임 있는 승인 표면을 남기는 구조입니다.

[Claude Managed Agents 업데이트](https://claude.com/blog/new-in-claude-managed-agents)는 장기 실행 agent의 기억과 검증을 전면에 둡니다. Dreaming은 과거 session과 memory store를 주기적으로 검토해 memory를 정리하는 연구 preview이고, outcomes는 성공 기준을 rubric으로 정의해 별도의 grader가 결과를 평가하고 agent가 재시도하게 만드는 구조입니다. Multiagent orchestration도 포함되지만, 같은 주의 논문 신호와 함께 읽으면 "더 많은 agent"보다 "언제 분리하고 언제 통합할 것인가"가 더 중요한 질문이 됩니다.

## 2. 하네스가 연구 대상이 되었습니다

이번 회차의 가장 중요한 논문 묶음은 세 편입니다.

[Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723)는 agent performance가 harness engineering에 점점 더 의존한다고 진단합니다. 기존 harness 설계가 controller code와 runtime-specific convention 안에 숨어 있어 비교와 전이가 어렵기 때문에, harness behavior를 natural language artifact로 외부화하고 실행 가능한 형태로 다루자는 제안입니다.

[Meta-Harness](https://arxiv.org/abs/2603.28052)는 한 걸음 더 나아갑니다. 이 논문은 harness code를 사람이 손으로만 설계하는 대신, prior candidate의 code, score, execution trace를 참조하는 outer-loop system으로 최적화할 수 있다고 주장합니다. 이 관점에서는 하네스가 prompt snippet이 아니라 성능을 좌우하는 탐색 공간입니다.

[In-Context Prompting Obsoletes Agent Orchestration for Procedural Tasks](https://arxiv.org/abs/2604.27891)는 방향이 조금 다릅니다. 이 논문은 travel booking, Zoom technical support, insurance claims 같은 절차형 작업에서 전체 절차를 system prompt에 넣고 모델이 self-orchestrate하게 하는 방식이 LangGraph 기반 외부 orchestration보다 높은 점수와 낮은 failure rate를 보였다고 보고합니다.

이 결과를 "오케스트레이션은 끝났다"로 읽으면 과합니다. 논문이 다룬 것은 절차가 정의된 multi-turn task입니다. 독립적인 자료 조사, 병렬 실험, 서로 다른 권한 영역을 가진 작업, reviewer와 implementer를 분리해야 하는 coding workflow에서는 orchestration이 여전히 필요할 수 있습니다. 다만 이 논문은 중요한 균형추를 제공합니다. 강한 모델이 절차 전체를 한 번에 이해할 수 있다면, 외부 orchestrator가 매 turn마다 state와 routing instruction을 주입하는 방식은 상태 단절과 복잡도를 만들 수 있습니다.

## 3. DeepSeek-TUI, Hermes, OpenSwarm, InsForge는 모두 하네스를 제품화합니다

[DeepSeek-TUI](https://github.com/Hmbown/DeepSeek-TUI)는 DeepSeek V4용 terminal coding agent입니다. README는 file edit, shell, git, web search/browse, apply-patch, sub-agents, MCP, RLM, LSP diagnostics, session resume 등을 제시합니다. 이 프로젝트의 의미는 특정 모델 지원보다 더 넓습니다. 모델 API가 같더라도 terminal agent가 어떤 모드, 승인, rollback, diagnostics, cost tracking, context management를 제공하느냐가 사용 경험을 결정합니다.

[Hermes Agent](https://github.com/nousresearch/hermes-agent)는 CLI와 messaging gateway를 함께 제공합니다. 사용자는 terminal UI에서 대화하거나 Telegram, Discord, Slack, WhatsApp, Signal, Email 같은 messaging surface를 통해 agent와 상호작용할 수 있습니다. [Hermes Curator 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)는 agent-created skills가 쌓이는 문제를 다룹니다. Curator는 skill 사용과 patch 빈도를 추적하고, 오래 쓰지 않는 skill을 stale 또는 archived 상태로 이동시키는 background maintenance pass입니다. 이건 "에이전트가 스스로 skill을 만든다"는 멋진 문장보다 더 현실적인 문제를 건드립니다. skill catalog가 오염되면 context budget과 tool 선택 품질이 같이 무너집니다.

[OpenSwarm](https://github.com/VRSEN/OpenSwarm)은 slide deck, research report, data visualization, document, image, video 같은 deliverable을 한 prompt에서 생성하겠다는 multi-agent system입니다. 이 방향은 하네스가 coding에만 국한되지 않는다는 점을 보여줍니다. 문서와 발표자료, 영상 산출물도 agent workflow의 대상으로 들어오고 있습니다.

[InsForge](https://github.com/InsForge/InsForge)는 agentic coding을 위한 backend platform으로 자신을 설명합니다. MCP server와 CLI+Skills 인터페이스를 통해 coding agent가 database, auth, storage, compute, hosting, AI gateway를 다룰 수 있게 한다는 구조입니다. 이는 "코딩 agent가 코드를 잘 쓴다" 다음 단계의 문제입니다. agent가 full-stack app을 만들려면 backend resource를 만들고 설정하고 검증하는 표준 작업면이 필요합니다.

## 4. Connector는 비기술 사용자를 위한 하네스입니다

[xAI Grok connectors 문서](https://docs.x.ai/grok/connectors)는 Gmail, Google Calendar, Google Drive, OneDrive, Outlook Mail & Calendar, SharePoint 같은 built-in connectors를 설명합니다. OAuth로 한 번 연결하면 Grok이 conversation 안에서 email, cloud files, calendar를 활용할 수 있다는 구조입니다.

이 방향은 기술적으로 새롭다기보다 제품적으로 중요합니다. Claude Desktop이나 MCP server를 직접 설정하는 방식은 개발자에게는 유연하지만, 일반 업무 사용자의 adoption surface로는 무겁습니다. Connector는 "도구를 연결했다"는 설정 경험을 최대한 숨기고, 사용자가 작업 요청을 자연어로 던지면 필요한 외부 데이터를 agent가 가져오게 만드는 방향입니다.

Perplexity Workflows, Microsoft Copilot Actions와 Cowork도 같은 축에서 읽을 수 있습니다. 이번 패키지에서는 해당 항목을 깊게 검증하지 않았지만, 흐름은 분명합니다. 검색, 메일, 문서, 일정, 사내 파일이 연결된 상태에서 agent가 반복 업무를 수행하는 `개인 디지털 직원` 표면이 넓어지고 있습니다.

## 5. 개발자 도구의 병목은 생성에서 병합과 통제로 이동합니다

AI coding이 늘수록 "코드를 얼마나 빨리 만들 수 있는가"보다 "여러 agent가 만든 변경을 어떻게 검토하고 합칠 것인가"가 중요해집니다.

[Zed AI overview](https://zed.dev/docs/ai/overview)는 Zed를 open-source AI code editor로 설명하고, agent, inline transformation, completions, conversations with models를 native GPU-accelerated Rust app 안에서 제공한다고 말합니다. Zed의 핵심 신호는 editor가 단순 editing surface가 아니라 agent interaction surface가 된다는 점입니다.

[Jujutsu](https://github.com/jj-vcs/jj)는 Git-compatible VCS입니다. Git repository를 storage layer로 사용하지만, staging area가 없고, anonymous branches와 history rewrite 중심의 workflow를 강조합니다. agent가 여러 변경을 실험하고 되돌리고 병렬화하는 환경에서는 이러한 version control model이 더 자연스러울 수 있습니다.

[Mergiraf](https://mergiraf.org/)는 syntax tree aware merge를 제공하고, [Weave](https://ataraxy-labs.github.io/weave/)는 entity-level semantic merge driver와 multi-agent coordination layer, MCP server까지 표방합니다. Weave 문서는 두 agent가 같은 파일의 다른 function을 고쳤을 때 line-based conflict가 아니라 entity-level merge로 처리하는 사례를 전면에 둡니다.

이 항목들은 주변 도구처럼 보이지만, agentic coding의 실제 병목과 맞닿아 있습니다. agent를 많이 돌리면 code generation은 많아지고, 그 결과 branch, patch, conflict, test, review, audit 문제가 커집니다. 따라서 merge driver, VCS model, worktree coordination, review surface는 agent productivity의 하부 인프라가 됩니다.

## 6. AI co-clinician은 도메인 agent의 안전 설계를 보여줍니다

[Google DeepMind의 AI co-clinician 발표](https://deepmind.google/blog/ai-co-clinician/)는 의료 분야 사례입니다. DeepMind는 AI co-clinician을 patient history collection, diagnostic reasoning, examination guidance를 보조하는 research project로 설명합니다. 중요한 것은 성능 수치보다 안전 구조입니다. 글은 clinical conversation simulation에서 `Planner` module이 `Talker` agent가 안전한 임상 경계 안에 머무는지 감시하는 dual-agent architecture를 설명합니다.

또한 해당 발표는 이 연구가 질병의 진단, 치료, 완화, 예방이나 의료 조언 제공을 위한 단계가 아니라고 명시합니다. 따라서 이 사례는 "의료 agent가 곧 의사를 대체한다"가 아니라, 고위험 도메인에서 agent를 쓰려면 evidence prioritization, citation checking, safety boundary monitoring, phased real-world evaluation이 필요하다는 신호로 읽어야 합니다.

## 7. 낮은 신뢰도 항목은 결론에서 내려야 합니다

이번 회차는 빠른 weekly update이기 때문에 일부 항목은 주의가 필요합니다.

첫째, OpenAI 관련 항목입니다. 영상 설명란에는 `GPT 4.5 Instant`, 슬라이드에는 `GPT 5.5 Instant`가 등장합니다. 표기가 서로 다르고, 공식 OpenAI 문서 검색에서 동일한 기능명과 `52% fewer hallucinations` 주장을 직접 확인하지 못했습니다. Codex CLI `/goal` 및 `goals = true`도 공개 공식 문서에서 확인하지 못했습니다. 따라서 이 항목들은 "영상/슬라이드가 제시한 claim"으로만 보관하고, 리뷰 결론에는 올리지 않았습니다.

둘째, layoffs 관련 수치입니다. AI가 노동시장에 영향을 주고 있다는 큰 흐름은 별도로 추적할 가치가 있지만, 특정 회사의 감원 수와 원인을 AI 대체 효과로 직접 연결하려면 기업 공시, 공식 발표, 신뢰 가능한 보도 확인이 필요합니다. 이번 패키지에서는 그 검증을 수행하지 않았습니다.

셋째, OpenClaw 안정성 평가입니다. 영상과 슬라이드는 OpenClaw release와 사용자 경험담을 함께 다룹니다. 흥미로운 신호지만, 한 사용자 경험담을 제품 전체 품질 판단으로 일반화하지 않았습니다.

## 결론

이번 `AI Updates Weekly`는 `모델이 더 좋아졌다`는 익숙한 결론으로 끝내기 아깝습니다. 더 중요한 변화는 모델 주변의 실행층이 제품과 연구의 중심으로 올라왔다는 점입니다.

기업용 에이전트는 connector, audit, template, approval을 필요로 합니다. 개발자용 에이전트는 file edit, shell, git, rollback, diagnostics, merge, review를 필요로 합니다. 장기 agent는 memory와 self-improvement를 필요로 하지만, 그 memory가 오염되지 않게 curator도 필요합니다. multi-agent 구조는 강력하지만, 절차형 작업에서는 오히려 전체 맥락을 한 모델에 유지하는 것이 더 나을 수 있습니다.

따라서 이번 회차의 기술적 메시지는 분명합니다.

`에이전트 경쟁은 모델 호출 경쟁이 아니라, 하네스를 어떻게 설계하고 운영할 것인가의 경쟁으로 이동하고 있습니다.`

## External References

- [Exciting AI Updates Weekly - May 8, 2026](https://www.youtube.com/watch?v=yDfupTHYshQ)
- [lselector/seminar GitHub repository](https://github.com/lselector/seminar)
- [2026-05-08-AI-Updates.pptx](https://raw.githubusercontent.com/lselector/seminar/master/2026/2026-05-08-AI-Updates.pptx)
- [Anthropic - Higher usage limits for Claude and a compute deal with SpaceX](https://www.anthropic.com/news/higher-limits-spacex)
- [Anthropic - Agents for financial services](https://www.anthropic.com/news/finance-agents)
- [Anthropic - Building a new enterprise AI services company](https://www.anthropic.com/news/enterprise-ai-services-company)
- [Anthropic - Claude Code Security](https://www.anthropic.com/news/claude-code-security)
- [Claude - New in Claude Managed Agents](https://claude.com/blog/new-in-claude-managed-agents)
- [arXiv:2604.27891 - In-Context Prompting Obsoletes Agent Orchestration for Procedural Tasks](https://arxiv.org/abs/2604.27891)
- [arXiv:2603.25723 - Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723)
- [arXiv:2603.28052 - Meta-Harness](https://arxiv.org/abs/2603.28052)
- [DeepSeek-TUI](https://github.com/Hmbown/DeepSeek-TUI)
- [xAI Grok connectors](https://docs.x.ai/grok/connectors)
- [OpenSwarm](https://github.com/VRSEN/OpenSwarm)
- [Hermes Agent](https://github.com/nousresearch/hermes-agent)
- [Hermes Curator](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)
- [InsForge](https://github.com/InsForge/InsForge)
- [Zed AI overview](https://zed.dev/docs/ai/overview)
- [Jujutsu](https://github.com/jj-vcs/jj)
- [Mergiraf](https://mergiraf.org/)
- [Weave](https://ataraxy-labs.github.io/weave/)
- [Google DeepMind - AI co-clinician](https://deepmind.google/blog/ai-co-clinician/)
