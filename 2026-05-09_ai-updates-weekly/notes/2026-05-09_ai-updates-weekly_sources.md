---
title: 2026-05-09 AI Updates Weekly Sources
date: 2026-05-09
type: source-note
aliases:
  - Lev Selector AI Updates Weekly Sources 2026-05-09
author: Codex
date created: 2026-05-09
date modified: 2026-05-09
topic: ai-updates-weekly
source_date: 2026-05-08
status: processed
tags:
  - source-note
  - ai
  - agents
  - harness-engineering
---

# 2026-05-09 AI Updates Weekly Sources

## 원천 패키지

- 영상: [Exciting AI Updates Weekly - May 8, 2026](https://www.youtube.com/watch?v=yDfupTHYshQ)
- 채널: Lev Selector
- 영상 업로드일: 2026-05-08
- 영상 길이: 26:59
- 로컬 설명 파일: `sources/20260508_Exciting AI Updates Weekly - May 8, 2026 [yDfupTHYshQ].description`
- 로컬 자막 파일: `sources/20260508_Exciting AI Updates Weekly - May 8, 2026 [yDfupTHYshQ].en.vtt`
- 정리 자막 파일: `sources/20260508_Exciting AI Updates Weekly - May 8, 2026 [yDfupTHYshQ].en.clean.txt`
- 메타데이터 파일: `sources/2026-05-08_Exciting_AI_Updates_Weekly_May_8_2026_yDfupTHYshQ.info.json`
- 원본 슬라이드: `sources/2026-05-08-AI-Updates.pptx`
- 슬라이드 텍스트 추출: `sources/2026-05-08-AI-Updates_slide-extract.md`
- 슬라이드 원천 저장소: [lselector/seminar](https://github.com/lselector/seminar)
- 다운로드한 슬라이드 원본: [2026-05-08-AI-Updates.pptx](https://raw.githubusercontent.com/lselector/seminar/master/2026/2026-05-08-AI-Updates.pptx)

## 영상이 제시한 주제 맵

이번 회차는 `In 2026, your agents have agents`라는 문장으로 시작합니다. 항목 수는 많지만, 실제로는 다음 네 축으로 묶입니다.

1. 에이전트 하네스와 오케스트레이션
   - DeepSeek-TUI
   - Hermes Agent Curator
   - OpenSwarm
   - "No AI Agent Orchestration Needed" 논문
   - "Harness more important than the model" 논문 묶음
   - InsForge

2. 기업용 에이전트 작업면
   - Anthropic 금융 서비스 에이전트
   - Anthropic SpaceX compute deal
   - Claude Code Security
   - Claude Managed Agents의 dreaming, outcomes, multiagent orchestration
   - xAI Grok connectors
   - Perplexity Workflows
   - Microsoft Copilot Actions and Cowork

3. 개발자 작업 도구와 협업 기반
   - Claude Code, Codex CLI, Hermes goals
   - Zed
   - Jujutsu
   - Weave와 Mergiraf
   - Superpowers

4. 산업별 또는 산출물 중심 사례
   - Google DeepMind AI co-clinician
   - TradingAgents
   - Higgsfield
   - Suno
   - HyperFrames
   - Unity AI
   - 노동시장과 layoffs 해설

## 영상의 직접 Takeaways

영상 설명란은 세 가지 결론을 직접 제시합니다.

- `Harness engineering`이 모델 자체보다 중요해졌고, 같은 모델도 하네스에 따라 성능 차이가 크게 날 수 있다.
- 강한 frontier 모델은 복잡한 작업을 하나의 흐름으로 처리할 수 있으므로, 과도한 multi-agent orchestration이 오히려 추론을 쪼개고 품질을 낮출 수 있다.
- 코딩은 더 넓은 사람에게 열리고 있으며, Boris Cherny는 이를 printing press moment로 표현했다.

이번 리뷰에서는 이 세 결론 중 첫째와 둘째를 중심축으로 삼습니다. 셋째는 개발자 역할 변화의 배경으로만 다룹니다.

## 확인된 1차 또는 준1차 출처

### Anthropic

- [Higher usage limits for Claude and a compute deal with SpaceX](https://www.anthropic.com/news/higher-limits-spacex)
  - 2026-05-06 발표.
  - Claude Code 5시간 rate limit 확대, peak-hour reduction 제거, SpaceX Colossus 1 compute capacity 사용 계약을 직접 언급.
- [Agents for financial services](https://www.anthropic.com/news/finance-agents)
  - 2026-05-05 발표.
  - 10개 금융 서비스 에이전트 템플릿, Microsoft 365 add-ins, 금융 데이터 connector와 Moody's MCP app을 직접 설명.
- [Building a new enterprise AI services company with Blackstone, Hellman & Friedman, and Goldman Sachs](https://www.anthropic.com/news/enterprise-ai-services-company)
  - 2026-05-04 발표.
  - Anthropic, Blackstone, H&F, Goldman Sachs가 새 AI services company를 만든다는 내용.
- [Making frontier cybersecurity capabilities available to defenders](https://www.anthropic.com/news/claude-code-security)
  - 2026-02-20 발표.
  - Claude Code Security는 limited research preview이며, codebase scanning, vulnerability reasoning, patch suggestion, human approval을 강조.
- [New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration](https://claude.com/blog/new-in-claude-managed-agents)
  - 2026-05-06 발표.
  - dreaming, outcomes, multiagent orchestration, webhook을 Managed Agents 업데이트로 설명.

### Agent harness와 orchestration 논문

- [In-Context Prompting Obsoletes Agent Orchestration for Procedural Tasks](https://arxiv.org/abs/2604.27891)
  - 2026-04-30 제출, 2026-05-05 v2.
  - 절차형 작업에서 전체 절차를 system prompt에 넣는 방식이 LangGraph 기반 외부 orchestration보다 높은 점수와 낮은 failure rate를 보였다고 주장.
- [Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723)
  - 2026-03-26 제출.
  - agent harness를 코드 내부 convention이 아니라 portable executable natural-language artifact로 다루자는 제안.
- [Meta-Harness: End-to-End Optimization of Model Harnesses](https://arxiv.org/abs/2603.28052)
  - 2026-03-30 제출.
  - harness code 자체를 외부 루프로 탐색하고 최적화하는 시스템을 제안.

### 에이전트 도구와 작업면

- [xAI Grok Connectors](https://docs.x.ai/grok/connectors)
  - Gmail, Google Calendar, Google Drive, OneDrive, Outlook Mail & Calendar, SharePoint 등 built-in connectors를 설명.
- [DeepSeek-TUI](https://github.com/Hmbown/DeepSeek-TUI)
  - DeepSeek V4용 terminal coding agent.
  - file edit, shell, git, web search/browse, MCP, sub-agent, RLM, 1M context 등을 README에서 제시.
- [OpenSwarm](https://github.com/VRSEN/OpenSwarm)
  - slide deck, research report, visualization, documents, images, videos를 한 prompt에서 만들겠다는 open-source multi-agent system.
- [Hermes Agent](https://github.com/nousresearch/hermes-agent)
  - terminal UI와 messaging gateway를 모두 제공하는 personal agent 계열 프로젝트.
- [Hermes Curator](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)
  - agent-created skills를 active, stale, archived 상태로 관리하는 background maintenance pass.
- [InsForge](https://github.com/InsForge/InsForge)
  - agentic coding을 위한 backend platform. MCP server와 CLI+Skills 인터페이스를 제공한다고 설명.

### 개발자 협업 기반

- [Zed AI overview](https://zed.dev/docs/ai/overview)
  - Zed는 open-source AI code editor이며, native GPU-accelerated Rust app 안에서 agent, inline transformation, completions, model conversation을 제공한다고 설명.
- [Jujutsu](https://github.com/jj-vcs/jj)
  - Git-compatible VCS. Git repository를 storage layer로 사용하지만 index/staging, anonymous branches, rewrite workflow 등 다른 사용 모델을 제시.
- [Mergiraf](https://mergiraf.org/)
  - Git의 line-based merge를 보완하기 위해 syntax tree aware merge를 제공.
- [Weave](https://ataraxy-labs.github.io/weave/)
  - entity-level semantic merge driver와 multi-agent coordination layer, MCP server를 표방.

### 도메인 사례

- [Google DeepMind AI co-clinician](https://deepmind.google/blog/ai-co-clinician/)
  - 2026-04-30 발표.
  - AI co-clinician을 clinical conversation, diagnostic reasoning, safe boundary monitoring을 위한 research project로 설명.
  - 진단, 치료, 질병 예방을 위한 의료 조언으로 사용하려는 단계가 아니라고 명시.

## 주의해서 다룰 주장

다음 항목은 영상과 슬라이드에 등장하지만, 이번 리뷰에서는 결론의 근거로 쓰지 않습니다.

- `OpenAI GPT 4.5 Instant` 또는 슬라이드의 `OpenAI GPT 5.5 Instant`
  - 영상 설명과 슬라이드 표기가 서로 다릅니다.
  - 공식 OpenAI 문서에서 같은 명칭과 수치 주장을 직접 확인하지 못했습니다.
- `Codex CLI /goal` 및 `goals = true`
  - 공개 OpenAI 도움말과 공식 문서 검색에서 동일한 기능명을 직접 확인하지 못했습니다.
- 일부 layoffs 수치와 AI 대체 주장
  - 영상 해설과 2차 출처에 가까우며, 원천 기업 공시나 공식 발표로 확인하지 않았습니다.
- OpenClaw의 stars, release 상세, 안정성 평가
  - 슬라이드가 제시한 흥미로운 신호이지만 이번 패키지에서는 저장소와 릴리스 전체를 별도 검증하지 않았습니다.

## 이번 리뷰의 중심 질문

이번 회차를 단순한 뉴스 목록으로 읽으면 정보량은 많지만 남는 구조가 약합니다. 더 중요한 질문은 다음과 같습니다.

- 모델 성능 경쟁이 아니라, 모델을 실제 업무에 넣는 하네스 경쟁이 본격화되고 있는가?
- multi-agent orchestration은 언제 필요한 구조이고, 언제 불필요한 복잡도인가?
- 기업용 에이전트는 일반 chatbot에서 어떤 작업면으로 이동하고 있는가?
- 개발자 도구는 코드 작성 도구에서 agent control surface로 재편되고 있는가?
- 개인 또는 팀 단위의 `digital employee`를 만들 때 핵심 병목은 모델 선택인가, 하네스/권한/검증/기억/병합인가?
