---
title: MIT AI 10 Keywords Memo
date: 2026-04-24
topic: mit-ai-10-keywords
tags:
  - memo
  - ai
  - strategy
  - mit-technology-review
---

# MIT Technology Review `AI 10대 키워드` 메모

## Summary

- 2026년 AI의 핵심은 더 이상 `좋은 모델이 하나 나왔다`가 아니다. `데이터`, `도구`, `오케스트레이션`, `보안`, `사회적 반발`, `물리 세계`, `과학 자동화`가 동시에 재편되고 있다.
- MIT Technology Review가 제시한 키워드는 서로 별개가 아니라, `텍스트 AI -> 시스템 AI -> 물리/사회/과학으로 확장되는 전환기`를 보여주는 묶음으로 읽는 편이 맞다.
- 지금 준비해야 하는 것은 새로운 모델 하나를 도입하는 일이 아니라, `신뢰 가능한 agent stack`, `고유 데이터 확보`, `합성미디어 대응`, `오픈모델 활용 원칙`, `도메인 연구 자동화 기반`을 미리 갖추는 일이다.

## 한 줄 해석

2026년의 AI 경쟁축은 `모델 성능`에서 `현실 세계에 안전하게 붙는 운영 시스템`으로 이동하고 있다.

## 10개 키워드를 다시 묶으면

### 1. 물리 세계로 가는 AI

- 휴머노이드 로봇 데이터
- 월드 모델

핵심:
- 텍스트/이미지 데이터만으로는 다음 단계가 어렵다.
- 사람의 움직임, 센서 로그, 시뮬레이션, 합성 데이터가 새로운 전략 자산이 되고 있다.

### 2. 포스트-LLM 시스템화

- LLMs+
- 에이전트 오케스트레이션
- AI 과학자

핵심:
- 단일 모델보다 `모델 + 도구 + 메모리 + 샌드박스 + 평가 + 관찰가능성`이 더 중요해졌다.
- 성능은 모델에서 나오고, 가치와 실패는 오케스트레이션에서 나온다.

### 3. 악용과 신뢰의 전장

- AI로 더 교묘해진 사기 수법
- 무기화된 딥페이크
- 새로운 작전실
- AI 불안/반발

핵심:
- AI는 이제 productivity 도구이면서 동시에 사회공학, 심리 조작, 정보전, 지휘지원의 도구가 되었다.
- 따라서 `배포`보다 `신뢰 인프라`가 더 중요해진다.

### 4. 생태계와 지정학

- 중국의 오픈소스 전략

핵심:
- 오픈 웨이트 공개는 단순 기술 공유가 아니라 개발자 채택, 비용 구조, 표준, 공급망 지배력 경쟁이다.

## 지금 시점의 핵심 판단

### Confirmed

- 로보틱스와 physical AI는 `실세계 데이터 부족`을 시뮬레이션/합성 데이터로 메우는 방향으로 빠르게 움직이고 있다.
- frontier AI는 단일 모델 제품이 아니라 에이전트 실행 환경과 도구 호출 체계까지 포함하는 방향으로 이동 중이다.
- 합성미디어 기반 사기와 딥페이크 악용은 이미 규제기관과 수사기관이 실무 이슈로 다루는 단계에 들어갔다.
- 중국계 오픈모델은 글로벌 개발자 채택과 비용 효율성 측면에서 무시하기 어려운 존재가 되었다.
- 과학 연구용 AI는 `문헌 탐색`, `가설 생성`, `실험 제안`에서 실질적 가치가 나타나기 시작했다.

### Interpretation

- 앞으로 경쟁력은 `최고 모델 접근권`만으로는 부족하고, `내부 데이터 + 실행 환경 + 통제 체계 + 도메인 워크플로우`를 얼마나 빨리 묶느냐에 좌우될 가능성이 크다.
- 기업은 단일 챗봇 전략보다 `고위험 업무는 제약형`, `저위험 탐색은 개방형`으로 스택을 분리해야 할 가능성이 높다.

### Open Questions

- 멀티에이전트 시스템의 안정성과 비용은 어디까지 생산적으로 통제 가능한가?
- 오픈모델 채택이 가져오는 지정학/보안/컴플라이언스 비용은 어떻게 계량할 것인가?
- scientific agent가 실제 연구 생산성을 높이는 조건은 무엇이며, 어떤 분야부터 먼저 효과가 나는가?

## 앞으로 고민해야 할 질문

1. 우리 조직의 `고유 데이터 moat`는 무엇인가?
2. agent를 도입할 때 어떤 업무는 자동화하고 어떤 업무는 인간 승인형으로 남길 것인가?
3. deepfake/voice clone/사칭에 대응하는 검증 루틴은 준비되어 있는가?
4. 오픈모델을 도입할 때 성능이 아니라 `운영 통제 가능성`을 어떻게 평가할 것인가?
5. 연구개발 조직은 AI scientist를 어디서부터 보조 도구로 붙일 것인가?

## 준비 우선순위

### 0-30일

- agent 사용 범주를 `탐색`, `작성`, `분석`, `실행`으로 나누고 위험 등급을 매긴다.
- 사칭/딥페이크/음성복제 대응용 사용자 교육과 검증 프로토콜을 만든다.
- 조직 내에서 축적 가능한 고유 데이터셋 후보를 정리한다.

### 30-90일

- 1~2개의 업무 흐름에 대해 `모델 + 도구 + 로그 + 승인`이 포함된 agent pilot를 만든다.
- 오픈모델 사용 가이드라인과 승인 절차를 분리한다.
- 연구조직은 문헌 탐색/가설 생성용 AI 워크플로우를 소규모로 시범 적용한다.

### 3-6개월

- 멀티에이전트 실행 로그, 평가, 비용, 실패모드 리포트를 쌓는다.
- 실세계/센서/비정형 작업 데이터가 필요한 영역의 데이터 전략을 새로 설계한다.
- 외부 공개 모델 의존성과 내부 보안 요건의 균형점을 명문화한다.

## 결론

이 리스트는 `올해 유행할 기술 10개`가 아니라, `AI가 이제 어디까지 침투하고 무엇을 다시 설계하게 만드는가`에 대한 체크리스트에 가깝다. 준비의 초점은 모델 선택이 아니라, 시스템 설계와 조직 설계로 옮겨가고 있다.

## External References

- MIT Technology Review Korea:
  - [예고 기사](https://www.technologyreview.kr/%EC%A7%80%EA%B8%88-ai-%EB%B6%84%EC%95%BC%EC%97%90%EC%84%9C-%EC%A3%BC%EB%AA%A9%ED%95%B4%EC%95%BC-%ED%95%A0-10%EB%8C%80-%ED%82%A4%EC%9B%8C%EB%93%9C-21%EC%9D%BC-%EC%B2%AB-%EA%B3%B5%EA%B0%9C/)
  - [본편 기사](https://www.technologyreview.kr/%EC%A7%80%EA%B8%88-ai-%EB%B6%84%EC%95%BC%EC%97%90%EC%84%9C-%EC%A3%BC%EB%AA%A9%ED%95%B4%EC%95%BC-%ED%95%A0-10%EB%8C%80-%ED%82%A4%EC%9B%8C%EB%93%9C/)
- NVIDIA:
  - [GR00T N1](https://research.nvidia.com/publication/2025-03_nvidia-isaac-gr00t-n1-open-foundation-model-humanoid-robots)
  - [Cosmos](https://research.nvidia.com/publication/2025-01_cosmos-world-foundation-model-platform-physical-ai)
- Google:
  - [Genie 2](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/)
  - [AI co-scientist](https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist)
- OpenAI:
  - [Responses API tools](https://openai.com/index/new-tools-and-features-in-the-responses-api/)
  - [Agents SDK update](https://openai.com/index/the-next-evolution-of-the-agents-sdk)
  - [OpenAI for Science](https://openai.com/science/)
- Security / policy:
  - [FTC AI risk](https://www.ftc.gov/policy/advocacy-research/tech-at-ftc/2025/01/ai-risk-consumer-harm)
  - [FBI AI scams](https://www.fbi.gov/news/press-releases/cryptocurrency-and-ai-scams-bilk-americans-of-billions)
  - [NIST deepfake evaluation](https://www.nist.gov/publications/guardians-forensic-evidence-evaluating-analytic-systems-against-ai-generated-deepfakes)
