---
title: 2026-05-18 Lev Selector Recent Updates
date: 2026-05-18
topic_slug: lev-selector-recent-updates
related_topic_folder: 2026-05-09_ai-updates-weekly
tags:
  - daily-review
  - ai-updates-weekly
  - lev-selector
  - agents
  - rag
  - enterprise-ai
---

# 2026-05-18 Lev Selector 최근 업데이트 메모

## 오늘 대화 요약
- 2026년 5월 18일 기준으로 Lev Selector 채널의 최신 주간 AI 업데이트는 2026년 5월 15일 공개된 [Exciting AI Updates Weekly - May 15, 2026](https://www.youtube.com/watch?v=5bgrHdi8mcE)입니다.
- GitHub 슬라이드 저장소에서도 최신 `AI Updates` 파일은 [2026-05-15-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-05-15-AI-Updates.pptx)로 확인했습니다.
- 이번 주 신호는 `chatbot`에서 `digital employee`, 즉 여러 도구를 오래 붙잡고 실행하는 개인/업무용 에이전트로 관심이 이동했다는 점입니다.

## 확인한 최신 자료

| 날짜 | 자료 | 확인 내용 |
|---|---|---|
| 2026-05-15 | [YouTube 영상](https://www.youtube.com/watch?v=5bgrHdi8mcE) | 채널 RSS와 `yt-dlp` 메타데이터 기준 최신 주간 영상입니다. 영상 설명에는 전체 챕터, 요약, Takeaways가 포함되어 있습니다. |
| 2026-05-15 | [GitHub PPTX](https://github.com/lselector/seminar/blob/master/2026/2026-05-15-AI-Updates.pptx) | `lselector/seminar` 저장소의 최신 AI Updates 슬라이드입니다. GitHub API 기준 2026년 폴더 최신 커밋은 2026-05-15에 기록되었습니다. |
| 2026-05-08 | [YouTube 영상](https://www.youtube.com/watch?v=yDfupTHYshQ) / [GitHub PPTX](https://github.com/lselector/seminar/blob/master/2026/2026-05-08-AI-Updates.pptx) | 직전 주 흐름은 `harness engineering`, `multi-agent orchestration`, `Claude/Codex workflow`, `agentic engineering` 중심이었습니다. |
| 2026-05-01 | [YouTube 영상](https://www.youtube.com/watch?v=Z-Qvqfv5760) / [GitHub PPTX](https://github.com/lselector/seminar/blob/master/2026/2026-05-01-AI-Updates.pptx) | `personal agent OS`, `AI harness`, 중국 오픈 모델, Claude Code workflow, job-market advice가 중심이었습니다. |

## 핵심 해석

최근 3주를 이어 보면 Lev Selector의 관심은 모델 이름 자체보다 모델을 실제 업무에 오래 묶어두는 실행 환경으로 옮겨가고 있습니다. 2026년 5월 1일 영상에서는 `personal agent OS`와 `agentic harness`가 중심이었고, 5월 8일에는 `harness engineering now matters more than the model itself`라는 문장으로 더 노골화되었습니다. 5월 15일 업데이트에서는 이 흐름이 `digital employee`라는 표현으로 정리됩니다.

여기서 `digital employee`는 사람처럼 고용된 존재라기보다, 이메일, 브라우저, 파일, CRM, 회의, 코드 배포 같은 도구를 연결해 다단계 업무를 끝까지 처리하려는 에이전트 제품군을 가리키는 표현에 가깝습니다. Lev Selector는 Genspark Claw, OpenClaw, Hermes Agent, holaOS, Pokee.ai, Pi.dev, Pareto Code 등을 이 범주에서 묶고 있습니다. 다만 각 제품의 사용량, 스타 수, 매출, 성능 주장은 변동이 크기 때문에 원자료 확인 없이는 결론으로 쓰기 어렵습니다.

## 2026-05-15 업데이트에서 눈에 띄는 항목

### 1. Claude 계열은 `에이전트 운영 화면`과 `업무 패키지`를 넓히고 있습니다
- [Claude Code Agent View](https://claude.com/blog/agent-view-in-claude-code)는 2026년 5월 11일 Anthropic이 공개한 기능입니다. 여러 Claude Code 세션을 한 화면에서 보고, `/bg`로 백그라운드화하고, 입력이 필요한 세션과 진행 중인 세션을 구분하는 방향입니다.
- [Claude for Small Business](https://www.anthropic.com/news/claude-for-small-business?hsLang=en)는 2026년 5월 13일 공개되었습니다. QuickBooks, PayPal, HubSpot, Canva, Docusign, Google Workspace, Microsoft 365 같은 도구 안에서 Claude를 쓰게 하는 패키지입니다.
- [Agents for financial services](https://www.anthropic.com/news/finance-agents?pubDate=20260206)는 2026년 5월 5일 공개되었습니다. pitchbook, KYC, month-end close 같은 금융 업무용 agent template 10개를 Claude Cowork/Claude Code plugin과 Claude Managed Agents cookbook으로 제공합니다.
- 해석: Anthropic의 방향은 `모델 API` 판매보다 더 위에 있는 workflow package, plugin, connector, managed agent 운영면을 잡는 쪽입니다. 이 부분은 `하니스 엔지니어링` 관점에서 더 볼 만합니다.

### 2. Meta Muse Spark와 OpenAI Realtime Voice는 `모델 자체의 효율`과 `음성 인터페이스` 신호입니다
- [Meta Muse Spark](https://about.fb.com/news/2026/04/introducing-muse-spark-meta-superintelligence-labs/)는 2026년 4월 8일 발표되고 5월 12일 업데이트되었습니다. Meta는 Muse Spark를 Meta AI 앱, 웹, WhatsApp, Instagram, Facebook, Messenger, AI glasses로 확대한다고 설명합니다.
- [OpenAI Realtime voice models](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)는 2026년 5월 7일 발표되었습니다. GPT-Realtime-2, GPT-Realtime-Translate, GPT-Realtime-Whisper가 핵심이며, GPT-Realtime-2는 128K context와 병렬 tool call을 포함합니다.
- 해석: Lev Selector는 이 둘을 단순 모델 업데이트가 아니라 `더 많은 사용 장면을 AI 인터페이스로 흡수하는 신호`로 다룹니다. Meta는 생활형 앱/안경 쪽, OpenAI는 실시간 음성 agent API 쪽입니다.

### 3. RAG 논의는 vector DB 일변도에서 `검색, graph, agent loop` 조합으로 돌아오고 있습니다
- 5월 15일 슬라이드는 `Agentic RAG`, `TGS-RAG`, Meta의 [SIRA](https://github.com/facebookresearch/sira)를 함께 다룹니다.
- SIRA 저장소는 BM25 retrieval을 LLM 기반 문서/쿼리 확장과 reranking으로 강화하는 multi-stage retrieval pipeline으로 설명합니다.
- 해석: 최근 RAG 논의의 재미있는 지점은 `vector search를 더 크게`가 아니라, private documentation에서 재현 가능한 검색 절차, line-level citation, graph/node 복구, BM25 재평가 같은 쪽입니다. 사내 문서 검색과 기술 검토 자동화에는 이 흐름이 꽤 직접적으로 닿습니다.

### 4. Hallucination 논의는 `평가 종류`를 먼저 나누어야 합니다
- Lev Selector의 슬라이드는 summarization hallucination과 open-knowledge/factual recall hallucination을 구분합니다.
- Vectara류 요약 벤치마크와 AA-Omniscience류 사실 회상 벤치마크는 같은 숫자로 비교하면 안 됩니다.
- 실무적으로는 `I do not know` 허용, 근거 인용 강제, retrieval quote 확인, reranker, LLM-as-judge, multi-model consensus 같은 방식을 제안합니다.
- 주의: 슬라이드의 모델별 환각률 표는 여러 벤치마크와 추정치를 섞고 있으므로, 보고서 결론으로 쓰려면 각 수치를 별도로 재검증해야 합니다.

### 5. `End of Chats` 서사는 강하지만, 그대로 받아쓰기보다는 제품 설계 질문으로 바꾸어 읽는 편이 좋습니다
- 5월 15일 영상의 큰 문장은 `Chats are dead. Long live agent.`입니다.
- 하지만 실제 업무에서는 대화형 인터페이스가 사라진다기보다, 대화가 plan, tool call, background session, approval, audit log로 확장되는 쪽에 가깝습니다.
- 그래서 우리 쪽 질문은 `채팅이 끝났는가`보다 `어떤 업무를 background agent에게 맡겨도 되는가`, `어디에서 사람이 승인해야 하는가`, `실행 기록과 근거를 어떻게 남길 것인가`로 두는 편이 좋습니다.

## 공식 확인과 주의가 필요한 주장

| 구분 | 항목 | 상태 |
|---|---|---|
| 공식 확인 | Claude Code Agent View | Anthropic 공식 블로그에서 확인했습니다. |
| 공식 확인 | Claude for Small Business | Anthropic 공식 발표에서 확인했습니다. |
| 공식 확인 | Claude financial services agents | Anthropic 공식 발표와 GitHub 저장소에서 확인했습니다. |
| 공식 확인 | Meta Muse Spark | Meta 공식 발표에서 확인했습니다. |
| 공식 확인 | OpenAI Realtime voice models | OpenAI 공식 발표에서 확인했습니다. |
| 공식 확인 | Ramp AI Index의 Anthropic/OpenAI business adoption 수치 | [Ramp May 2026 AI Index](https://ramp.com/leading-indicators/ai-index-may-2026)는 Anthropic 34.4%, OpenAI 32.3%라고 제시합니다. 표본과 측정 방식은 별도 해석이 필요합니다. |
| 추가 검증 필요 | `OpenClaw` 재허용과 월별 credit pool | 여러 보도와 개발자 커뮤니티에서 확인되지만, 최종 보고서에는 Anthropic의 공식 개발자 공지 원문을 다시 확인하는 편이 안전합니다. |
| 추가 검증 필요 | Hermes/OpenClaw 사용량, GitHub star, product ARR | 숫자가 빠르게 바뀌고 일부는 커뮤니티/마케팅 자료 기반입니다. |
| 추가 검증 필요 | Hallucination 모델별 수치 | benchmark 정의와 측정 시점이 다릅니다. 결론화하려면 원 벤치마크별로 따로 보아야 합니다. |
| 추가 검증 필요 | 채용/해고 수치와 `companies are re-hiring developers` | 영상이 여러 2차 자료를 요약한 영역입니다. 노동시장 리포트로 쓰려면 별도 자료가 필요합니다. |

## 다음 심층 검토 후보

1. **Digital Employee / Personal Agent OS**
   - Claude Code, OpenClaw, Hermes, Genspark Claw, holaOS, Pokee.ai를 `memory`, `permission`, `tool connector`, `approval`, `audit log`, `background execution` 기준으로 비교하면 좋습니다.

2. **RAG의 재정렬: vector DB 이후의 private documentation search**
   - Agentic RAG, SIRA, GraphRAG/TGS-RAG를 비교해 사내 문서 검색 자동화에 어떤 구조가 맞는지 볼 수 있습니다.

3. **Anthropic의 vertical agent package 전략**
   - 금융, 법무, SMB, Microsoft 365, Agent View를 하나의 제품 전략으로 묶어 보면 `model company`가 `workflow company`로 확장되는 흐름을 볼 수 있습니다.

4. **Hallucination benchmark 분해**
   - Summarization, factual recall, citation faithfulness, tool-grounded QA를 나누고, OLED/소재/특허/시장 리포트 자동화에 어떤 평가가 필요한지 정리할 수 있습니다.

## 상세 리뷰 방향 선정

### 후보 A. Digital Employee / Personal Agent OS: 실행 하네스의 제품화

이 방향이 가장 넓고, 이번 Lev Selector 업데이트의 중심 흐름과도 가장 잘 맞습니다. 2026년 5월 1일 영상은 `personal agent OS`와 `agentic harness`를, 5월 8일 영상은 `harness engineering now matters more than the model itself`를, 5월 15일 영상은 `digital employee`를 전면에 둡니다. 세 주를 이어 읽으면 단순히 새 모델이 많이 나왔다는 이야기가 아니라, 모델을 업무 안에 오래 머물게 하는 운영 계층이 제품 경쟁의 중심으로 올라왔다는 흐름이 보입니다.

이 리뷰의 장점은 공식 출처와 시장 사례를 함께 묶을 수 있다는 점입니다. Anthropic의 [Agent View](https://claude.com/blog/agent-view-in-claude-code), [Claude for Small Business](https://www.anthropic.com/news/claude-for-small-business?hsLang=en), [financial services agents](https://www.anthropic.com/news/finance-agents?pubDate=20260206)는 모두 공식 발표가 있어 근거가 비교적 단단합니다. 여기에 Genspark Claw, Hermes Agent, OpenClaw, holaOS, Pokee.ai 같은 사례를 `시장 내러티브`로 붙이면, `AI employee`라는 말이 실제 제품 구조에서는 무엇을 뜻하는지 분해할 수 있습니다.

다만 주의할 점도 분명합니다. `AI employee`라는 표현은 마케팅 언어가 섞여 있습니다. 제품별 매출, 사용량, GitHub star, agent ranking 같은 숫자는 빠르게 바뀌고, 일부는 커뮤니티 주장이나 2차 요약을 거친 자료입니다. 따라서 이 방향으로 갈 경우 리뷰의 중심 문장은 `AI 직원 시대가 왔다`가 아니라 `대화형 AI가 실행 하네스와 결합하면서 업무 도구 안에서 지속 실행되는 제품으로 바뀌고 있다`가 되어야 합니다.

추천 제목 후보:
- `AI 직원이라는 말 뒤에 있는 것: 에이전트 실행 하네스의 제품화`
- `채팅 이후의 AI 업무 도구: Digital Employee를 하니스 관점에서 읽기`
- `모델보다 오래 남는 것은 실행 환경입니다: Personal Agent OS와 업무용 AI 에이전트`

핵심 질문:
- `AI employee`라고 불리는 제품들은 실제로 어떤 구성요소를 공유하는가?
- memory, connector, permission, approval, audit log, background session은 왜 중요해졌는가?
- Anthropic, OpenAI, Meta, Genspark, open-source agent 생태계는 서로 다른 경로로 같은 문제를 풀고 있는가?
- 사내 업무 자동화나 AI_Tech_Review 같은 리포트 자동화에는 어떤 구조가 바로 적용 가능한가?

### 후보 B. RAG의 재정렬: vector DB 이후의 private documentation search

이 방향은 기술적으로 가장 선명합니다. 5월 15일 업데이트는 `Agentic RAG`, `TGS-RAG`, Meta의 [SIRA](https://github.com/facebookresearch/sira)를 함께 다루며, 검색 기반 RAG가 다시 세분화되는 흐름을 보여줍니다. [TGS-RAG 논문](https://arxiv.org/abs/2605.05643)은 text search와 knowledge graph를 양방향으로 검증/보완하는 방식을 제안하고, SIRA는 BM25 기반 lexical retrieval을 LLM 기반 query/document expansion과 reranking으로 강화하는 쪽입니다.

이 주제는 AI_Tech_Review의 실제 사용처와도 잘 맞습니다. 소재/디스플레이/특허/논문 리뷰에서는 `비슷한 문장을 잘 찾는 것`보다 `어떤 파일의 어느 줄이 주장을 뒷받침하는지`가 훨씬 중요합니다. 그래서 agentic RAG, ripgrep 기반 검색, line-level citation, graph-augmented retrieval을 비교하면 실무적인 깊이가 나옵니다.

다만 Lev Selector 업데이트 전체를 설명하기에는 범위가 좁습니다. 별도 심층 기술 리뷰로는 좋지만, 이번 `최근 업데이트`의 대표 주제로 삼기보다는 후보 A 안의 기술 기반 섹션으로 넣는 편이 자연스럽습니다.

### 후보 C. Anthropic의 vertical agent package 전략

Anthropic 쪽만 떼어 보면 매우 좋은 vendor strategy 리뷰가 됩니다. 2026년 5월 Anthropic은 Agent View, Small Business, financial services agents를 거의 연속적으로 공개했습니다. 이는 `Claude라는 모델`보다 `업무별 패키지`, `connector`, `managed agents`, `plugin/skill`이 중요해지고 있음을 보여줍니다.

이 방향의 장점은 공식 근거가 강하다는 점입니다. 반대로 약점은 리뷰가 Anthropic 중심으로 좁아져 Lev Selector 업데이트의 넓은 시장 감각이 줄어든다는 점입니다. 후보 A의 `대표 사례`로 Anthropic을 두고, 별도 박스에서 `Anthropic은 왜 vertical package로 가는가`를 설명하는 구성이 더 좋아 보입니다.

### 후보 D. Hallucination benchmark 분해

이 주제는 신뢰성 리뷰로 만들면 가치가 높습니다. Lev Selector가 정리한 것처럼 summarization hallucination, open-knowledge factual recall, citation faithfulness, tool-grounded QA는 서로 다른 평가입니다. 같은 `환각률`이라는 단어로 묶으면 모델 선택이나 사내 도입 판단을 잘못할 수 있습니다.

다만 이 주제는 원 벤치마크를 다시 읽어야 하므로 별도의 검증 작업이 큽니다. 이번 업데이트 리뷰의 본론으로 삼기보다는, `digital employee를 업무에 투입하려면 어떤 검증 계층이 필요한가`라는 섹션에 넣는 것이 좋습니다.

### 후보 E. Realtime Voice와 consumer agent interface

[OpenAI Realtime voice models](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)와 [Meta Muse Spark](https://about.fb.com/news/2026/04/introducing-muse-spark-meta-superintelligence-labs-first-model-built-to-prioritize-people/)는 AI가 텍스트 입력창 밖으로 나오는 흐름을 보여줍니다. OpenAI는 GPT-Realtime-2, Translate, Whisper를 API로 제공하고, Meta는 Muse Spark를 Meta AI 앱과 WhatsApp, Instagram, Facebook, Messenger, Threads, AI glasses로 확장한다고 설명합니다.

이 방향은 흥미롭지만, Lev Selector의 5월 업데이트에서 가장 강한 흐름인 업무용 agent harness와는 조금 떨어져 있습니다. `AI employee` 리뷰 안에서 `인터페이스는 채팅창에서 음성/앱/안경으로 확장된다`는 보조 축으로 두는 편이 좋습니다.

## 선정안

이번 상세 리뷰의 주제는 **`Digital Employee라는 말 뒤에 있는 에이전트 실행 하네스`**로 잡는 것이 가장 좋겠습니다.

선정 이유는 세 가지입니다.

첫째, Lev Selector의 최근 3주 업데이트를 가장 자연스럽게 묶습니다. 2026년 5월 1일의 `personal agent OS`, 5월 8일의 `harness engineering`, 5월 15일의 `digital employee`가 같은 질문으로 이어집니다.

둘째, 공식 출처가 충분합니다. Anthropic, OpenAI, Meta, Genspark, SIRA/TGS-RAG를 각각 `업무 패키지`, `실시간 인터페이스`, `consumer distribution`, `AI employee 마케팅`, `knowledge substrate`로 분리해 다룰 수 있습니다.

셋째, 우리 워크스페이스의 관심사와 바로 연결됩니다. AI_Tech_Review 자체도 source intake, deep research, HTML rendering, Skywork, Obsidian, OpenProject를 잇는 실행 하네스입니다. 따라서 이 리뷰는 외부 시장 분석에 그치지 않고, `우리의 리포트 자동화/에이전트 운영 설계에 무엇을 가져올 것인가`까지 이어질 수 있습니다.

## 추천 리뷰 구조

1. **도입: AI 직원이라는 말이 왜 다시 등장했는가**
   - Chatbot에서 agent로 이동한다는 표현을 그대로 받아쓰기보다, 사용자가 기대하는 일이 `답변`에서 `업무 완료`로 바뀌었다는 점을 설명합니다.

2. **Digital Employee를 구성요소로 분해하기**
   - memory, connector, permission, approval, audit log, background execution, workflow template, model routing을 표로 정리합니다.

3. **Anthropic은 업무 패키지로 간다**
   - Agent View, Small Business, financial services agents를 공식 발표 중심으로 정리합니다.

4. **OpenAI와 Meta는 인터페이스와 배포면을 넓힌다**
   - Realtime voice models와 Muse Spark를 agent interface/distribution 관점에서 봅니다.

5. **RAG와 검색은 agent의 지식 기반이 된다**
   - SIRA, TGS-RAG, Agentic RAG를 사내 문서 검색과 연결합니다.

6. **검증 없이는 AI 직원이 아니라 위험한 자동화다**
   - Hallucination benchmark의 종류, line-level citation, LLM-as-judge, human approval을 다룹니다.

7. **우리에게 남는 설계 질문**
   - 어떤 업무는 background agent에게 맡기고, 어떤 업무는 사람 승인 없이는 넘기면 안 되는지 정리합니다.

## 한 줄 결론 초안

이번 Lev Selector 업데이트에서 오래 남는 신호는 `AI 직원이 곧 사람을 대체한다`는 문장이 아닙니다. 더 중요한 변화는 모델이 메모리, 도구 연결, 권한, 승인, 검증 절차를 갖춘 실행 환경 안으로 들어오면서, AI 제품의 경쟁축이 `좋은 답변`에서 `안전하게 일을 끝내는 운영 하네스`로 이동하고 있다는 점입니다.

## 참고자료
- Lev Selector YouTube channel RSS: `https://www.youtube.com/feeds/videos.xml?channel_id=UCA4GfsgbI09cLzonTKryC6g`
- Lev Selector, [Exciting AI Updates Weekly - May 15, 2026](https://www.youtube.com/watch?v=5bgrHdi8mcE)
- Lev Selector, [Exciting AI Updates Weekly - May 8, 2026](https://www.youtube.com/watch?v=yDfupTHYshQ)
- Lev Selector, [Exciting AI Updates Weekly - May 1, 2026](https://www.youtube.com/watch?v=Z-Qvqfv5760)
- lselector/seminar, [2026-05-15-AI-Updates.pptx](https://github.com/lselector/seminar/blob/master/2026/2026-05-15-AI-Updates.pptx)
- Anthropic, [Agent view in Claude Code](https://claude.com/blog/agent-view-in-claude-code)
- Anthropic, [Introducing Claude for Small Business](https://www.anthropic.com/news/claude-for-small-business?hsLang=en)
- Anthropic, [Agents for financial services](https://www.anthropic.com/news/finance-agents?pubDate=20260206)
- Anthropic GitHub, [financial-services](https://github.com/anthropics/financial-services)
- Meta, [Introducing Muse Spark](https://about.fb.com/news/2026/04/introducing-muse-spark-meta-superintelligence-labs/)
- OpenAI, [Advancing voice intelligence with new models in the API](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)
- Ramp, [Anthropic beats OpenAI on business adoption](https://ramp.com/leading-indicators/ai-index-may-2026)
- Meta Research, [SIRA GitHub repository](https://github.com/facebookresearch/sira)
