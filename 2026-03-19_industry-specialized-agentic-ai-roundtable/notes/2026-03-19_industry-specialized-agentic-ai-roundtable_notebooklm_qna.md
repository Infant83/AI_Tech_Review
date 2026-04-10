---
title: NotebookLM Q&A Log - Industry-Specialized Agentic AI Roundtable
date: 2026-03-22
tags:
  - notebooklm
  - qna
  - agentic-ai
  - korea-policy
---

# NotebookLM Q&A Log

## Notebook
- URL: https://notebooklm.google.com/notebook/d64c863c-febc-4da6-af71-35a3c0116867
- Session ID: `3553a06d`
- Source basis: deep research report, NotebookLM source pack, source note

## Question 1
`업로드된 소스만 바탕으로, 한국이 산업 특화 Agentic AI를 추진할 때 가장 방어 가능한 전략 3가지를 정리해 주세요. 각 전략마다 90일, 12개월, 36개월 실행 과제를 붙여 주세요.`

### Condensed Answer
- 전략 1: foundation model race보다 `workflow operating layer`를 선점한다.
  - 90일: 문서·승인 중심 workflow 2-3개를 선정하고 단일 agent pilot를 설계한다.
  - 12개월: 도메인 스킬 카탈로그와 재사용 가능한 tool chain을 축적한다.
  - 36개월: 산업별 reference workflow를 수출 가능한 패키지로 전환한다.
- 전략 2: 공공 인허가를 `reference market`으로 활용한다.
  - 90일: 누락 검토, 보완 요청, 사전 적합성 판단 같은 좁은 단계부터 실증한다.
  - 12개월: 표준 프로세스 데이터와 평가셋을 만든다.
  - 36개월: 국내 검증 사례를 기반으로 해외 공공·규제 산업으로 확장한다.
- 전략 3: 보안·감사 가능성 중심의 `trust layer`를 차별화 자산으로 만든다.
  - 90일: 민감 데이터 분류, 반출 통제, human escalation 규칙을 정의한다.
  - 12개월: action log, source trace, approval checkpoint를 제품 기본값으로 넣는다.
  - 36개월: 국내 배치와 감사 가능성을 포함한 산업 표준 운영 패턴으로 정착시킨다.

## Question 2
`이 간담회의 가장 큰 맹점 또는 과소논의된 주제 3가지를 정리해 주세요. 특히 평가 체계, 실패 관리, 조직 도입 관점에서 말해 주세요.`

### Condensed Answer
- 평가 체계: 성공률만이 아니라 절차 오류, 근거 적절성, 승인 전환율, 재작업률을 측정하는 harness가 부족하다.
- 실패 관리: 사람이 언제 개입하는지, rollback은 어떻게 할지, 어떤 오류를 자동 차단할지에 대한 규칙이 더 구체화되어야 한다.
- 조직 도입: pilot가 조직 내에서 AX 전환으로 이어지려면 현업 오너, 프로세스 설계자, 평가자가 같이 움직여야 한다.

## Question 3
`업로드된 소스만 바탕으로, 이 간담회가 제안하는 산업 특화 Agentic AI 전략을 3개의 원칙과 3개의 금지사항으로 압축해 주세요. 각 항목은 한 문장으로, 한국 산업 전략 관점에서 써 주세요.`

### Condensed Answer
#### Principles
- 한국은 모델 경쟁보다 `workflow operating layer`의 표준화와 재사용성 확보에 집중해야 한다.
- 공공 인허가 같은 복잡한 프로세스를 고부가 reference workflow로 만들어 수출 무기로 전환해야 한다.
- 데이터 반출 통제와 판단 근거 제시를 보장하는 `trust layer`를 핵심 차별화 요소로 삼아야 한다.

#### Anti-Patterns
- 전사적 거대 multi-agent 플랫폼에 선행 투자하지 말고, 단일 agent 기반의 좁은 업무부터 시작해야 한다.
- UI나 프롬프트만 바꾼 가짜 버티컬이 아니라 도메인 온톨로지와 workflow graph를 묶어야 한다.
- human escalation과 process data 구조화 없이 자동화부터 밀어붙이면 실패 확률이 높다.

## Question 4
`업로드된 소스만 바탕으로, '우리가 산업 특화 측면에서 Agentic AI에 어떻게 접근해야 하는가'에 대한 7문장짜리 경영진용 결론을 작성해 주세요. 사실과 해석을 분리해 주세요.`

### Condensed Answer
- 사실: 시장은 거대 모델 경쟁을 넘어 MCP, A2A, 도메인 스킬 중심의 agent ecosystem으로 이동하고 있다.
- 사실: 실제 산업 적용은 문서 판독, 근거 제시, human escalation, 보안 통제가 있어야 성립한다.
- 사실: 현재 유망 use case는 공공 인허가, 제조 품질 문서, 금융 심사처럼 좁고 문서 중심인 작업이다.
- 해석: 따라서 우리는 거대 모델 경쟁보다 조직 내부 workflow와 도메인 지식의 캡슐화에 역량을 집중해야 한다.
- 해석: 투자 방식은 전사 플랫폼 선행 도입이 아니라 `8-12주 단위 pilot + workflow asset 축적`이 맞다.
- 해석: 국내 시장에서는 trust layer를 기술 옵션이 아니라 핵심 차별화 무기로 설계해야 한다.
- 해석: 공공 인허가를 전략적 실증장으로 삼아 이후 민간 및 해외 B2B 패키지로 확장하는 경로가 가장 현실적이다.

## Note
- 이 문서는 NotebookLM이 `업로드된 동일 소스`를 다시 압축·재구성한 결과를 기록한 것이다.
- 따라서 외부 독립 검증이라기보다, 본 보고서의 논지를 2차 합성 관점에서 cross-check한 참고 기록으로 해석해야 한다.
