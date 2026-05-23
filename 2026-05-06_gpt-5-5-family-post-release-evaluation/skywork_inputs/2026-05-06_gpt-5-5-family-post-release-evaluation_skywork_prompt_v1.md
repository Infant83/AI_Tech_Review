---
title: Skywork prompt v1 - GPT-5.5 family post-release evaluation
date: 2026-05-07
template: LGD_Template.pptx
language: ko
status: ready-for-skywork
---

# Skywork Prompt v1

업로드된 자료와 `LGD_Template.pptx`를 기반으로 한국어 PowerPoint deck을 생성하라.

## 기본 설정

- 프로젝트명: `GPT-5.5 기술동향 리포트`
- 청중: AI researchers, ML engineers, product leaders, executives
- 목적: GPT-5.5, GPT-5.5 Pro, GPT-5.5 Instant의 실제 변화, 성능 근거, Hallucination과 사실성 리스크, 도입 판단을 한 번에 이해시키는 기술 리뷰 deck
- 권장 분량: 15장
- 비율: 16:9
- 기본 템플릿: `LGD_Template.pptx`
- 작성자: `김현중 with Codex Agent | AI Governance Team`
- 작성일: `2026-05-07`
- 톤: 친근하지만 기술적으로 엄격한 내부 리뷰 스타일
- 문체: 과장된 marketing tone 금지. "final review"라는 표현은 제목이나 본문 표면에 쓰지 말고, 보고서 성격이 드러나는 `기술동향 리포트`, `기술 리뷰`, `도입 판단` 중심으로 쓴다.

## 업로드해야 할 source pack

1. `C:\Users\angpa\.codex\skills\skywork-ppt-workflow\assets\LGD_Template.pptx`
2. `reports/2026-05-06_gpt-5-5-family-post-release-evaluation_deepresearch.md`
3. `reports/2026-05-06_gpt-5-5-family-post-release-evaluation_final_review.md`
4. `reports/2026-05-06_gpt-5-5-family-post-release-evaluation_memo.md`
5. `artifacts/final_review/figures/gpt55_variant_map.svg`
6. `artifacts/final_review/figures/gpt55_benchmark_surface.svg`
7. `artifacts/final_review/figures/gpt55_hallucination_methods.svg`

## 소스 우선순위

1. OpenAI official release, system cards, Help Center, API docs, pricing docs
2. Artificial Analysis, Scale MCP Atlas, Scale SWE-Bench Pro, SWE-Bench Pro arXiv, UK AISI
3. Axios/TechCrunch 등 secondary commentary는 field framing에만 사용

정량 수치와 현재 제품 사실은 업로드된 source pack에 있는 링크가 확인되는 경우에만 사용하라. 출처가 불명확한 수치, architecture 추정, 내부 training claim은 추가하지 말라.

## 전체 서사

GPT-5.5 계열은 하나의 모델명으로 읽으면 판단이 거칠어진다. Thinking은 긴 코드 작업, 터미널 작업, 웹 탐색, 긴 문서 기반 조사처럼 여러 단계를 이어 가는 작업 수행 모델이다. Pro는 같은 기반 모델에 더 많은 계산 시간을 배정해 품질을 높이는 실행 방식이고, Instant는 ChatGPT 기본 응답 경험을 바꾸는 배포 업데이트다. 성능 향상은 코드 작업, 도구 사용, 컴퓨터 조작, 긴 문맥 처리에서 넓게 보이지만 벤치마크별 선두 모델은 갈린다. Hallucination은 일부 사실성 평가에서 줄었지만, 모르는 질문에서 멈추는 능력과 불확실성 표시는 따로 검증해야 한다.

## Slide outline

### CH00. Cover

- Title: `GPT-5.5 기술동향 리포트`
- Subtitle: `긴 작업 성능과 Hallucination 리스크를 함께 읽기`
- Small footer: `김현중 with Codex Agent | AI Governance Team | 2026-05-07`
- Visual: clean model-family map motif, not decorative abstract gradient

### CH01. Executive takeaways

- 5 bullets only:
  - GPT-5.5 release: 2026-04-23; Instant release: 2026-05-05
  - Thinking, Pro, Instant는 서로 다른 평가 object
  - strongest evidence: agentic execution, tool use, long-context work
  - mixed evidence: SWE-Bench Pro and MCP Atlas peer comparisons
  - factuality improved, calibration still needs in-house audit
- Use `Fact / Inference / Caution` badges.

### CH02. Variant map

- Use or redraw `gpt55_variant_map.svg`.
- Show:
  - GPT-5.5 Thinking: 긴 작업 수행 모델
  - GPT-5.5 Pro: 같은 기반 모델 + 더 많은 계산 시간
  - GPT-5.5 Instant: ChatGPT 기본 모델, 비교 기준은 GPT-5.3 Instant
- Add small annotation: `GPT-5.4 Instant라는 공식 baseline은 없다.`

### CH03. Release timeline

- Timeline:
  - 2026-04-23 GPT-5.5 release
  - 2026-04-24 API/safeguard update
  - 2026-04-30 UK AISI cyber evaluation
  - 2026-05-05 GPT-5.5 Instant release
  - 2026-05-06 Help Center confirms default/context/tool support
- Keep dense but readable.

### CH04. Benchmark surface

- Use or redraw `gpt55_benchmark_surface.svg`.
- Highlight:
  - Terminal-Bench 2.0: 82.7 vs 75.1
  - Graphwalks BFS 1M: 45.4 vs 9.4
  - MRCR 512K-1M: 74.0 vs 36.6
  - MCP Atlas: 75.3 vs 70.6, but Claude/Gemini higher
  - SWE-Bench Pro: 58.6 vs 57.7, but Claude Opus 4.7 at 64.3

### CH05. 코드 작업과 에이전트형 실행

- One dense slide:
  - Terminal-Bench, SWE-Bench Pro, Expert-SWE
  - Show what each benchmark actually tests.
  - Explain why `best coding model` depends on terminal workflow vs GitHub issue resolution vs harness.
- Include caveat: OpenAI table uses xhigh research environment. 단, 슬라이드 문구는 `xhigh 연구 환경`처럼 자연스럽게 쓴다.

### CH06. 도구 사용과 컴퓨터 조작

- Compare BrowseComp, MCP Atlas, OSWorld, Toolathlon, Tau2-bench Telecom.
- Layout: source comparison board.
- Make the takeaway:
  - GPT-5.5 improves over GPT-5.4.
  - External MCP Atlas does not make GPT-5.5 absolute leader.
  - 도구 표면 설계와 평가 방식이 결과에 영향을 준다.

### CH07. 긴 문맥 처리

- Visual: context ladder.
- Show Graphwalks and MRCR examples.
- Point:
  - Long-context capacity improved.
  - Retrieval design and citation verification remain necessary.

### CH08. 비용, 지연 시간, 추론 강도

- Model-selection economics slide.
- Use:
  - `gpt-5.5`: $5 input / $30 output per 1M tokens
  - `gpt-5.5-pro`: $30 input / $180 output
  - `gpt-5.4`: $2.50 input / $15 output
  - Artificial Analysis: about 40% fewer output tokens on its Index run
- Caveat:
  - effective cost = token price + retries + review time + latency.

### CH09. Hallucination methods

- Use or redraw `gpt55_hallucination_methods.svg`.
- Make the core distinction:
  - OpenAI Instant high-stakes: hallucinated claims down 52.5%
  - OpenAI user-flagged failures: inaccurate claims down 37.3%
  - Artificial Analysis AA-Omniscience: GPT-5.5 xhigh hallucination rate 86%
- Add label: `These are different evals, not interchangeable production rates.`

### CH10. 사실성 vs 불확실성 표시

- Use a 2x2:
  - knows and answers
  - knows but under-explains
  - does not know and abstains
  - does not know and guesses
- Position GPT-5.5 evidence:
  - more knowledge and better internal factuality signals
  - unresolved answer-when-uncertain risk
- Make this slide practical for evaluator teams.

### CH11. Safety and cyber capability

- Use UK AISI and OpenAI system card.
- Explain:
  - GPT-5.5 treated as High capability in Cybersecurity and Biological/Chemical domains
  - UK AISI sees long-horizon cyber capability rising
  - defensive value and misuse risk move together
- Include operational controls: identity, scope, sandbox, approval, logging.

### CH12. Use-case map

- Matrix:
  - Daily assistant: GPT-5.5 Instant
  - Coding agent: GPT-5.5 medium/high
  - Hard review: GPT-5.5 Pro
  - Customer workflow: evaluate GPT-5.5 vs Instant
  - High-stakes factual domain: retrieval + review + calibration eval
  - Bulk extraction: smaller model first

### CH13. 배치 전 점검표

- Checklist:
  - variant and effort recorded
  - tool access and side effects scoped
  - citations and provenance required
  - abstention allowed and rewarded
  - production drift monitored
  - irreversible actions gated
  - human review for high-stakes domains

### CH14. 경영진용 한 장 요약

- Summarize for executives:
  - what changed
  - what is decision-relevant
  - what should be piloted first
  - what should not be overclaimed
- End with:
  - `GPT-5.5는 더 많은 작업을 맡길 수 있는 모델입니다. 따라서 더 넓은 권한을 주기 전에 기록 체계, 근거 검증, 도구 범위, 사람 승인, 되돌리기 경로를 먼저 갖추는 편이 안전합니다.`

## Visual and layout policy

- Use LGD template rhythm and white-grid corporate style.
- Prefer dense technical briefing over sparse marketing deck.
- Use small dark-green inline annotations for definitions and caveats.
- Use small dark-gray source labels near the evidence, not only at the end.
- Avoid large decorative hero-style slides after the cover.
- Avoid generic AI brain images, robot hands, glowing network backgrounds, and meaningless gradients.
- Use the provided SVG figures as visual anchors; redraw them only if the deck style requires it.
- Tables should be compact and readable. If a table is too wide, split it into two slides.

## Keep rules

- Separate `Fact`, `Inference`, and `Caution`.
- Preserve exact dates.
- Distinguish model-level change, compute setting, product-layer change, prompting guidance, safety-policy change.
- Mention when benchmark rows are not like-for-like.
- Make hallucination methodology explicit before showing any hallucination number.
- Use Korean prose that sounds like a friendly internal technical reviewer.
- 영문 기술용어는 필요한 경우에만 남긴다. `coding`은 `코드 작업`, `terminal task`는 `터미널 작업`, `browsing`은 `웹 탐색`, `long-context research`는 `긴 문서 기반 조사`, `underlying model`은 `기반 모델`, `tool access`는 `도구 접근 권한`, `human review`는 `사람 검토`, `factuality`는 `사실성`으로 쓴다. Hallucination, RAG처럼 현장에서 널리 쓰이는 용어는 유지하되 짧게 뜻을 풀어 준다.
- 근거 출처는 본문 또는 각주처럼 보이게 처리한다. 예: `[OpenAI 발표]`, `[Artificial Analysis 분석]`. 출처명은 일반 명사처럼 흘려 쓰지 말고 링크나 작은 source label로 표시한다.
- 강조는 한 슬라이드에 1-2개만 사용한다. 독자가 먼저 읽어야 하는 판단, 수치, 위험 문구에만 굵게 표시한다.
- 보고서 작성 정보는 마지막 또는 부록 슬라이드에 2-3줄로만 둔다: `작성자: 김현중 with Codex Agent | AI Governance Team`, `작성일: 2026-05-07`, `작성 방식: 공식 발표, 시스템 카드, 벤치마크, 독립 평가를 정리한 deepresearch 기반`.

## Avoid rules

- Do not invent architecture details.
- Do not claim hallucination is solved.
- Do not present targeted hallucination evals as production prevalence.
- Do not turn GPT-5.5 Pro into a separate disclosed architecture.
- Do not flatten the external disagreement around SWE-Bench Pro and MCP Atlas.
- Do not add unsourced benchmark numbers.

## Required source footer examples

- `Source: OpenAI, Introducing GPT-5.5, 2026-04-23`
- `Source: OpenAI Deployment Safety Hub, GPT-5.5 System Card, 2026-04-23`
- `Source: Artificial Analysis, 2026-04-23`
- `Source: Scale Labs MCP Atlas, April 2026 update`
- `Source: UK AISI, 2026-04-30`

이 기준으로 전체 deck을 생성하라.
