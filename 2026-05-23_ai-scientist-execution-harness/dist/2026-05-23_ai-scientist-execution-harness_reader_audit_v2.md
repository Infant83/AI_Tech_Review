# Reader Audit v2

## 확인한 추가 참고

- Scientific American, `An amateur just solved a 60-year-old math problem-by asking AI`, 2026-04-24
  - Liam Price의 경로, Kevin Barreto 전달, Tao/Lichtman의 해석, 원시 집합 설명이 독자 진입에 도움.
- KIAS Horizon, `수학, 인공지능, 그리고 형식화 1 - 수학을 위한 인공지능`, 2026-04
  - 카페/학생/코딩 같은 친숙한 장면에서 시작해 수학 연구와 형식화 문제로 좁혀가는 호흡 참고.
- Quanta Magazine, `The AI Revolution in Math Has Arrived`, 2026-04-13
  - 수학계의 흥분과 불안, AI slop과 형식 검증의 tension, 강한 이미지/캡션 리듬 참고.

## 독자 입장 문제

1. 도입부는 좋아졌지만 아직 `보도했습니다`, `적고 있습니다` 같은 전달문이 이어져 신문 기사 요약처럼 보일 위험이 있음.
2. 에르되시 #1196 설명은 충분하지만, 대중강연식으로 독자 손에 작은 예시를 쥐여주는 문장이 조금 더 필요함.
3. Scientific American의 핵심 장면, 즉 Liam Price가 문제의 역사도 모르고 AI에 던졌고, Barreto와 전문가들이 의미를 알아본 흐름을 더 넣으면 호기심이 살아남.
4. KIAS Horizon식으로 `처음엔 이상해 보이는 작은 예시 -> 용어 -> 연구 질문 -> 최신 사례` 흐름을 더 살릴 수 있음.
5. 그림은 7개로 충분함. 추가 생성보다 현재 3개 bitmap과 4개 SVG의 역할을 caption에서 더 분명히 하는 편이 좋음.

## 수정 방향

- 도입 첫 문단에 Price 경로를 조금 더 살아 있는 장면으로 삽입.
- primitive set 설명을 `6, 10, 15` 예시에서 한 문장 더 풀어 대중강연 느낌을 강화.
- KIAS Horizon 수학-AI 글을 참고자료에 추가하고, 본문에는 한국어 독자가 더 깊게 읽을 수 있는 연결 자료로 배치.
- `했습니다/합니다/있습니다` 반복 문단을 줄이고, 일부 문장을 짧게 끊어 말하듯이 바꿈.
- figure 추가는 보류. 현재 density가 충분하고, 추가 그림은 오히려 글의 호흡을 끊을 가능성이 큼.

## provenance pass

- Gmail 제목 `ai for sci` 메일을 확인했고, 본문에는 Sergei Kalinin의 AI for Science LinkedIn 공유 링크가 담겨 있었음.
- 메일과 LinkedIn 공유는 주제 탐색 신호로만 기록하고, 본문 claim은 Erdős Problems, arXiv, Nature, Google 공식 자료, 도구 공식 문서로 다시 확인함.
- 이전 `AI Updates Weekly`와 `TabPFN OLED` final review의 `작성 정보` / `References` 형식을 참고해 `작성 정보`, `직접 검증 참고자료`, `처음 참고한 자료`, `문체와 시각자료 참고`를 추가함.
- Nature `Towards end-to-end automation of AI research`를 추가 확인해 The AI Scientist 문단과 References에 반영함.
- 전체 figure 7개를 `FIGURE_MANIFEST.md`에 정리함. 추가 그림은 보류하고, 배포용 또는 deck 단계에서 참고자료 맵이 필요할 때 별도 제작 후보로 둠.
