---
title: Harness Term Background
date: 2026-05-09
topic: ai-updates-weekly
status: reference-note
---

# Harness Term Background

이 노트는 `에이전트 하네스`라는 표현을 리뷰 본문에서 어떻게 설명할지 정리하기 위한 참고자료입니다.

## 확인한 배경

`하네스(harness)`는 이 리뷰에서 새로 만든 표현이 아니다. 소프트웨어 테스트에서는 `test harness`가 테스트 실행 엔진, 테스트 스크립트 저장소, driver/stub 등으로 구성되어 테스트 대상 소프트웨어를 실행하고 결과를 확인하는 구조를 가리킨다. [TechTarget의 test harness 설명](https://www.techtarget.com/searchsoftwarequality/definition/test-harness)은 test harness가 test drivers와 stubs, test execution engine, test script repository로 구성된다고 설명한다.

LLM 평가 문맥에서도 `harness`라는 말은 이미 널리 쓰인다. [EleutherAI Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness)는 스스로를 “language model evaluation framework”로 설명하며, 여러 모델을 같은 평가 환경에서 시험하기 위한 실행 구조로 쓰인다.

2026년 에이전트 연구에서는 이 표현이 평가 장치에서 실행·제어 구조로 확장되어 쓰인다.

- [Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723)는 에이전트 성능이 `harness engineering`에 점점 더 의존한다고 설명한다. 이 논문은 하네스 동작을 자연어로 외부화하고, 명시적 contract, durable artifact, adapter를 통해 실행하는 구조를 제안한다.
- [Meta-Harness](https://arxiv.org/abs/2603.28052)는 LLM 시스템 성능이 모델 가중치뿐 아니라 `what information to store, retrieve, and present to the model`을 정하는 harness code에 의존한다고 설명한다. 여기서 하네스는 기억, 검색, 제시, 실행 기록, 점수와 연결된 최적화 대상이다.

## 본문 표현 원칙

피해야 할 표현:

- `그 작업 구조를 이 리뷰에서는 하네스라고 부르겠습니다.`
- 이유: 하네스가 리뷰 안에서 임의로 붙인 이름처럼 보인다.

권장 표현:

- `이러한 에이전트의 작업을 실행하고, 검증하고, 제어하는 구조를 보통 하네스라고 부릅니다.`
- `원래 소프트웨어 테스트에서 test harness는 테스트를 실행하고 결과를 확인하는 장치를 가리켰고, LLM 평가와 최근 에이전트 연구에서는 모델 주변의 실행·제어 구조를 뜻하는 말로 넓게 쓰이고 있습니다.`

주의:

- `하네스라는 표현을 누가 처음 사용했다`고 단정하지 않는다. 확인 가능한 범위에서는 소프트웨어 테스트의 test harness, LLM evaluation harness, 2026년 agent harness 연구 흐름으로 이어지는 계보를 설명하는 편이 안전하다.
- 어원 설명은 길게 끌지 않는다. 리뷰의 초점은 말의 역사보다 `에이전트 활용에서 왜 검증·권한·기억·승인 구조가 중요해지는가`에 있다.
