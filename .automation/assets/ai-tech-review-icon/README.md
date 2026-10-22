# AI Tech Review Letters quantum / AI review icon

2026-10-22 · Asset version: `20261022-qai-review-watercolor`

최신 양자·AI 렉처, 학술 리뷰, 기술 리뷰와 저널 형식의 기사를 발행하는
**독립 리뷰·학습 매체**의 로고다. 저널 페이지가 접힌 큰 **R**은 Review를,
그 여백 안의 **Q / AI**는 양자와 인공지능을 나타낸다. 실제 장치·회로나
학술 인증을 나타내는 도식이 아닌 매체의 상징이다.

어두운 월넛 브라운, 종이색 베이지와 차분한 청록을 유지한다. R의 선명한
외곽은 오른쪽 아래에서 수채화 안료와 얇은 번짐으로 풀린다. 표면빛은 매우
약하게 억제하고, 첫 시안의 금박 같은 질감을 한 번의 생성 편집으로 낮췄다.
표면의 종이·안료 무늬는 남아 있으며 완전한 단색 벡터 로고가 아니다.

## Actual revised concept comparison

사용자가 제안한 펼친 책의 좌우 Q/AI와 기존 B/C/D를 각각 발전시켜 실제
이미지 네 장을 built-in `image_gen`으로 제작했다. 모두 같은 다크 월넛 계열에서
비교했으며, 이전 버건디 시안은 별도 이력으로 남겨 둔다.

| 후보 | 의미 | 실제 결과의 판단 |
|---|---|---|
| A · 열린 저널 Q / AI | 왼쪽 Q와 오른쪽 AI, 펼친 지면 | 180/64px 문자 판독 우선 시 독립 판독 검토자의 추천안. 활자와 책 외곽이 다소 빽빽함 |
| B · 리뷰의 여백 | 접힌 원고와 주석 괄호, Q/AI | 코드 문서 인상이 강함 |
| C · 한 권의 저널 | 저널 표지의 Q/AI, 청록 제본 | 출판 인상은 분명하지만 투시·페이지 단면·상단 빛이 경쟁함 |
| **D · 페이지로 만든 R** | 큰 Review 기호 속 작은 Q/AI | **디자인 디렉터 선택. 하나의 기호와 16px 실루엣 우선** |

글자 인지를 우선한 별도 판독 검토자는 A를 추천했다. 최종 선택은 디자인
디렉터의 D를 따르되 축소 한계를 기록했다. D에 재질만 한 번 보정한 실제
결과를 다시 검토한 뒤 `selected-D-watercolor.png`로 확정했다. 생성 편집이므로
원본과 픽셀 단위로 동일한 형태라는 뜻은 아니며 구조·비례가 시각적으로 유지됐다.
에이전트의 디자인·판독 평가이며 사람 선호도 조사나 실제 iOS 설치 검수는 아니다.

- [네 실제 시안 비교](studies/20261022-quantum-ai-editorial/comparison.png)
- [선택안 보정까지 반영한 비교](studies/20261022-quantum-ai-editorial/comparison-final.png)
- [후보별 실제 축소·흑백](studies/20261022-quantum-ai-editorial/legibility.png)
- [선택 D의 재질 보정 전후](studies/20261022-quantum-ai-editorial/refinement-comparison.png)
- [최종안 실제 축소·흑백](studies/20261022-quantum-ai-editorial/selected-legibility.png)
- [디자인 판단](studies/20261022-quantum-ai-editorial/design-review.md)
- [독립 판독 검토](studies/20261022-quantum-ai-editorial/legibility-review.md)
- [프롬프트 전문](studies/20261022-quantum-ai-editorial/prompts.json)
- [원본 해시·크기](studies/20261022-quantum-ai-editorial/assets.json)
- [프로덕션 검증](studies/20261022-quantum-ai-editorial/production-validation.json)

## Source and regeneration

최종 원본은 [selected-D-watercolor.png](studies/20261022-quantum-ai-editorial/selected-D-watercolor.png)다.
고정된 원본을 크기 조정하고 metadata 없이 내보낸다. 재빌드에는 생성 호출,
네트워크, 색 보정, 크롭이나 예술적 필터가 필요 없다.

```sh
python3 .automation/assets/ai-tech-review-icon/build_favicon.py
```

- `ai-tech-review-icon-512.png`: 원본의 512px 내보내기
- `apple-touch-icon.png`: 180px 불투명 RGB
- `favicon-16x16.png`, `favicon-32x32.png`, `favicon-64x64.png`: 같은 원본의 축소본
- `favicon.ico`: 16/32/48/64/128/256px 슬롯
- `ai-tech-review-icon.svg`: 같은 512px PNG를 data URL로 내장한 SVG. 벡터 원화가 아니다.

180px에서는 Q·AI를 읽을 수 있지만, 64px부터 작아지고 32/16px에서 문자
완독을 보장하지 않는다. 16px에서는 R의 큰 실루엣이 브랜드를 담당한다.
작은 크기에도 별도 그림을 대입하지 않고 같은 원본을 사용한다.
게시기는 최종 공개 아이콘만 `site/`에 복사한다. 시안·프롬프트·검토 기록과
QA 이미지는 공개 사이트 자산에 포함하지 않는다.

## Historical studies

- [Q 수채화 로고](studies/20261022-watercolor/design-review.md)
- [출판 정체성 네 시안](studies/20261022-editorial/design-review.md)
- [펼친 저널의 월넛 팔레트](studies/20261022-editorial-walnut/color-review.md)

과거 시안과 판단은 당시 상태로 보존한다. 이 변경은 사이트 아이콘만 다루며
기사 본문·표지·PDF를 재제작하지 않는다.
