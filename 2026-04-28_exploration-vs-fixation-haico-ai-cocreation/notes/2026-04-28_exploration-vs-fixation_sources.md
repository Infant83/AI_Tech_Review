# Exploration vs. Fixation source note

date: 2026-04-28
topic: HAICo, design fixation, divergent/convergent AI co-creation
scope: 논문 중심 리뷰. 기사 자체보다 논문이 주는 실무 인사이트와 AI 활용 방식에 초점.

## 원문

- AI Matters 기사: [챗GPT에 아이디어를 물으면 안 되는 이유, 독일 연구팀이 밝혔다](https://aimatters.co.kr/news-report/ai-report/40718/)
  - 게시일: 2026-04-20
  - 역할: 논문 발견 경로와 대중적 요약.
  - 보관본: `sources/aimatters_40718_article.html`
- 논문: [Exploration vs. Fixation: Scaffolding Divergent and Convergent Thinking for Human-AI Co-Creation with Generative Models](https://arxiv.org/abs/2512.18388)
  - arXiv: `2512.18388v2`
  - 최초 제출: 2025-12-20
  - v2 개정: 2026-04-06
  - 저자: Chao Wen, Tung Phung, Pronita Mehrotra, Sumit Gulwani, Roger E. Beaty, Tomohiro Nagashima, Adish Singla
  - 보관본: `sources/2512.18388v2_exploration_vs_fixation.pdf`, `sources/2512.18388v2_exploration_vs_fixation.html`, `sources/2512.18388v2_exploration_vs_fixation.txt`

## 논문에서 직접 확인한 수치

- 연구 설계: poster image creation task, within-subjects study, `N = 24`.
- Creativity Support Index: HAICo가 ChatGPT보다 5개 차원 모두 높음. 논문 캡션 기준 `all W < 30.0`, `all p < 0.002`.
- UMUX-Lite: HAICo `M = 81.25`, ChatGPT `M = 64.24`, `W = 17.0`, `p < 0.001`.
- 결과물 novelty: HAICo `M = 3.22`, ChatGPT `M = 2.41`, `W = 0.0`, `p < 0.001`.
- 결과물 diversity: HAICo `M = 0.48`, ChatGPT `M = 0.36`, `W = 26.0`, `p = 0.001`.
- Fluency와 usefulness는 유의미한 차이가 없었다고 보고됨.
- Divergent exploration: HAICo image cluster `M = 2.88`, ChatGPT `M = 2.04`, `W = 33.0`, `p = 0.021`.
- Refinement prompts per cluster: HAICo `M = 1.56`, ChatGPT `M = 2.94`, `W = 52.0`, `p = 0.004`.
- HAICo refinement에서 non-default option adoption 평균 `74.8%`, `SD = 27.40%`.
- Self-reported learning: HAICo `M = 5.29`, ChatGPT `M = 3.12`, `W = 21.0`, `p < 0.001`.
- 학습 응답 유형: ChatGPT는 system behavior/prompting strategy 쪽이 많고, HAICo는 task-specific knowledge/new directions and ideas 쪽이 많다.

## 보강 근거

- [The Effects of Generative AI on Design Fixation and Divergent Thinking](https://arxiv.org/abs/2403.11164)
  - CHI 2024, `N = 60`.
  - AI-generated image에 노출된 참가자가 초기 예시에 더 고착되고, 더 적은 아이디어와 낮은 다양성/독창성을 보였다는 결과.
- [Generative artificial intelligence enhances creativity but reduces the diversity of novel content](https://arxiv.org/abs/2312.00506)
  - Science Advances 관련 DOI: `10.1126/sciadv.adn5290`.
  - GenAI 아이디어 접근은 개인 글쓰기 결과를 향상시킬 수 있으나, GenAI 도움을 받은 이야기들이 서로 더 비슷해지는 경향을 보고.
- [Homogenization Effects of Large Language Models on Human Creative Ideation](https://arxiv.org/abs/2402.01536)
  - C&C 2024, `N = 36`.
  - ChatGPT 사용자는 더 많은 상세 아이디어를 만들었지만 사용자 간 아이디어가 덜 구별되고, 아이디어에 대한 책임감도 낮았다는 결과.
- [Stanford d.school Design Questions Library - prototyping summary](https://dlibrary.stanford.edu/questions/why-does-building-and-testing-prototypes-help-you-get-to-a-good-solution)
  - Dow et al.의 parallel prototyping 연구를 소개. 병렬 프로토타입은 더 다양하고 serial prototype보다 좋은 결과를 냈다고 요약.
- [Fixation and Creativity in Data Visualization Design](https://arxiv.org/abs/2108.06451)
  - 데이터 시각화 설계에서도 fixation을 창의적 결과를 제한하는 조기 고착으로 다룸.

## 이번 리뷰의 해석 기준

- `확인됨`: 논문 수치와 원문에서 직접 확인되는 주장.
- `주의 필요`: 표본, 도메인, 측정 방식 때문에 일반화가 제한되는 주장.
- `확장 해석`: 논문 결과를 업무·코딩·기획·슬라이드 작성 워크플로로 옮긴 판단.

## 초점에서 제외한 것

- HAICo 자체의 제품화 가능성 평가는 제한적으로만 다룬다. 현재 연구 시스템이며 일반 공개 서비스가 아니다.
- 이미지 생성 성능 비교 자체를 결론으로 삼지 않는다. 이번 리뷰의 중심은 창작 과정 설계와 사용자 워크플로다.
