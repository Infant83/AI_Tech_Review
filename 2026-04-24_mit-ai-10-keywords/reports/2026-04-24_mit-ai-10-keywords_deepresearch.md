---
title: MIT AI 10 Keywords Deep Research
date: 2026-04-24
topic: mit-ai-10-keywords
tags:
  - deepresearch
  - ai
  - strategy
  - mit-technology-review
---

# MIT Technology Review `AI 10대 키워드` 심층 리서치

## Summary

- MIT Technology Review가 2026년 4월 제시한 키워드들은 `생성형 AI 다음 단계`를 가리킨다. 초점은 더 좋은 챗봇이 아니라 `물리 세계`, `멀티에이전트 시스템`, `신뢰/안보`, `과학 자동화`, `오픈 생태계`로 이동 중이다.
- 물리 AI와 로보틱스는 `모델`보다 `데이터 획득 방식`이 병목이 되고 있고, 이를 풀기 위해 teleoperation, internet video, simulation, synthetic data가 결합되고 있다.
- 기업용 AI는 단일 모델 도입에서 끝나지 않는다. 실제 가치는 `도구 호출`, `권한`, `메모리`, `실행 환경`, `관찰가능성`, `승인 체계`가 묶인 orchestration layer에서 만들어진다.
- 동시에 AI는 사기, 딥페이크, 정보전, 군사 의사결정 지원으로 깊게 파고들고 있어, 향후 12개월은 `기술 배치` 못지않게 `신뢰 인프라` 경쟁의 시기가 된다.

## Review Context

- 출발점:
  - MIT Technology Review Korea의 `2026-04-15` 예고 기사
  - MIT Technology Review Korea의 `2026-04-22` 본편 기사
- 제약:
  - 사용자가 본 Gmail 원문 자체는 2026-04-24 기준 Gmail connector에서 정확히 재구성되지 않았다.
  - 따라서 본 보고서는 공개 기사와 1차 자료를 기반으로 작성되었다.
- 주의:
  - 공개 기사 제목은 `10대 키워드`이나, 실제 공개 페이지에는 11개 소제목이 보였다.
  - 본 보고서는 `AI가 만든 불안의 시대`와 `반발`을 하나의 사회적 수용성 클러스터로 묶어 10개 전략 축으로 정리한다.

## Why This Matters Now

2023년의 AI 화두가 `LLM이 얼마나 많은 일을 할 수 있는가`였다면, 2025~2026년의 화두는 `그 LLM과 주변 시스템이 어디까지 실세계와 제도, 조직, 연구, 보안에 들어갈 것인가`다.

이번 목록을 관통하는 공통점은 네 가지다.

1. AI는 디지털 작업을 넘어서 물리 세계와 실험 세계로 이동하고 있다.
2. AI의 성능은 모델 자체보다 에이전트 실행 구조에서 결정되는 비중이 커지고 있다.
3. AI의 위험은 편향 논쟁을 넘어 사기, 딥페이크, 안보, 사회적 불신의 운영 리스크가 되었다.
4. 오픈모델과 공개 생태계는 기술 선택 문제가 아니라 지정학적 의존성과 산업표준 경쟁의 문제로 바뀌고 있다.

## Signal Map

| 전략 클러스터 | 확인된 사실 | 지금 중요한 이유 | 앞으로 준비할 것 |
| --- | --- | --- | --- |
| 휴머노이드 로봇 데이터 | 로봇 foundation model은 인간 시연, 원격조작, 시뮬레이션, 합성데이터를 함께 사용한다 | 실세계 로봇 데이터 자체가 가장 희소한 자산이기 때문 | 데이터 수집 파이프라인, 시뮬레이션, 평가 루프 |
| LLMs+ | frontier 모델은 tool use, memory, reasoning, multimodal, sandbox execution으로 확장 중 | 단일 챗에서 실제 업무 실행 시스템으로 이동 중 | model-native runtime, tool policy, observability |
| AI 사기 | 규제기관과 수사기관이 AI 기반 사칭/금융사기를 실무 이슈로 다룸 | 진입장벽이 낮아져 대규모 자동화 사기가 쉬워짐 | identity verification, user education, escalation flow |
| AI 불안/반발 | 대중 불안과 규제·노동·창작자 반발이 구조화됨 | 배포 속도보다 신뢰 확보가 더 큰 제약이 됨 | communication, governance, human override |
| 월드 모델 | world model이 로보틱스/physical AI의 핵심 기반으로 부상 | text-centric AI 한계를 넘기 위한 핵심 후보 | synthetic data strategy, embodied evaluation |
| 새로운 작전실 | 군은 생성형 AI를 지휘/상황인식/의사결정 지원에 넣기 시작 | AI의 사용처가 back-office를 넘어 command layer로 이동 | human-in-command, adversarial testing |
| 무기화된 딥페이크 | 음성복제/합성미디어 사칭이 실사례와 대응 체계로 등장 | 사회적 신뢰 자체가 공격면이 됨 | provenance, verification, response drill |
| 에이전트 오케스트레이션 | handoff, supervisor, workflow graph, sandbox형 agent stack이 제품화됨 | 성능보다 제어가능성이 경쟁력이 됨 | routing, permissions, cost control, evals |
| 중국 오픈소스 전략 | DeepSeek/Qwen 계열은 공개모델과 빠른 릴리즈로 개발자 채택 확대 중 | 성능, 비용, 생태계, 표준 선점 경쟁이 함께 진행 | open model policy, dependency review |
| AI 과학자 | 가설 생성, 문헌 탐색, 실험 제안형 시스템이 실제 연구 보조에 투입 중 | 연구 생산성 재구조화 가능성이 현실권으로 진입 | lab workflow digitization, reproducibility |

## 1. 휴머노이드 로봇 데이터

### Confirmed

- NVIDIA는 `2025-03-17/18` 공개한 GR00T N1에서 인간 시점 비디오, 실제 로봇 trajectory, 합성 데이터를 함께 사용한 휴머노이드 foundation model 방향을 제시했다.
- `2025-05-18`에는 GR00T N1.5와 synthetic motion data 생성을 위한 GR00T-Dreams를 추가 공개했다.
- Figure는 `Helix`를 통해 동일 모델 가중치로 범용 휴머노이드 제어를 시도하고 있다.
- Hugging Face `LeRobot`는 커뮤니티 기반 로봇 데이터셋 허브를 실질적 인프라로 만들고 있다.

### What It Means

- 로보틱스의 병목은 더 이상 알고리즘만이 아니라 `실세계 행동 데이터`다.
- 텍스트 인터넷처럼 대규모 공개 코퍼스가 있는 영역과 달리, 로봇은 `수집 비용`, `장비 다양성`, `라벨링 난도`, `안전성` 때문에 데이터가 매우 비싸다.
- 그래서 지금 로봇 AI 경쟁은 `누가 더 좋은 policy를 만들었는가`보다 `누가 더 풍부한 행동 데이터 플라이휠을 갖고 있는가`에 가깝다.

### Interpretation

- 향후 1~2년은 휴머노이드 로봇 그 자체보다, `작업 시연 데이터 인프라`, `원격조작 인프라`, `시뮬레이션/합성 데이터` 툴체인이 더 큰 전략 자산이 될 가능성이 높다.

### What To Prepare

- 사람의 작업 동작을 구조화해 수집할 수 있는 internal data pipeline
- 시뮬레이션에서 먼저 학습하고 실기로 옮기는 sim2real 전략
- 센서/동작/실패 로그를 표준 포맷으로 남기는 로보틱스 observability 체계

## 2. LLMs+

### Confirmed

- OpenAI는 `2025-05-21` Responses API 업데이트에서 MCP, image generation, code interpreter, file search, background mode, reasoning items 등 agentic primitive를 묶어 제공했다.
- OpenAI는 `2026-04-15` Agents SDK 업데이트에서 controlled sandbox, filesystem 작업, long-horizon task, configurable memory를 강조했다.
- Anthropic은 tool use와 agent/tool 문서를 통해 모델을 독립 답변 엔진이 아니라 도구 호출 엔진으로 다루는 패턴을 공식화했다.

### What It Means

- `LLMs+`는 단순히 더 나은 LLM을 뜻하지 않는다.
- 실제 의미는 `LLM + reasoning + tool use + state + memory + multimodal + execution environment`다.
- 즉, 모델이 중앙이긴 하지만 제품 가치는 이제 모델 외부 레이어가 함께 결정한다.

### Interpretation

- 2026년의 LLM 경쟁은 foundation model benchmark 경쟁만이 아니라, 누가 더 잘 `작업을 끝내는 시스템`을 제공하느냐의 경쟁이다.
- 앞으로는 챗 인터페이스 자체보다 `모델이 외부 세계에 어떤 권한으로 접근하는가`가 핵심 차별화 포인트가 된다.

### What To Prepare

- model-native runtime 선택 기준
- tool registry와 접근권한 설계
- reasoning trace/summary/logging 정책
- failure mode별 rollback/approval flow

## 3. AI로 더 교묘해진 사기 수법

### Confirmed

- FTC는 `2025-01` AI 관련 소비자 피해를 `voice cloning`, impersonation, bogus AI business schemes, deceptive AI claims까지 포함해 실무 이슈로 다뤘다.
- FTC는 `Operation AI Comply`를 통해 AI-infused fraud와 deception을 단속 대상으로 명시했다.
- FBI는 `2026-04` AI와 암호화폐 사기가 실제로 미국인들에게 대규모 손실을 입히고 있으며, 가짜 social profile, voice clone, believable video가 결합되고 있다고 경고했다.

### What It Means

- AI는 사기꾼 입장에서 `콘텐츠 생성 속도`, `개인화 수준`, `현실감`, `다국어 대응`을 동시에 높여준다.
- 이로 인해 사기의 진입장벽이 내려가고 실험 비용이 줄어들며, 조직형 사기가 더 싸고 빠르게 반복된다.

### Interpretation

- 향후 기업과 기관의 가장 흔한 AI 리스크는 `모델이 틀린 답을 했다`보다 `사람이 AI를 이용해 더 정교한 사칭을 했다`가 될 수 있다.

### What To Prepare

- 금융/결제/민감 요청 시 voice-only 승인 금지
- 고위험 요청에 대한 out-of-band verification
- 사용자/임직원 대상 deepfake/voice clone 대응 교육
- 보안팀과 고객지원팀의 공통 incident script

## 4. AI 불안/반발

### Confirmed

- Pew는 `2026-03-12` 발표에서 `2025-06` 조사 기준 미국 성인의 절반이 AI 확산에 대해 `더 우려된다`고 답했다고 정리했다.
- 같은 흐름에서 Pew는 대중이 AI의 창의성, 인간관계, 자율성 훼손 가능성에 대해 지속적으로 경계하고 있음을 보여준다.
- 글로벌 조사에서도 국가별 강도 차이는 있지만 AI에 대한 `excited`보다 `concerned`가 강한 집단이 구조적으로 존재한다.

### What It Means

- AI 불안은 추상적 감정이 아니라 실제 채택 속도, 노동 협상, 창작자 저항, 브랜드 신뢰, 규제 압력에 영향을 주는 배포 변수다.
- MIT 기사에서 `AI가 만든 불안의 시대`와 `반발`이 분리되어 보인 것도, 정서적 거부감과 조직화된 저항이 서로 다른 층위라는 점을 보여준다.

### Interpretation

- 기술적으로 가능한 것과 조직이 받아들이는 것은 다르다.
- AI 도입의 병목은 점점 모델 품질이 아니라 `설명 가능성`, `통제 가능성`, `노동 영향`, `인간 역할 재정의`가 된다.

### What To Prepare

- 내부 커뮤니케이션: 무엇을 자동화하고 무엇은 인간 승인형으로 유지하는지 명확히 설명
- 외부 커뮤니케이션: 고객/사용자에게 AI 사용 범위와 책임 경계를 명시
- 인력 전략: 대체 담론 대신 역할 재설계와 재교육 로드맵 제시

## 5. 월드 모델

### Confirmed

- Google DeepMind는 `2024-12-04` Genie 2를 `large-scale foundation world model`로 공개했고, action-controllable 3D environments 생성 가능성을 제시했다.
- NVIDIA는 `2025-01-06` Cosmos를 `world foundation model platform for physical AI`로 공개하며 world model을 physical AI의 기반으로 위치시켰다.
- Google은 이후 Gemini Robotics, Genie 3 등으로 embodied AI와 world model 계열 연구를 확장했다.

### What It Means

- world model은 단순 비디오 생성이 아니라 `행동 결과를 예측 가능한 환경 모델`을 뜻한다.
- 이는 로봇, 자율주행, embodied agent 학습에서 실제 환경 데이터를 완전히 대체하지는 못하더라도, 데이터 증강과 평가 환경으로 큰 역할을 할 수 있다.

### Interpretation

- LLM이 언어적 세계 모델이라면, world model은 물리적/공간적/행동적 세계 모델이다.
- 2026년 이후 AI의 큰 확장 중 하나는 이 두 층을 연결하는 것이다.

### What To Prepare

- 시뮬레이션 친화적 문제 정의
- synthetic data와 real-world data의 검증 루프
- world model 기반 평가가 실제 성능을 얼마나 대변하는지 측정하는 benchmark

## 6. 새로운 작전실

### Confirmed

- DoD는 `2023-08-10` generative AI task force를 출범시켜 전 부문 use case를 검토하기 시작했다.
- Pentagon은 `2024-02-21`과 `2025-08-27` 발표를 통해 AI를 decision advantage, warfighting support, modeling and simulation의 핵심으로 설명했다.
- DARPA SABER는 battlefield AI 시스템에 대한 adversarial robustness와 operational red teaming을 공식 프로그램으로 두고 있다.

### What It Means

- 군사 분야에서 AI는 더 이상 단순 후방업무 자동화가 아니라 `상황 인식`, `정보 결합`, `판단 보조`, `의사결정 속도 향상` 문제로 이동 중이다.
- 이때 핵심 쟁점은 성능 그 자체보다 `적대적 교란`, `신뢰성`, `인간 지휘권`, `검증 가능성`이다.

### Interpretation

- 민간 영역에서도 고위험 운영 환경에서는 같은 질문이 반복될 것이다.
- 즉, AI는 추천 엔진에서 끝나지 않고 `decision room` 안으로 들어오며, 그 순간 오류 비용이 급격히 커진다.

### What To Prepare

- high-stakes AI에 대한 human-in-command 원칙
- adversarial red teaming
- provenance와 audit trail 확보
- 의사결정 지원과 자동 결정을 엄격히 구분하는 정책

## 7. 무기화된 딥페이크

### Confirmed

- NIST는 2025년 deepfake detection/evaluation 문제를 공식 연구 주제로 다루고 있다.
- FBI는 `2025` senior U.S. officials impersonation 사례에서 AI-generated voice messages를 명시적으로 경고했다.
- FTC는 deepfakes와 voice clones가 사칭, 갈취, 금융사기에 쓰일 수 있음을 이미 사업자/소비자 가이드 차원에서 다뤘다.

### What It Means

- 딥페이크는 더 이상 `가짜 영상`만의 문제가 아니다.
- 음성, 이미지, 문서, 문자, 소셜 계정이 결합된 다중채널 사칭으로 진화하고 있으며, 실제 피해는 금융 손실과 평판 손상, 정책 오판으로 나타난다.

### Interpretation

- 조직의 공격면이 `시스템 취약점`에서 `신뢰 취약점`으로 확장되고 있다.
- 가장 위험한 deepfake는 눈에 띄게 정교한 영상이 아니라, 짧은 음성 메시지와 plausible context를 결합한 low-friction 사칭일 수 있다.

### What To Prepare

- 임원/재무/HR 관련 고위험 요청에 대한 검증 프로토콜
- media provenance와 내부 발신자 검증 관행
- 외부 커뮤니케이션용 incident response 문안

## 8. 에이전트 오케스트레이션

### Confirmed

- OpenAI는 Agents SDK와 Responses API를 통해 handoff, tools, traces, sandbox execution, memory를 공식 제품 축으로 제시하고 있다.
- LangGraph는 graph 기반 multi-agent orchestration을 전면에 내세우고 있다.
- Microsoft AutoGen은 multi-agent conversation 프레임워크를 공개적으로 발전시켜 왔다.

### What It Means

- agent orchestration은 프롬프트 엔지니어링의 연장이 아니다.
- 본질은 `어떤 agent가 어떤 맥락을 들고 어떤 도구를 언제 쓰며, 어떤 조건에서 다른 agent나 인간에게 넘기느냐`의 문제다.

### Interpretation

- 멀티에이전트는 parallelizable task에서는 강점을 보일 수 있지만, sequential dependency가 강한 업무에서는 오히려 복잡도와 비용을 늘릴 수 있다.
- 따라서 모든 문제를 swarm으로 푸는 것이 아니라 `supervisor`, `specialist`, `approval checkpoint`를 설계하는 편이 중요하다.

### What To Prepare

- 단일 agent와 multi-agent를 구분해 쓰는 기준
- 권한과 도구 범위 최소화
- trace, eval, rollback을 포함한 운영 체계
- 비용/지연/정확도 간 tradeoff 측정

## 9. 중국의 오픈소스 전략

### Confirmed

- DeepSeek는 V3, R1 계열을 공개 리포지토리와 문서, permissive license 전략으로 밀고 있다.
- DeepSeek는 공개 문서에서 스스로를 open-source approach를 따르는 AGI 연구팀으로 규정한다.
- Qwen 계열도 `2026-02-16` Qwen3.5 공개, `2026-04-22` Qwen3.6-27B 공개 등 빠른 cadence로 open weights를 내놓고 있다.

### What It Means

- 중국계 모델 전략은 `폐쇄형 모델과 같은 성능을 싼 비용으로 준다`는 차원을 넘어선다.
- 더 중요한 것은:
  - 개발자 친화적 배포
  - 빠른 릴리즈 주기
  - open weights 기반 fine-tuning 가능성
  - ecosystem mindshare 확대

### Interpretation

- 이는 단순 기술 공개가 아니라 `표준/생태계/의존성` 경쟁이다.
- 향후 기업은 모델 선택 시 `성능`과 `비용`만이 아니라:
  - 법적/지정학적 리스크
  - 공급망 의존성
  - 내부 보안 검토 가능성
  - 장기 유지보수 가능성
  를 함께 봐야 한다.

### What To Prepare

- open model intake policy
- 모델 provenance와 license 검토
- 고위험 환경에서의 자체 호스팅/격리 여부 판단
- vendor-neutral architecture 확보

## 10. AI 과학자

### Confirmed

- Google Research는 `2025-02-19` AI co-scientist를 공개하며 hypothesis generation, literature synthesis, protocol drafting을 돕는 multi-agent 시스템을 제시했다.
- FutureHouse는 `2025-05-01` scientific agents 플랫폼을 공개했고, `2025-11-05` Edison Scientific spinout까지 전개했다.
- Sakana AI는 `2026-03-26` Nature 게재와 함께 AI Scientist 방향을 다시 강조했다.
- OpenAI도 `OpenAI for Science`를 통해 과학 연구 가속화에 초점을 맞춘 프로그램과 성과를 전면화하고 있다.

### What It Means

- AI scientist는 아직 인간 과학자를 대체하는 완결된 자율 연구자가 아니라,
  - 문헌 탐색
  - 연구 질문 구조화
  - 가설 제안
  - 실험/분석 계획 초안
  - 일부 코딩/분석 자동화
  영역에서 먼저 실제 가치를 내고 있다.

### Interpretation

- 과학 연구에서 AI의 병목은 모델 성능만이 아니다.
- 실험 데이터 구조화, 문헌 접근성, 랩 워크플로우 디지털화, 재현성 문화가 함께 갖춰져야 생산성 향상이 현실화된다.

### What To Prepare

- 연구 노트, 문헌, 실험 로그의 구조화
- hypothesis-to-experiment workflow의 디지털화
- 인간 검토자와 AI 연구 보조자의 역할 분담
- reproducibility와 citation discipline

## Cross-Cutting Implications

### 1. 데이터 moat의 형태가 바뀐다

- 공개 웹 텍스트는 점점 commoditized된다.
- 앞으로 경쟁력은 행동 데이터, 실험 데이터, 작업 로그, 도메인 메모리, 상호작용 기록처럼 쉽게 복제되지 않는 데이터에서 나온다.

### 2. 모델보다 실행 환경이 더 중요해진다

- 좋은 모델을 쓰는 것만으로는 차별화가 어렵다.
- 차별화는 `어떤 도구를`, `어떤 권한으로`, `어떤 검증 절차 아래`, `어떤 데이터에 붙여` 쓰는가에서 나온다.

### 3. 신뢰 인프라가 제품 인프라가 된다

- deepfake, 사칭, agent autonomy, military decision support가 모두 보여주는 것은 같은 문제다.
- 신뢰성, provenance, auditability, human override는 더 이상 compliance 부속물이 아니라 핵심 아키텍처 요소다.

### 4. 오픈 생태계는 선택지가 아니라 전략 변수다

- 비용 문제 때문에라도 많은 조직이 open model을 계속 실험할 것이다.
- 따라서 `무조건 금지` 또는 `무조건 채택`이 아니라, 사용 범주와 통제 경계를 나누는 정책이 필요하다.

## What To Prepare

## 30-90 Days

- 고위험/저위험 AI 업무를 분리한 사용 정책 수립
- 사칭/음성복제/딥페이크 incident playbook 작성
- 내부 agent pilot 1~2건 설계:
  - 문서 분석
  - 리서치
  - 코드/운영 보조
- 데이터 자산 후보 정의:
  - 작업 로그
  - 센서 데이터
  - 연구 노트
  - 의사결정 이력

## 3-6 Months

- agent runtime 표준화:
  - tool registry
  - permission model
  - logging / tracing
  - approval gates
- open model governance 초안 수립
- AI-assisted scientific workflow 또는 technical research workflow 소규모 적용

## 6-12 Months

- synthetic data / simulation 전략 수립
- provenance, watermarking, verification 체계 도입 여부 결정
- 멀티에이전트 운영 메트릭 구축:
  - task completion
  - failure mode
  - retry rate
  - human override rate
  - cost per successful task

## Final View

MIT Technology Review의 이번 리스트는 2026년 AI를 `모델 업그레이드의 연속`으로 보지 말라고 경고한다. AI는 지금 다음 세 방향으로 동시에 이동하고 있다.

1. 물리 세계로 이동한다.
2. 시스템과 오케스트레이션으로 이동한다.
3. 신뢰, 안보, 사회적 수용성의 문제로 이동한다.

따라서 앞으로의 핵심 질문은 `어떤 모델을 쓸까?`가 아니다. 더 중요한 질문은 다음과 같다.

- 어떤 데이터가 우리 조직의 진짜 경쟁력인가?
- 어떤 업무까지 agent에게 맡길 것인가?
- 어떤 승인, 검증, 로그가 있어야 안전한가?
- 어떤 오픈 생태계에 어느 정도 의존할 것인가?
- 연구와 실험의 생산성을 AI로 어디까지 재구성할 것인가?

2026년 AI 전략은 model adoption 전략이 아니라 `execution system strategy`가 되고 있다.

## External References

### MIT Technology Review Korea

- [‘지금 AI 분야에서 주목해야 할 10대 키워드’ 21일 첫 공개](https://www.technologyreview.kr/%EC%A7%80%EA%B8%88-ai-%EB%B6%84%EC%95%BC%EC%97%90%EC%84%9C-%EC%A3%BC%EB%AA%A9%ED%95%B4%EC%95%BC-%ED%95%A0-10%EB%8C%80-%ED%82%A4%EC%9B%8C%EB%93%9C-21%EC%9D%BC-%EC%B2%AB-%EA%B3%B5%EA%B0%9C/)
- [지금 AI 분야에서 주목해야 할 10대 키워드](https://www.technologyreview.kr/%EC%A7%80%EA%B8%88-ai-%EB%B6%84%EC%95%BC%EC%97%90%EC%84%9C-%EC%A3%BC%EB%AA%A9%ED%95%B4%EC%95%BC-%ED%95%A0-10%EB%8C%80-%ED%82%A4%EC%9B%8C%EB%93%9C/)

### Physical AI / Robotics

- [NVIDIA Isaac GR00T N1](https://research.nvidia.com/publication/2025-03_nvidia-isaac-gr00t-n1-open-foundation-model-humanoid-robots)
- [NVIDIA Isaac GR00T N1 release](https://nvidianews.nvidia.com/news/nvidia-isaac-gr00t-n1-open-humanoid-robot-foundation-model-simulation-frameworks)
- [Figure Helix](https://www.figure.ai/news/helix)
- [LeRobot datasets](https://huggingface.co/lerobot/datasets)

### World Models

- [Genie 2](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/)
- [Genie](https://deepmind.google/research/publications/genie-generative-interactive-environments/)
- [NVIDIA Cosmos paper](https://research.nvidia.com/publication/2025-01_cosmos-world-foundation-model-platform-physical-ai)
- [NVIDIA Cosmos blog](https://blogs.nvidia.com/blog/cosmos-world-foundation-models/)

### Agent Systems / LLMs+

- [OpenAI Responses API tools](https://openai.com/index/new-tools-and-features-in-the-responses-api/)
- [OpenAI Agents SDK update](https://openai.com/index/the-next-evolution-of-the-agents-sdk)
- [OpenAI Agents SDK docs](https://platform.openai.com/docs/guides/agents-sdk/)
- [Anthropic tool use docs](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use)
- [LangGraph](https://www.langchain.com/langgraph)
- [Microsoft AutoGen](https://www.microsoft.com/en-us/research/?p=962712)

### Safety / Security / Social Reaction

- [FTC AI risk](https://www.ftc.gov/policy/advocacy-research/tech-at-ftc/2025/01/ai-risk-consumer-harm)
- [FTC Operation AI Comply](https://consumer.ftc.gov/consumer-alerts/2024/09/operation-ai-comply-detecting-ai-infused-frauds-and-deceptions)
- [FBI AI scams](https://www.fbi.gov/news/press-releases/cryptocurrency-and-ai-scams-bilk-americans-of-billions)
- [NIST deepfake evaluation](https://www.nist.gov/publications/guardians-forensic-evidence-evaluating-analytic-systems-against-ai-generated-deepfakes)
- [NIST deepfake awareness note](https://www.nist.gov/document/deepfake-desktop-version)
- [FBI malicious messaging / AI-generated voice](https://www.fbi.gov/investigate/cyber/alerts/psa/senior-us-officials-impersonated-in-malicious-messaging-campaign)
- [Pew AI sentiment overview](https://www.pewresearch.org/short-reads/2026/03/12/key-findings-about-how-americans-view-artificial-intelligence/)
- [Pew global concern/excitement](https://www.pewresearch.org/global/2025/10/15/concern-and-excitement-about-ai/)

### Military / National Security

- [DoD generative AI task force](https://www.defense.gov/News/Release/Release/Article/3489803/dod-announces-establishment-of-generative-ai-task-force/)
- [Pentagon AI vision](https://www.defense.gov/News/News-Stories/Article/article/3682355/pentagon-official-lays-out-dod-vision-for-ai/)
- [AI and future warfighting](https://www.defense.gov/News/News-Stories/Article/Article/4287970/dod-official-says-ai-other-innovations-will-transform-future-warfighting/)
- [DARPA SABER](https://www.darpa.mil/research/programs/saber-securing-artificial-intelligence)

### Open Models / China

- [DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3)
- [DeepSeek-R1 release](https://api-docs.deepseek.com/news/news250120)
- [DeepSeek algorithm disclosure](https://cdn.deepseek.com/policies/en-US/model-algorithm-disclosure.html)
- [Qwen3 repo](https://github.com/QwenLM/Qwen3)
- [Qwen research hub](https://qwen.ai/research/)
- [Qwen 3.6-27B release](https://qwen.ai/blog?id=qwen3.6-27b)

### AI for Science

- [Google AI co-scientist](https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist)
- [Google summary page](https://blog.google/feed/google-research-ai-co-scientist/)
- [FutureHouse platform](https://www.futurehouse.org/research-announcements/launching-futurehouse-platform-ai-agents?_bhlid=b2b50af9254da4cf97bbad70959795fa728b14f6)
- [FutureHouse Edison Scientific](https://www.futurehouse.org/research-announcements/announcing-edison-scientific)
- [Sakana AI Scientist](https://sakana.ai/ai-scientist-nature/)
- [OpenAI for Science](https://openai.com/science/)
