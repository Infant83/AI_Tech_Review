# AI Tech Review Letters topic-keyword review icon

2026-10-22 · Asset version: `20261022-topic-keywords`

최신 양자·AI 렉처, 학술 리뷰, 기술 리뷰와 저널 형식의 기사를 발행하는
**독립 리뷰·학습 매체**의 로고다. 저널 페이지가 접힌 큰 **R**은 Review를,
그 안과 주변 여백의 **Q / AI / DFT / VQE / LLM / OLED / GPU**는 이 매체가
다루는 짧은 주제 키워드를 나타낸다. 실제 장치·회로나 학술 인증을 나타내는
도식이 아닌 매체의 상징이다.

Q는 Quantum의 브랜드 축약, AI는 artificial intelligence, DFT는 density
functional theory, VQE는 variational quantum eigensolver, LLM은 large language
model, OLED는 organic light-emitting diode, GPU는 graphics processing unit이다.
약어의 크기·위치·색은 성능·인과관계·연구량·증거 수준을 나타내지 않는다.
현재 공개 리뷰·렉처에서 확인한 주제를 골랐으며 근거는 별도 감사 기록에 남긴다.

어두운 월넛 브라운, 종이색 베이지와 차분한 청록을 유지한다. R의 선명한
외곽은 오른쪽 아래에서 수채화 안료로 풀리고, 짧은 약어는 크기와 각도를 달리해
여백에 배치한다. 표면의 종이·안료 무늬는 남아 있으며 단색 벡터 로고가 아니다.

## Actual revised concept comparison

기존 페이지형 R 원본을 built-in `image_gen`으로 편집하여 실제 시안 두 장을
비교했다. 이전의 Q/AI 중심 D는 이력으로 보존한다.

| 후보 | 배치 | 실제 결과의 판단 |
|---|---|---|
| **A · 자유로운 여백 주석** | R 안과 주변 여백에 약어의 크기·각도를 달리함 | **독립 디자인 검토 선택. 자유로운 배치와 R 실루엣의 균형** |
| B · 페이지를 따라 흐르는 주제 | R의 사선 다리를 따라 약어를 줄지어 배치 | 일곱 약어는 정확하지만 배치가 규칙적이고 밝은 R 면과 경쟁함 |

최종 원본은 A를 그대로 채택한 `selected-A-keywords.png`다. 두 시안 모두
일곱 약어가 각각 한 번씩 정확하게 보이며, A는 자유로운 배치라는 요청에 더
가깝다. 검토자는 재생성이 필요한 중대한 결함을 발견하지 않았다.
이는 에이전트의 디자인 평가이며 사람 선호도 조사나 실제 iOS 설치 검수는 아니다.

- [주제·기획 근거](studies/20261022-topic-keywords/design-brief.md)
- [공개 게시물의 키워드 감사](studies/20261022-topic-keywords/keyword-audit.json)
- [실제 시안 비교](studies/20261022-topic-keywords/comparison.png)
- [실제 축소·흑백](studies/20261022-topic-keywords/legibility.png)
- [독립 디자인 판단](studies/20261022-topic-keywords/design-review.md)
- [독립 축소·문자 판독](studies/20261022-topic-keywords/legibility-review.md)
- [프롬프트 전문](studies/20261022-topic-keywords/prompts.json)
- [원본·내보내기 해시](studies/20261022-topic-keywords/release-manifest.json)
- [프로덕션 검증](studies/20261022-topic-keywords/production-validation.json)

## Source and regeneration

최종 원본은 [selected-A-keywords.png](studies/20261022-topic-keywords/selected-A-keywords.png)다.
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

큰 이미지에서 주제어를 읽고, 작은 아이콘에서는 R의 실루엣과 색으로 매체를
식별한다. 180/64/32/16px의 실제 축소본을 비교하며 모든 크기에서 일곱 약어의
완독을 보장하지 않는다. 작은 크기에도 별도 그림을 대입하지 않고 같은 원본을 쓴다.
게시기는 최종 공개 아이콘만 `site/`에 복사한다. 시안·프롬프트·검토 기록과
QA 이미지는 공개 사이트 자산에 포함하지 않는다.

## Historical studies

- [Q/AI 중심 페이지형 R과 네 출판 시안](studies/20261022-quantum-ai-editorial/design-review.md)
- [Q/AI 중심 D의 독립 판독 검토](studies/20261022-quantum-ai-editorial/legibility-review.md)
- [Q/AI 중심 D의 최종 비교](studies/20261022-quantum-ai-editorial/comparison-final.png)
- [Q 수채화 로고](studies/20261022-watercolor/design-review.md)
- [출판 정체성 네 시안](studies/20261022-editorial/design-review.md)
- [펼친 저널의 월넛 팔레트](studies/20261022-editorial-walnut/color-review.md)

과거 시안과 판단은 당시 상태로 보존한다. 이 변경은 사이트 아이콘만 다루며
기사 본문·표지·PDF를 재제작하지 않는다.
