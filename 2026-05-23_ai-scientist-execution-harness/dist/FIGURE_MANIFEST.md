# Figure Manifest

## 생성 정보

- Review: `2026-05-23_ai-scientist-execution-harness`
- Report: `reports/2026-05-23_ai-scientist-execution-harness_final_review.md`
- 작성일: 2026-05-23
- Figure count: 7
- Bitmap illustration: `imagegen` 3개
- Deterministic diagram: SVG 4개
- 역할 분리: imagegen은 장면과 독자 진입점, SVG는 정확한 한국어 라벨과 관계 설명을 담당했습니다.

## 채택 Figure

| Figure | 파일 | 형식 | 본문 위치 | 목적 | 검토 기록 |
|---|---|---|---|---|---|
| 그림 1 | `imagegen/ai_scientist_erdos_blackboard.png` | imagegen PNG | 도입부 | 에르되시 #1196, primitive set, AI와 수학자의 협업 장면 | 채택. 가짜 텍스트와 로고가 보이지 않고 도입부의 호기심을 열기에 적합함. |
| 그림 2 | `ai_scientist_erdos_1196_explainer.svg` | SVG | 에르되시 문제 설명 뒤 | primitive set, 에르되시 합, 기존 상한, Markov chain/von Mangoldt 경로, 인간 검증 연결 | 채택. 정확한 한국어 라벨이 필요해 SVG로 작성함. |
| 그림 3 | `imagegen/ai_scientist_coscientist_lab.png` | imagegen PNG | AI Co-Scientist 섹션 | 문헌, 가설, 실험, 도구가 같은 작업면에서 왕복하는 장면 | 1차 생성물은 읽을 수 있는 영어 텍스트가 보여 기각. 재생성본 채택. |
| 그림 4 | `imagegen/ai_scientist_guarded_library.png` | imagegen PNG | Bixonimania 우려 섹션 | 지식 오염, 원문 확인, citation trail, 검증 책상 분위기 | 채택. 선정적인 경고 이미지가 아니라 차분한 검토 장면으로 읽힘. |
| 그림 5 | `ai_scientist_validation_loop.svg` | SVG | 회사 문제를 작업대에 올리기 | 문제 카드, 자료, 에이전트, 평가, 검토 로그의 반복 루프 | 채택. 실행 루프를 정확한 라벨과 방향으로 설명함. |
| 그림 6 | `ai_scientist_harness_example.svg` | SVG | 작은 작업 폴더 | 작업 폴더, 프롬프트, manifest, 후보 JSON, 평가 결과, 결정 로그 관계 | 채택. 실전 파일 구조와 산출물 흐름을 한 번에 확인하게 함. |
| 그림 7 | `ai_scientist_guardrail_matrix.svg` | SVG | 우려를 작업 안에 넣는 방법 | 지식 오염, 데이터 보안, 책임 경계, 검증 비용과 대응 가드레일 | 채택. 우려 섹션을 추상적 경고가 아니라 작업 산출물로 연결함. |

## 제외 또는 보류 Figure

- `ai_scientist_hero.svg`: 초기 hero 후보였으나, 에르되시 #1196 도입부와 더 잘 맞는 imagegen hero로 교체했습니다. 파일은 이전 작업 흔적 보존을 위해 남겼지만 본문에서는 참조하지 않습니다.

## 추가 그림 가능성 점검

- 현재 본문은 hero 1개, 도입 개념도 1개, section opener 2개, 실행/폴더/위험 SVG 3개로 구성되어 있습니다.
- `작성 정보`와 계층형 `References` 추가 뒤에는 텍스트 밀도가 높아졌지만, 이 영역은 문헌 provenance가 목적이므로 새 그림을 넣지 않았습니다.
- 추가 그림이 필요해지는 경우는 Skywork deck 또는 배포용 웹진에서 `참고자료 맵`을 별도 인포그래픽으로 만들 때입니다. 현재 article 본문에는 새 그림을 더 넣으면 흐름이 분산될 가능성이 더 큽니다.

