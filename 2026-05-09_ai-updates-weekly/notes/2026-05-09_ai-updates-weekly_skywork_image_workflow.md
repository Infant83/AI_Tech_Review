---
title: Skywork Image Agent Workflow for AI Updates Weekly Review
date: 2026-05-09
status: verified-candidate-path
scope:
  - skywork_inputs/
  - skywork_exports/image_candidates/
  - artifacts/final_review/figures/candidates/skywork-image/
---

# Skywork Image Agent Workflow

## 확인한 기능

Skywork 도움말의 Images Agent 문서는 이미지 생성, 편집, export를 하나의 흐름으로 설명합니다. 공식 도움말 기준으로 Images Agent는 prompt 기반 생성, 참고 이미지 기반 생성, canvas 편집, layer separation, erase, remove background, expand image, upscale, inpaint를 지원합니다.

- Help: `https://skywork.ai/help/tutorial?key=019c040e-a839-7550-8a19-633aeb0b1708`
- Home UI에서 확인한 agent: `이미지`, `GPT Image 2`
- Home UI에서 확인한 category: `포스터`, `소셜 미디어`, `로고`, `브랜딩`, `크리에이티브`

## 2026-05-10 UI 재확인

Playwright로 `https://skywork.ai/?skill_id=119`를 다시 열어 현재 이미지 생성 홈을 확인했습니다. 이번 세션은 로그인되지 않은 상태였지만, 이미지 생성 UI와 카테고리 구조는 확인할 수 있었습니다.

- 확인 screenshot: `../artifacts/final_review/figure_audit/skywork-image-ui-2026-05-10.png`
- 상단 입력 영역: `이미지 생성·편집`, 참고 이미지 추가, 자동 모델 선택
- 선택된 agent: `이미지`, 하단에 `GPT Image 2` 표시
- 입력 영역 category button: `포스터`, `소셜 미디어`, `로고`, `브랜딩`, `크리에이티브`
- 디자인 영감 filter: `인포그래픽`, `포스터`, `소셜 미디어`, `로고`, `브랜딩`, `크리에이티브`

판단:

- Skywork는 단순한 장면 생성뿐 아니라 `인포그래픽`, `포스터`, `브랜딩`, `소셜 카드`를 나눠 시도할 수 있는 후보 생성기입니다.
- 리뷰 본문에서는 `인포그래픽`을 구조 설명용, `포스터`를 section opener용, `브랜딩`을 시리즈형 반복 요소용, `소셜 미디어`를 공유 카드용으로 나눠 쓰는 편이 맞습니다.
- 한국어 라벨과 정확한 흐름은 여전히 SVG/HTML 후처리로 관리합니다.

## 2026-05-10 Figure 4 생성 시도

Figure 4 교체를 위해 `Enterprise Agent Operating Path` brief를 Skywork 이미지 입력창에 넣었습니다.

- Prompt: `../artifacts/final_review/figures/prompts/enterprise-operating-path-skywork.txt`
- Evidence screenshot: `../artifacts/final_review/figures/candidates/enterprise-operating-path/skywork/skywork-prompt-filled-v2.png`

결과:

- 입력창에 prompt를 넣는 것은 가능했습니다.
- 생성 단계에서는 로그인/회원가입 모달이 표시되었습니다.
- 이번 pass에서는 Skywork export가 생성되지 않았으므로 본문 채택 후보로 쓰지 않았습니다.

후속 원칙:

- Skywork는 로그인된 세션에서 다시 시도합니다.
- 생성이 완료되면 project URL, 원본 PNG, candidate copy, accept/reject note를 남긴 뒤 imagegen 후보와 같은 rubric으로 비교합니다.
- Figure 4처럼 운영 경로가 핵심인 그림은 Skywork `인포그래픽` 후보를 우선 시도하되, 한국어 라벨과 화살표는 SVG/HTML 후처리로 관리합니다.

## 검증한 다운로드 경로

사용자 제공 Skywork project URL에서 기존 Image Agent 결과를 확인했습니다.

- Project URL: `https://skywork.ai/project/2053052153576058880?from=home_query&is_new_project=false`
- Artifact URL: `https://skywork.ai/project/2053052153576058880?from=notification&artifact_id=2053052423530975233&file_id=2053052423522586624&file_name=GPT-5.5%20%EB%A6%AC%EB%B7%B0%20%EC%9D%BC%EB%9F%AC%EC%8A%A4%ED%8A%B8%EB%A0%88%EC%9D%B4%EC%85%98&file_type=gen_poster&file_url=`
- DOM에서 확인한 생성물: `Poster page 1`
- 원본 이미지 URL: `https://skyagent-artifacts.skywork.ai/image/2053052153576058880/e3bc4df7-a1b6-4b8a-9bac-5b77480ec436/prod_agent_2053052153576058880/gpt55_review_illustration_1.png`
- 저장 파일:
  - `../skywork_exports/image_candidates/2026-05-09_skywork_gpt55_review_illustration_1.png`
  - `../artifacts/final_review/figures/candidates/skywork-image/2026-05-09_skywork_gpt55_review_illustration_1.png`

현재 확인한 가장 안정적인 개별 다운로드 방식은 다음입니다.

1. Skywork project 또는 notification artifact URL을 엽니다.
2. `Poster page 1` 같은 결과 이미지가 보이면 Playwright `eval`로 `document.images`를 확인합니다.
3. `image_process=...resize...`가 붙은 thumbnail URL이 있으면 query string을 제거해 원본 PNG URL을 확인합니다.
4. `Invoke-WebRequest`로 원본 PNG를 `skywork_exports/image_candidates/`에 저장합니다.
5. 본문 후보로 검토할 파일만 `artifacts/final_review/figures/candidates/skywork-image/`에 복사합니다.

## 이번 리뷰에 필요한 Skywork 이미지 후보

Skywork Image Agent는 글자까지 포함한 infographic을 만들 수 있지만, 한국어 라벨 정확도와 주제 적합성은 별도 검증이 필요합니다. 이번 `에이전트 하네스` 리뷰에서는 아래처럼 그림 역할을 나눠 요청하는 편이 좋습니다.

| 후보 | 본문 위치 | Skywork 요청 방식 | 텍스트 정책 | 채택 기준 |
|---|---|---|---|---|
| Section opener: agent workbench | 도입부 다음 | `크리에이티브` 또는 `포스터`, editorial line art | 이미지 내부 텍스트 금지 | 에이전트가 권한, 문서, connector, 승인 흐름 위에서 일한다는 장면이 보일 것 |
| Technical cutaway: harness layers | 하네스 설명 섹션 | `포스터`, isometric technical infographic | 영어 short label까지만 허용 | model core, connectors, memory, permission, evaluation, approval, merge가 분리돼 보일 것 |
| Governance workflow | 기업용 AI 섹션 | `브랜딩` 또는 `크리에이티브`, professional editorial diagram | 텍스트 최소화 | 승인, 권한, 감사 로그, 되돌리기 흐름이 한눈에 보일 것 |
| Developer merge bottleneck | 개발 workflow 섹션 | `포스터`, clean software diagram | 내부 텍스트 금지, 라벨은 HTML/SVG 후처리 | code generation보다 test, review, merge, rollback이 병목으로 보일 것 |

## Skywork category 운용

Skywork Image는 `imagegen`과 같은 역할로 쓰지 않습니다. `imagegen`은 독자의 시선을 여는 장면을 만들고, Skywork는 독자가 구조를 이해하도록 돕는 설명형 그림을 맡깁니다.

| Category | 리뷰에서의 역할 | 좋은 예 |
|---|---|---|
| 인포그래픽 | 구조, 비교, 흐름을 한 컷으로 설명 | 하네스 구성요소, 에이전트 작업 흐름, 권한-승인 루프 |
| 포스터 | 섹션 opener와 한 문장 메시지 | “모델보다 작업 구조가 중요해지는 순간” 같은 메시지형 그림 |
| 소셜미디어 | 내부 공유용 요약 카드 | 리뷰를 공유할 때 쓰는 1:1 또는 4:5 카드 |
| 로고 | topic icon 또는 시리즈 motif | `AI Harness`, `Agent Workflow`, `Governance` 같은 주제 아이콘 |
| 브랜딩 | 반복 가능한 시각 체계 | 색상, 아이콘, 카드 스타일을 맞춘 리뷰 시리즈 assets |
| 크리에이티브 | 비유적 장면 | 도입부 hero 후보, 독자의 관심을 여는 scene |

Skywork가 텍스트를 잘 배치할 수 있더라도, 한국어 문장형 라벨은 최소화합니다. 본문에서 사실과 연결되는 라벨은 HTML/SVG로 후처리하는 편이 안전합니다.

## Prompt pattern

Skywork에는 `그럴듯한 AI 그림`보다 `어떤 주장에 쓰일 그림인지`를 먼저 줍니다. 한국어 라벨을 이미지 모델에 맡기면 오탈자 가능성이 있으므로, 최종 리뷰용 그림은 가급적 텍스트 없는 장면으로 생성하고 라벨은 HTML/SVG에서 얹습니다.

```text
리뷰 아티클에 사용할 16:9 editorial technology illustration.
주제: AI agent가 실무에서 유용해지려면 모델만이 아니라 권한, connector, memory, 검증, 승인, 병합/되돌리기 하네스가 필요하다는 점.
장면: 중앙의 모델 코어가 문서, 코드 변경, 브라우저, 데이터 connector, 권한 카드, 승인 체크리스트, 감사 로그와 연결된 작업대 위에 놓여 있다.
구성: 한눈에 "agent workbench / harness"가 보이게 하고, 사람 얼굴/로봇/추상 AI cloud는 넣지 않는다.
스타일: Quanta Magazine처럼 차분한 과학/기술 일러스트레이션, 선명한 line art, warm white background, restrained teal and amber accents.
텍스트: 이미지 내부에는 단어, 문장, 로고, UI 텍스트를 넣지 않는다. 필요한 라벨은 후처리로 추가할 예정이다.
품질: high resolution, clean composition, no fake letters, no brand logos, no stock-photo look.
```

## 채택 감사

Skywork 이미지는 아래 네 가지를 통과해야 본문 figure로 승격합니다.

1. 주제 적합성: 인접 문단의 핵심 문장이 그림만 보고도 추정됩니다.
2. 텍스트 위생: 가짜 글자, 틀린 라벨, 어색한 한국어가 없습니다.
3. 파일 추적성: prompt, project URL, 원본 PNG, 후보 복사본이 모두 남아 있습니다.
4. 렌더링: HTML desktop/mobile에서 crop, overlap, 해상도 문제가 없습니다.
