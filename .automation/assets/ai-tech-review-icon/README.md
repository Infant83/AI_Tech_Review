# AI Tech Review Letters editorial icon

2026-10-22 · Asset version: `20261022-editorial-walnut`

최신 양자·AI 렉처, 학술 리뷰, 기술 리뷰와 저널 형식의 기사를 발행하는
**독립 리뷰·학습 매체**의 로고다. 펼친 학술지의 두 페이지와 중앙 제본선으로
읽기·설명·출판을 먼저 드러낸다. 어두운 매트 월넛 브라운, 누른 베이지 외곽,
차분한 청록 제본선을 사용하며 오른쪽 페이지 끝이 한 획의 수채화 안료로 풀린다.

페이지 내부는 밝은 면으로 채우지 않아 어두운 인상을 유지한다. 문구·본문 흉내·
인장·인증 체크를 넣지 않으며 특정 논문이나 실제 양자 장치의 도식으로 제시하지 않는다.
양자·AI 분야는 매체명과 실제 콘텐츠가 설명하고, 로고는 리뷰·렉처·기사 전반을 담는다.

## Actual concept comparison

이전 Q 수채화 로고를 색감·무광·수채화의 참고로만 사용하고 핵심 기호를 다시 설계했다.
built-in `image_gen`으로 네 가지 실제 시안을 제작했다. 각 원본은 1254×1254px RGB이고
정확한 내부 모델 식별자는 도구에서 제공되지 않았다.

| 후보 | 의미 | 판단 |
|---|---|---|
| **A · 펼친 학술지** | 두 페이지·제본·열린 읽기 경험 | **독립 디자인 디렉터 선택** |
| B · 리뷰의 여백 | 원고와 주석 괄호 | 실제 결과의 중괄호가 코드 문서로 먼저 읽힘 |
| C · 한 권의 저널 | 학술지 한 권과 제본 | 닫힌 책·도서관의 인상, 작은 테두리 약화 |
| D · 페이지로 만든 R | REVIEW 모노그램과 종이 접힘 | 개성·16px 판독성은 좋지만 작은 크기에서는 출판보다 문자 R이 먼저 남음 |

- [기존 Q와 네 시안 비교](studies/20261022-editorial/comparison.png)
- [로고·매체명 조합 시안](studies/20261022-editorial-walnut/brand-context.png)
- [180/64/32/16px·흑백 비교](studies/20261022-editorial/legibility.png)
- [디자인 선택 기록](studies/20261022-editorial/design-review.md)
- [별도 판독성·매체 적합성 검토](studies/20261022-editorial/legibility-review.md)
- [프롬프트 전문](studies/20261022-editorial/prompts.json), [원본 해시·크기](studies/20261022-editorial/assets.json)
- [브라운 색상 조정 비교](studies/20261022-editorial-walnut/palette-comparison.png)
- [색상 편집 프롬프트](studies/20261022-editorial-walnut/prompt.json), [색상·형태 검토](studies/20261022-editorial-walnut/color-review.md)

A는 열린 학술지의 직관성과 작은 크기의 두 페이지 구조를 우선해 선택했다.
익숙한 펼친 책 기호라는 한계가 있으므로 매체 고유성은 이름·기사와 함께 형성한다.
선택은 실제 이미지에 대한 에이전트의 편집·디자인 평가이며 사람 선호도 조사가 아니다.
이전 [Q 수채화 연구](studies/20261022-watercolor/design-review.md)는 별도 이력으로 보존한다.
형태 선정 뒤 사용자가 선호한 이전 다크 월넛 팔레트로 built-in `image_gen` 색상 편집을 했다.
버건디로 제작한 네 형태 비교 시안과 그 선정 기록은 당시 상태로 보존한다.

## Source and regeneration

최종 원본은 [journal-walnut.png](studies/20261022-editorial-walnut/journal-walnut.png)다.
고정된 원본을 수정하지 않고 크기 조정과 metadata 없는 내보내기만 수행한다.
재빌드에 네트워크나 이미지 생성 호출은 필요 없다.

```sh
python3 .automation/assets/ai-tech-review-icon/build_favicon.py
```

- `ai-tech-review-icon-512.png`: 원본의 512px 내보내기
- `apple-touch-icon.png`: 180px 불투명 RGB
- `favicon-16x16.png`, `favicon-32x32.png`, `favicon-64x64.png`: 같은 원본의 작은 크기
- `favicon.ico`: 16/32/48/64/128/256px 슬롯
- `ai-tech-review-icon.svg`: 같은 512px PNG를 data URL로 내장한 SVG. 벡터 원화가 아니다.

16px에서는 수채화 입자 대부분이 사라지지만 두 페이지의 외곽과 중앙 접힘은 남는다.
다른 작은 로고로 교체하지 않고 같은 원본을 사용한다. 공개 아이콘만 게시기가
`site/`에 복사하며 시안·프롬프트·검토 기록은 공개 사이트 자산에 포함하지 않는다.

## Verification

실제 180/64/32/16px, 둥근 마스크, 흑백에서 후보를 비교했다.
공개 내보내기의 RGB·크기·metadata·ICO 슬롯·내장 PNG와 원본/공개본 일치를 확인했다.
임시 폴더의 재생성 결과가 바이트 단위로 같았으며 전체 사이트 검증을 통과했다.
실제 iOS 설치 검수나 사람 선호도 평가는 하지 않았다.
