---
title: AI Updates Weekly Artwork Infographic Briefs
date: 2026-05-09
status: draft
target:
  - Skywork Image
  - GPT Image 2 / imagegen
scope:
  - reports/2026-05-09_ai-updates-weekly_final_review.md
  - artifacts/final_review/figures/
---

# Artwork Infographic Briefs

이 문서는 현재 리뷰의 다음 그래픽 패스에서 Skywork Image와 GPT Image 2/imagegen에 넣을 후보 brief입니다. 목적은 plain SVG 패널을 그대로 늘리는 것이 아니라, 잡지형 artwork infographic 후보를 만들고, 필요하면 SVG/HTML 라벨을 얹어 최종 figure로 다듬는 것입니다.

## 공통 생성 원칙

- 긴 한국어 문장을 이미지 안에 넣지 않습니다.
- 정확한 라벨, 화살표, 출처명은 생성 후 SVG/HTML로 얹습니다.
- 가짜 로고, 가짜 UI, 깨진 글자, 의미 없는 AI cloud, generic neural network 배경을 피합니다.
- 색은 차분한 과학/기술 editorial palette를 씁니다: warm paper, muted teal, soft amber, ink gray.
- 생성 이미지 위에 정확한 라벨을 후처리할 때는 큰 라벨 박스를 사물 위에 얹지 않습니다. 이미지가 이미 정보가 많은 경우에는 `작은 번호 배지 + 하단/측면 범례`를 기본 후보로 둡니다.
- 각 후보는 `prompt`, `tool route`, `project/artifact URL`, `original export`, `accept/reject note`를 남깁니다.

## Candidate A. Harness Stack

Adjacent section:

- `하네스는 모델이 업무를 통과하게 만드는 장치입니다`

Message:

- 모델 하나가 업무 산출물로 이어지려면 주변에 맥락, 도구, 기억, 권한, 평가, 승인, 병합과 되돌리기가 함께 놓여야 합니다.

Skywork Image prompt:

```text
Create a magazine-style technology infographic, 16:9.
Message: an AI model becomes useful at work when surrounded by a harness of context, tools, memory, permissions, evaluation, approval, merge and rollback.
Scene: a central compact AI work engine on a clean desk, surrounded by document folders, API cables, permission badge, memory ledger, test checklist, approval stamp, Git merge rails, rollback handle, and final work output tray.
Composition: central object with 7-8 clearly separated surrounding zones, large negative space for later Korean labels, calm hierarchy.
Style: Quanta-like editorial science illustration, warm paper texture, muted teal and amber accents, refined infographic look, no corporate slide style.
Avoid: readable text, fake logos, fake software UI, neural network cloud, dense labels, photorealistic stock look.
Text: no text inside image.
```

GPT Image 2/imagegen prompt:

```text
Editorial science-and-technology illustration of an AI agent workbench. A glowing central work engine is connected to document stacks, an access badge, API cables, a memory ledger, test checklist, approval stamp, Git merge rails, rollback handle, and a final output tray. Warm paper texture, clean composition, muted teal and amber, high-quality magazine infographic style. Leave open space for later labels. No readable text, no logos, no fake UI, no generic neural network or cloud.
```

Expected post-processing:

- Add exact Korean labels around objects in SVG/HTML.
- Keep caption short; the figure should explain the harness stack without many sentences.

## Candidate B. Reference Map

Adjacent section:

- `에이전트 경쟁은 실행 환경을 함께 묻기 시작했습니다`

Message:

- 하네스는 모델 주변에 기준 자료, 작업 절차, 업무 앱 연결, 오픈소스 도구, 개발자 워크플로, 거버넌스를 붙여 실제 업무 조건을 만듭니다.

Skywork Image prompt:

```text
Create a polished editorial infographic, 16:9, source-map style.
Message: different AI updates point to the same design layer around agents: harness engineering.
Scene: six execution-condition islands around a central work-harness hub. Islands should visually suggest source-of-truth reference documents and research papers, work procedures, workplace app connections such as mail and calendars, open-source terminal/repository tools, developer workflow tools, and governance controls such as audit, delegated permission, and human review. Connect them with clean thin lines to the central hub.
Composition: central hub, six balanced clusters, lots of whitespace, designed like a magazine explanatory graphic.
Style: clean editorial infographic, warm off-white background, restrained colors, subtle paper texture.
Avoid: long text, logos, company badges, fake article screenshots, crowded arrows.
Text: no readable text. Use abstract icons only; Korean labels will be added later.
```

GPT Image 2/imagegen prompt:

```text
Magazine-style explanatory artwork showing six execution-condition clusters connected to a central agent harness hub. The clusters visually suggest source-of-truth reference documents and research papers, work procedures, workplace app connections such as mail and calendars, open-source terminal tools, developer merge workflow, and governance controls such as audit, delegated permission, and human review. Warm off-white background, refined editorial infographic style, subtle lines and icon-like objects, generous whitespace. No readable text, no logos, no fake UI.
```

Expected post-processing:

- Add compact Korean labels: `기준 자료`, `작업 절차`, `업무 앱 연결`, `오픈소스 도구`, `개발자 워크플로`, `거버넌스`.
- If these labels cover the clusters, replace them with small numbered badges and a bottom legend.
- Link caption to References section.

## Candidate C. Connector as Permission Gate

Adjacent section:

- `Connector는 편의 기능이자 권한의 입구입니다`

Message:

- connector는 사용자가 업무 데이터에 쉽게 접근하는 손잡이이면서, 관리자에게는 권한과 감사 지점을 만드는 통로입니다.

Skywork Image prompt:

```text
Create a one-cut editorial infographic, 16:9.
Message: AI connectors are both convenience handles and permission gates.
Scene: on the left, workplace data objects such as mail envelopes, calendar pages, cloud document folders, and shared drive boxes. In the middle, a visible permission gate with keycard, policy sliders, audit log strip, and privacy filter. On the right, an AI work surface producing a concise work output.
Composition: left-to-right flow, three clear zones, enough open space for later Korean labels and arrows.
Style: polished magazine technology infographic, soft teal, muted amber, ink-gray outlines, warm paper background.
Avoid: real brand logos, long text, fake email UI, unreadable labels, glowing cyberpunk style.
Text: no text inside image.
```

Expected post-processing:

- Add labels only after export: `업무 데이터`, `권한 게이트`, `AI 작업면`, `산출물`.
- Add a small dashed audit path if useful.

## Candidate C2. Enterprise Agent Operating Path

Adjacent section:

- `기업용 에이전트는 권한과 승인을 지나야 업무에 들어갑니다`

Message:

- 기업용 에이전트는 답변을 잘 만드는 것만으로 충분하지 않습니다. 업무 데이터 접근, 권한 범위, 문서 산출물, 사람 검토, 승인, 감사 기록이 하나의 운영 경로로 이어져야 합니다.

Why current Figure 4 is weak:

- `enterprise-harness-illustration-v2-web.png` has relevant objects: documents, lock, checklist, stamp, identity badge.
- But it reads as an atmospheric desk scene. The reader cannot easily see the operating path from data access to approval and audit.
- This figure should become an information graphic, not just an editorial illustration.

Skywork Image prompt:

```text
Create a polished enterprise technology infographic, 16:9.
Message: an enterprise AI agent becomes usable only when data access, permission scope, AI draft/output, human review, approval, and audit log are connected as one operating path.
Scene: left-to-right workflow with five clear zones: 1) business data and documents, 2) permission boundary with access card and policy controls, 3) AI work surface producing a document draft, 4) human review and approval checkpoint, 5) audit log and compliance record. Use concrete objects, not abstract clouds.
Composition: calm editorial infographic, clear flow path, enough whitespace for later Korean labels and arrows. Avoid crowded desk decoration.
Style: refined magazine technology infographic, warm paper background, muted teal, amber, ink gray, professional but not corporate slide art.
Avoid: readable text, fake UI, logos, long labels, generic neural network, cyberpunk glow, unrelated office props.
Text: no readable text inside the image; Korean labels will be added later in SVG/HTML.
```

GPT Image 2/imagegen prompt:

```text
Use case: infographic-diagram
Asset type: enterprise AI section figure
Primary request: a text-free editorial infographic showing the operating path around an enterprise AI agent.
Scene/background: warm paper background, clean technology workspace.
Subject: five clear zones connected left-to-right: business data and documents, permission boundary, AI document draft, human review and approval checkpoint, audit log and compliance record.
Composition/framing: 16:9, clear path, separated zones, generous whitespace for later Korean labels.
Style/medium: magazine-style science and technology infographic, refined line art, muted teal and amber accents.
Constraints: no readable text, no logos, no fake UI, no generic AI cloud; do not make it a decorative desk scene.
```

Expected post-processing:

- Add exact Korean labels after export: `업무 데이터`, `권한 범위`, `AI 산출물`, `사람 검토`, `승인·감사 기록`.
- If the generated image gives good texture but weak sequence, use it only as a base and overlay deterministic arrows.
- Reject if it becomes another desk still-life.

## Candidate D. Memory and Evaluation Loop

Adjacent section:

- `오래 맡기는 일일수록 기억은 선별되어야 합니다`

Message:

- 장기 작업에서는 모든 기록을 들고 가는 양보다, 다음 작업에 쓸 기억을 고르고 결과를 기준에 맞춰 다시 보는 구조가 중요합니다.

Revised route:

- 이 figure는 순서, 조건, 재시도 경로가 핵심이므로 이미지 생성 결과를 바로 본문에 넣지 않습니다.
- 먼저 deterministic SVG로 `작업 기록 -> 기억 선별 -> 작업 문맥 -> 에이전트 작업 -> 평가 기준 -> 사람 승인 / 재시도 계획`의 통제 흐름을 고정합니다.
- Skywork Image 또는 GPT Image 2/imagegen은 후보 배경이나 대체 section opener로만 비교합니다.

Skywork Image prompt:

```text
Create a calm magazine-style process infographic, 16:9.
Message: long-running AI agents need selected memory and evaluation loops.
Scene: a workbench with a memory ledger, a small agent work engine, an evaluation checklist, a retry loop track, and a human approval stamp. Show selected notes moving into the work engine, output going to checklist, failed item returning through a retry path.
Composition: simple loop with only four or five objects, clear separation, no clutter, open space for Korean labels.
Style: editorial science illustration, warm paper, muted teal and amber, clean lines.
Avoid: lots of arrows, tiny helper text, fake UI, generic brain imagery.
Text: no readable text.
```

Expected post-processing:

- Compare this against the deterministic control-loop SVG, not against the old imagegen icon-flow version.
- Reject generated candidates that look like a cute object parade, even if the texture is pleasant.

## Candidate E. Coding Merge Bottleneck

Adjacent section:

- `AI 코딩의 병목은 이제 변경 관리에 남습니다`

Message:

- 코드 생성 속도가 올라갈수록 테스트, 리뷰, 병합, 되돌리기, 기록 관리가 팀 작업의 병목이 됩니다.

Skywork Image prompt:

```text
Create an editorial technology illustration, 16:9.
Message: when AI generates many code changes quickly, the bottleneck moves to test, review, merge, rollback and history.
Scene: many paper code fragments and colored branch ribbons flowing toward a central review-and-test checkpoint, then splitting into merge rail, rollback spool, and version history ledger.
Composition: movement from left chaos to right organized change management; one clear checkpoint in the middle.
Style: refined magazine infographic, hand-drawn technical objects, warm paper, muted teal, blue, amber.
Avoid: real code text, fake IDE screenshots, logos, dark cyberpunk, cluttered arrows.
Text: no readable text.
```

Expected post-processing:

- Current bitmap Figure 7 is acceptable; use this candidate only if a more explicit infographic is needed.

## Selection Rule for This Review

1. Generate Skywork Image candidates for B and C first.
2. Generate GPT Image 2/imagegen candidates for A and D if the SVG diagrams feel too slide-like.
3. Keep the current bitmap Figures 1, 4, and 7 unless a new candidate clearly improves subject clarity.
4. Use SVG/HTML labels after generation for Korean terms and exact arrows.
5. Archive rejected candidates with one-line reasons.
