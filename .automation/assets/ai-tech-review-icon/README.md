# AI Tech Review watercolor Q/node icon

2026-10-22 · Asset version: `20261022-watercolor-tail-release`

짙은 매트 버건디와 베이지 Q, 연결된 두 청록색 노드를 유지하며 Q 꼬리에서
한 획의 수채화 안료가 풀려 나가도록 표현했다. 꼬리 시작의 선명한 경계가
불규칙한 안료와 옅은 끝으로 이어진다. 특정 양자 상태나 실험 장치의 도식이 아닌 브랜드 심볼이다.

## Compared designs

기존 기하학 로고를 기준으로 실제 수채화 시안 네 장을 built-in `image_gen`으로 제작했다.
각 원본은 1254×1254px RGB이며, 정확한 내부 모델 식별자는 도구에서 제공되지 않았다.

| 후보 | 방향 | 결과 |
|---|---|---|
| **A · Tail release** | Q 꼬리가 한 획의 안료로 풀림 | **독립 디자인 디렉터 선택** |
| B · Pigment orbit | Q 바깥의 비대칭 초승달 한 획 | 기호보다 별도의 장식으로 읽힘 |
| C · Two-stroke counterpoint | 베이지·청록 두 획의 대비 | 작은 크기에서 복잡하고 밝은 면적이 큼 |
| D · Wet-edge Q | Q 원호 일부의 젖은 가장자리 | 가독성 QA의 우선안, 디자인 검토의 차선 |

- [동일 크기 비교판](studies/20261022-watercolor/comparison.png)
- [180/64/32/16px·흑백 비교판](studies/20261022-watercolor/legibility.png)
- [독립 디자인 선택 기록](studies/20261022-watercolor/design-review.md)
- [별도 판독성 검토](studies/20261022-watercolor/legibility-review.md)
- [프롬프트 전문](studies/20261022-watercolor/prompts.json), [원본 해시·크기](studies/20261022-watercolor/assets.json)

디자인 디렉터는 기호와 회화적 획의 결합을 이유로 A를 선택했다. 별도 QA는 D를
먼저 추천하면서 A도 채택 가능하다고 판단했다. A의 휘는 꼬리가 작게 보면 갈고리처럼
보일 수 있다는 점을 재검토했고, Q와 연결의 판독을 막지 않아 현재 A를 그대로 채택했다.
이 판단은 에이전트의 편집·디자인 평가이며 사람 선호도 조사나 실제 iOS 설치 시험은 아니다.

## Source and regeneration

최종 원본은 [candidate-A.png](studies/20261022-watercolor/candidate-A.png)다.
원본 안료·색상·구도를 수정하지 않으며 크기 조정과 metadata 없는 내보내기만 수행한다.
생성은 제작 단계에서 끝났고 재빌드에는 네트워크나 이미지 생성 도구가 필요 없다.

```sh
python3 .automation/assets/ai-tech-review-icon/build_favicon.py
```

- `ai-tech-review-icon-512.png`: 선택 원본의 512px 내보내기
- `apple-touch-icon.png`: 180px, 불투명 RGB
- `favicon-16x16.png`, `favicon-32x32.png`, `favicon-64x64.png`: 동일 원본의 작은 크기 내보내기
- `favicon.ico`: 16/32/48/64/128/256px 슬롯
- `ai-tech-review-icon.svg`: 512px PNG를 data URL로 내장한 SVG. 벡터 원화가 아니다.

16px에서는 안료 세부 질감 대부분이 사라지지만 Q와 가운데 연결이 남는다.
작은 아이콘만 다른 기하학 로고로 바꾸지 않고 같은 원본을 사용한다.
SVG는 외부 이미지 경로에 의존하지 않는다. 공개용 파일만 게시기가 `site/`에 복사한다.
프롬프트·검토 기록·비교판·채택하지 않은 원본은 공개 사이트 자산에 포함하지 않는다.

## Verification

180/64/32/16px, 둥근 마스크, 흑백에서 실제 시안을 비교했다.
공개 내보내기는 RGB·크기·metadata, ICO 슬롯, 내장 PNG 일치와 원본/공개본 일치를 확인했다.
임시 폴더의 재생성 결과도 바이트 단위로 같았으며 전체 사이트 검증을 통과했다.
실제 iOS 설치 검수나 사람 선호도 평가는 하지 않았다.
