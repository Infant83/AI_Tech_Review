---
title: "Skywork Image Prompt Pack - TabPFN OLED AI Tech Review Letters"
date: 2026-05-10
slug: tabpfn-oled-manufacturing-foundation-model
status: ready-for-generation
---

# Skywork Image Prompt Pack

목적: `AI Tech Review Letters` 웹진형 리뷰에 넣을 수 있는 Skywork Image 후보를 만들기 위한 입력 패킷이다. 실제 본문에는 PNG export, project/artifact URL, 채택 메모가 확보된 그림만 올린다.

## 공통 스타일

- Category: `인포그래픽` 또는 `포스터`
- 비율: 16:9
- 스타일: 차분한 과학/기술 editorial infographic, 흰 배경, graphite line, muted teal, deep red accent, light warm paper texture
- 텍스트 정책: 이미지 안의 긴 한국어 문장 금지. 필요한 경우 1-3단어 영어 label만 허용. 최종 한국어 라벨은 HTML/SVG 후처리.
- 피할 것: fake logo, fake UI, stock-photo lab, generic AI cloud, glowing brain, dense Korean text, exaggerated factory automation scene

## Prompt A - Table Junction One-Cut Infographic

```text
Create a 16:9 editorial infographic for a technology webzine article.

One-sentence message:
TabPFN is most useful in OLED R&D and manufacturing at the tabular junction where molecular, device, and process records meet and decide which expensive next experiment deserves attention.

Must show:
- Left stream: molecular cards, small quantum-calculation sheets, descriptor tiles.
- Center stream: OLED device stack samples, measurement curves, lifetime test cards.
- Right stream: manufacturing recipe cards, inspection-feature tiles, lot-history records.
- These streams converge into one clean tabular sorting surface.
- A small ranked queue leaves the table toward DFT, device experiment, and pilot-line check trays.

Avoid:
No Korean text, no fake logo, no fake UI labels, no AI cloud, no glowing brain, no unrealistic robot factory, no photorealistic stock image.

Style:
High-end science magazine infographic, restrained white background, graphite linework, muted teal and deep red accents, clear hierarchy, enough empty margin for later Korean annotation.
```

## Prompt B - Candidate Compression Poster

```text
Create a 16:9 poster-like editorial explainer.

One-sentence message:
In OLED inverse design, TabPFN should be shown as a filter that reduces generated molecule candidates before expensive DFT and device experiments.

Must show:
- Many candidate molecule cards entering from the left.
- A compact analytical filter in the center with spreadsheet-like tiles and probability/ranking cues, but no readable text.
- A much smaller set of candidate cards exiting toward three trays: DFT recalculation, device experiment, pilot check.
- A subtle feedback loop from the experiment trays back to a label ledger.

Avoid:
No exact numbers, no fake labels, no long text, no molecule names, no company logos, no overstated "automatic discovery" mood.

Style:
Editorial science illustration, precise but not slide-like, white paper texture, teal path for accepted candidates, red path for rejected risk, clean visual rhythm.
```

## Prompt C - Manufacturing Boundary Social Card

```text
Create a square or 4:5 social summary card for internal sharing.

One-sentence message:
Use TabPFN first where a well-defined table can change the next experiment or process check; be cautious when the problem requires causal claims or out-of-distribution manufacturing decisions.

Must show:
- Three vertical zones: "try first", "supporting layer", "use with caution" as short English labels only.
- Small icons or abstract objects for molecular screening, multimodal bridge, production decision risk.
- A simple boundary line between exploratory analytics and production decision.

Avoid:
No Korean paragraph text, no legal-looking warning stamp, no fake dashboard, no overdramatic risk color.

Style:
Clean AI Tech Review Letters share card, restrained color, readable at thumbnail size, magazine-like not marketing-like.
```

## Archive Procedure

1. Skywork Image Agent에서 위 prompt 중 하나를 실행한다.
2. Project URL과 artifact URL을 `figure_manifest.md`에 기록한다.
3. 원본 PNG를 `skywork_exports/image_candidates/`에 저장한다.
4. 본문 후보 복사본을 `artifacts/final_review/figures/candidates/skywork-image/`에 둔다.
5. 텍스트 오류, 가짜 로고, 과장된 사실 claim, HTML 렌더링 품질을 확인한다.
6. 채택된 경우에만 `reports/*_final_review.md`에 figure로 삽입한다.
