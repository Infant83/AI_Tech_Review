# Visuals And Image Generation Rules

이 문서는 AI_Tech_Review의 리뷰, 리포트, 발표 자료에서 figure, illustration, generated image를 어떻게 사용할지 정한다. 목표는 장식이 아니라 이해 보조다.

## When To Add Visuals

다음 경우에는 텍스트만 두지 말고 figure 또는 illustration을 검토한다.

- 여러 구성 요소가 관계를 이루는 경우
- 시간 흐름, 절차, 파이프라인, 승인 흐름이 있는 경우
- 비교 대상이 3개 이상인 경우
- 독자가 처음 보는 개념을 빠르게 잡아야 하는 경우
- 본문이 추상적인데 실제 적용 지점을 보여줘야 하는 경우
- final_review가 article-like reading surface로 쓰이는 경우

좋은 visual 유형:

- 계층도: model, connector, memory, permission, verification, merge 같은 층을 보여줄 때
- 흐름도: 입력, 처리, 검증, 병합, 배포 순서를 보여줄 때
- 비교도: 기존 방식과 하네스 기반 방식을 비교할 때
- 참고자료 맵: 논문, 공식 발표, 저장소, 문서의 신뢰도와 역할을 보여줄 때
- 작은 spot illustration: 강의나 인트로에서 분위기와 주제를 연결할 때

## Placement

- 인트로 figure는 주제의식을 빠르게 잡아주는 역할만 한다.
- 본문 중간 figure는 독자가 막히는 지점 바로 앞이나 뒤에 둔다.
- 결론 figure는 새로운 내용을 넣기보다 정리와 회수를 돕는다.
- 한 페이지 또는 한 섹션에 figure가 너무 적으면 추상적으로 느껴질 수 있다. 핵심 개념마다 적절한 시각 자료를 검토한다.
- figure를 넣은 뒤 본문에서 반드시 그 figure가 왜 필요한지 받아준다.

## Caption Style

캡션은 짧고 독자 중심으로 쓴다.

좋은 예:

- `이 그림은 connector, memory, 권한, 검증, 병합이 하나의 실행 구조로 맞물리는 모습을 보여줍니다.`
- `이 도식은 모델 성능만으로는 설명되지 않는 운영 계층을 분리해서 보여줍니다.`
- `이 표는 세 접근법이 책임 분리, 검증 가능성, 운영 부담에서 어떻게 다른지 비교합니다.`

피할 예:

- `AI가 이 메시지를 시각화했습니다.`
- `이 그림은 제가 만든 구조를 보여줍니다.`
- `모델 하나가 아니라 ... 있어야 한다는 메시지를 시각화했습니다.`

## Image Generation Metadata

이미지 생성 정보는 유지하되, 본문 설명과 분리한다.

권장 형식:

```markdown
<small>Image generated with OpenAI image model. Prompt and editing notes are recorded in `artifacts/final_review/figure_manifest.md`.</small>
```

가능하면 figure manifest를 남긴다.

```markdown
| Figure | Purpose | Tool | Prompt Summary | Source/Reference | Review Notes |
| --- | --- | --- | --- | --- | --- |
| Figure 1 | 하네스 계층 인트로 | OpenAI image model | White LG-style layered execution harness | Internal concept sketch | 캡션은 독자 중심으로 수정 |
```

## Generated Image Rules

- LG 스타일 문맥에서는 흰 배경, 짙은 회색 글씨, LG Red 포인트를 기본으로 한다.
- 장식용 gradient blob, 과한 bokeh, 추상 배경만 있는 이미지는 피한다.
- 인트로 이미지는 주제를 암시하되, 본문을 대신 설명하려 들지 않는다.
- 기술 리뷰용 이미지는 예쁜 장면보다 구조, 관계, 책임 분리를 보여줘야 한다.
- 이미지 안의 글자는 최소화한다. 필요한 레이블은 렌더링 후 읽히는지 확인한다.
- 캡션 없이 이미지만 두지 않는다.
- 생성 이미지가 실제 제품, 논문, 벤치마크 결과처럼 오해될 수 있으면 명확히 구분한다.

## Tool Roles

이미지 생성 도구는 같은 역할로 쓰지 않는다.

| 도구 | 주된 역할 | 적합한 결과물 |
|---|---|---|
| imagegen | 주제형 장면과 hero | 기사형 hero, section opener, 개념 비유 장면 |
| Skywork Image | 정보형 editorial infographic | 인포그래픽, 포스터형 설명 그림, 소셜 공유 카드, topic icon, branding kit |
| deterministic SVG/HTML | 정확한 도식 | 하네스 구조, 참고자료 맵, timeline, 비교 매트릭스 |
| NotebookLM | 참고자료 기반 후보 | 요약형 infographic 후보, source-grounded visual check |
| Playwright screenshot | 증거형 이미지 | 실제 UI, 저장소, export/download 확인 |

Skywork category는 목적별로 고른다.

- `인포그래픽`: 구조, 비교, 흐름을 한 컷으로 설명할 때
- `포스터`: 섹션 opener나 한 문장 메시지를 강하게 보여줄 때
- `소셜미디어`: 내부 공유용 요약 카드나 thumbnail이 필요할 때
- `로고`: topic icon이나 시리즈 motif가 필요할 때
- `브랜딩`: 리뷰 시리즈의 반복 가능한 색/아이콘 체계를 잡을 때
- `크리에이티브`: 비유적 장면이나 hero 후보를 만들 때

Skywork 결과를 본문에 넣으려면 prompt, project/artifact URL, 원본 export, 후보 복사본, 채택/기각 이유를 남긴다. 한국어 장문 라벨은 이미지 모델에 맡기지 않고 HTML/SVG 후처리를 우선한다.

## Verification

이미지를 포함한 산출물은 반드시 눈으로 확인한다.

- Markdown/HTML에서 이미지 링크가 깨지지 않는지 확인한다.
- 공유용 ZIP이나 패키지에는 이미지 파일과 manifest를 함께 포함한다.
- 강조, 링크, caption, small metadata가 렌더링에서 보이는지 확인한다.
- 슬라이드나 HTML에서 figure가 너무 작아 읽기 어려우면 다시 배치한다.
- HTML companion을 만들었다면 Playwright 또는 브라우저로 hero, figure, caption, callout이 실제로 보이는지 확인한다.
