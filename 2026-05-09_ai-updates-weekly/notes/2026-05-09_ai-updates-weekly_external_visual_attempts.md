---
title: External Visual Generator Attempts
date: 2026-05-09
status: attempted
scope:
  - notebooklm_exports/
  - skywork_inputs/
  - skywork_exports/
---

# External Visual Generator Attempts

## 목적

그림 1 후보를 `imagegen`, NotebookLM, Skywork 경로로 비교해 보고, 본문에 넣을 만큼 명확한 그림이 있는지 확인했습니다.

## 결과 요약

| 경로 | 진행 상태 | 저장된 증거 | 본문 적용 여부 |
|---|---|---|---|
| imagegen | 원본 hero 채택 | `artifacts/final_review/figures/agent-harness-hero-v2-web.png` | 적용 |
| hybrid SVG | 후보 생성 후 기각 | `artifacts/final_review/figures/agent-harness-hero-annotated.svg` | 미적용 |
| NotebookLM | source 추가, Studio Infographic 생성, PNG export 확보 | `notebooklm_exports/agent-harness-infographic/notebooklm-agent-harness-infographic.png` | 후보 확보, 본문 미적용 |
| Skywork | 기존 Image Agent 프로젝트 확인, 생성 PNG 원본 CDN 경로 확보 및 다운로드 | `skywork_exports/image_candidates/2026-05-09_skywork_gpt55_review_illustration_1.png`, `artifacts/final_review/figures/candidates/skywork-image/2026-05-09_skywork_gpt55_review_illustration_1.png` | 후보 확보, 본문 미적용 |

## NotebookLM

- Notebook URL: `https://notebooklm.google.com/notebook/bbc9028a-9465-49d6-b366-d0795bc121ca`
- 1차 확인 상태: 새 Notebook 화면과 Studio 패널의 `슬라이드 자료`, `마인드맵`, `인포그래픽` 항목까지 확인했습니다.
- 1차 저장 화면: `notebooklm_exports/notebooklm-state.png`
- 재시도 결과: NotebookLM 인증을 복구한 뒤 Playwright CLI로 browser state를 불러왔고, `Copied text` source를 추가했습니다.
- 생성 artifact: `에이전트 실무 하네스 구성도`
- export 파일:
  - `notebooklm_exports/agent-harness-infographic/notebooklm-agent-harness-infographic.png`
  - `notebooklm_exports/agent-harness-infographic/notebooklm-agent-harness-infographic-preview.png`
- 품질 판단: 구성은 명확하지만, 이미지 내부에 작은 한국어 표기 오류가 보이고 NotebookLM watermark가 남아 있습니다. 현재 본문 그림으로 바로 쓰기보다는 후보로 보관합니다.
- 판단: NotebookLM은 후보 생성 경로로 유효합니다. 다만 보고서에 직접 넣을 때는 내부 텍스트 오탈자, watermark, 해상도, HTML 배치까지 별도 audit이 필요합니다.

## Skywork

- Prompt file: `skywork_inputs/2026-05-09_ai-updates-weekly_skywork_visual_prompt_v1.md`
- 1차 확인 상태: Skywork PowerPoint skill 화면에 one-slide editorial infographic prompt를 입력했습니다.
- 1차 저장 화면:
  - `skywork_inputs/skywork_prompt_filled_no_login.png`
  - `skywork_inputs/skywork_sxs_clone_device_limit.png`
- 재시도 결과:
  - Chrome 기본 profile clone: headed Playwright CLI로 열렸지만 로그인 상태가 아니었습니다. Google 로그인 버튼 클릭 후 세션 응답이 불안정해졌습니다.
  - Chrome SxS profile clone: Skywork 홈/PowerPoint skill 화면은 열렸지만 API 응답은 401이었고 `Not signed in with the identity provider`가 기록되었습니다.
  - No-profile proof session: Skywork 화면은 열렸지만 Google 계정 provider list가 비어 있고 token retrieval error가 발생했습니다.
- 재시도 저장 화면:
  - `skywork_inputs/retry_2026-05-09/skywork-proof-no-auth.png`
  - `skywork_inputs/retry_2026-05-09/skywork-proof-console.log`
- 추가 확인: 사용자가 공유한 Skywork Image Agent 프로젝트 URL을 Playwright CLI로 열어 기존 생성 결과를 확인했습니다.
  - Project URL: `https://skywork.ai/project/2053052153576058880?from=home_query&is_new_project=false`
  - Notification artifact URL: `https://skywork.ai/project/2053052153576058880?from=notification&artifact_id=2053052423530975233&file_id=2053052423522586624&file_name=GPT-5.5%20%EB%A6%AC%EB%B7%B0%20%EC%9D%BC%EB%9F%AC%EC%8A%A4%ED%8A%B8%EB%A0%88%EC%9D%B4%EC%85%98&file_type=gen_poster&file_url=`
  - UI에서 확인한 기능 성격: `이미지` agent, `GPT Image 2`, prompt 입력, 참고 이미지 추가, `포스터`, `소셜 미디어`, `로고`, `브랜딩`, `크리에이티브` category.
  - 생성 결과: `Poster page 1`
  - 원본 이미지 URL: `https://skyagent-artifacts.skywork.ai/image/2053052153576058880/e3bc4df7-a1b6-4b8a-9bac-5b77480ec436/prod_agent_2053052153576058880/gpt55_review_illustration_1.png`
  - 원본 다운로드: `skywork_exports/image_candidates/2026-05-09_skywork_gpt55_review_illustration_1.png`
  - 본문 후보 복사본: `artifacts/final_review/figures/candidates/skywork-image/2026-05-09_skywork_gpt55_review_illustration_1.png`
- 품질 판단: Skywork가 만든 그림은 line-art/isometric editorial infographic에 가깝고, 원본 PNG 해상도와 파일 확보는 성공했습니다. 다만 이미지 안의 텍스트가 영어 중심이고, GPT-5.5 평가 메모용 그림이라 이번 `에이전트 하네스` 리뷰의 주장과 직접 맞지는 않습니다.
- 판단: Skywork Image Agent는 후보 생성 경로로 유효합니다. 본문에는 `주제 적합성`, `텍스트 품질`, `원본 PNG 확보`, `HTML 렌더링`을 통과한 결과만 채택합니다.

## 채택 결정

그림 1은 원본 imagegen hero를 사용합니다. NotebookLM 후보는 실제 export까지 확보했지만, 내부 텍스트 품질 문제가 있어 즉시 채택하지 않습니다. Skywork 후보도 실제 PNG 원본까지 확보했지만 이번 리뷰 주제에 직접 맞는 그림은 아니므로 본문에 바로 넣지 않습니다. 독자에게 보여줄 그림은 실제로 읽히는 그림이어야 하므로, 생성기는 `파일 확보`만으로 통과하지 않고 인접 문단의 메시지와 맞는지까지 감사합니다.
