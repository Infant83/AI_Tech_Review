---
title: Style Harness Revision Diagnosis
date: 2026-05-09
topic: ai-updates-weekly
status: applied
---

# Style Harness Revision Diagnosis

## 진단

이번 재검토에서 확인한 문제는 단순한 문장 어색함보다 더 깊다. 초반 도입부는 독자 장면으로 잘 열렸지만, 본문이 진행될수록 작업자가 자료를 어떻게 분류했는지 설명하는 문장이 다시 앞에 섰다. 이때 문장은 자연스럽게 보이더라도 독자에게는 `AI가 리포트 구조를 설명하는 문장`처럼 읽힌다.

대표 문제:

- `그 작업 구조를 이 리뷰에서는 하네스라고 부르겠습니다.`
  - 하네스가 업계에서 이미 쓰이는 말인데, 리뷰 내부에서 임의로 붙인 정의처럼 보인다.
- `먼저 붙잡을 문장은 이것입니다.`
  - 독자에게 읽기 방식을 지시하는 생성형 진행 멘트처럼 들린다.
- `이 변화는 한 회사의 제품 발표만으로 보기는 어렵습니다.`
  - 근거 범위를 방어하는 문장이 섹션의 주제를 늦게 꺼낸다.
- `참고자료로 본 쟁점`
  - 작업자가 자료를 어떻게 묶었는지에 초점이 가고, 독자가 가져갈 메시지가 약해진다.

## 개선 원칙

1. 기술어는 `내가 정의`하지 않고 `현재 쓰이는 맥락`을 설명한다.
   - 예: `이러한 에이전트의 작업을 실행하고, 검증하고, 제어하는 구조를 보통 하네스라고 부릅니다.`
   - 필요한 경우 `test harness -> LLM evaluation harness -> agent harness` 계보를 짧게 붙인다.

2. 섹션 첫 문장은 방어가 아니라 주제를 말한다.
   - 피함: `이 변화는 한 회사의 발표만으로 보기는 어렵습니다.`
   - 사용: `논문, 공식 발표, 제품 문서, 저장소를 같이 읽으면 관심의 위치가 달라졌음을 느낄 수 있습니다.`

3. 제목은 작업자의 분류가 아니라 독자의 takeaway를 말한다.
   - 피함: `참고자료로 본 쟁점: 모델보다 작업 환경`
   - 사용: `AI 경쟁은 모델 바깥의 작업 환경으로 넓어지고 있습니다`

4. 친근한 진행 문장은 허용하되, 독자에게 결론을 지시하지 않는다.
   - 피함: `먼저 붙잡을 문장은 이것입니다.`
   - 사용: `요즘 에이전트 경쟁은 모델 이름만으로는 설명되지 않는 부분이 늘고 있습니다.`

## Artwork 적용 방침

그림 2의 하네스 스택은 정확한 라벨과 관계가 중요하므로 deterministic SVG가 더 적합하다. Skywork Image는 더 예쁜 포스터형 설명 이미지를 만들 수 있지만, 하네스 구성요소의 정확한 한국어 라벨과 화살표가 필요한 그림에서는 텍스트 오류 위험이 있다.

다만 다음 그림은 Skywork `인포그래픽` 후보를 만들 가치가 있다.

- `test harness -> LLM evaluation harness -> agent harness` 용어 계보형 도식
- 기업용 에이전트의 `데이터 접근 -> 산출물 작성 -> 승인 -> 감사 기록` 흐름
- AI 코딩의 `생성 -> 테스트 -> 리뷰 -> 병합 -> 되돌리기` 흐름

채택 기준은 기존 규칙과 같다. Skywork 후보는 prompt, project URL, export file, accept/reject reason을 남기고, 긴 한국어 텍스트는 이미지 안에 넣지 않는다.

## 반영한 하네스 업데이트

- `.automation/writing-style-audit-harness.md`
  - `이 리뷰에서는 ...라고 부르겠습니다`
  - `먼저 붙잡을 문장은 이것입니다`
  - `한 회사의 제품 발표만으로 보기는 어렵습니다`
  - 위 패턴을 금지/주의 대상으로 추가.
- `.automation/editorial-graphics-audit-harness.md`
  - 핵심 용어 계보형 도식 규칙 추가.
- `ai-tech-review-editorial-harness`
  - established field term을 리뷰 내부 정의처럼 쓰지 않는 규칙 추가.
  - audit script에 새 AI cadence pattern 추가.
- `.automation/editorial-reference-pool.md`
  - Quanta Magazine, 고등과학원 HORIZON, 최종현학술원 Science Note를 AI_Tech_Review의 기본 글쓰기/시각 자료 레퍼런스풀로 등록.
  - 각 매체를 모방하지 않고, Quanta의 article-grade figure, HORIZON의 한국어 과학 설명 리듬, Science Note의 시의성 있는 뉴스레터형 프레이밍을 목적별로 참고하도록 정리.
