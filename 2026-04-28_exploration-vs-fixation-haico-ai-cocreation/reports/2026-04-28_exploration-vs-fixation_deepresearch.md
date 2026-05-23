# AI 협업은 첫 산출물을 늦출수록 넓어진다

date: 2026-04-28
topic: Exploration vs. Fixation, HAICo, AI co-creation workflow
primary source: [arXiv:2512.18388v2](https://arxiv.org/abs/2512.18388)

## 요약

- Wen et al.의 HAICo 논문은 ChatGPT형 즉시 실행 인터페이스가 창의 작업에서 조기 수렴과 설계 고착을 만들 수 있다고 실험으로 다룬다.
- HAICo는 두 모드를 분리한다. Divergent mode는 이미지 생성 전 원격 개념 아이디어를 펼치고, Convergent mode는 선택한 방향을 semantic parameter로 다듬는다.
- `N = 24` within-subjects 실험에서 HAICo는 ChatGPT보다 CSI 전 차원, UMUX-Lite, novelty, diversity에서 높았다. Fluency와 usefulness는 유의미한 차이가 없었다.
- 이 결과는 AI 활용 교육의 초점을 바꾼다. 프롬프트 문장 기술보다 "탐색을 먼저 구조화하고 실행을 늦추는 작업 설계"가 중요하다.
- GenAI가 개인 결과물 품질을 올리더라도, 조직 전체 결과물은 비슷해질 수 있다. 같은 모델을 같은 방식으로 쓰면 다양성은 관리 대상이 된다.

## 1. 논문이 다룬 문제

ChatGPT 같은 챗봇 인터페이스는 사용자의 요청을 바로 결과물로 바꾼다. 이 방식은 실행 속도에 강하다. 문제는 창의 작업에서 발생한다. 사용자가 충분히 방향을 탐색하기 전에 완성된 형태를 먼저 보면, 그 산출물이 이후 판단의 기준점이 된다.

논문은 이를 두 개념으로 설명한다.

- `Premature convergence`: 충분한 탐색 전에 하나의 방향으로 빨리 수렴하는 상태.
- `Design fixation`: 처음 본 예시나 결과물의 특징에 묶여 더 넓은 대안을 보지 못하는 상태.

논문은 여기에 `gulf of envisioning`도 붙인다. 사용자는 원하는 느낌을 어렴풋이 알지만, 모델이 해석할 수 있는 구체 지시로 바꾸기 어렵다. 그래서 "더 생동감 있게" 같은 요청을 넣고, 모델이 임의로 색감이나 배경을 바꾸면 다시 고치는 루프에 들어간다.

## 2. HAICo의 설계

HAICo는 창작 과정을 두 단계로 나눈다.

| 단계 | 기능 | 사용자가 얻는 것 |
|---|---|---|
| Divergent mode | 이미지 생성 전에 idea grid를 만든다. 각 카드는 제목, 설명, thumbnail, 배경, 태그를 갖는다. | 서로 다른 개념 방향을 비교할 수 있다. |
| Convergent mode | 선택한 아이디어를 이미지로 만들고, 수정 의도를 semantic parameter와 option으로 바꾼다. | 모델이 수정 요청을 어떻게 해석하는지 실행 전에 볼 수 있다. |

Divergent mode의 특징은 원격 개념을 끌어오는 것이다. 논문은 신화, 역사적 사건, 인터넷 문화, 예술작품 같은 멀리 떨어진 영역에서 연상을 만들도록 프롬프트를 설계했다. "창의적으로 여러 개 만들어줘"라는 일반 요청보다 idea diversity가 높았다.

Convergent mode는 prompt refinement가 아니다. 사용자의 수정 의도를 매개변수로 분해한다. 예를 들어 "뒤쪽 학생들이 더 재미있는 일을 하게 해줘"라는 요청을 받으면, 시스템은 어떤 대상이 어떤 역할로 바뀔 수 있는지 옵션을 보여준다. 사용자는 실행 전에 해석을 바꿀 수 있다.

## 3. 실험 결과

논문은 24명의 참가자를 대상으로 ChatGPT와 HAICo를 같은 포스터 이미지 생성 과제에서 비교했다.

| 항목 | 결과 | 해석 |
|---|---|---|
| Creativity Support Index | HAICo가 5개 차원 모두 높음, `all p < 0.002` | 사용자는 HAICo를 창작 지원 도구로 더 강하게 평가했다. |
| UMUX-Lite | HAICo `81.25`, ChatGPT `64.24`, `p < 0.001` | 사용성 차이가 컸다. |
| Novelty | HAICo `3.22`, ChatGPT `2.41`, `p < 0.001` | 결과물 아이디어가 더 독창적이라는 평가를 받았다. |
| Diversity | HAICo `0.48`, ChatGPT `0.36`, `p = 0.001` | 참가자별 결과물 묶음이 더 다양했다. |
| Fluency / Usefulness | 유의미한 차이 없음 | HAICo가 더 많이 만들거나 더 유용한 결과를 냈다고 보기는 어렵다. |
| Refinement prompts | HAICo `1.56`, ChatGPT `2.94`, `p = 0.004` | 구조화된 수정 옵션이 시행착오를 줄였다. |
| Self-reported learning | HAICo `5.29`, ChatGPT `3.12`, `p < 0.001` | 참가자는 HAICo에서 더 많이 배웠다고 보고했다. |

학습 결과가 특히 중요하다. ChatGPT를 쓴 참가자는 도구의 행동과 프롬프트 작성법을 배웠다고 답하는 경우가 많았다. HAICo를 쓴 참가자는 과제 지식, 새로운 방향, 작업 순서를 배웠다고 답했다. 도구 사용법을 익히는 시간과 문제 자체를 이해하는 시간이 갈라진다.

## 4. 보강 근거

이 논문은 단독으로 보면 작은 실험이다. 다만 주변 연구와 맞물리면 메시지가 선명해진다.

- [Wadinambiarachchi et al. 2024](https://arxiv.org/abs/2403.11164)는 AI-generated image에 노출된 참가자가 초기 예시에 더 고착되고, 아이디어 수와 다양성, 독창성이 낮아졌다고 보고했다.
- [Doshi and Hauser 2024](https://arxiv.org/abs/2312.00506)는 GenAI가 개인의 글쓰기 창의성 평가를 높일 수 있지만, GenAI 도움을 받은 이야기들이 서로 더 비슷해지는 경향을 보였다고 보고했다.
- [Anderson, Shah, Kreminski 2024](https://arxiv.org/abs/2402.01536)는 ChatGPT 사용자가 더 많은 상세 아이디어를 만들었지만, 사용자 간 아이디어가 덜 구별되고 책임감도 낮았다고 분석했다.
- [Stanford d.school의 parallel prototyping 정리](https://dlibrary.stanford.edu/questions/why-does-building-and-testing-prototypes-help-you-get-to-a-good-solution)는 병렬 프로토타입이 serial prototype보다 더 다양하고 좋은 결과를 냈다는 Dow et al. 연구를 소개한다.
- [Parsons et al. 2021](https://arxiv.org/abs/2108.06451)은 데이터 시각화 설계에서도 fixation을 창의적 결과를 제한하는 조기 고착으로 다룬다.

보강 근거는 한 방향을 가리킨다. AI 사용자는 혼자서는 더 빠르고 그럴듯한 결과를 얻을 수 있다. 팀이나 조직 전체로 보면 결과물이 같은 방향으로 몰릴 수 있다. 탐색 폭을 의도적으로 설계하지 않으면 생산성 향상이 다양성 저하와 같이 온다.

## 5. 실무자가 바꿔야 할 AI 사용법

### 5.1 아이디어 요청을 카드화한다

처음부터 최종안을 만들지 않는다. 먼저 아이디어 카드를 만든다.

```text
아래 주제로 서로 멀리 떨어진 아이디어 카드 9개를 만들어줘.
각 카드는 title, source domain, concept, why it fits, execution hint, risk로 구성해줘.
source domain은 신화, 역사, 과학, 제품 디자인, 인터넷 문화, 업무 프로세스 등 서로 겹치지 않게 해줘.
아직 최종 문안이나 이미지는 만들지 마.
```

이 요청은 모델에게 결과를 만들지 말라는 제약을 준다. 사용자는 먼저 방향을 본다.

### 5.2 선택 기준을 먼저 쓴다

아이디어가 나온 뒤에는 기준을 만든다.

```text
위 9개 아이디어를 novelty, usefulness, feasibility, audience fit, risk 기준으로 평가해줘.
점수만 주지 말고 왜 높은지와 왜 위험한지를 한 줄씩 적어줘.
```

선택 기준 없이 바로 고르면 첫눈에 보기 좋은 방향에 끌린다. 선택 기준은 고착을 늦추는 장치다.

### 5.3 수정 요청을 매개변수로 바꾼다

수정 단계에서 "더 세련되게", "더 강하게", "덜 밋밋하게"라고 바로 실행시키지 않는다.

```text
내 수정 의도를 바로 실행하지 말고, 먼저 변경 가능한 semantic parameter 표로 분해해줘.
각 parameter는 name, current interpretation, 4 options, expected effect, possible side effect를 포함해줘.
내가 옵션을 고른 뒤에만 수정안을 만들어줘.
```

이렇게 하면 사용자는 모델의 해석을 실행 전에 볼 수 있다.

### 5.4 병렬 분기를 남긴다

ChatGPT 대화 하나에서 계속 고치면 이전 갈래가 묻힌다. 실무에서는 최소 3개 분기를 남기는 편이 낫다.

- conservative branch: 기존 요구를 안전하게 만족.
- remote branch: 멀리 떨어진 유추를 반영.
- contrarian branch: 일반적인 답을 일부러 피함.

각 분기는 별도 파일, 별도 채팅, 별도 슬라이드 섹션으로 보관한다.

### 5.5 팀에서는 다양성을 배정한다

여러 사람이 같은 모델에 같은 질문을 넣으면 결과가 비슷해질 수 있다. 팀에서는 source domain이나 persona를 나눠야 한다.

- A: 고객/사용자 관점
- B: 기술 리스크 관점
- C: 비용/운영 관점
- D: 반대 가설 관점
- E: 전혀 다른 산업 유추

결과를 합칠 때는 중복 아이디어를 버리고, 서로 충돌하는 가정을 따로 표시한다.

## 6. 업무별 적용

| 업무 | 기존 사용 패턴 | 바꿀 패턴 |
|---|---|---|
| 리서치 | "이 논문 요약해줘" | claim map, 반례, 후속 연구, 적용 가능성으로 분해 |
| 슬라이드 | "10장 PPT 만들어줘" | narrative 후보 3개, audience별 메시지, evidence map 먼저 생성 |
| 제품 기획 | "기능 아이디어 줘" | 사용자 문제, 원격 유추, 실패 시나리오를 카드화 |
| 코딩 | "이 기능 구현해줘" | 아키텍처 대안, tradeoff, rollback path를 먼저 비교 |
| 이미지/디자인 | "포스터 만들어줘" | concept card를 먼저 만들고 선택 후 생성 |
| 회의 | "회의록 정리해줘" | 결정, 미결정, 가정, 후속 질문을 분리 |

## 7. 도구 설계 관점

이 논문은 UI 설계자에게도 직접적인 요구를 남긴다.

- 결과물을 바로 보여주기 전에 exploration surface를 제공한다.
- 사용자의 첫 요청을 실행 준비 완료 상태로 보지 않는다.
- 수정 의도를 옵션과 매개변수로 드러낸다.
- 대화형 history만 두지 말고 branch, tab, library, comparison view를 둔다.
- AI 제안은 complete solution보다 incomplete suggestion으로 제시한다.
- 사용자가 도구 조작법에 시간을 빼앗기지 않고 과제 자체를 배우도록 설계한다.

## 8. 제한과 남은 질문

이 연구를 과장하면 안 된다.

- 표본은 24명이다.
- 참가자 배경은 CS/IT 쪽에 치우쳤다.
- 과제는 포스터 이미지 생성이다.
- 학습 효과는 자기보고 중심이다.
- 세션은 단회성이다.
- agency와 ownership 문제는 혼재된 결과로 남았다.

남은 질문은 실무에 가깝다.

- 스캐폴딩이 늘어날 때 속도 손실을 어디까지 감수할 수 있는가.
- 숙련 사용자는 언제 스캐폴딩을 끄고 직접 실행해야 하는가.
- 조직이 같은 AI 도구를 쓸 때 결과물 다양성을 어떻게 측정할 것인가.
- coding agent, slide generator, data analysis agent에서도 같은 방식의 mode separation이 효과가 있는가.

## 9. 권장 워크플로

```text
1. Problem frame
   - 목표, 독자, 제약, 금지할 방향을 적는다.

2. Divergent pass
   - 서로 멀리 떨어진 아이디어 카드 7-9개를 만든다.
   - 아직 최종 산출물을 만들지 않는다.

3. Selection pass
   - novelty, usefulness, feasibility, audience fit, risk로 평가한다.

4. Convergent pass
   - 고른 방향을 구조화한다.
   - 수정 요청은 semantic parameter로 분해한다.

5. Artifact pass
   - 선택한 방향만 산출물로 만든다.

6. Audit pass
   - 중복, 고착, 과확신, 근거 부족, 말투를 점검한다.

7. Branch archive
   - 버린 대안과 이유를 남긴다.
```

## 10. 외부 참고 링크

- [AI Matters article](https://aimatters.co.kr/news-report/ai-report/40718/)
- [Wen et al., Exploration vs. Fixation, arXiv:2512.18388](https://arxiv.org/abs/2512.18388)
- [Wadinambiarachchi et al., The Effects of Generative AI on Design Fixation and Divergent Thinking](https://arxiv.org/abs/2403.11164)
- [Doshi and Hauser, Generative AI enhances creativity but reduces the diversity of novel content](https://arxiv.org/abs/2312.00506)
- [Anderson, Shah, Kreminski, Homogenization Effects of Large Language Models on Human Creative Ideation](https://arxiv.org/abs/2402.01536)
- [Stanford d.school, prototyping and parallel prototype summary](https://dlibrary.stanford.edu/questions/why-does-building-and-testing-prototypes-help-you-get-to-a-good-solution)
- [Parsons et al., Fixation and Creativity in Data Visualization Design](https://arxiv.org/abs/2108.06451)
