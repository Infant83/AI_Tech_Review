---
title: AI Updates Weekly 리뷰 하네스 업데이트 제안
date: 2026-05-09
status: proposed
scope:
  - AGENTS.md
  - .automation/writing-style-audit-harness.md
  - C:/Users/angpa/.codex/skills/ai-tech-review-editorial-harness
  - reports/2026-05-09_ai-updates-weekly_final_review.md
---

# AI Updates Weekly 리뷰 하네스 업데이트 제안

## 1. 이번 감사에서 확인한 문제

현재 리뷰의 기조는 대체로 맞지만, 일부 제목과 전환 문장이 아직 AI식 문장으로 읽힙니다. 문제는 단순한 어휘 선택보다 더 구조적입니다. 현재 하네스 문서 안에도 같은 표현을 다시 만들 수 있는 규칙이 남아 있습니다.

| 위치 | 현재 표현 | 문제 | 수정 방향 |
|---|---|---|---|
| final_review.md | `근거 지도: 흩어진 업데이트가 같은 방향을 가리킵니다` | 무엇을 말하려는지 주제가 늦게 보임 | `에이전트 경쟁은 하네스 구축 경쟁으로 넓어지고 있습니다` |
| final_review.md | `근거 축`, `대표 소스`, `소스 성격` | 작업자 내부 용어처럼 보임 | `확인한 흐름`, `주요 참고자료`, `자료 성격` |
| final_review.md | `논문은 하네스를 연구 대상으로 올려놓았습니다` | 말은 되지만 정보량이 낮음 | `하네스 엔지니어링 연구가 본격화되고 있습니다` |
| final_review.md | `기업용 AI는 권한과 승인 표면으로 이동합니다` | 영어식 표현의 직역처럼 읽힘 | `기업용 AI는 권한과 승인 체계를 더 중요하게 다루기 시작했습니다` |
| writing-style-audit-harness.md | `근거 축`, `근거 지도`, `소스` | 하네스가 reader-facing 표현을 오염시킬 수 있음 | `참고자료`, `참고문헌`, `검증 자료`, `자료 맵`으로 교체 |

핵심 수정 원칙은 간단합니다. 제목은 현상을 묘사하는 대신, 그 현상이 가리키는 주제를 바로 말해야 합니다. 예를 들어 `흩어진 업데이트가 같은 방향을 가리킨다`보다 `에이전트 경쟁은 하네스 구축 경쟁으로 넓어지고 있습니다`가 더 낫습니다.

## 2. 하네스에 추가할 편집자 역할

### 2.1 Korean Review Expression Editor

목적: AI식 문장, 번역체, 내부 작업 용어, 낮은 정보량의 제목을 잡습니다.

필수 검사:

- 제목이 주제를 직접 말하는가, 아니면 현상만 묘사하는가
- `표면으로 이동`, `연구 대상으로 올려놓다`, `흩어진 업데이트`, `근거 축`처럼 번역체 또는 내부 용어가 남아 있는가
- `이번 리뷰는 A가 아닙니다`, `A가 아니라 B입니다`, `정리하면`, `핵심은` 같은 자동 요약체가 남아 있는가
- 첫 문단과 각 섹션 첫 문장이 독자에게 줄 메시지를 바로 보여주는가
- 기술용어가 필요한 경우 쉬운 설명이 붙어 있는가

수정 방식:

- 금지어만 제거하지 않고, 문장 주어를 구체화합니다.
- `업데이트`, `흐름`, `소식` 같은 넓은 말은 가능한 한 `논문`, `기업 발표`, `오픈소스 프로젝트`, `개발자 도구`, `권한/승인 체계`로 바꿉니다.
- 링크가 붙은 첫 언급은 참고자료 표식 역할을 하게 두고, bold는 주장이나 판단 문장에만 씁니다.

### 2.2 Review Artwork Editor

목적: Quanta Magazine식으로 글의 중간중간에 독자의 이해를 돕는 figure를 계획합니다. 다만 장식용 그림을 늘리지 않고, 각 그림이 본문 논지를 설명해야 합니다.

필수 검사:

- 글의 길이에 비해 figure가 부족하지 않은가
- hero artwork가 글의 주제를 직관적으로 열어주는가
- 구조 설명은 imagegen이 아니라 deterministic SVG/HTML 도식으로 작성되었는가
- 표로만 설명한 내용 중 figure가 더 적합한 부분은 없는가
- 각 figure에 caption, alt text, 본문 연결 문장이 있는가
- 모바일/HTML 화면에서 글자 크기와 선 두께가 읽히는가

현재 리뷰에 필요한 추가 figure 후보:

| 후보 | 목적 | 권장 형식 | 배치 |
|---|---|---|---|
| 참고자료 맵 | 논문, 기업 발표, 오픈소스, 개발자 도구, 도메인 안전 사례가 하네스 논지에 어떻게 연결되는지 보여줌 | SVG/HTML diagram | `AI 기술동향은...` 섹션 |
| 기업용 AI 하네스 흐름도 | 데이터 연결, 권한, 승인, 감사 기록이 기업용 AI의 기본 요구가 되는 흐름 설명 | SVG/HTML diagram | 권한/승인 섹션 |
| AI 코딩 병목 흐름도 | 생성보다 테스트, 리뷰, 병합, 되돌리기가 중요해지는 흐름 설명 | SVG/HTML diagram | 코딩 병목 섹션 |
| 오케스트레이션 판단 매트릭스 | 단일 모델 절차 수행과 다중 에이전트 분할의 차이를 설명 | SVG/HTML matrix | 오케스트레이션 섹션 |

## 3. .codex 스킬 제안

새 스킬명:

`ai-tech-review-editorial-harness`

권장 위치:

`C:/Users/angpa/.codex/skills/ai-tech-review-editorial-harness/`

권장 구조:

```text
ai-tech-review-editorial-harness/
  SKILL.md
  references/
    korean-review-expression-editor.md
    review-artwork-editor.md
    ai-tech-review-final-pass.md
  scripts/
    audit_review_text.py
```

`SKILL.md`는 짧게 유지하고, 세부 규칙은 `references/`로 분리합니다. 이는 `skill-creator` 기준에 맞습니다. 즉, 스킬 자체는 트리거와 절차만 담고, 긴 금지어 목록과 artwork 계획표는 필요한 경우에만 불러오도록 둡니다.

스킬 트리거:

- AI_Tech_Review의 `final_review` 작성 또는 재작성
- 한국어 기술 리뷰의 AI식 표현 감사
- Quanta-style figure/artwork 계획
- `하네스`, `governance`, `agent workflow`, `AI Updates Weekly` 같은 실행층 리뷰 작성

## 4. 워크스페이스 규칙 수정 제안

### AGENTS.md

- `근거 지도`를 reader-facing 기본 구조명으로 쓰지 않습니다.
- 구조 추천 항목은 `검증 자료표`, `참고자료 맵`, `기술동향 연결도`처럼 독자에게 보이는 표현으로 바꿉니다.
- `source`는 작업 내부에서는 허용하지만, 독자-facing 산출물에서는 `참고자료`, `참고문헌`, `Reference`, `자료`, `논문`, `공식 문서`로 바꿉니다.
- final review 작성 전에 `Korean Review Expression Editor`와 `Review Artwork Editor`를 순서대로 호출하도록 명시합니다.

### .automation/writing-style-audit-harness.md

- 금지/주의 패턴에 다음을 추가합니다.
  - `흩어진 업데이트가 같은 방향을 가리킨다`
  - `연구 대상으로 올려놓다`
  - `표면으로 이동하다`
  - `근거 축`
  - reader-facing 문맥의 `소스`
- artwork 기준을 `그림이 필요할 수도 있다`에서 `섹션별 figure 필요성을 감사한다`로 강화합니다.
- 완료 기준에 `장문 final review는 hero 외에 최소 2개 이상의 설명용 figure 후보를 검토한다`를 추가합니다.

## 5. deterministic 감사 스크립트 제안

`scripts/audit_review_text.py`는 완성도를 판정하지 않고, 사람이 볼 문제 후보만 뽑습니다.

검출 항목:

- AI식 전환어: `핵심은`, `주목할 점은`, `결론적으로`, `요컨대`
- 빈 contrast framing: `A가 아니라 B`, `A가 아닙니다`
- 번역체 후보: `표면으로 이동`, `연구 대상으로 올려놓`, `방향을 가리킵`
- 내부 용어 후보: reader-facing 문맥의 `소스`, `근거 축`, `근거 지도`
- figure 밀도: 본문 글자 수 대비 image/figure 수
- 영어 기술어: 정의되지 않은 영문 token 후보

스크립트 출력은 `pass/fail`보다 `review-needed`가 적절합니다. 글쓰기 품질은 정규식으로 판단할 수 없기 때문에, 스크립트는 편집자가 볼 위치를 빠르게 찾는 용도로만 둡니다.

## 6. 현재 리뷰에 대한 1차 수정 계획

문체 수정:

1. `근거 지도...` 섹션 제목을 주제형 제목으로 교체합니다.
2. 표의 `근거 축/소스` 표현을 독자용 표현으로 바꿉니다.
3. 표 다음 문단을 `여러 독립 자료가 같은 방향...` 식의 현상 묘사에서 `무엇이 명확해졌는지`를 말하는 문단으로 바꿉니다.
4. `논문은 하네스를...`, `권한과 승인 표면...` 같은 제목을 자연스러운 한국어 제목으로 바꿉니다.
5. References 앞 `작성 정보`에서 `발견 지도`, `소스` 같은 작업자 표현을 제거합니다.

시각 자료 수정:

1. 기존 hero artwork는 유지합니다.
2. 기존 Harness Stack 도식은 글자 크기와 레이블을 키워 다시 작성합니다.
3. `참고자료 맵` figure를 추가합니다.
4. `AI 코딩 병목 흐름도` 또는 `기업용 AI 하네스 흐름도` 중 최소 하나를 추가합니다.
5. HTML 렌더 후 Playwright로 데스크톱/모바일 가독성을 확인합니다.

## 7. 검증 루프

적용 후에는 아래 순서로 Ralph loop를 돌립니다.

1. 정규식 감사: 금지/주의 패턴 잔존 여부 확인
2. 제목 감사: 모든 H2/H3가 독립적으로 읽히는 주장인지 확인
3. 참고자료 감사: 첫 언급 링크와 References의 직접 검증 가능성 확인
4. artwork 감사: figure 수, caption, 본문 연결, 모바일 가독성 확인
5. HTML 감사: `markdown_to_html.py` 렌더 후 Playwright screenshot 확인

완료 기준:

- reader-facing 본문에 `근거 축`, `근거 지도`, `소스`가 남지 않습니다.
- 제목은 현상 묘사가 아니라 기술동향의 의미를 말합니다.
- hero 외에 최소 2개 이상의 설명용 figure가 계획되거나 삽입됩니다.
- 본문에서 bold는 주장/판단에만 쓰이고, 출처명은 링크가 강조 역할을 합니다.
- 작성 정보는 짧고 감사 가능한 수준으로 유지하되, 작업자 내부 용어를 노출하지 않습니다.

## 8. 2차 artwork 감사 반영

2026-05-09 추가 피드백에 따라 artwork 기준을 다시 높였습니다.

- 리뷰 제목과 hero는 `AI 개발 일반`이 아니라 `에이전트 활용에서 하네스가 중요해지는 흐름`을 직접 보여주도록 수정합니다.
- imagegen 그림은 분위기용으로만 쓰지 않습니다. 인접 섹션의 한 가지 메시지를 직관적으로 설명해야 하며, 가짜 텍스트·로고·라벨이 보이면 다시 생성합니다.
- SVG는 정확한 구조와 비교가 필요한 곳에만 남깁니다. 비슷한 카드형 SVG가 반복되면 기사형 bitmap illustration 또는 표로 바꿉니다.
- NotebookLM Infographic은 현재 MCP에서 직접 export가 노출되어 있지 않으므로, 사용할 경우 브라우저/수동 export로 실제 파일을 확보해 `notebooklm_exports/`에 보관합니다.
- Skywork 또는 Nano Banana 계열 artwork도 실제 export 파일, prompt, viewer capture가 있어야 본문에 넣습니다.
- 현재 리뷰에서는 새 hero `agent-harness-hero-v2-web.png`, 기업용 AI illustration, AI coding merge illustration을 사용하고, 정확한 설명이 필요한 부분에만 `harness-stack.svg`, `reference-map.svg`, `orchestration-matrix.svg`를 남깁니다.
