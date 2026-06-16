---
title: 2026-06-16 Lev Selector Recent Updates
date: 2026-06-16
topic_slug: lev-selector-recent-updates
tags:
  - daily-review
  - ai-updates-weekly
  - lev-selector
  - agents
  - harness-engineering
  - enterprise-ai
  - ai-infrastructure
---

# 2026-06-16 Lev Selector 최근 YouTube 신기술 확인

## 오늘 대화 요약

- 2026-06-16 기준 Lev Selector 채널의 최신 주간 AI 업데이트는 2026-06-12 공개된 [Exciting AI Updates Weekly - June 12, 2026](https://www.youtube.com/watch?v=zyE4uXQ5hS4)입니다.
- GitHub companion slide도 [2026-06-12-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-06-12-AI-Updates.pptx)가 최신 AI Updates 파일로 확인되었습니다.
- 이번 주 신호는 새 모델 이름보다 `agent memory`, `harness engineering`, `context compression`, `enterprise data platform 안의 agent`에 더 강하게 모입니다.
- 바로 추적할 신기술은 [DiffusionGemma 26B](https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/)이고, 심층 리뷰 후보로는 `Agent memory와 harness engineering`을 가장 추천합니다.

## 확인 범위

- 기준일: 2026-06-16
- 채널: [Lev Selector](https://www.youtube.com/@lev-selector)
- 확인 경로:
  - YouTube RSS: `https://www.youtube.com/feeds/videos.xml?channel_id=UCA4GfsgbI09cLzonTKryC6g`
  - `yt-dlp` 채널/영상 메타데이터
  - GitHub companion slides: [lselector/seminar](https://github.com/lselector/seminar)
  - 주요 기술 항목의 공식 발표, 제품 문서, 저장소, 벤치마크 페이지
- 이번 메모는 심층리서치 본문이 아니라 intake review입니다. YouTube와 슬라이드는 discovery map으로 보고, 기술 결론은 원 출처가 확인된 항목만 올렸습니다.

## 최근 영상 목록

| 공개일 | 영상 | companion slide | 1차 확인 |
|---|---|---|---|
| 2026-06-12 | [Exciting AI Updates Weekly - June 12, 2026](https://www.youtube.com/watch?v=zyE4uXQ5hS4) | [2026-06-12-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-06-12-AI-Updates.pptx) | YouTube RSS, `yt-dlp`, GitHub API |
| 2026-06-05 | [Exciting AI Updates Weekly - June 05, 2026](https://www.youtube.com/watch?v=dR0G4sr9u5A) | [2026-06-05-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-06-05-AI-Updates.pptx) | `yt-dlp`, GitHub API |
| 2026-05-29 | [Exciting AI Updates Weekly - May 29, 2026](https://www.youtube.com/watch?v=na-sQ-g2MAc) | [2026-05-29-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-05-29-AI-Updates.pptx) | `yt-dlp`, GitHub API |
| 2026-05-22 | [Exciting AI Updates Weekly - May 22, 2026](https://www.youtube.com/watch?v=-NqSCfOB8yg) | [2026-05-22-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-05-22-AI-Updates.pptx) | `yt-dlp`, GitHub API |

## 먼저 보는 결론

최근 Lev Selector의 흐름은 새 모델 이름을 따라가는 방식에서 조금 더 운영 쪽으로 이동했습니다. 2026년 5월 중순 메모에서 보았던 `personal digital employee`, `agent OS`, `harness engineering` 흐름이 6월에는 더 구체화되어 있습니다. 특히 2026-06-12 영상은 "agent has no memory, it has no career"라는 문제의식으로 시작하고, `agent 선택`, `harness 선택`, `harness 구성`, `persistent memory`, `enterprise data platform 안의 agent`를 한 묶음으로 다룹니다.

AI_Tech_Review 관점에서는 네 가지가 중요합니다.

1. 모델 성능보다 에이전트의 지속 상태, 메모리, 도구 실행 환경을 어떻게 설계할지가 더 큰 주제가 되고 있습니다.
2. Claude Code, Codex, Cursor 같은 coding agent 경쟁은 곧 비용 통제, context compression, cheap sub-agent routing 문제로 이어지고 있습니다.
3. Snowflake와 Databricks가 AI agent를 데이터 플랫폼 안으로 넣으면서, 기업형 AI의 핵심이 `데이터 거버넌스 안에서 실행되는 agent`로 이동하고 있습니다.
4. DiffusionGemma처럼 decoding 방식을 바꾸는 모델도 나왔지만, 이번 Lev 영상 묶음에서는 모델 자체보다 agent runtime, memory, evaluation, governance 쪽 신호가 더 큽니다.

## 확인된 신기술 후보

### 1. Persistent memory와 Stateful Swarms

Lev의 6월 12일 영상은 agent memory를 가장 앞에 둡니다. 여기서 말하는 memory는 긴 prompt에 기록을 계속 밀어 넣는 방식이 아니라, 여러 agent가 함께 읽고 쓰는 지속형 상태 저장소에 가깝습니다. 슬라이드에서는 `Stateful Swarms`를 예로 들며, append-only typed knowledge base, provenance, 반복 재처리 비용 절감, Harvey Legal Agent Benchmark 결과를 연결합니다.

확인 상태는 `관심 신호`입니다. `Stateful Swarms` 자체는 현재 블로그/해설 글을 중심으로 퍼지고 있어 바로 확정된 표준으로 보기는 어렵습니다. 다만 비교 대상으로 쓰인 [Harvey Legal Agent Benchmark](https://www.harvey.ai/blog/introducing-harveys-legal-agent-benchmark)는 2026-05-06에 공개된 장기 법률 agent 벤치마크이며, 1,200개 이상 agent task와 24개 법률 업무 영역을 제시합니다. 따라서 `memory가 긴 agent 작업의 비용과 재현성에 얼마나 영향을 주는가`는 심층리서치 주제로 충분합니다.

AI_Tech_Review 적용 포인트는 분명합니다. FEATHER, Task Memory Hub, OpenProject, Obsidian처럼 이미 작업 기록이 남는 환경에서는 단순한 chat history보다 `작업별 상태`, `근거 파일`, `승인 기록`, `실행 로그`를 agent가 재사용할 수 있게 만드는 편이 더 실용적입니다.

### 2. Harness engineering

6월 12일 companion slide는 `Choose an Agent`, `Choose a Harness`, `How to make a harness`를 따로 둡니다. 여기서 harness는 LLM 바깥의 실행 환경입니다. tool registry, sandbox, lifecycle hook, human-in-the-loop gate, context compaction, iteration cap 같은 요소가 들어갑니다.

공식적으로 확인되는 흐름도 있습니다. [Microsoft Agent Framework 1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)은 2026-04-03에 .NET/Python용 production-ready release로 발표되었고, multi-agent orchestration, multi-provider model support, A2A/MCP 상호운용성을 전면에 둡니다. GitHub 저장소도 [microsoft/agent-framework](https://github.com/microsoft/agent-framework)로 공개되어 있습니다.

실무적으로는 `어떤 모델을 쓰는가`보다 `어떤 권한으로 어떤 도구를 호출하고, 실패하면 어떻게 되돌아오며, 어디까지 사람이 승인하는가`가 더 중요해지고 있습니다. 이 주제는 이전 AI Updates Weekly 메모의 `harness engineering now matters more than the model itself` 흐름과도 이어집니다.

### 3. Context compression과 agent 비용 통제

2026-06-05 영상의 핵심 takeaways는 비용 절감입니다. Lev는 Headroom context compression, agent compiler, cheap or local sub-agent routing을 함께 묶어 설명합니다. 이 흐름은 6월 12일의 persistent memory 논의와 같이 보아야 합니다. agent가 오래 일할수록 토큰 비용과 context 오염이 먼저 한계가 되기 때문입니다.

[Headroom](https://github.com/chopratejas/headroom)은 GitHub README 기준으로 tool output, logs, RAG chunks, files, conversation history를 LLM에 보내기 전에 압축하는 layer입니다. library, proxy, agent wrapper, MCP server 형태를 제공하며, cross-agent memory와 failed session learning도 표방합니다. 아직 성능 수치는 각 사용자가 재현 검증해야 하지만, `agent 비용 절감`이라는 문제의식은 매우 직접적입니다.

우리 쪽에서는 긴 research run, browser log, markdown evidence pack을 다루는 AI_Tech_Review 자동화에 바로 닿습니다. 단순 요약기가 아니라 `무엇을 버리고 무엇을 남기는지 추적 가능한 compression`인지가 검토 포인트입니다.

### 4. DiffusionGemma 26B

Lev의 6월 12일 영상은 [Google DiffusionGemma 26B](https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/)를 다룹니다. Google은 2026-06-10 DiffusionGemma를 공개했고, 이 모델을 26B MoE 기반의 experimental open model로 설명합니다. 일반적인 autoregressive LLM처럼 token을 순차적으로 내는 대신, text diffusion 방식으로 block 단위 출력을 병렬 생성하는 접근입니다.

Google 발표 기준 주요 확인 사항은 다음과 같습니다.

- Apache 2.0 라이선스의 experimental open model입니다.
- 26B total MoE 모델이지만 inference 때 활성화되는 파라미터는 3.8B 규모라고 설명합니다.
- dedicated GPU에서 최대 4배 빠른 text generation을 목표로 합니다.
- H100에서 1,000 tokens/sec 이상, RTX 5090에서 700 tokens/sec 이상을 주장합니다.
- production quality의 일반 답변보다 inline editing, rapid iteration, local interactive workflow 같은 latency-sensitive 사용처를 먼저 염두에 둡니다.

이 항목은 별도 심층리서치 가치가 있습니다. 특히 `local interactive agent`와 `fast drafting/editing loop`에 어떤 의미가 있는지, 기존 speculative decoding이나 small model routing과 어떻게 비교되는지 확인할 필요가 있습니다.

### 5. Snowflake Cortex Agents와 Databricks Agent Bricks

6월 12일 영상 후반부는 Snowflake와 Databricks를 크게 다룹니다. 이 부분은 단순 제품 소개보다 중요합니다. 기업 데이터 플랫폼이 agent runtime을 자기 안으로 흡수하는 흐름이기 때문입니다.

[Snowflake Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)는 Snowflake의 governed environment 안에서 agent를 만들고 실행하는 fully managed agentic platform입니다. 문서 기준으로 agent는 요청을 해석하고, 계획을 세우고, tool을 호출하고, code를 실행하며, structured data와 unstructured data를 함께 다룹니다. Cortex Analyst, Cortex Search, Python sandbox, Data to Chart, stored procedure/UDF custom tools, packaged agent skills가 연결됩니다.

[Databricks Agent Bricks](https://www.databricks.com/product/artificial-intelligence/agent-bricks)는 production AI agents를 build, govern, improve하는 플랫폼으로 설명됩니다. Databricks는 enterprise context, schemas, business definitions, custom semantics를 agent 의사결정에 연결하고, model choice, governance, deployment, MLflow tracing, Unity Catalog 기반 권한 통제를 강조합니다.

검토 포인트는 분명합니다. 기업형 agent는 standalone chatbot이 아니라 데이터 권한, lineage, audit log, semantic layer, 비용 제한 안에서 돌아가야 합니다. Snowflake와 Databricks는 이 조건을 자신들의 플랫폼 장점으로 가져가려 하고 있습니다.

### 6. Agent evaluation: Agent Arena와 Legal Agent Benchmark

Lev는 6월 12일 영상에서 `Agent Arena`를 다룹니다. [Agent Arena](https://arena.ai/leaderboard/agent)는 2026-06-12 기준 real-world agentic task에서 tool reliability, task completion, steerability 같은 신호로 모델을 비교한다고 설명합니다. Factory 문서의 [Agent Arena methodology](https://docs.factory.ai/benchmarks/agent-arena)는 crowdsourced head-to-head comparison과 Elo rating을 내세웁니다.

이런 leaderboards는 재미있지만, 그대로 구매 판단표로 쓰기에는 이릅니다. 어떤 task가 포함되는지, user voting bias가 어떤지, tool access와 UI 조건이 어떻게 맞춰졌는지 확인해야 합니다. 그럼에도 `chatbot benchmark`에서 `tool-use benchmark`로 평가 관심이 옮겨가는 신호로는 중요합니다.

Harvey LAB도 같은 축에 있습니다. 법률 분야처럼 긴 문서, 근거, work product review가 필요한 영역에서 agent를 평가하려면 단발 QA가 아니라 장기 업무 단위의 benchmark가 필요합니다.

### 7. Lilly TuneLab과 AI drug discovery platform

6월 12일 영상은 Eli Lilly도 다룹니다. [Lilly TuneLab](https://investor.lilly.com/news-releases/news-release-details/lilly-launches-tunelab-platform-give-biotechnology-companies)은 2025-09-09 공식 발표된 AI/ML platform입니다. Lilly는 초기 biotech 회사가 Lilly 연구 데이터로 학습된 drug discovery models에 접근할 수 있게 한다고 설명했고, 첫 release에 10억 달러 이상 비용이 투입된 proprietary research data가 포함된다고 밝혔습니다.

이 항목은 AI for Science 관점에서 중요합니다. 공개 모델 성능보다 `수십 년간 축적한 proprietary experimental data`, `partner network`, `privacy-preserving collaboration`, `drug discovery workflow integration`이 moat가 되는 사례이기 때문입니다. OLED/재료/DFT 쪽 연구 자동화와 직접 비교하려면, public benchmark보다 domain data와 closed-loop experiment design이 얼마나 중요한지 보는 방향이 좋습니다.

## 확인 유보 항목

아래 항목은 Lev 영상/슬라이드에는 나오지만, 이번 intake에서 보고서 결론으로 올리기에는 확인 강도가 낮거나 별도 검증이 필요합니다.

- `Claude Fable 5`, `Claude Mythos 5`, `Oceanus leak`, `ant CLI`: Agent Arena나 영상/슬라이드에는 등장하지만, Anthropic 공식 제품 발표와 연결되는지 별도 확인이 필요합니다.
- `Google Dreambeans app`: 슬라이드에는 개인화 story card 앱으로 나오지만, 공식 제품 문서 확인 후에만 본문에 올리는 편이 안전합니다.
- `SpaceX IPO`, 특정 회사 valuation, blacklisting, layoffs 수치: 기술 리뷰 핵심과 거리가 있고 날짜 민감도가 높습니다. 필요하면 별도 재확인해야 합니다.
- 모델별 leaderboard 순위: Leaderboard 자체는 확인되더라도, task 구성과 scoring 방식에 따라 해석이 크게 달라집니다. `어느 모델이 최고`라는 결론보다 `agentic evaluation이 중요해지고 있다`는 신호로 다루는 편이 좋습니다.

## 심층리서치 후보

### A. Agent memory와 harness engineering

가장 추천하는 후속 주제입니다. Lev의 5월 말부터 6월 12일까지 흐름이 모두 이 주제로 모입니다. Task Memory Hub, AI_Tech_Review 자동화, OpenProject/Obsidian 연동에도 바로 연결됩니다.

핵심 질문:

- 긴 agent 작업에서 memory는 prompt history, vector store, blackboard, event log 중 어느 형태가 가장 안정적인가?
- harness는 tool registry, sandbox, permission, lifecycle hook, human review를 어떻게 묶어야 하는가?
- context compression과 persistent memory는 서로 보완 관계인가, 대체 관계인가?
- 실제 업무 자동화에서 `agent가 일을 끝냈다`는 판정은 어떻게 남겨야 하는가?

### B. Enterprise data platform agents

Snowflake Cortex Agents와 Databricks Agent Bricks를 비교하면 기업형 agent의 운영 조건이 잘 보입니다.

핵심 질문:

- data warehouse/lakehouse 안의 agent는 일반 SaaS agent와 무엇이 다른가?
- semantic layer, RBAC, row-level policy, audit log, MLflow tracing, cost guardrail은 agent 안전성에 어떤 역할을 하는가?
- 기업 내부 분석/보고/데이터 품질 업무에 어느 쪽이 더 현실적인가?

### C. Diffusion LLM과 local interactive workflow

DiffusionGemma는 모델 구조 자체가 새롭습니다. 단순히 `빠른 모델`로 보기보다, agent UI와 local inference loop에서 latency가 어떤 제품 경험을 바꾸는지 확인할 필요가 있습니다.

핵심 질문:

- text diffusion LLM은 autoregressive LLM과 어떤 작업에서 품질/속도 trade-off가 다른가?
- inline editing, code suggestion, rapid planning loop에서 체감 차이가 있는가?
- local GPU 제약에서 small autoregressive model, speculative decoding, routing과 비교하면 어떤 선택지가 되는가?

### D. Proprietary scientific data as AI moat

Lilly TuneLab은 AI for Science에서 `모델보다 데이터와 실험 네트워크`가 더 큰 자산이 될 수 있음을 보여주는 사례입니다.

핵심 질문:

- proprietary research data를 외부 biotech과 공유하면서도 privacy와 model improvement를 어떻게 설계하는가?
- drug discovery의 TuneLab 모델을 OLED/materials inverse design workflow와 비교할 수 있는가?
- 공개 논문/benchmark만으로는 보이지 않는 domain data moat를 어떻게 평가해야 하는가?

## 오늘의 판단

이번 주 Lev Selector 최신 영상에서 바로 추적할 만한 신기술은 `DiffusionGemma 26B`입니다. 하지만 더 큰 흐름은 `agent memory + harness + enterprise governance + cost control`입니다. 새 모델을 한 번 써보는 것보다, agent가 장시간 작업하면서 상태를 잃지 않고, 비용을 폭발시키지 않고, 조직의 데이터 권한 안에서 실행되게 하는 운영 기술이 더 중요한 검토 대상입니다.

AI_Tech_Review 후속 작업으로는 A안 `Agent memory와 harness engineering`을 먼저 추천합니다. 이미 이 workspace의 작업 방식과 맞닿아 있고, Lev의 최근 4개 주간 업데이트를 한 줄로 연결하는 주제입니다.

## 주요 출처

- Lev Selector YouTube: [channel](https://www.youtube.com/@lev-selector), [2026-06-12 video](https://www.youtube.com/watch?v=zyE4uXQ5hS4), [2026-06-05 video](https://www.youtube.com/watch?v=dR0G4sr9u5A), [2026-05-29 video](https://www.youtube.com/watch?v=na-sQ-g2MAc), [2026-05-22 video](https://www.youtube.com/watch?v=-NqSCfOB8yg)
- Lev Selector GitHub slides: [lselector/seminar](https://github.com/lselector/seminar), [2026-06-12-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-06-12-AI-Updates.pptx), [2026-06-05-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-06-05-AI-Updates.pptx)
- Google: [DiffusionGemma: 4x faster text generation](https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/)
- Microsoft: [Microsoft Agent Framework Version 1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/), [microsoft/agent-framework](https://github.com/microsoft/agent-framework)
- Snowflake: [Cortex Agents documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents), [Snowflake Cortex AI](https://www.snowflake.com/en/product/features/cortex/)
- Databricks: [Agent Bricks](https://www.databricks.com/product/artificial-intelligence/agent-bricks)
- Lilly: [Lilly TuneLab announcement](https://investor.lilly.com/news-releases/news-release-details/lilly-launches-tunelab-platform-give-biotechnology-companies)
- Agent evaluation: [Agent Arena](https://arena.ai/leaderboard/agent), [Factory Agent Arena methodology](https://docs.factory.ai/benchmarks/agent-arena), [Harvey Legal Agent Benchmark](https://www.harvey.ai/blog/introducing-harveys-legal-agent-benchmark)
- Context compression: [Headroom GitHub repository](https://github.com/chopratejas/headroom)

## 작업 로그

- YouTube RSS에서 최신 영상이 2026-06-12 `Exciting AI Updates Weekly - June 12, 2026`임을 확인했습니다.
- `yt-dlp --flat-playlist --dump-single-json --playlist-end 10`으로 최근 영상 목록을 확인했습니다.
- `yt-dlp --dump-single-json --skip-download`로 2026-06-12, 2026-06-05, 2026-05-29, 2026-05-22 영상의 제목, 날짜, 설명, 챕터를 확인했습니다.
- GitHub API `https://api.github.com/repos/lselector/seminar/contents/2026`로 최신 AI Updates slide가 2026-06-12임을 확인했습니다.
- 2026-06-12, 2026-06-05, 2026-05-29, 2026-05-22 PPTX를 system temp 아래에 내려받아 `ppt/slides/slide*.xml` 텍스트를 추출해 검토했습니다.
- Skywork Search 스킬로 YouTube/GitHub 보조 검색을 실행했지만, YouTube 쪽은 일반 페이지 snippet만 반환되어 최종 근거는 RSS, `yt-dlp`, GitHub API, 공식 문서 중심으로 정리했습니다.
