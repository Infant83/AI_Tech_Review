# Skills And Verification Rules

이 문서는 AI_Tech_Review에서 스킬과 검증 절차를 어떻게 사용할지 정한다. 기본 원칙은 “그럴듯한 초안”이 아니라 출처, 산출물, 렌더링, 공유 경로까지 확인된 결과를 남기는 것이다.

## Skill Use

요청이 스킬 설명과 맞으면 해당 스킬을 사용한다. 스킬을 사용했다면 짧게 이유를 밝힌다.

주요 사용 기준:

- OpenAI 제품/API 사용법 확인: `openai-docs`
- Skywork 발표 자료 생성/수정/검수: `skywork-ppt-workflow`
- 이미지 생성 또는 이미지 편집: `imagegen`
- PDF 읽기/생성/검수: `pdf`
- DOCX 읽기/생성/검수: `doc`
- HWPX 생성/편집: `hwpx`
- 브라우저 기반 검증, HTML 렌더링 확인, 외부 웹앱 확인: `playwright` 또는 `build-web-apps:frontend-testing-debugging`
- OpenProject 조회/업데이트: `openproject`
- Gmail 발송/메일 패키지 확인: `gmail:gmail`

스킬은 만능 규칙이 아니다. `AGENTS.md`, `.automation/writing-style-audit-harness.md`, `.codex/rules`, topic package runlog가 더 구체적이면 로컬 규칙을 우선한다.

## Research Verification

리뷰 본문에 들어가는 핵심 주장은 반드시 출처 강도를 확인한다.

- 가능하면 공식 발표, 논문, 제품 문서, 저장소 README 같은 1차 출처를 먼저 쓴다.
- YouTube, 슬라이드, Pulse, LinkedIn feed는 discovery map으로 취급한다.
- 낮은 신뢰도의 intake claim은 final_review 본문에 그대로 올리지 않는다.
- 검증이 약한 내용은 source note나 runlog에 남기고, 본문에서는 제외하거나 `확인 필요`로 낮춘다.

## Writing Verification

리뷰/리포트/발표 원고를 만들면 다음을 확인한다.

- `.codex/rules/writing-harness.md`의 금지 표현이 남아 있지 않은가?
- `.automation/writing-style-audit-harness.md`의 intro, conclusion, emphasis hierarchy 기준을 통과하는가?
- figure와 caption이 독자 중심으로 작성되었는가?
- 이미지 생성 정보가 본문 설명과 분리되어 있는가?
- 링크, 볼드, 기울임, 음영 박스, caption이 실제 렌더링에서 보이는가?
- source claim과 해석이 구분되는가?

## HTML / Markdown Rendering

final_review나 human-facing report를 만들면 HTML companion을 생성하고 확인한다.

기본 명령:

```powershell
python scripts\markdown_to_html.py --mode auto <topic>\reports\<file>.md
```

확인 항목:

- HTML이 같은 basename으로 생성되었는가?
- hero subtitle, section map, evidence links, callout, figure caption이 보이는가?
- 이미지 상대경로가 깨지지 않는가?
- 공유 패키지에 `artifacts/final_review/figures/`가 같이 포함되는가?

## Obsidian / OpenProject / Share Package

AI_Tech_Review 산출물은 로컬 파일에서 끝나지 않는 경우가 많다.

- 사용자가 명시적으로 제외하지 않으면 Obsidian mirror를 갱신한다.
- OpenProject 업데이트 요청이 있으면 work package를 먼저 읽고 lockVersion을 확인한다.
- 큰 PPTX/PDF 첨부가 제한될 수 있으므로, 실패 시 로컬 경로와 직접 URL을 description/comment에 남긴다.
- 최종 리뷰가 source check, prose audit, figure review, HTML rendering을 통과해 공유 가능한 상태가 되면 사용자에게 `이제 배포용으로 정리할까요?`라고 먼저 묻는다. 사용자가 이미 배포나 메일 발송을 요청한 경우에는 바로 진행한다.
- 공유용 ZIP이나 메일 패키지를 만들 때는 `scripts/html_to_dist.py`를 우선 사용해 `<topic>/dist/index.html`, 같은 폴더의 image/SVG asset, 그리고 `<topic>/dist.zip`을 만든다.
- 배포 패키지는 `[local-ref-check] ok`를 확인하고, Playwright나 브라우저로 `dist/index.html`을 열어 hero, 주요 figure, reference 링크가 보이는지 확인한다.
- 검증용 screenshot은 의도한 산출물이 아니면 `dist/`와 zip에 남기지 않는다.
- 이메일 발송 요청이 있으면 `dist.zip`을 첨부한다. Outlook 자동화가 실패하면 Gmail connector를 사용할 수 있으며, 발송 id나 실패 사유를 runlog에 남긴다.

## Image Verification

이미지를 생성하거나 배치했으면 다음을 확인한다.

- 이미지가 주제를 설명하는가, 아니면 장식으로만 보이는가?
- 캡션이 짧고 명확한가?
- generated image metadata가 남아 있는가?
- HTML/Markdown/슬라이드에서 이미지 크기와 글자 가독성이 충분한가?
- figure manifest 또는 runlog에 생성 목적과 검토 메모가 남아 있는가?

## Change Hygiene

- 사용자가 만든 unrelated change는 되돌리지 않는다.
- 검증용 스크린샷, 임시 리포트, 브라우저 프로필은 repo root에 남기지 않는다.
- 작업 후 final response에는 바꾼 파일, 검증 명령, 남은 위험을 짧게 적는다.
