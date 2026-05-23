---
title: Editorial Graphics Audit Harness
date: 2026-05-09
status: active
scope:
  - AI_Tech_Review final reviews
  - artifacts/final_review/figures/
  - skywork_exports/image_candidates/
  - notebooklm_exports/
---

# Editorial Graphics Audit Harness

## 목적

AI_Tech_Review의 최종 리뷰는 글과 그림이 따로 놀면 안 됩니다. 그림은 독자가 글의 구조를 편하게 따라가도록 돕는 설명 장치입니다. 이 하네스는 Skywork Image, GPT Image 2/imagegen, NotebookLM, deterministic SVG/HTML을 각각 다른 역할로 쓰기 위한 편집 규칙입니다.

목표는 Quanta Magazine류의 과학 기사처럼 세련되지만, 한국어 기술 리뷰에 맞게 더 빠르게 주제를 보여주는 구성입니다. 독자는 바쁜 동료, 기술 리더, 실무 담당자입니다. 그림은 예쁘기만 하면 부족하고, “아, 이 글은 이 이야기를 하려는 거구나”라는 감을 줘야 합니다.

기본 참고 사이트는 [editorial-reference-pool](./editorial-reference-pool.md)에 등록합니다. 현재 기준은 [Quanta Magazine](https://www.quantamagazine.org/), [고등과학원 HORIZON](https://horizon.kias.re.kr/), [최종현학술원 Science Note 과학노트](https://www.chey.org/Kor/ScienceNote/ScienceNoteList.aspx)입니다.

## 역할 분리

| 경로 | 주된 역할 | 좋은 용도 | 피해야 할 용도 |
|---|---|---|---|
| Skywork Image | 잡지형 artwork infographic의 주 후보 | 개념 설명, 작업 흐름, “한 컷으로 보는 구조”, 포스터형 설명 그림, section opener | 검증되지 않은 숫자/출처, 긴 한국어 문장, 가짜 UI |
| GPT Image 2 / `imagegen` | 고품질 editorial scene과 시각 은유 | hero image, section opener, 독자의 관심을 여는 editorial metaphor, 텍스트 없는 infographic base | 정확한 라벨, 회사별 비교, 논문 관계도 |
| deterministic SVG/HTML | 정확한 라벨과 구조 보정 | 하네스 구성도, reference map, timeline, 비교 매트릭스, 생성 이미지 위의 라벨/화살표 후처리 | 반복 사용으로 슬라이드처럼 보이게 만들기 |
| NotebookLM | 참고자료 기반 요약형 시각화 | source-grounded infographic 후보, 글 흐름 점검용 visual brief | watermark/오탈자 있는 이미지를 바로 본문에 넣기 |
| Playwright screenshot | 증거형 그림 | 실제 제품 UI, 저장소, 다운로드/설정 화면 증명 | 장식용 screenshot |

## Default Artwork Route

잡지형 리뷰에서는 평면 SVG를 기본값으로 두지 않습니다. H2가 많은 긴 글이라면, 아래 그림은 먼저 Skywork Image 또는 GPT Image 2/imagegen 후보를 검토합니다.

- Hero artwork.
- 독자가 개념 전환을 해야 하는 첫 번째 설명 그림.
- 기업/제품/업무 흐름을 한 컷으로 보여주는 그림.
- 참고자료 맵이나 프로세스 맵이 너무 슬라이드처럼 보이는 경우의 대체 후보.
- 내부 공유용 thumbnail, poster, social card.

SVG/HTML은 여전히 중요합니다. 다만 역할은 `정확한 구조`, `한글 라벨`, `화살표`, `출처 연결`, `생성 이미지 위 후처리` 쪽으로 둡니다. 그림 자체의 흡입력과 잡지형 완성도는 Skywork/GPT Image 2 후보와 비교해 판단합니다.

## Skywork Image 사용 기준

Skywork Image와 GPT Image 2/imagegen은 둘 다 적극적으로 검토합니다. Skywork는 설명적인 포스터와 infographic에 유리하고, GPT Image 2/imagegen은 장면의 질감, 사물 배치, hero artwork, 개념적 metaphor에 유리합니다.

Skywork category는 아래처럼 씁니다.

| Skywork category | 리뷰에서의 쓰임 | Prompt 방향 |
|---|---|---|
| 인포그래픽 | 개념 구조, 비교, 흐름 설명 | “한 컷으로 읽히는 editorial infographic, 짧은 라벨, 넓은 여백” |
| 포스터 | 섹션 opener, 강한 한 문장 메시지 | “본문 중간에 들어갈 16:9 poster-style explainer, 큰 장면 중심, 텍스트 최소화” |
| 소셜미디어 | 짧은 요약 카드, 내부 공유 thumbnail | “정사각형/4:5 summary card, 핵심 메시지 1개” |
| 로고 | 리뷰 시리즈, topic icon, visual motif | “AI_Tech_Review topic mark, no brand imitation, simple vector-like symbol” |
| 브랜딩 | 시리즈 일관성, 색/아이콘 체계 | “같은 리뷰 시리즈에서 반복 가능한 icon set, restrained palette” |
| 크리에이티브 | 비유적 장면, hero 후보 | “text-free editorial scene, concrete objects, no generic AI cloud” |

## Figure Planning Loop

최종 리뷰를 쓰거나 고칠 때, artwork editor는 본문을 읽고 아래 순서로 판단합니다.

1. 글의 주제를 한 문장으로 적습니다.
2. 독자가 어려워할 technical jump를 찾습니다.
3. H2마다 그림이 필요한지, 표로 충분한지, 문장만으로 충분한지 분류합니다.
4. 필요한 그림을 `주제형`, `정보형`, `정확도형`, `증거형`으로 나눕니다.
5. `주제형`과 `정보형`은 Skywork/GPT Image 2 후보를 먼저 검토하고, `정확도형`은 SVG/HTML 또는 hybrid를 고릅니다.
6. 후보 그림을 만든 뒤, 본문 옆에 놓고 다시 읽습니다.

## Figure Purpose Gate

본문 중간에 들어가는 그림은 먼저 목적을 통과해야 합니다. 그림의 목적이 “분위기를 부드럽게 한다” 정도에 머물면 hero나 section opener로는 쓸 수 있지만, 기술 설명 figure로는 약합니다.

각 figure를 만들기 전에 아래 네 줄을 먼저 씁니다.

```text
인접 섹션:
독자가 이해해야 할 한 문장:
그림 안에 보여야 할 관계:
그림 없이도 되는지:
```

채택하지 않을 신호:

- 본문 캡션을 읽기 전에는 왜 이 그림이 있는지 알기 어렵습니다.
- 사물은 많지만 관계가 보이지 않습니다. 예: 문서, 자물쇠, 체크리스트가 놓여 있으나 `접근 -> 권한 -> 검토 -> 승인 -> 감사`의 순서가 보이지 않습니다.
- 같은 역할의 분위기 그림이 이미 앞뒤에 있습니다.
- 정보형 그림이어야 하는데 imagegen 장면이 article decoration처럼만 보입니다.

이 경우에는 route를 바꿉니다.

| 실패한 상태 | 바꿀 방향 |
|---|---|
| 분위기 있는 사물 배치 | Skywork `인포그래픽` 또는 deterministic workflow |
| 정확한 관계가 필요한데 라벨이 없음 | imagegen/Skywork base + SVG 라벨 |
| 그림이 설명보다 장식에 가까움 | 삭제하거나 section opener로 이동 |
| 절차가 핵심 | deterministic SVG skeleton 먼저 작성 |

## Term-Lineage Visual Rule

핵심 용어가 글의 중심일 때는, 용어 설명을 글로만 길게 끌지 말고 작은 계보형 도식을 검토합니다.

예:

- `test harness` -> `LLM evaluation harness` -> `agent harness`
- `모델 평가` -> `도구 실행` -> `권한/기억/검증/승인`

권장 도구:

- 정확한 용어 계보와 짧은 라벨이 필요하면 deterministic SVG/HTML.
- 독자가 첫 장면에서 감을 잡아야 하면 imagegen 또는 Skywork `크리에이티브`.
- “한 컷으로 보는 하네스의 진화”처럼 글과 그림이 함께 설명해야 하면 Skywork `인포그래픽` 후보를 만들고, 텍스트는 후처리합니다.

주의:

- 생성 이미지 안에 긴 한국어 문장을 넣지 않습니다.
- 하네스가 특정 회사가 만든 용어처럼 보이게 하지 않습니다.
- 출처가 필요한 계보는 caption이나 본문 문장에 링크로 붙입니다.

## Reader-First Figure Map

긴 기술 리뷰는 보통 아래 rhythm이 좋습니다.

| 위치 | 그림 역할 | 권장 도구 |
|---|---|---|
| 제목 직후 | 이 글의 주제를 한 장면으로 열기 | `imagegen` 또는 Skywork `크리에이티브` |
| 첫 개념 설명 뒤 | 용어와 구조를 붙잡기 | Skywork `인포그래픽`, GPT Image 2 base + SVG 라벨, 또는 deterministic SVG |
| 참고자료가 많이 나오는 곳 | 자료가 어떤 주장에 쓰였는지 보여주기 | Skywork `인포그래픽` 후보 후 SVG/reference map과 비교 |
| 기업/제품 사례 | 실제 업무 흐름을 한 컷으로 보여주기 | Skywork `포스터` 또는 `인포그래픽` |
| 개발/운영 병목 | 순서와 병목을 보여주기 | Skywork `인포그래픽`, GPT Image 2 editorial scene, 또는 SVG process map |
| 결론 직전 | 독자가 가져갈 질문을 정리하기 | small decision matrix, pull quote, or summary card |

## Prompt 원칙

Skywork와 GPT Image 2/imagegen prompt 모두 “멋진 AI 그림”으로 시작하지 않습니다. 독자가 이해해야 할 문장을 먼저 씁니다.

```text
이 그림이 설명해야 할 한 문장:
[독자가 이해해야 할 메시지]

그림 안에 보여야 할 대상:
[구체 사물, 관계, 흐름]

그림에서 피할 것:
가짜 로고, 긴 문장, 어색한 한국어 라벨, 추상 AI cloud, 과한 gradient, stock-photo 느낌

스타일:
차분한 과학/기술 editorial infographic, 넓은 여백, 선명한 hierarchy, 작은 포인트 컬러

텍스트 정책:
정확한 라벨이 필요하면 이미지 안에 넣지 말고 후처리한다.
Skywork가 텍스트를 넣어야 한다면 1-3단어짜리 짧은 영어 라벨만 허용한다.
```

## Process Figure Rule

절차, 루프, 승인 흐름, 재시도 흐름, 기억 선별처럼 순서와 조건이 중요한 그림은 이미지 생성부터 시작하지 않습니다. 이런 그림은 먼저 deterministic SVG/HTML로 통제 흐름을 고정한 뒤, 필요한 경우에만 Skywork Image나 GPT Image 2/imagegen을 배경 질감, section opener, 대체 후보로 씁니다.

이미지 생성 모델에 `작업 엔진`, `기억 장부`, `평가 체크리스트`, `재시도 루프`, `승인 도장`을 한 줄로 배치하게 맡기면 아이콘 나열처럼 보이기 쉽습니다. 특히 장기 작업 에이전트 그림에서는 `어떤 기억이 선별되는지`, `어떤 기준으로 평가되는지`, `무엇이 재시도 조건이 되는지`가 주제이므로, 사물보다 제어 관계가 먼저 보여야 합니다.

프로세스형 figure의 기본 순서:

1. 그림이 설명해야 할 한 문장을 쓴다.
2. 주요 상태와 조건을 노드로 적는다.
3. 정상 경로와 재시도/예외 경로를 서로 다른 선 스타일로 분리한다.
4. 사람 승인, 평가 기준, 기억 선별처럼 책임이 걸린 지점은 큰 노드로 둔다.
5. 이미지 생성 후보가 필요하면 이 SVG skeleton을 기준으로 비교한다.

채택하지 않을 신호:

- 루프가 단순한 원형 화살표 장식으로 보인다.
- 로봇 팔, 도장, 체크리스트 같은 사물이 많지만 제어 관계가 보이지 않는다.
- 라벨을 제거하면 adjacent paragraph의 핵심이 사라진다.
- 실제 HTML 폭에서 노드 라벨보다 아이콘이 먼저 눈에 들어온다.

## Label Occlusion Rule

생성 이미지 위에 SVG/HTML 라벨, 화살표, 말풍선, 칩을 얹을 때는 라벨이 그림의 주된 사물과 관계를 가리면 안 됩니다. 라벨이 정확해도, 그 라벨 때문에 독자가 원래 그림을 읽지 못하면 실패한 figure입니다.

기본 원칙:

1. 큰 라벨 박스는 그림 안쪽 사물 위가 아니라 여백, 가장자리, 하단 범례, 측면 레일에 둡니다.
2. 본 그림 위에는 작은 번호 배지, 짧은 포인터, 얇은 leader line만 남기는 방식을 우선 검토합니다.
3. 생성 이미지의 잘못된 글자나 불필요한 잔여 텍스트를 가릴 때도, 그것이 새 라벨처럼 보이거나 핵심 사물을 덮지 않는지 확인합니다.
4. 라벨이 필요하면 `번호 배지 + 범례`, `외곽 callout`, `측면 legend`, `caption 보강` 중 하나를 먼저 시도합니다.
5. 실제 HTML 폭에서 캡처해 라벨을 눈으로 확인합니다. 자동 로드 검사는 라벨 가림을 잡지 못합니다.

채택하지 않을 신호:

- 라벨 박스가 문서 더미, 체크리스트, 도구, 사람 승인 지점, 흐름선 같은 주요 시각 단서를 덮습니다.
- 라벨을 읽기 전에는 그림의 장면이 무엇인지 파악하기 어렵습니다.
- generated artwork의 장점보다 후처리 라벨이 먼저 보입니다.
- 모바일/본문 폭에서 라벨과 원본 이미지가 경쟁합니다.

## Feynman Explanation Rule

그림과 본문은 함께 쉬워져야 합니다.

- 어려운 개념을 먼저 말하고 독자를 따라오게 하지 않습니다.
- “이건 회사에서 일을 맡길 때 책상, 출입증, 체크리스트를 같이 주는 일과 비슷합니다”처럼 가까운 예시로 시작합니다.
- 비유가 기술 관계를 흐리면 제거합니다.
- 그림 caption은 다시 논문 제목을 나열하지 말고, 독자가 알아야 할 한 가지 관계를 말합니다.

## Audit Checklist

각 figure는 아래 질문을 통과해야 합니다.

| 항목 | 질문 |
|---|---|
| Message | 그림만 보고도 인접 문단의 메시지를 짐작할 수 있는가 |
| Specificity | 이 글에만 맞는 구체 사물이 있는가 |
| Text hygiene | 가짜 글자, 어색한 라벨, 틀린 한국어가 없는가 |
| Visual comfort | 독자가 쉬어갈 수 있는 여백과 hierarchy가 있는가 |
| Readability | 실제 HTML 폭에서 글자, 화살표, 라벨이 겹치지 않고 읽히는가 |
| Occlusion | 라벨, 칩, 배지가 원본 그림의 주요 사물과 흐름을 가리지 않는가 |
| Variety | hero, infographic, 도식, 표가 서로 다른 역할을 하는가 |
| Evidence | 사실을 주장하는 그림이면 참고자료와 연결되는가 |
| HTML | 모바일/데스크톱에서 crop, overlap, 작은 글자 문제가 없는가 |

## Rendered Screenshot Rule

`complete=true`, `overflow=false`, `broken image=0` 같은 자동 점검만으로 figure를 통과시키지 않습니다. 특히 SVG 도식은 실제 HTML 폭에서 캡처를 보고 아래 항목을 눈으로 확인합니다.

- 화살표가 박스 안의 제목이나 보조 설명을 가리지 않는가.
- 작은 보조 라벨이 화살표, 박스 테두리, 다른 라벨과 겹치지 않는가.
- 곡선 화살표가 의미를 돕는가, 아니면 장식처럼 복잡하게 만드는가.
- 본문 폭으로 줄어든 뒤에도 제목, 노드 라벨, 캡션이 한 번에 읽히는가.
- 루프를 보여주려다 시각적 충돌이 생기면, 루프 라벨을 줄이고 주요 경로와 예외 경로를 분리했는가.

검증 기록에는 캡션 번호, 이미지 경로, 실제 렌더링 폭, 확인한 스크린샷 경로를 남깁니다. 문제가 있으면 “로드 정상”이라고 쓰지 말고 “로드는 정상이나 시각 겹침 있음”으로 기록합니다.

## 채택 기준

아래 중 하나라도 맞으면 본문에 넣지 않습니다.

- caption을 길게 읽어야만 그림의 의미가 보입니다.
- 실제 HTML 캡처에서 라벨이 작거나, 화살표가 박스를 가로지르거나, 긴 문장이 그림 안에서 겹칩니다.
- 생성 이미지 안의 글자가 틀리거나 출처처럼 보이는 가짜 요소가 있습니다.
- 같은 스타일의 SVG 카드가 반복되어 기사보다 슬라이드처럼 보입니다.
- 본문 주장보다 그림이 더 넓거나 과한 주장을 합니다.
- 이미지 파일, prompt, 생성 경로, 채택 이유가 남아 있지 않습니다.

채택하지 않은 그림은 삭제하지 말고 candidate 폴더에 보관합니다. 나중에 같은 주제의 slide, thumbnail, 내부 공유 카드에 재활용할 수 있습니다.
