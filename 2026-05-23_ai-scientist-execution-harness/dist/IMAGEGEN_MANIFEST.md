# Imagegen Manifest

## 생성 정보

- Skill: `imagegen`
- CLI: `C:\Users\angpa\.codex\skills\imagegen\scripts\image_gen.py`
- Model default: `gpt-image-1.5`
- Output folder: `2026-05-23_ai-scientist-execution-harness/artifacts/final_review/figures/imagegen/`
- Size: `1536x1024`
- Quality: `high`
- Output format: `png`
- API key: local `OPENAI_API_KEY` 사용

## 채택 이미지

### `ai_scientist_erdos_blackboard.png`

- Use case: `illustration-story`
- 용도: 기사 hero
- 목적: 에르되시 문제 #1196, primitive set, Markov chain, 인간 수학자와 AI 에이전트의 협업 분위기
- 검토 결과: 채택. 칠판의 약수 격자와 빛의 경로가 도입부의 수학적 흥미와 맞음. 읽을 수 있는 실제 수식/텍스트가 없어 본문 claim과 충돌하지 않음.

### `ai_scientist_coscientist_lab.png`

- Use case: `illustration-story`
- 용도: AI Co-Scientist 섹션 opener
- 목적: 문헌 카드, 실험 접시, 현미경, 노트북 도구, 후보 카드의 왕복 흐름
- 검토 결과: 1차 생성물에는 `Hypothesis`, `Review` 같은 영어 텍스트가 보여 재생성. 최종본은 읽을 수 있는 텍스트가 없어 채택.

### `ai_scientist_guarded_library.png`

- Use case: `illustration-story`
- 용도: Bixonimania 및 지식 오염/검증 섹션 opener
- 목적: 불확실한 문서, citation trail, 검증 책상, 차분한 우려의 분위기
- 검토 결과: 채택. 선정적이지 않고 우려 섹션의 온도와 맞음. 읽을 수 있는 질병명이나 과장된 경고 표식이 없음.

## 프롬프트 요약

- 공통 스타일: Quanta Magazine / KIAS Horizon 계열의 고급 과학 일러스트레이션, 장면형, no logos, no watermark, no readable text.
- 역할 분리: bitmap 이미지는 장면과 감정, SVG는 한국어 라벨과 정확한 논리 구조를 담당.
- 재검토 기준: 주제 구체성, 텍스트 오염 여부, 장식성 과다 여부, 본문 adjacent section과의 연결성.

