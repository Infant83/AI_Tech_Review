---
title: 2026-03-19 Industry-Specialized Agentic AI Roundtable Deep Research
date: 2026-03-22
tags:
  - ai-review
  - deepresearch
  - agentic-ai
  - enterprise-ai
  - korea-policy
  - workflow-automation
---

# 2026-03-19 Industry-Specialized Agentic AI Roundtable Deep Research

## Scope
이 문서는 국가인공지능전략위원회가 2026년 3월 19일 공개한 영상 `('26.3.17) 산업 특화 에이전틱 AI 간담회 개최`를 출발점으로 삼아, 영상의 주장과 질의응답을 구조적으로 재해석한 보고서다. 기준 시점은 `2026년 3월 22일`이며, 영상 transcript와 공식 외부 자료를 함께 사용했다.

## Executive Synthesis
- 이 간담회의 본질은 “Agentic AI가 뜬다”는 선언이 아니라, `한국은 모델 경쟁보다 산업별 workflow operating layer 경쟁에서 기회를 잡아야 한다`는 제안이다.
- 조동근의 발표는 ecosystem lens다. 핵심은 `MCP`, `Skills`, `A2A`, coding agent, desktop agent 같은 운영 레이어의 표준화와 재사용성이다.
- 김성훈의 발표는 deployment lens다. 핵심은 `문서`, `근거 제시`, `프로세스 데이터`, `현업 협업`, `설명 가능성`이다.
- 질의응답은 policy lens다. 핵심은 `지금 투자해야 하나`, `공공이 어떤 데이터와 실증장을 제공할 수 있나`, `보안과 국내 공급망을 어떻게 확보할 것인가`, `수출 산업으로 어떻게 만들 것인가`다.
- 외부 공식 자료와 비교하면, 영상의 방향은 대체로 타당하다. 다만 `평가`, `관측성`, `운영 거버넌스`, `실패시 인간 개입 규칙`에 대한 논의는 더 보강되어야 한다.

## 1. 이 영상이 실제로 말하는 것

### 1.1 모델이 아니라 workflow layer가 경쟁 무대라는 주장
조준희 분과장과 발제자들의 공통 메시지는 분명하다. 한국이 foundation model 자체에서 미국 빅테크와 같은 게임을 하는 것은 어렵지만, 산업별 업무를 재구성하는 agent layer에서는 충분히 공간이 있다는 것이다.

이 지점이 중요한 이유는 agentic AI의 경쟁력이 더 이상 “누가 가장 큰 모델을 가졌는가”로만 정해지지 않기 때문이다. 실제 도입에서는 다음이 더 중요해진다.
- 어떤 시스템과 연결되는가
- 어떤 업무 순서를 알고 있는가
- 어떤 권한 경계를 갖는가
- 어떤 실수는 자동으로 막는가
- 왜 그런 판단을 했는지 보여줄 수 있는가

이 간담회는 바로 이 운영층을 산업화 대상으로 본다.

### 1.2 JoCoding의 메시지: 표준과 재사용 단위가 중요하다
조동근의 발표는 AI agent를 `LLM + tool use + memory + feedback`로 설명한 뒤, 실제 실전 표준으로 `MCP`, `Skills`, `A2A`를 묶어 소개한다. 이 발표를 요약하면 다음과 같다.

- agent는 도구 연결과 외부 데이터 접근이 있어야 실무형 시스템이 된다
- 스킬은 절차와 지식을 캡슐화한 재사용 단위다
- agent 간 협업도 표준화되는 중이다
- coding agent와 desktop agent는 agent interface의 양대 실험장이다

이 주장의 가치가 큰 이유는 “산업 특화”를 별도 모델 학습으로만 보지 않기 때문이다. 영상은 오히려 산업 특화를 `도메인 스킬의 조합`으로 본다. 이는 외부 공식 자료와도 잘 맞는다. Anthropic의 공식 아키텍처 자료는 `Skills`를 domain-specific expertise, standardized workflows, specialized tool integrations, industry-specific best practices와 compliance requirements를 담는 모듈로 설명한다.

즉, 버티컬 agent 전략의 핵심은 모델을 새로 만드는 것보다 `스킬 카탈로그를 잘 설계하는 것`일 가능성이 높다.

### 1.3 Kim Sung-hoon의 메시지: 산업화는 문서와 프로세스 데이터에서 시작한다
김성훈의 발표는 훨씬 현실적이다. 그는 agent가 이제 실제로 쓸 만해졌다고 보지만, 동시에 실제 업무 적용에서는 몇 가지 조건이 반드시 필요하다고 말한다.

- 문서와 업무 근거를 읽을 수 있어야 한다
- 왜 맞고 왜 틀렸는지 보여줄 수 있어야 한다
- 프로세스를 구조화할 수 있어야 한다
- 현업 전문가와 함께 데이터를 만들어야 한다

특히 `문서 중심 업무`를 출발점으로 삼는 접근은 매우 중요하다. 보험, 신용평가, 품질 심사, 규정 검토, 인허가, 계약 검토, 제조 품질 문서, 의료 비정형 문서 등은 모두 agent가 바로 가치 창출을 시도할 수 있는 영역이다.

이 접근은 산업 특화 agentic AI의 올바른 출발 순서를 보여준다.

1. 문서를 이해한다
2. 문서에서 구조를 뽑는다
3. 규칙과 예외를 붙인다
4. 판단 근거를 보여준다
5. 마지막 승인만 사람에게 넘긴다

이 순서는 훨씬 현실적이고, 규제 산업에서도 받아들여지기 쉽다.

## 2. 이 영상이 특히 잘 짚은 지점

### 2.1 `프로세스 데이터`가 진짜 희소 자산이라는 점
김성훈이 강조한 핵심은 단순한 raw document보다 `이 일을 실제로 어떻게 처리하는가`에 대한 데이터가 부족하다는 것이다. 예를 들어 공공 인허가 업무에서는 신청 서류만으로는 부족하다. 실제 현장에서는 다음이 중요하다.

- 어떤 순서로 검토하는가
- 어느 시점에 무엇을 확인하는가
- 어떤 예외 사유로 반려하는가
- 어느 단계에서 사람이 최종 결재하는가

이런 데이터는 모델 파라미터에 들어 있지 않다. 조직 내부에 있고, 대부분 암묵지다. 따라서 산업 특화 agent의 경쟁우위는 `사내·산업별 workflow capture` 능력에서 나온다.

### 2.2 공공을 “느린 규제자”가 아니라 “고부가 실증장”으로 본 점
간담회는 공공 인허가 자동화를 예시로 들며, agent가 서류를 받고 부족한 부분을 안내하고 판정 근거를 준비한 뒤 공무원은 최종 확인만 하는 구조를 상상한다. 이것은 단순한 효율화 아이디어가 아니다. 만약 이런 시스템이 실제로 만들어지면 다음 가치가 생긴다.

- 민원 체감 속도 개선
- 공무원 업무 부담 경감
- 프로세스 표준화
- 정책 데이터셋 축적
- 해외 수출 가능한 reference workflow 확보

이 점에서 공공은 단지 규제 기관이 아니라, 한국형 산업 agent를 검증하는 reference market이 될 수 있다.

### 2.3 보안과 국내 공급망을 전략 변수로 본 점
질의응답 후반부의 가장 실전적인 대목은 보안이다. 플로우, 도면, 스펙, VOC, 프로세스가 한 agent stack 안으로 들어오면 사실상 기업의 핵심 운영 정보가 한곳에 모인다. 이때 보안은 부가 요건이 아니라 제품 채택의 전제 조건이 된다.

이 인식은 UiPath의 2025년 공식 발표와도 맞는다. UiPath는 enterprise agent adoption의 핵심 조건으로 보안, 신뢰성, 컴플라이언스, stalled pilots 문제를 직접 언급한다. Salesforce 역시 Agentforce를 설명할 때 기존 workflow, APIs, permissions, trust layer 위에서 동작시키는 구조를 강조한다.

영상의 시사점은 명확하다.
- 한국 시장에서는 `agent 성능`과 `데이터 경계`를 분리해서 볼 수 없다
- 국내 배치 가능성, 데이터 반출 통제, 감사 가능성이 제품 전략의 일부다
- 이 요소는 오히려 글로벌 빅테크와 다른 차별점이 될 수 있다

## 3. 외부 자료로 본 시장 검증

### 3.1 Anthropic: Start simple, then specialize
Anthropic의 공식 자료는 영상의 핵심 직관을 잘 뒷받침한다.

- domain-specific expertise가 필요한 경우 `single agent + specialized skills`가 더 효율적일 수 있다
- multi-agent는 필요한 경우에만 점진적으로 가야 한다
- multi-agent는 single agent보다 훨씬 더 많은 토큰과 운영 복잡성을 수반한다
- document processing, compliance checking, routine reporting 같은 영역은 명확한 초기 적용처다

이것은 산업 특화 agent 전략의 첫 원칙을 준다. `처음부터 거대한 multi-agent OS를 만들지 말고, 좁은 업무에 강한 single agent를 도메인 스킬로 강화하라.`

### 3.2 MCP and A2A: integration and interoperability are becoming the real substrate
영상에서 언급된 MCP와 A2A는 hype가 아니라 실제로 agent ecosystem의 표준화 시도다.

- MCP는 host, client, server 구조를 통해 모델과 외부 시스템 연결을 표준화하려 한다
- A2A는 agent 간 상호작용과 협업의 표준 인터페이스를 지향한다

이 두 흐름은 산업 특화 agent가 폐쇄형 사일로로 끝나기보다, `업무 시스템 위에서 호환 가능한 모듈`로 진화할 가능성을 보여준다.

이는 산업 전략에도 중요하다. 한국 기업이 모든 것을 독자 stack으로 만들기보다, 표준을 활용해 도메인에 집중하는 편이 더 현실적이다.

### 3.3 UiPath and Salesforce: enterprise agents are really workflow products
UiPath의 발표는 agentic automation을 `human + agent + robot` 협업 플랫폼으로 설명하며, 보안과 운영성 문제를 전면에 둔다. Salesforce는 Agentforce를 기존 업무 흐름과 actions 위에서 작동하는 구조로 설명한다.

둘을 합쳐 보면 실무 결론은 분명하다.
- enterprise agent는 챗봇이 아니라 workflow product다
- agent가 해야 할 일은 기존 SaaS를 대체하는 것이 아니라, 여러 시스템을 가로질러 작업을 끝내는 것이다
- 따라서 기업은 모델 벤더를 고르는 것만으로는 충분하지 않고, workflow substrate를 같이 설계해야 한다

### 3.4 Korean policy context: accessibility, workforce, and data
대통령실 브리핑과 K-디지털 트레이닝 AI 캠퍼스 자료를 보면, 한국 정책은 다음 세 축으로 움직이고 있다.

- `모두의 AI`: 국민 접근성 확대
- `AI 캠퍼스`: 실무형 AI 전문인력 1만 명 양성
- `한국형 AI/ODA`: 국제 확산과 시장 개척

이 정책 축은 영상 속 문제의식과 만나는 지점이 있다. 다만 현 시점에서 부족한 부분은 `Agentic AI용 workflow datasets`, `평가 체계`, `부처 간 재사용 가능한 reference processes`다.

## 4. 이 간담회의 한계와 보완 포인트

### 4.1 Agent evaluation 논의가 약하다
영상은 가능성과 기회는 잘 짚지만, 다음 문제는 상대적으로 얕게 다룬다.
- 언제 agent가 실패했다고 판정할 것인가
- 사람에게 넘기는 기준은 무엇인가
- 환각보다 더 위험한 `절차 오류`를 어떻게 탐지할 것인가
- 테스트 환경과 운영 환경 차이를 어떻게 줄일 것인가

산업 특화 agent는 데모보다 `재현성 있는 평가 harness`가 더 중요하다.

### 4.2 Observability and auditability가 제품 핵심이라는 점이 더 강조될 필요가 있다
공공과 규제 산업에서는 “결과가 맞다”보다 `왜 그렇게 했는가`, `무슨 도구를 썼는가`, `어떤 문서를 참고했는가`, `언제 사람 승인을 받았는가`가 더 중요할 수 있다.

따라서 산업 특화 agent 전략은 처음부터 다음을 포함해야 한다.
- action log
- source trace
- approval checkpoints
- failure taxonomy
- rollback and replay capability

### 4.3 버티컬화를 “UI 커스터마이징”으로 오해할 위험
영상은 전반적으로 좋은 방향을 제시하지만, 시장에서는 “산업 특화”를 단순한 도메인별 화면이나 프롬프트 정도로 착각할 수 있다. 실제로는 전혀 다르다.

산업 특화 agent는 최소한 다음을 묶어야 한다.
- domain ontology
- workflow graph
- document schema
- permissions model
- evaluation rubric
- human escalation rules

이 여섯 가지가 없으면 산업 특화가 아니라 산업 라벨만 붙은 범용 챗봇이 된다.

## 5. 산업 특화 Agentic AI에 대한 실전 접근법

### 5.1 출발점은 “산업”보다 “작업 단위”
가장 흔한 실패는 “제조용 agent”, “금융용 agent”처럼 너무 넓게 시작하는 것이다. 실제로는 아래처럼 `작업 단위`로 잘라야 한다.

- 인허가 사전 검토
- 보험 청구 문서 정합성 검사
- 신용평가 문서 요약 및 근거 추출
- 제조 품질 문서 판독과 불량 사유 정리
- VOC 분류와 우선순위 추천
- 계약서 조항 비교와 red-flag 탐지

이 단위는 ROI 측정이 가능하고, 실수 범위를 통제하기 쉽다.

### 5.2 기본 아키텍처는 이렇게 가는 편이 맞다

#### Layer 1. Domain knowledge layer
- 용어집
- 규정집
- 표준 서식
- 예외 규칙

#### Layer 2. Workflow layer
- 단계 정의
- 입력/출력 조건
- 승인 지점
- 실패 시 human handoff

#### Layer 3. Tool layer
- 문서 파서
- OCR
- 사내 시스템 API
- 검색
- 데이터베이스
- 이메일/결재 연동

#### Layer 4. Trust layer
- 근거 표시
- 로그
- 재현성
- 권한 분리
- 데이터 반출 통제

#### Layer 5. Evaluation layer
- 태스크 성공률
- 반려 정확도
- 근거 적절성
- 재작업률
- 승인 전환율

이 구조가 갖춰져야 산업 특화 agent가 “업무에 붙는 제품”이 된다.

### 5.3 한국 시장에서 먼저 유리한 영역

#### 공공 인허가와 행정 심사
- 프로세스가 길고 문서가 많다
- 시민 체감 가치가 크다
- 표준화되면 재사용 범위가 넓다

#### 제조 품질/기술 문서
- 도면, 스펙, 검사 기준, 불량 기록 등 문서가 풍부하다
- AI가 근거를 제시해야 하므로 explainability가 중요하다
- 국내 기업의 보안 니즈가 강해 한국 벤더 기회가 있다

#### 금융/보험 심사
- 문서 중심
- 규칙과 예외가 많다
- audit trail 요구가 강하다

#### B2B export operations
- 계약, 규정, 현지화, 고객사 요구사항 정리가 중요하다
- 국내 AI와 문서 자동화 역량을 패키지화하기 좋다

### 5.4 지금 투자해야 하는가에 대한 답
영상 속 CEO 질문은 정당하다. 기술 변화 속도가 빠른 상황에서 대규모 선행 투자는 위험할 수 있다. 하지만 “기다리는 전략”도 위험하다. 따라서 답은 다음과 같다.

- 거대한 전사 플랫폼 투자부터 하지 말 것
- 좁고 고통이 큰 workflow를 8-12주 단위로 파일럿할 것
- 파일럿의 목표는 멋진 데모가 아니라 `처리시간`, `정확도`, `재작업`, `승인시간` 개선일 것
- tool and workflow asset은 축적하고, model은 교체 가능하게 둘 것

즉, `크게 베팅하지 말고, 작게 시작하되 workflow asset은 반드시 남겨라`가 맞다.

### 5.5 NotebookLM cross-check
동일 소스를 NotebookLM에 업로드해 다시 질의했을 때도 결론은 거의 같았다. 이는 외부 독립 검증이라기보다 `동일 자료에 대한 2차 합성`이지만, 적어도 본 보고서의 핵심 구조가 과도하게 편향되지는 않았는지 점검하는 데는 유용했다.

NotebookLM이 압축한 3대 원칙은 다음과 같다.
- 한국은 foundation model race보다 `workflow operating layer`의 표준화와 재사용성에 집중해야 한다.
- 공공 인허가 같은 복잡한 프로세스를 `reference workflow`로 만들어 실증과 수출의 기반으로 써야 한다.
- 보안, 데이터 반출 통제, 판단 근거 제시를 포함한 `trust layer`를 차별화의 중심에 둬야 한다.

같은 맥락에서 NotebookLM이 경고한 3대 금지사항도 의미가 있다.
- 전사적 거대 multi-agent 플랫폼에 선행 투자하지 말 것
- UI와 프롬프트만 바꾼 가짜 버티컬에 머물지 말 것
- human escalation과 process data 구조화 없이 자동화부터 밀어붙이지 말 것

이 3원칙과 3금지사항은 결국 본 보고서의 핵심 결론을 다른 표현으로 다시 확인해 준다. `산업 특화 Agentic AI는 모델 선택의 문제가 아니라 workflow asset, domain skill, trust layer, evaluation discipline을 어떻게 묶느냐의 문제`다.

## 6. Ralph Pass: 이 결과물의 현재 품질 점검

### Round 1 findings
- 강점: 영상의 핵심 쟁점을 hype가 아니라 workflow, policy, enterprise design 관점으로 재구성했다.
- 강점: 외부 공식 자료와 연결해 주장 강도를 보강했다.
- 잔여 위험: 영상 transcript 자동 자막 오차 때문에 일부 인명·제품명·조직명은 재검증 여지가 있다.
- 잔여 위험: Upstage 제품 사례의 세부 상용 현황은 본 영상과 외부 공개 자료 범위 내에서만 제한적으로 해석해야 한다.

### Round 1 fixes applied
- transcript의 시간대별 핵심 주장만 채택하고, 수치성 주장이나 불명확한 이름은 과도하게 확대 해석하지 않았다.
- policy, standards, enterprise platform, workforce 자료를 추가해 영상의 직관을 보강했다.

### Round 2 findings
- 강점: Playwright CLI로 데스크톱·모바일 전체 페이지 검증을 수행해 실제 프레젠테이션 가독성을 점검했다.
- 강점: NotebookLM에 동일 소스를 업로드하고 추가 질의를 수행해 전략 원칙과 금지사항을 재정리했다.
- 잔여 위험: NotebookLM 슬라이드/인포그래픽 export는 활성 Chrome 세션 충돌 때문에 자동 다운로드까지 마무리하지 못했다.

### Round 2 fixes applied
- 모바일 히어로 타이포를 조정해 작은 화면에서의 시선 분산을 줄였다.
- NotebookLM cross-check 결과를 memo, deep research, presentation에 반영했다.
- NotebookLM 질의 로그를 별도 노트로 남겨 후속 재사용성을 확보했다.

## Bottom Line
이 간담회가 던지는 가장 중요한 메시지는 한국이 Agentic AI를 `모델 국뽕`이나 `범용 에이전트 데모`로 접근하면 늦는다는 점이다. 승부처는 산업별 업무 흐름을 얼마나 빨리 캡처하고, 그것을 보안 경계와 근거 제시, 승인 체계까지 포함한 제품으로 묶어내느냐에 있다.

정리하면 다음 한 문장이 가장 중요하다.

`한국형 산업 특화 Agentic AI 전략은 foundation model 추격전이 아니라 workflow asset, domain skill, trust layer, public reference use case를 동시에 쌓는 전략이어야 한다.`

## References
- [YouTube video: 산업 특화 에이전틱 AI 간담회 개최](https://www.youtube.com/watch?v=InozhblHe-0)
- [국가인공지능전략위원회 출범 관련 대통령실 브리핑](https://m.president.go.kr/newsroom/briefing/yqqm7nR3)
- [고용노동부, K-디지털 트레이닝 AI 캠퍼스](https://m.korea.kr/briefing/pressReleaseView.do?newsId=156738769)
- [Anthropic: Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic architecture PDF](https://resources.anthropic.com/hubfs/Building%20Effective%20AI%20Agents-%20Architecture%20Patterns%20and%20Implementation%20Frameworks.pdf?hsLang=en)
- [Model Context Protocol Architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [Google A2A GitHub repository](https://github.com/google/A2A)
- [Google Cloud blog: Agentspace Toolkit and A2A enhancements](https://cloud.google.com/blog/products/ai-machine-learning/agentspace-toolkit-and-a2a-enhancements)
- [UiPath enterprise-grade platform for agentic automation](https://www.uipath.com/newsroom/uipath-introduces-first-enterprise-grade-platform-for-agentic-automation-designed-to-transform-the-way-humans-ai-agents-and-robots-work)
- [Salesforce: How Agentforce Works](https://www.salesforce.com/agentforce/how-agentforce-works/)
- [Salesforce Agentforce Education datasheet](https://www.salesforce.com/en-us/wp-content/uploads/sites/4/Industry%20-%20Education/Agentforce-Education-for-Academic-Operations-Datasheet.pdf)
