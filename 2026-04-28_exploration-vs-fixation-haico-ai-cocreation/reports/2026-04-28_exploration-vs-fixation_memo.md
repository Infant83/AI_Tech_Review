# 발산을 먼저 설계해야 AI 협업이 덜 좁아진다

date: 2026-04-28
source: Wen et al., arXiv:2512.18388v2
status: memo

## 요약

- 이 논문은 ChatGPT 같은 즉시 실행형 인터페이스가 사용자를 초기 산출물에 고정시킬 수 있다고 본다. 문제의 중심은 모델 성능보다 작업 순서다.
- HAICo는 이미지를 바로 만들기 전에 원격 개념을 끌어온 idea card를 먼저 제시하고, 이후 선택한 방향을 semantic parameter로 다듬는다.
- 실험은 작지만 결과는 일관된다. HAICo는 ChatGPT보다 usability, creativity support, novelty, diversity에서 높았다. Fluency와 usefulness는 유의미한 차이가 없었다.
- 사용자는 AI에게 최종안을 바로 묻기보다, 먼저 가능한 방향을 펼치고, 기준을 세워 고르고, 선택한 방향만 실행해야 한다.
- 조직 단위에서는 같은 모델과 비슷한 프롬프트가 결과물의 동질화를 만들 수 있다. 개인 생산성과 집단 다양성은 따로 관리해야 한다.

## 판단

이 논문이 주는 실무 메시지는 간단하다. AI를 잘 쓰는 사람은 더 긴 프롬프트를 쓰는 사람이 아니다. 산출물을 만들기 전에 탐색판을 만들고, 실행 전에 선택 기준을 드러내는 사람이다.

ChatGPT식 흐름은 빠르다. 사용자가 한 문장을 입력하면 바로 결과물이 나온다. 이 속도는 초안이 필요한 작업에는 유리하다. 다만 창의적 문제에서는 첫 결과물이 기준점이 된다. 이후 사용자는 새로운 방향을 찾기보다 기존 결과물을 조금씩 고치는 쪽으로 끌려간다.

HAICo는 이 지점을 인터페이스로 막는다. 먼저 여러 개념 방향을 카드로 펼치고, 사용자가 고른 뒤에야 이미지를 생성한다. 수정 단계에서도 "더 생동감 있게" 같은 모호한 말을 바로 실행하지 않고, 어떤 요소를 어떤 방식으로 바꿀지 선택 가능한 매개변수로 보여준다. 사용자는 AI의 해석을 실행 전에 볼 수 있다.

## 실무 적용

1. 아이디어 작업은 `탐색 -> 선택 -> 실행 -> 감사` 순서로 나눈다.
2. 첫 요청은 "서로 멀리 떨어진 방향 7-9개를 카드로 만들어줘"로 시작한다. "최종안을 만들어줘"는 선택 이후 단계에 둔다.
3. 각 카드에는 출처 영역, 아이디어, 적용 방식, 위험을 함께 적게 한다.
4. 실행 전에는 선택 기준을 만든다. 참신성, 사용성, 구현 난이도, 브랜드 적합성 같은 기준이 필요하다.
5. 수정 요청은 형용사 한두 개로 끝내지 않는다. 변경할 요소와 가능한 옵션을 먼저 표로 뽑는다.
6. 팀에서는 서로 다른 AI persona, 출처 영역, 제약 조건을 나눠야 결과물이 덜 비슷해진다.

## 주의할 점

- 논문 표본은 24명이고, 주로 CS/IT 배경이며, 과제는 포스터 이미지 생성이다.
- HAICo의 학습 효과는 자기보고 중심이다. 장기 효과는 아직 확인되지 않았다.
- 사용자가 이미 목표와 형식을 정확히 알고 있다면 ChatGPT식 직접 실행도 효율적이다.
- 스캐폴딩이 많아지면 속도와 주도감이 떨어질 수 있다.

## 참고 링크

- [Exploration vs. Fixation - arXiv](https://arxiv.org/abs/2512.18388)
- [The Effects of Generative AI on Design Fixation and Divergent Thinking](https://arxiv.org/abs/2403.11164)
- [Generative AI enhances creativity but reduces diversity](https://arxiv.org/abs/2312.00506)
- [Homogenization Effects of LLMs](https://arxiv.org/abs/2402.01536)
- [Stanford d.school prototyping summary](https://dlibrary.stanford.edu/questions/why-does-building-and-testing-prototypes-help-you-get-to-a-good-solution)
