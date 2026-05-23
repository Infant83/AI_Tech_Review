# Korean prose style audit note

date: 2026-04-28
purpose: 이번 리뷰와 향후 AI_Tech_Review 산출물에서 "AI스러운 말투"를 줄이기 위한 근거와 편집 기준.

## 업데이트한 운영 규칙

- `C:\Users\angpa\myProjects\Daily_Work\AI_Tech_Review\AGENTS.md`
  - `Korean Human Writing Style Rules` 섹션 추가.
- `C:\Users\angpa\AGENTS.md`
  - `Korean writing style baseline` 섹션 추가.
- `C:\Users\angpa\.codex\rules\korean-writing-style.md`
  - `.codex` 쪽 재사용 가이드로 추가.

메모리 파일은 수정하지 않았다. `C:\Users\angpa\.codex\memories\*`는 읽기 전용으로 취급했다.

## 근거로 확인한 소스

- [OpenAI - New AI classifier for indicating AI-written text](https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/)
  - 2023-07-20 업데이트에서 낮은 정확도로 classifier가 더 이상 제공되지 않는다고 명시.
  - classifier는 primary decision tool로 쓰지 말라는 제한을 둔다.
- [Herbold et al., Scientific Reports 2023](https://www.nature.com/articles/s41598-023-45644-9)
  - ChatGPT 에세이는 결론 시작 문장과 도입 구조가 반복되는 등 rigid structure를 보였다고 분석.
  - 인간 글과 AI 글 사이에 통계적 언어 차이가 있음을 보고.
- [Juzek and Ward, arXiv:2412.11385](https://arxiv.org/abs/2412.11385)
  - scientific English에서 특정 단어가 LLM 영향으로 과대표현될 가능성을 분석.
- [Geng and Trotta, arXiv:2404.08627](https://arxiv.org/abs/2404.08627)
  - 2018-05부터 2024-01까지 arXiv 초록 약 100만 건을 분석해 ChatGPT-style drift를 추정.
- [Vrije Universiteit Amsterdam ALP Guide](https://vu.nl/en/about-vu/more-about/alp-guide-spotting-ai-writing)
  - AI writing clue는 proof가 아니라 tendency라고 전제.
  - 반복 구조, 반복 어휘, 과확신, bland style, broad statement를 주요 단서로 정리.

## 이번 산출물 편집 기준

- `A가 아니라 B이다`, `단순히 A가 아니다. B다`, `A뿐만 아니라 B` 구조를 문장 습관으로 쓰지 않는다.
- `핵심은`, `시사하는 바는`, `결론적으로`, `요컨대`, `흥미롭게도`는 정보량이 없으면 삭제한다.
- 문단마다 하나의 구체적 판단을 둔다.
- 연구 수치, 표본, 도메인 제한을 숨기지 않는다.
- 슬라이드 제목은 구호보다 판단문으로 쓴다.
- AI detector식 판정은 쓰지 않는다. 말투 점검은 편집 품질 기준으로만 쓴다.
