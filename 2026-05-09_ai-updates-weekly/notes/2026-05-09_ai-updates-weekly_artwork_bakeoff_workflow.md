---
title: AI Updates Weekly Artwork Bake-Off Workflow
date: 2026-05-09
status: active
scope:
  - artifacts/final_review/figures/
  - notebooklm_exports/
  - skywork_inputs/
  - skywork_exports/
---

# Artwork Bake-Off Workflow

## 목적

중요한 한 컷짜리 그림은 한 생성기 결과만 바로 채택하지 않습니다. 같은 visual brief를 imagegen, NotebookLM, Skywork, deterministic SVG/HTML 경로에 맞게 변환해 후보를 만들고, 가장 설명력이 좋은 그림을 고릅니다.

## 언제 쓰나

- hero image
- 섹션 opener
- 한 컷짜리 개념 설명 그림
- article-quality final review에서 독자가 복잡한 기술 흐름을 한눈에 잡아야 하는 지점

## 그림 성격 먼저 나누기

생성기를 고르기 전에 그림의 역할을 먼저 나눕니다.

| 그림 성격 | 목적 | 권장 경로 |
|---|---|---|
| 주제형 그림 | 독자가 리뷰의 문제의식을 빠르게 느끼게 함 | imagegen hero 또는 section artwork |
| 기술형 그림 | 구성요소, 순서, 권한, 검증, 병합, 되돌리기 관계를 읽히게 함 | deterministic SVG/HTML 또는 hybrid |
| 참고자료형 그림 | 논문, 공식 발표, 저장소가 어느 주장에 쓰였는지 연결 | 참고자료 맵, 표, NotebookLM/Skywork export |
| 증거형 그림 | 실제 화면, 저장소, 데이터 구조를 확인 | 공식 screenshot 또는 Playwright capture |

imagegen 그림이 좋은 질감을 주지만 주장이 잘 보이지 않으면 그대로 쓰지 않습니다. 배경 장면만 imagegen으로 두고, 정확한 라벨과 화살표를 SVG/HTML로 얹는 hybrid 그림으로 전환합니다.

## Visual Brief

각 figure마다 먼저 아래 항목을 씁니다.

| 항목 | 내용 |
|---|---|
| 섹션 | 그림이 들어갈 본문 섹션 |
| 한 문장 메시지 | 그림이 설명해야 하는 핵심 문장 |
| 반드시 보여야 할 요소 | 오브젝트, 관계, 흐름 |
| 피해야 할 요소 | 가짜 텍스트, 로고, UI hallucination, generic AI cloud |
| 추천 형식 | bitmap illustration, infographic, SVG, screenshot |
| 검증 기준 | 사실성, 가독성, 모바일 렌더링, source traceability |

## 후보 생성 경로

| 경로 | 장점 | 주의점 | 저장 위치 |
|---|---|---|---|
| imagegen | Quanta-style hero, 기사형 은유, 분위기와 subject 조율 | 가짜 텍스트와 두루뭉술한 AI imagery 감사 필요 | `artifacts/final_review/figures/candidates/<slug>/imagegen/` |
| NotebookLM + Playwright | source-grounded infographic, 요약형 구조화 | 현재 MCP는 Infographic export를 직접 제공하지 않으므로 UI export/screenshot 필요 | `notebooklm_exports/<slug>/` |
| Skywork + Playwright | presentation-quality one-cut graphic, Nano Banana-style 그림 실험 | 실제 project/export URL과 파일이 있어야 채택 가능 | `skywork_inputs/`, `skywork_exports/` |
| deterministic SVG/HTML | 정확한 labels, flow, comparison, reference map | 반복되면 slide-like해질 수 있음 | `artifacts/final_review/figures/` |

## 선택 기준

각 후보를 1-5점으로 봅니다.

| 기준 | 질문 |
|---|---|
| Message fit | 인접 문단의 핵심 메시지가 한눈에 보이는가 |
| Specificity | 이 리뷰 주제에 맞는 구체 요소가 있는가 |
| Factual safety | 사실 관계를 왜곡하지 않는가 |
| Text hygiene | 가짜 글자, 로고, 잘못된 라벨이 없는가 |
| Article fit | 본문 옆에 놓았을 때 기사형 그림처럼 보이는가 |
| Render quality | desktop/mobile HTML에서 깨지지 않는가 |
| Traceability | prompt, export, screenshot, 선택 이유가 남아 있는가 |

## 현재 리뷰 적용 상태

- 채택 hero: `agent-harness-hero-v2-web.png`
  - 방식: imagegen editorial illustration
  - 선택 이유: 원본 그림이 기사형 도입부에 더 자연스럽고, 독자가 "에이전트가 권한, 문서, 체크리스트, 연결 장치 위에서 일한다"는 문제의식을 빠르게 잡을 수 있음.
  - 기각 candidate: `agent-harness-hero-annotated.svg`
  - 기각 이유: deterministic 라벨과 화살표가 메시지를 명확하게 만들기는 했지만, 그림이 슬라이드형 도식처럼 무거워지고 배경 일러스트레이션과 라벨층이 어색하게 충돌함.
- 채택 section figures:
  - `enterprise-operating-path-hybrid.svg`
  - `coding-merge-illustration-web.png`
- 유지 deterministic figures:
  - `harness-stack.svg`
  - `reference-map.svg`
  - `orchestration-matrix.svg`

## NotebookLM/Skywork 시도 결과

- NotebookLM
  - 재시도에서 NotebookLM 인증 복구, source 추가, Studio Infographic 생성, PNG export까지 완료했습니다.
  - 증거 screenshot: `../notebooklm_exports/notebooklm-state.png`
  - export: `../notebooklm_exports/agent-harness-infographic/notebooklm-agent-harness-infographic.png`
  - 한계: 그림 구성은 명확하지만 이미지 내부에 작은 한국어 표기 오류가 보이고 NotebookLM watermark가 남아 있습니다.
  - 판단: 후보로 보관하되 본문에는 즉시 채택하지 않습니다. NotebookLM 그림은 텍스트 audit과 HTML 배치 확인 후에만 승격합니다.
- Skywork
  - PowerPoint skill 화면에 prompt를 입력하는 데까지 진행했습니다.
  - 증거 screenshot: `../skywork_inputs/skywork_prompt_filled_no_login.png`
  - Chrome SxS profile clone 시도에서는 계정의 최대 로그인 기기 수 초과 알림이 나타났습니다.
  - 증거 screenshot: `../skywork_inputs/skywork_sxs_clone_device_limit.png`
  - 재시도에서는 Chrome 기본 profile clone, Chrome SxS profile clone, no-profile proof session을 Playwright CLI로 확인했습니다.
  - 재시도 증거: `../skywork_inputs/retry_2026-05-09/skywork-proof-no-auth.png`
  - 이후 사용자 제공 project URL에서 Skywork Image Agent의 기존 생성 결과를 확인했고, `Poster page 1` 원본 PNG를 CDN 경로에서 내려받았습니다.
  - export: `../skywork_exports/image_candidates/2026-05-09_skywork_gpt55_review_illustration_1.png`
  - 후보 복사본: `../artifacts/final_review/figures/candidates/skywork-image/2026-05-09_skywork_gpt55_review_illustration_1.png`
  - 판단: Skywork Image Agent는 후보 생성 및 개별 이미지 다운로드 경로로 유효합니다. 다만 확보한 그림은 GPT-5.5 평가 메모용이라 이번 하네스 리뷰 본문에는 바로 채택하지 않습니다.

외부 생성기를 쓸 때도 최종 판단은 `message fit`, `factual safety`, `render quality`, `artifact trail` 기준으로 합니다.

## 2026-05-10 Figure 4 Bake-Off

Goal:

- Replace the enterprise section still-life with a relationship-first operating-path figure.

Candidates:

- Original: `enterprise-harness-illustration-v2-web.png`
  - Rejected for Figure 4 because it showed relevant objects but not the operating path.
- Imagegen candidate 1: `artifacts/final_review/figures/candidates/enterprise-operating-path/imagegen/image_1-web.png`
  - Good object clarity, but the human review zone was less cleanly separated.
- Imagegen candidate 2: `artifacts/final_review/figures/candidates/enterprise-operating-path/imagegen/image_2-web.png`
  - Selected as base because the sequence from data to permission, AI output, human review, and audit was easiest to read.
- Skywork attempt: `artifacts/final_review/figures/candidates/enterprise-operating-path/skywork/skywork-prompt-filled-v2.png`
  - Not selected because generation was blocked by login/signup modal in this Playwright session.

Final:

- `artifacts/final_review/figures/enterprise-operating-path-hybrid.svg`
- Method: imagegen base + deterministic Korean labels and arrows.
- Render evidence: `artifacts/final_review/figure_audit/figure-04-enterprise-operating-path-v1.png`

## 2026-05-09 Graphics Placement Audit

그래픽 배치 감사 결과, 현재 리뷰는 figure 수는 충분하지만 `memory/evaluation`, `connector`, `domain safety` 구간의 시각적 받침이 약한 것으로 판단했습니다. 자세한 감사 기록은 `2026-05-09_ai-updates-weekly_editorial_graphics_audit.md`에 남겼습니다.

다음 Skywork Image 실험은 아래 순서로 진행합니다.

1. `Memory / Evaluation Loop`: Skywork `인포그래픽`
2. `Connector Permission Surface`: Skywork `인포그래픽` 또는 deterministic SVG
3. `High-risk Domain Safety Harness`: deterministic process map 또는 Skywork `인포그래픽`

Prompt pack은 `../skywork_inputs/2026-05-09_ai-updates-weekly_skywork_image_prompt_pack.md`를 사용합니다.
