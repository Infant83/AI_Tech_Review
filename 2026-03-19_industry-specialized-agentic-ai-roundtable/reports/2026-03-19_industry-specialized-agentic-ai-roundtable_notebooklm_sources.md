---
title: NotebookLM Source Pack - Industry-Specialized Agentic AI Roundtable
date: 2026-03-22
tags:
  - notebooklm
  - agentic-ai
  - enterprise-ai
  - korea-policy
---

# Industry-Specialized Agentic AI Roundtable

## Core Question
`Agentic AI를 산업 특화 관점에서 어떻게 접근해야 하며, 한국은 어디에서 경쟁 우위를 만들 수 있는가?`

## Source Context
- Seed video: [(`26.3.17) 산업 특화 에이전틱 AI 간담회 개최](https://www.youtube.com/watch?v=InozhblHe-0)
- Uploader: `국가인공지능전략위원회`
- Uploaded on `2026-03-19`
- Main speakers:
  - `조동근` (`조코딩`)
  - `김성훈` (`업스테이지`)
  - 분과 맥락: `조준희` 산업AX·생태계 분과장

## What The Video Argued

### 1. Agentic AI is more than LLM chat
- Agent는 `tool use`, `memory`, `feedback`, `multi-step execution`이 결합된 시스템으로 설명되었다.
- 이 관점에서는 모델 성능만큼이나 외부 시스템 연결과 실행 구조가 중요하다.

### 2. Standards and ecosystem modules are becoming important
- 발표에서는 `MCP`, `Skills`, `A2A`를 중요한 agent 표준으로 소개했다.
- 의미:
  - MCP: 외부 도구/데이터 연결 표준
  - Skills: 절차와 도메인 지식을 재사용 가능한 패키지로 만드는 방식
  - A2A: agent 간 협업 표준

### 3. Industrial value starts from documents and workflows
- 업스테이지 쪽 설명은 `문서 파싱`, `근거 추출`, `설명 가능성`, `프로세스 데이터`를 강조했다.
- 요점: agent는 범용 데스크톱 조작보다 먼저 `문서 중심 업무`와 `정형화 가능한 절차`에서 산업 가치가 크다.

### 4. Public-sector workflows can become export-grade reference products
- 공공 인허가 업무를 예로 들어, agent가 사전 검토와 보완 요청을 수행하고 사람은 최종 승인만 하는 구조가 논의되었다.
- 이 관점에서 공공은 단순 규제자가 아니라 `표준화 가능한 reference workflow를 만드는 실증장`이 된다.

### 5. Security and domestic deployment matter
- 기업의 플로우, 도면, 스펙, VOC가 agent 시스템 안으로 들어오면 보안이 핵심 이슈가 된다.
- 국내 공급망과 데이터 통제는 한국 시장에서 제품 채택의 중요한 조건으로 제시되었다.

### 6. Workforce strategy must shift toward AX experts
- 개발자 양성 중심 교육만으로는 부족하고, `AI/AX 전문가`, `프로세스 설계자`, `현업-기술 브리지 인력`이 중요하다는 의견이 나왔다.

## External Validation

### Anthropic
- [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents)
- 핵심 포인트:
  - 처음부터 복잡한 multi-agent를 만들지 말고 단순한 구조로 시작할 것
  - domain-specific skills가 있으면 single-agent로도 많은 문제를 해결할 수 있음
  - document processing, compliance checking, reporting 등은 좋은 초기 적용처

### Model Context Protocol
- [MCP Architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- 핵심 포인트:
  - host-client-server 구조
  - agent와 외부 시스템 연결을 표준화
  - 권한 경계와 분리가 중요

### Google A2A
- [A2A GitHub](https://github.com/google/A2A)
- [Google Cloud blog on A2A and Agentspace Toolkit](https://cloud.google.com/blog/products/ai-machine-learning/agentspace-toolkit-and-a2a-enhancements)
- 핵심 포인트:
  - agent interoperability
  - multi-agent coordination
  - enterprise-grade evaluation and ecosystem tooling 강화

### UiPath
- [Enterprise-grade platform for agentic automation](https://www.uipath.com/newsroom/uipath-introduces-first-enterprise-grade-platform-for-agentic-automation-designed-to-transform-the-way-humans-ai-agents-and-robots-work)
- 핵심 포인트:
  - agentic AI adoption의 핵심 병목은 보안, 신뢰성, stalled pilots
  - 사람, agent, robot의 협업이 중요

### Salesforce
- [How Agentforce Works](https://www.salesforce.com/agentforce/how-agentforce-works/)
- [Agentforce for Academic Operations datasheet](https://www.salesforce.com/en-us/wp-content/uploads/sites/4/Industry%20-%20Education/Agentforce-Education-for-Academic-Operations-Datasheet.pdf)
- 핵심 포인트:
  - enterprise agent는 기존 workflow와 actions 위에서 동작해야 함
  - education처럼 명확한 버티컬 use case에 특화된 agent 사례가 실제로 등장 중

### Korean policy context
- [국가인공지능전략위원회 출범 관련 대통령실 브리핑](https://m.president.go.kr/newsroom/briefing/yqqm7nR3)
- [K-디지털 트레이닝 AI 캠퍼스](https://m.korea.kr/briefing/pressReleaseView.do?newsId=156738769)
- 핵심 포인트:
  - `모두의 AI`, `안전한 데이터 활용`, `ODA 기반 한국형 AI 확산`, `실무형 AI 인재 1만 명 양성`

## Synthesized Insight

### Agentic AI의 산업 특화는 “모델 특화”보다 “workflow 특화”다
- 산업 특화 agent의 핵심은 다음 네 가지를 묶는 것이다.
  - domain skill
  - workflow graph
  - trusted data access
  - human approval logic

### 한국의 현실적인 전략
1. foundation model 정면 승부보다 `workflow operating layer`를 노린다
2. 공공과 민간에서 공통 재사용 가능한 `reference workflow`를 만든다
3. 문서 중심, 규칙 중심, 승인 중심의 업무부터 공략한다
4. 보안과 국내 배치를 제품 핵심으로 설계한다
5. 버티컬 use case를 수출 가능한 product package로 만든다

### Recommended vertical starting points
- 공공 인허가 사전 검토
- 제조 품질 문서/규격 검토
- 금융/보험 심사 문서 처리
- B2B 수출/컴플라이언스 문서 작업

## Recommended Product Pattern

### Stage 1
- single-agent
- document parsing
- retrieval
- rule checking
- evidence citation
- human approval

### Stage 2
- domain skills added
- workflow routing
- company system integration
- metrics and audit trail

### Stage 3
- selective multi-agent orchestration
- agent-to-agent handoff
- role-specialized evaluators
- export-ready packaging

## What To Ask NotebookLM
- 이 소스들을 종합할 때 한국형 산업 특화 Agentic AI의 가장 현실적인 초기 시장 3개는 무엇인가?
- 공공 인허가 업무를 reference workflow로 삼을 때 필요한 데이터, 평가 기준, human-in-the-loop 설계는 무엇인가?
- 국내 AI 기업이 보안과 데이터 주권을 차별점으로 삼아 수출형 agent product를 만들려면 어떤 product strategy가 필요한가?
- `single agent + domain skills`와 `multi-agent orchestration`을 어떤 시점에서 나눠 적용하는 것이 가장 현실적인가?
- AX 전문가를 양성하기 위한 교육 커리큘럼은 어떤 역량 묶음으로 설계되어야 하는가?
