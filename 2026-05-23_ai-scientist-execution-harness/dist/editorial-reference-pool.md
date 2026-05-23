---
title: AI_Tech_Review Editorial Reference Pool
date: 2026-05-09
status: active
scope:
  - reports/*_final_review.md
  - artifacts/final_review/figures/
  - skywork_inputs/
tags:
  - writing
  - visual-style
  - reference-pool
---

# AI_Tech_Review Editorial Reference Pool

이 문서는 `AI_Tech_Review` 리뷰의 글쓰기와 시각 자료를 점검할 때 참고할 외부 편집 스타일 풀입니다. 특정 매체를 모방하기 위한 문서가 아닙니다. 좋은 과학·기술 글쓰기의 공통 원칙을 AI 기술 리뷰에 맞게 빌려오기 위한 기준입니다.

## 등록 레퍼런스

| 매체 | 참고할 지점 | AI_Tech_Review 적용 방식 |
|---|---|---|
| [Quanta Magazine](https://www.quantamagazine.org/) | 추상적인 수학·물리·컴퓨터과학 주제를 강한 hero illustration, 간결한 dek, 중간 figure로 풀어가는 방식 | 추상 AI 개념을 article-grade hero와 정확한 caption으로 열 때 참고합니다. 단, AI_Tech_Review는 내부 기술 검토 독자를 고려해 결론과 참고자료를 더 빨리 보여줍니다. |
| [고등과학원 HORIZON](https://horizon.kias.re.kr/) | 한국어 대중 과학 글에서 일상 장면, 질문, 전문 개념, 연구 맥락을 자연스럽게 이어가는 방식 | 친근한 질문과 쉬운 예시를 쓰되, 기술적 엄밀성을 잃지 않는 한국어 설명 리듬을 참고합니다. 세부 패턴은 [horizon-style-patterns](./horizon-style-patterns.md)에 누적합니다. |
| [최종현학술원 Science Note 과학노트](https://www.chey.org/Kor/ScienceNote/ScienceNoteList.aspx) | `요주의 과학`처럼 시의성 있는 과학기술 주제를 짧고 선명한 제목, 뉴스레터형 호흡, 정책/사회적 맥락과 함께 소개하는 방식 | AI 기술동향을 산업·정책·조직 의사결정 맥락과 연결할 때 참고합니다. 제목은 독자가 바로 가져갈 질문이나 변화로 잡습니다. |

## 공통 원칙

1. 독자가 아는 장면에서 시작합니다.
   - 좋은 글은 쉬운 비유로 시작해도 개념을 얕게 만들지 않습니다.
   - 업무, 실험, 문서 검토, 코드 리뷰, 제품 운영처럼 독자가 떠올릴 수 있는 장면을 먼저 둡니다.

2. 전문 용어는 늦게 숨기지 않고, 처음 등장할 때 짧게 해체합니다.
   - `하네스`, `connector`, `memory`, `orchestration`처럼 글의 판단을 바꾸는 용어는 첫 등장 문단에서 설명합니다.
   - 이미 통용되는 용어는 리뷰 안에서 새로 정의하지 않고, 현재 쓰임과 짧은 계보를 제시합니다.

3. 제목은 작업자의 분류보다 독자의 takeaway를 먼저 말합니다.
   - 피함: `참고자료로 본 쟁점`
   - 권장: `AI 경쟁은 모델 바깥의 작업 환경으로 넓어지고 있습니다`

4. 그림은 장식보다 이해 장치에 가깝게 씁니다.
   - Quanta식 hero는 주제를 열고, Horizon식 도입 그림은 개념을 친근하게 만들고, Science Note식 카드/뉴스레터 감각은 시의성을 잡는 데 씁니다.
   - 도식은 실제 가독성을 확인합니다. 긴 문장, 작은 글자, 겹치는 화살표가 있으면 실패입니다.

5. 한국어 문장은 주어와 행위 주체를 정확히 둡니다.
   - 에이전트가 하는 일, 하네스가 제공하는 구조, 사람이 승인하는 일, 조직이 정하는 정책을 섞지 않습니다.

## 사용 절차

리뷰 초안 또는 재작성 전에 아래를 결정합니다.

| 점검 항목 | 질문 |
|---|---|
| Quanta 참고 | 이 글에 필요한 hero나 중간 figure는 무엇인가? 추상 개념을 어떤 장면으로 보여줄 수 있는가? |
| HORIZON 참고 | 독자가 들어올 수 있는 한국어 질문이나 일상/업무 장면은 무엇인가? |
| Science Note 참고 | 이 기술 변화가 지금 왜 중요하고, 조직·산업·정책 맥락에서는 어떤 질문으로 읽히는가? |

리뷰 후에는 아래를 확인합니다.

- 도입부가 독자 장면에서 시작하는가?
- 기술어가 쉽게 해체되었는가?
- 제목이 독자의 takeaway를 말하는가?
- figure가 실제 화면에서 읽히는가?
- 글이 매체 흉내에 머물지 않고 AI_Tech_Review의 기술 검토 목적에 맞게 정리되었는가?

## 주기적 갱신

- 월 1회 HORIZON 최신 글 3편을 확인하고, 새로 배울 만한 도입·전환·전문용어 설명 패턴을 [horizon-style-patterns](./horizon-style-patterns.md)에 추가합니다.
- 분기 1회 Quanta와 Science Note도 함께 훑어 figure 배치와 뉴스레터형 프레이밍을 점검합니다.
- 특정 리뷰 작성 전에는 해당 주제와 가까운 글만 빠르게 참고합니다. 모든 리뷰에서 외부 스타일 분석을 길게 반복하지 않습니다.
