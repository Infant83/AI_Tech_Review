---
title: 2026-03-06 AI Updates Weekly Deep Research
date: 2026-03-09
tags:
  - ai-review
  - deepresearch
  - agents
  - model-market
  - enterprise-ai
  - ai-governance
---

# 2026-03-06 AI Updates Weekly Deep Research

## Scope
이 문서는 Lev Selector의 2026년 3월 6일 AI 업데이트 영상과 슬라이드 덱을 출발점으로 삼되, 영상에 나온 모든 항목을 일대일 팩트체크하는 대신 실제로 중요한 축을 재구성해 심층적으로 정리한 보고서다. 기준 시점은 2026년 3월 6일부터 2026년 3월 9일까지다.

## Executive Synthesis
- 이번 주의 진짜 뉴스는 개별 모델 발표가 아니라 `범용 에이전트 운영층`의 부상이다.
- 모델 격차는 여전히 중요하지만, 실사용 경쟁력은 점점 `harness`, 메모리, 권한 통제, 스케줄링, 원격 제어, 작업 분해 방식에서 결정된다.
- 에이전트 생태계는 코딩 도구에서 데스크톱 자동화, 문서 작업, 메시징, 브라우저, 테스트 자동화까지 빠르게 확장 중이다.
- 엔터프라이즈의 유효한 경제성은 "최고 모델 하나"가 아니라 "상위 계획 + 저비용 실행 모델" 오케스트레이션에서 나온다.
- 안전과 거버넌스는 부차적 이슈가 아니다. 국방, 규제, 기업 경쟁이 겹치면서 모델 사용의 경계선 자체가 제품 전략 변수로 변하고 있다.

## 1. SaaS에서 Agent Operating Layer로 중심축이 이동한다

영상의 가장 큰 주장인 `skills instead of SaaS`는 자극적인 슬로건처럼 보이지만, 그 밑에 있는 구조 변화는 실제다. 슬라이드 덱은 Claude Code의 memory, remote control, co-work scheduling, Anthropic Skill Creator, Alibaba CoPaw, OpenClaw 계열, Accomplish, CodeBuff를 한 줄로 묶는다. 공통점은 모두 "단일 앱 기능"이 아니라 "범용 에이전트가 여러 작업을 처리하도록 확장하는 레이어"를 지향한다는 점이다.

이 관점에서 중요한 것은 사용자가 앞으로 앱을 전혀 쓰지 않는다는 뜻이 아니다. 오히려 앱은 점점 더 에이전트가 호출하는 백엔드 기능 조각이 된다. 사용자의 메인 인터페이스는 앱 목록이 아니라 에이전트, 대화, 작업 큐, 승인 요청, 메모리, 스케줄이다.

이 방향성은 다음과 같은 제품 시그널로 확인된다.
- Anthropic은 공개 `Skill Creator` 리포지토리로 스킬 설계와 선택 트리거 최적화를 전면화했다.
- Claude Code는 memory와 remote control 문서를 통해 "한 세션의 대화형 도우미"에서 "지속적으로 이어지는 작업 환경"으로 확장하고 있다.
- Alibaba의 CoPaw는 AgentScope 생태계 안에서 로컬 및 클라우드 에이전트 제어 허브를 지향한다.
- CodeBuff 같은 도구는 아예 다중 에이전트 소프트웨어 엔지니어링이라는 프레이밍을 전면에 둔다.

핵심 해석은 간단하다. 미래의 제품 차별화 포인트는 점점 "새로운 앱 하나"보다 "기존 시스템과 사람 사이에서 어떤 작업을 끝까지 수행하게 하느냐"에 가까워진다.

## 2. 모델 경쟁의 초점은 IQ가 아니라 latency, price, toolability로 이동 중이다

영상은 Mercury 2, GPT-5.3 Instant, GPT-5.4, Gemini 3.1, Qwen 계열, Liquid AI LFM2를 한 묶음으로 소개한다. 이들을 보면 공통된 메시지가 있다. 이제 모델 릴리스는 "더 똑똑함"만이 아니라 `더 빠름`, `더 저렴함`, `더 긴 컨텍스트`, `더 나은 툴 호출`, `더 좋은 실시간 에이전트 적합성`을 전면에 내세운다.

### Mercury 2
Inception Labs는 Mercury 2를 매우 빠른 diffusion-based LLM으로 포지셔닝한다. 발표 자료와 공식 페이지 모두 `1,000 tokens/sec`, `agentic applications`, `real-time`에 초점을 맞춘다. 이 포지셔닝이 중요한 이유는 음성 에이전트, 문서 탐색, 인터랙티브 툴 사용처럼 지연시간이 품질만큼 중요한 워크로드가 늘고 있기 때문이다.

### GPT-5.3 Instant와 GPT-5.4
OpenAI 측 자료에서 보이는 방향은 두 가지다.
- GPT-5.3 Instant는 비용과 응답성, 웹 통합, 실제 배포 편의성을 강조한다.
- GPT-5.4는 긴 컨텍스트, reasoning, computer use, spreadsheet와 slides 생성 같은 복합 업무 적합성을 강조한다.

즉, 고급 reasoning 모델과 고속 실무형 모델이 분화되고 있다. 앞으로 에이전트 스택은 둘 중 하나만 쓰지 않고, 계획과 실행을 분리해 조합할 가능성이 크다.

### Gemini 3.1 Flash-Lite와 Pro
Google의 Gemini 3.1 계열은 `thinking levels`, 속도, 가격, 멀티모달 입력, 장기 작업 안정성 같은 운영 특성을 민다. 여기서 중요한 것은 모델 하나의 절대 점수가 아니라, 특정 워크로드에 맞는 비용-속도-성능 조정 능력이다.

### Liquid AI LFM2-24B-A2B
Liquid AI의 LFM2는 오픈 웨이트, 비교적 낮은 하드웨어 요구량, 멀티에이전트 워크플로 적합성을 밀고 있다. 이것은 "최고 성능은 폐쇄형, 넓은 배포는 경량 개방형"이라는 시장 양극화를 보여준다.

### 실무적 의미
- 사용자-facing 실시간 작업에는 저지연 모델이 중요하다.
- 복잡한 계획과 검토에는 비싼 reasoning 모델이 남는다.
- 많은 실제 시스템은 한 모델이 아니라 여러 모델의 조합이 된다.
- 모델 선택은 단독 의사결정이 아니라 라우팅 정책 설계 문제가 된다.

## 3. Harness Engineering이 모델 자체보다 더 큰 병목이 되고 있다

이번 영상에서 가장 실무적인 통찰은 `harness engineering`이다. 이 표현은 단순한 유튜브 유행어가 아니다. OpenAI도 공식적으로 harness engineering을 별도 글에서 다루고 있으며, 실제 업무형 벤치마크인 TheAgentCompany는 높은 벤치마크 점수와 낮은 업무 완료율 사이의 간극을 상기시킨다.

이 주장이 중요한 이유는 다음과 같다.
- 모델은 똑똑해졌지만, 작업 환경은 여전히 취약하다.
- 실패는 대체로 추론 그 자체보다 잘못된 컨텍스트, 과도한 도구 수, 권한 문제, 상태 추적 실패, 복구 부재에서 나온다.
- 에이전트는 "정답 생성기"가 아니라 "작업 시스템의 한 구성요소"이므로 하네스 설계가 실제 성능을 결정한다.

영상이 소개한 OpenClaw 팁과 메모리 설계 아이디어도 같은 맥락이다. 토큰 사용량을 줄이는 설정, 세션 리셋, 도커 격리, 명시적 권한 요청, 레이어드 메모리 구조는 모두 모델 업그레이드가 아니라 하네스 개선에 해당한다.

여기서 얻는 결론은 분명하다.
- 도구는 많을수록 좋은 것이 아니다.
- 메모리는 크다고 좋은 것이 아니다.
- 스스로 실패를 감지하고 재시도하는 최소한의 루프가 필요하다.
- 샌드박스와 권한 설계는 품질 문제가 아니라 필수 기능이다.

## 4. 엔터프라이즈 ROI는 다중 에이전트 오케스트레이션에서 나타난다

AT&T 사례는 이 보고서에서 가장 실무 가치가 높은 사례다. VentureBeat에 따르면 Ask AT&T는 하루 80억 토큰을 처리하고, 10만 명 이상의 직원이 사용하며, 모델 라우팅과 멀티 에이전트 구조를 통해 관련 비용을 90% 절감했다.

이 사례가 중요한 이유는 세 가지다.
- 대기업도 더 이상 "최고 성능 모델 하나"만을 밀지 않는다는 점
- 상위 슈퍼 에이전트와 전문 워커 에이전트 조합이 비용과 응답성을 모두 개선할 수 있다는 점
- 자체 파운데이션 모델을 만들지 않아도 충분한 생산성 향상이 가능하다는 점

이 패턴은 향후 대부분의 기업형 에이전트 아키텍처에 재현될 가능성이 높다.
- 상위 계층: 의도 해석, 계획 수립, 라우팅
- 중간 계층: 도메인 스킬, 정책, 메모리, 권한
- 하위 계층: 저비용 모델, 자동화 도구, API 호출, 사내 시스템 실행

즉, 엔터프라이즈 경쟁력은 모델 개발보다 `workflow operating layer`에 더 크게 좌우될 수 있다.

## 5. 데스크톱 에이전트 생태계는 폭발적으로 늘지만, 아직 신뢰 스택은 미완성이다

OpenClaw, ClawX, Accomplish, NullClaw, MaxClaw, CoPaw, Claude Code는 서로 접근 방식이 다르지만 같은 문제를 푼다. 컴퓨터를 직접 쓰는 범용 에이전트를 어떻게 usable하게 만들 것인가.

영상과 슬라이드 덱을 종합하면 현재 생태계의 구도는 이렇다.
- Claude Code: 비교적 안정적이고 생산적인 코딩 중심 에이전트
- OpenClaw 계열: 강력한 비전이 있으나 보안, 설정, 안정성 면에서 거칠다
- Accomplish, ClawX, MaxClaw: 접근성, GUI, 쉬운 배포를 전면화한다
- CoPaw: 로컬 우선, 프레임워크 기반, 확장성에 초점을 둔다

하지만 이 영역에는 아직 해결되지 않은 문제가 많다.
- 승인 없는 도구 실행 위험
- 파일 시스템 과권한
- 장기 메모리 오염
- 과도한 토큰 비용
- UI 자동화의 취약성
- 사용자가 신뢰할 수 있는 상태 가시성 부족

따라서 이 영역의 승자는 "가장 강한 모델"이 아니라, `가장 예측 가능하고 안전하게 실패하는 시스템`을 만드는 팀이 될 가능성이 높다.

## 6. Safety와 국방 조달 이슈는 제품 외부 변수가 아니라 핵심 시장 변수다

Anthropic과 미 국방부 갈등은 AI 안전 논의가 추상 윤리 문제가 아니라 계약, 조달, 공급망, 국가 권력의 문제라는 점을 보여준다. Anthropic의 공식 성명, CBS 인터뷰, 후속 보도들을 종합하면 쟁점은 두 가지 red line에 집중된다.
- 미국인 대상 대규모 감시
- 인간 개입 없는 완전자율 무기

이 사건은 두 개의 불편한 사실을 드러낸다.

첫째, 자발적 안전 원칙은 경쟁과 국가 압력 앞에서 취약하다. 영상 말미에 소개된 "competitive pressure destroys voluntary restraint"라는 문구는 과장이 아니라 업계 현실을 반영한다.

둘째, 앞으로는 기술 기업의 모델 성능만이 아니라 `어떤 계약을 수용하는가`, `어떤 사용을 거부하는가`, `어떤 가드레일을 유지하는가`가 시장 포지셔닝의 일부가 된다.

실무자 관점에서 이것이 중요한 이유는 단순히 정치 이슈가 아니라, 기업이 어떤 모델 공급자를 쓰느냐가 보안, 규정 준수, 브랜드 리스크, 장기 조달 안정성에 직결되기 때문이다.

## 7. 이 영상이 말하는 더 큰 구조 변화

영상은 수십 개의 개별 뉴스를 나열하지만, 그 밑에 깔린 구조는 아래 세 줄로 요약할 수 있다.

### 7.1 모델은 commodity화되지만 완전히 평준화되지는 않는다
상위 모델 간 차이는 여전히 존재한다. 그러나 실제 시스템 설계에서는 "어느 모델이 절대적으로 최고인가"보다 "어떤 모델을 어떤 순간에 어떤 권한으로 쓰는가"가 더 중요해진다.

### 7.2 제품 단위가 앱에서 작업흐름으로 이동한다
사용자는 앞으로 더 자주 "앱을 열고 기능을 찾는" 대신 "에이전트에게 결과를 주문하고 승인하는" 방식으로 이동할 것이다. 이때 스킬과 메모리, 원격 제어, 워크플로 모듈이 새로운 UX 단위가 된다.

### 7.3 핵심 인재 수요는 더 공학적으로 바뀐다
모델 프롬프트만 잘 쓰는 사람이 아니라, 도구 체인, 데이터 접근, 실패 복구, 보안 경계, 업무 측정 체계를 설계할 수 있는 사람이 중요해진다. 영상의 마지막 메시지인 AI 엔지니어 수요 확대도 이 맥락에서 이해하는 편이 맞다.

## 8. 실무자와 팀을 위한 제안

### 바로 해볼 수 있는 것
- 현재 가장 자주 반복되는 문서, 리서치, 코딩, QA, 운영 업무 하나를 골라 에이전트 작업흐름으로 재설계한다.
- 단일 범용 메모리 파일 대신 `raw logs / curated notes / searchable memory` 구조를 채택한다.
- 고가 reasoning 모델과 저가 실행 모델을 분리해 라우팅한다.
- 모든 외부 액션에 승인과 감사 로그를 붙인다.
- 성공률보다 업무 완료율, 재작업률, 평균 비용, human handoff 비율을 함께 측정한다.

### 투자 우선순위
1. 도메인 스킬 정의
2. 메모리 구조화
3. 권한과 샌드박스
4. 평가 하네스
5. 모델 라우팅
6. 운영 관측성

### 피해야 할 함정
- 모델만 바꾸면 성능이 해결될 것이라는 기대
- 메모리를 한 파일에 계속 누적하는 방식
- 도구를 너무 많이 붙여 에이전트를 혼란스럽게 만드는 방식
- 승인 없이 로컬 파일과 외부 앱에 광범위 접근을 허용하는 방식
- 벤치마크 점수를 실제 업무 성능으로 오해하는 방식

## 9. Watchlist
- 범용 데스크톱 에이전트가 실제로 어떤 승인 UX를 표준화하는지
- 모델 공급자들이 memory, remote control, scheduling을 얼마나 빠르게 통합하는지
- 기업들이 Ask AT&T와 유사한 multi-agent routing 사례를 더 공개하는지
- Anthropic, OpenAI, xAI 등 주요 공급자의 국방 계약 언어가 어떻게 바뀌는지
- 에이전트 신뢰성을 평가하는 실무형 benchmark가 얼마나 빠르게 보급되는지

## Bottom Line
이 주간 영상은 여러 신제품을 한꺼번에 훑는 뉴스 브리핑처럼 보이지만, 실제로는 `AI agent operating system 시대의 초기 징후`를 꽤 선명하게 보여준다. 앞으로 가치가 쌓이는 곳은 단일 모델 자체보다, 여러 모델과 도구를 묶어 안전하게 실제 업무를 끝까지 수행하게 만드는 운영층이다. 팀과 개인 모두 이제는 "어떤 모델을 쓸까"보다 "어떤 에이전트 시스템을 설계할까"를 먼저 묻는 편이 맞다.

## References
- [YouTube video](https://www.youtube.com/watch?v=waMSY9hc8eU)
- [Slide deck on GitHub](https://raw.githubusercontent.com/lselector/seminar/master/2026/2026-03-06-AI-Updates.pptx)
- [OpenAI GPT-5.3 Instant](https://openai.com/index/gpt-5-3-instant/)
- [OpenAI GPT-5.4 Thinking System Card](https://openai.com/index/gpt-5-4-thinking-system-card/)
- [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)
- [Gemini 3.1 Flash-Lite model card](https://deepmind.google/models/model-cards/gemini-3-1-flash-lite/)
- [Gemini 3.1 Pro announcement](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/)
- [Mercury 2 by Inception Labs](https://www.inceptionlabs.ai/introducing-mercury)
- [CoPaw repository](https://github.com/agentscope-ai/CoPaw)
- [Claude Code memory docs](https://code.claude.com/docs/en/memory)
- [Claude Code remote control docs](https://code.claude.com/docs/en/remote-control)
- [AT&T multi-agent orchestration case](https://venturebeat.com/orchestration/8-billion-tokens-a-day-forced-at-and-t-to-rethink-ai-orchestration-and-cut/)
- [TheAgentCompany paper summary](https://huggingface.co/papers/2412.14161)
- [Anthropic statement on the Department of War](https://www.anthropic.com/news/statement-department-of-war)
- [TechCrunch Pentagon negotiation follow-up](https://techcrunch.com/2026/03/05/anthropic-ceo-dario-amodei-could-still-be-trying-to-make-a-deal-with-pentagon/)
- [CBS transcript with Dario Amodei](https://www.cbsnews.com/news/anthropic-ceo-dario-amodei-full-transcript/)
- [Liquid AI LFM2-24B-A2B](https://huggingface.co/LiquidAI/LFM2-24B-A2B)
- [CodeBuff repository](https://github.com/CodebuffAI/codebuff)
